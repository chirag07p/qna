import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "qna_db")

# Path to xlsx files
ANSWERS_PATH = os.path.join(os.path.dirname(__file__), "data", "answers.xlsx")
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "data", "questions.xlsx")

def migrate():
    print("Connecting to MySQL server...")
    # Connect without database first to create it if it doesn't exist
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"Database '{DB_NAME}' verified/created.")
    
    # Close initial connection
    cursor.close()
    conn.close()

    # Reconnect to the specific database
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    # Create knowledge_base table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Table 'knowledge_base' verified/created.")
    
    # Create source_questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Table 'source_questions' verified/created.")

    # Create question_matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_matches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source_question_id INT,
        source_question TEXT NOT NULL,
        matched_question TEXT NOT NULL,
        matched_answer TEXT NOT NULL,
        score FLOAT NOT NULL,
        accuracy_level VARCHAR(20) NOT NULL,
        FOREIGN KEY (source_question_id) REFERENCES source_questions(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    print("Table 'question_matches' verified/created.")
    
    # 1. Migrate answers.xlsx to knowledge_base
    if os.path.exists(ANSWERS_PATH):
        print(f"Reading Excel file: {ANSWERS_PATH}")
        df_answers = pd.read_excel(ANSWERS_PATH)
        
        if len(df_answers.columns) >= 2:
            q_col, a_col = df_answers.columns[0], df_answers.columns[1]
            print(f"Migrating answers using columns: Question='{q_col}', Answer='{a_col}'")
            
            # Disable foreign key checks for truncate
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE knowledge_base;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            print("Truncated existing records in 'knowledge_base' table.")
            
            insert_query = "INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)"
            records = []
            for _, row in df_answers.iterrows():
                question = str(row[q_col]).strip() if pd.notna(row[q_col]) else ""
                answer = str(row[a_col]).strip() if pd.notna(row[a_col]) else ""
                if question or answer:
                    records.append((question, answer))
                    
            if records:
                cursor.executemany(insert_query, records)
                conn.commit()
                print(f"Successfully migrated {len(records)} records to 'knowledge_base'.")
        else:
            print("Excel answers sheet must contain at least 2 columns.")
    else:
        print(f"Excel answers file not found at: {ANSWERS_PATH}")

    # 2. Migrate questions.xlsx to source_questions
    if os.path.exists(QUESTIONS_PATH):
        print(f"Reading Excel file: {QUESTIONS_PATH}")
        df_questions = pd.read_excel(QUESTIONS_PATH)
        
        if len(df_questions.columns) >= 1:
            q_col = df_questions.columns[0]
            print(f"Migrating source questions using column: '{q_col}'")
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE source_questions;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            print("Truncated existing records in 'source_questions' table.")
            
            insert_query = "INSERT INTO source_questions (question) VALUES (%s)"
            records = []
            for _, row in df_questions.iterrows():
                question = str(row[q_col]).strip() if pd.notna(row[q_col]) else ""
                if question:
                    records.append((question,))
                    
            if records:
                cursor.executemany(insert_query, records)
                conn.commit()
                print(f"Successfully migrated {len(records)} records to 'source_questions'.")
        else:
            print("Excel questions sheet must contain at least 1 column.")
    else:
        print(f"Excel questions file not found at: {QUESTIONS_PATH}")

    # 3. Perform batch matching and store in question_matches table
    if os.path.exists(QUESTIONS_PATH) and os.path.exists(ANSWERS_PATH):
        print("Performing batch matching of source questions against knowledge base...")
        try:
            from matcher import matching
            
            df_q = pd.read_excel(QUESTIONS_PATH)
            df_a = pd.read_excel(ANSWERS_PATH)
            
            if len(df_q.columns) >= 1 and len(df_a.columns) >= 2:
                q_col_q = df_q.columns[0]
                q_col_a = df_a.columns[0]
                a_col_a = df_a.columns[1]
                
                # Run matcher with 30.0 threshold to capture loose, medium, and strict matches
                results = matching(
                    sheet1=df_q,
                    sheet2=df_a,
                    cname1=q_col_q,
                    cname2=q_col_a,
                    ans_cname=a_col_a,
                    threshold=30.0,
                    top_k=10  # allow multiple matches
                )
                
                # Fetch source_questions ids for relational mapping
                cursor.execute("SELECT id, question FROM source_questions")
                source_q_map = {str(q).strip(): q_id for q_id, q in cursor.fetchall()}
                
                # Avoid foreign key constraint issues during TRUNCATE
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE question_matches;")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                print("Truncated existing records in 'question_matches' table.")
                
                insert_match_query = """
                INSERT INTO question_matches (source_question_id, source_question, matched_question, matched_answer, score, accuracy_level)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                match_records = []
                for res in results:
                    orig_q = str(res["original_question"]).strip()
                    s_id = source_q_map.get(orig_q)
                    
                    for match in res["matches"]:
                        score = match["score"]
                        if score >= 80.0:
                            acc_lvl = "strict"
                        elif score >= 50.0:
                            acc_lvl = "medium"
                        else:
                            acc_lvl = "loose"
                            
                        match_records.append((
                            s_id,
                            orig_q,
                            match["matched_question"],
                            match["answer"],
                            score,
                            acc_lvl
                        ))
                
                if match_records:
                    cursor.executemany(insert_match_query, match_records)
                    conn.commit()
                    print(f"Successfully migrated {len(match_records)} matches to 'question_matches'.")
            else:
                print("Skipping matching migration: Excel sheets have incorrect column structures.")
        except Exception as e:
            print(f"Error migrating matches: {e}")
        
    cursor.close()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
