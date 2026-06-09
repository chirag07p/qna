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

# Hardcoded seed data to avoid xlsx involvement
SEED_ANSWERS = [
    {"Question": "login error occurred", "Answer": "Clear browser cookies and cache, then restart the browser."},
    {"Question": "trouble logging in to application", "Answer": "Try logging in via Incognito mode or a different browser."},
    {"Question": "account signing and credentials support", "Answer": "Contact support to reset your locked login session."},
    {"Question": "password reset procedure", "Answer": "Click on Forgot Password on the login screen to receive a reset link."},
    {"Question": "retrieve lost password", "Answer": "Contact system administrator to manually trigger a password reset mail."},
    {"Question": "credentials profile update", "Answer": "Go to settings to update your username or passphrase."},
    {"Question": "payment issue and failures", "Answer": "Use an alternative payment method like PayPal or bank transfer."},
    {"Question": "credit card declined", "Answer": "Contact your bank to verify if international/online payments are blocked."},
    {"Question": "billing history and receipts", "Answer": "Check your monthly invoice inside the subscription panel."},
    {"Question": "account registration options", "Answer": "Yes, you can register using Google, Apple, or your email address."},
    {"Question": "social media login registration", "Answer": "You can sign up using Facebook or other social platforms if enabled."},
    {"Question": "new profile setup rules", "Answer": "Registration requires a valid email and password confirmation."},
    {"Question": "refund policy and requests", "Answer": "Refunds can be requested within 14 days of purchase via your billing portal."},
    {"Question": "returns and chargebacks support", "Answer": "To request a transaction rollback, contact billing support directly."},
    {"Question": "order disputes and cancellations", "Answer": "Orders can only be modified or canceled before shipping."},
    {"Question": "canceling your subscription", "Answer": "Go to Account Settings > Subscriptions > Cancel to turn off auto-renew."},
    {"Question": "stop recurring membership auto-renew", "Answer": "Submit a ticket to cancel your subscription auto-billing."},
    {"Question": "delete paid account details", "Answer": "Deleting your profile will immediately terminate all paid subscriptions."},
    {"Question": "app crash troubleshooting", "Answer": "Try clearing app storage, updating to the latest version, or reinstalling the app."},
    {"Question": "mobile platform system crash help", "Answer": "Report the bug logs to developer team using the in-app help button."},
    {"Question": "device compatibility warnings", "Answer": "Make sure your operating system meets the minimum hardware specifications."},
    {"Question": "updating account profile email", "Answer": "You can update your email under Profile Settings > Security > Update Email."},
    {"Question": "modify email login contact", "Answer": "Submit a request to change the email where you receive billing updates."},
    {"Question": "username change restrictions", "Answer": "Your username is fixed but your profile contact details can be modified."},
    # Extra answers to demonstrate multiple answers matching
    {"Question": "login error occurred", "Answer": "Check if your credentials caps-lock is enabled and verify your account status."},
    {"Question": "login error occurred", "Answer": "Try logging in using an alternative browser or clear application cookies."},
    {"Question": "payment issue and failures", "Answer": "Verify that your payment method has sufficient balance and is enabled for online transactions."},
    {"Question": "payment issue and failures", "Answer": "Try an alternative checkout process or payment gateway if the current one is failing."},
    {"Question": "change my primary email address", "Answer": "Ensure the new email address is verified by checking the confirmation link sent to it."},
    {"Question": "change my primary email address", "Answer": "If you signed up with social logins, you must change your email on the social provider platform."}
]

SEED_QUESTIONS = [
    {"Question": "i am facing issue in login"},
    {"Question": "how to reset password"},
    {"Question": "payment failed"},
    {"Question": "can I sign up with Google"},
    {"Question": "how to request a refund for my order"},
    {"Question": "cancel my premium membership subscription"},
    {"Question": "the android app keeps crashing on startup"},
    {"Question": "change my primary email address"}
]

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
    
    # 1. Seed knowledge_base from memory dataset
    print("Seeding answers to knowledge_base...")
    df_answers = pd.DataFrame(SEED_ANSWERS)
    if not df_answers.empty:
        # Disable foreign key checks for truncate
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE knowledge_base;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Truncated existing records in 'knowledge_base' table.")
        
        insert_query = "INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)"
        records = []
        for _, row in df_answers.iterrows():
            question = str(row["Question"]).strip() if pd.notna(row["Question"]) else ""
            answer = str(row["Answer"]).strip() if pd.notna(row["Answer"]) else ""
            if question or answer:
                records.append((question, answer))
                
        if records:
            cursor.executemany(insert_query, records)
            conn.commit()
            print(f"Successfully migrated {len(records)} records to 'knowledge_base'.")

    # 2. Seed source_questions from memory dataset
    print("Seeding questions to source_questions...")
    df_questions = pd.DataFrame(SEED_QUESTIONS)
    if not df_questions.empty:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE source_questions;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Truncated existing records in 'source_questions' table.")
        
        insert_query = "INSERT INTO source_questions (question) VALUES (%s)"
        records = []
        for _, row in df_questions.iterrows():
            question = str(row["Question"]).strip() if pd.notna(row["Question"]) else ""
            if question:
                records.append((question,))
                
        if records:
            cursor.executemany(insert_query, records)
            conn.commit()
            print(f"Successfully migrated {len(records)} records to 'source_questions'.")

    # 3. Perform batch matching using data queried entirely from MySQL
    print("Performing batch matching of source questions against knowledge base via MySQL...")
    try:
        from matcher import matching
        
        # Query datasets directly from MySQL
        df_q = pd.read_sql("SELECT question FROM source_questions", conn)
        df_a = pd.read_sql("SELECT question, answer FROM knowledge_base", conn)
        
        if not df_q.empty and not df_a.empty:
            # Run matcher with 30.0 threshold to capture loose, medium, and strict matches
            results = matching(
                sheet1=df_q,
                sheet2=df_a,
                cname1="question",
                cname2="question",
                ans_cname="answer",
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
            print("Skipping matching migration: MySQL tables are empty.")
    except Exception as e:
        print(f"Error migrating matches: {e}")
        
    cursor.close()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()

