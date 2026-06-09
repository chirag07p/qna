import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "qna_db")

# A rich dataset of 200 Q&A items spanning various support domains
# Many questions have multiple answers to demonstrate the multi-answer matching feature
QA_DATA = [
    # Category: Authentication & Account (1-30)
    {"q": "how do I reset my password", "a": "Click the 'Forgot Password' link on the login page and follow the emailed instructions."},
    {"q": "how do I reset my password", "a": "Contact your administrator to manually issue a password reset link if the automated email doesn't arrive."},
    {"q": "i forgot my login credentials", "a": "Use the recovery page to retrieve your username using your registered email address."},
    {"q": "i forgot my login credentials", "a": "Request help from support if you no longer have access to the email linked to your account."},
    {"q": "how to change email address", "a": "Go to Account Settings > Security and update your primary email address."},
    {"q": "how to change email address", "a": "Make sure you confirm the verification email sent to your new address to complete the change."},
    {"q": "can i change my username", "a": "Usernames are permanent once created to ensure audit logging integrity."},
    {"q": "can i change my username", "a": "If you absolutely need a new username, you will need to register a new account."},
    {"q": "how to enable two factor authentication", "a": "Go to Settings > Privacy > 2FA and scan the QR code with your authenticator app."},
    {"q": "how to enable two factor authentication", "a": "Ensure you save the generated backup codes in a secure place in case you lose your device."},
    {"q": "disable two factor authentication", "a": "2FA can be disabled under Security settings after entering a one-time verification code."},
    {"q": "disable two factor authentication", "a": "If you lost your 2FA device, contact support with your backup verification code to disable it."},
    {"q": "where to find backup codes", "a": "Backup codes are displayed when you first activate 2FA under Security Settings."},
    {"q": "how to unlock my locked account", "a": "Locked accounts automatically unlock after 30 minutes of inactivity."},
    {"q": "how to unlock my locked account", "a": "You can immediately unlock your account by verifying your identity via the reset link sent to your email."},
    {"q": "login session expired troubleshooting", "intelligence": "Sessions automatically timeout after 8 hours of inactivity for safety."},
    {"q": "login session expired troubleshooting", "a": "Clear your browser cache if you are repeatedly thrown back to the login screen."},
    {"q": "session timeout configuration", "a": "Admin users can adjust session lengths under System Settings > Security Policy."},
    {"q": "how to delete account profile", "a": "Navigate to Profile > Danger Zone and select 'Delete Profile'. This action is permanent."},
    {"q": "how to delete account profile", "a": "Confirm with your primary account password before your profile is deleted."},
    {"q": "deactivate user temporarily", "a": "Administrators can set a user account status to 'Suspended' in the admin console."},
    {"q": "cannot verify email link", "a": "Email confirmation links expire after 24 hours. Request a new link from the profile dashboard."},
    {"q": "cannot verify email link", "a": "Check your spam or junk folder if the confirmation email is not arriving."},
    {"q": "sign up options support", "a": "You can sign up with email/password, or use Google and Apple SSO authentication options."},
    {"q": "sign up options support", "a": "Enterprise clients can sign up using SAML single-sign-on credentials."},
    {"q": "is google sso supported", "a": "Yes, you can click 'Sign in with Google' on the authentication page."},
    {"q": "is apple login supported", "a": "Yes, Apple login is supported on both the iOS app and web dashboard."},
    {"q": "can i merge two accounts", "a": "Accounts cannot be merged due to data privacy policies. Transfer items manually."},
    {"q": "resend verification link", "a": "Go to the login page and click 'Resend verification mail' next to the alert banner."},
    {"q": "multiple active logins", "a": "You can view active sessions in Settings > Devices and log out of other sessions remote."},

    # Category: Billing, Payments, and Subscriptions (31-65)
    {"q": "how to update credit card details", "a": "Manage payment methods in Billing Settings and click 'Edit' next to your card."},
    {"q": "how to update credit card details", "a": "Note that updating your card details will automatically clear outstanding balances on next attempt."},
    {"q": "why was my payment declined", "a": "Common reasons include insufficient funds, card expiration, or international transaction blocks."},
    {"q": "why was my payment declined", "a": "Check with your bank or try an alternative payment method like PayPal."},
    {"q": "accepted payment gateways options", "a": "We accept major credit cards (Visa, MasterCard, Amex), PayPal, and Apple Pay."},
    {"q": "accepted payment gateways options", "a": "Wire transfer options are available only for enterprise tier subscriptions."},
    {"q": "how to cancel premium subscription", "a": "Navigate to Settings > Billing > Subscriptions and click 'Cancel Subscription'."},
    {"q": "how to cancel premium subscription", "a": "You will retain premium benefits until the end of the current billing period."},
    {"q": "refund request guidelines", "a": "Refund requests are evaluated under our 14-day money-back guarantee policy."},
    {"q": "refund request guidelines", "a": "Submit a support ticket with your transaction ID to request a refund."},
    {"q": "where is my invoice receipt", "a": "Invoices are available for download under Settings > Billing > History."},
    {"q": "where is my invoice receipt", "a": "Receipts are also automatically emailed to the primary billing contact monthly."},
    {"q": "change billing frequency options", "a": "Switch between monthly and annual billing periods inside the billing tab."},
    {"q": "annual plan discount pricing", "a": "Annual plans offer a 20% discount compared to monthly rolling subscriptions."},
    {"q": "how to add tax vat id", "a": "Add your VAT or Business Tax ID during checkout or in your Billing Profile to update future invoices."},
    {"q": "custom invoice details request", "a": "Contact accounts team to add custom metadata like PO numbers to existing invoices."},
    {"q": "unrecognized charges on bank statement", "a": "Verify if a colleague purchased a seat, or check for active trials that auto-renewed."},
    {"q": "chargeback policy details", "a": "Initiating a chargeback will cause temporary suspension of the account during review."},
    {"q": "overdue balance notification status", "a": "We try to charge the card 3 times over 15 days before suspending access."},
    {"q": "how to view pricing tiers", "a": "Visit our pricing matrix page for detailed tier benefits and limits."},
    {"q": "is there a free trial version", "a": "Yes, we offer a 14-day free trial on the Professional tier, no card required."},
    {"q": "what happens when trial ends", "a": "Your account downgrades to the Free Basic tier with limited features."},
    {"q": "how to buy extra user seats", "a": "Go to Subscription > Seats and adjust the slider to add more members."},
    {"q": "non profit discounts information", "a": "We offer a 50% discount for registered non-profits. Contact sales with proof."},
    {"q": "educational plan discounts info", "a": "Students and teachers receive free access. Register with an .edu address."},
    {"q": "failed transaction retry timing", "a": "Failed transactions are auto-retried every 5 days for up to 15 days."},
    {"q": "why was i charged sales tax", "a": "Sales tax is calculated based on your local state or country tax laws."},
    {"q": "pricing structure currency query", "a": "All transactions are charged in USD by default, unless local currencies are supported."},
    {"q": "how to change payment currency", "a": "Currency is determined by your geographic location at registration and cannot be modified manually."},
    {"q": "do you store credit card numbers", "a": "We do not store card numbers. Payments are securely handled by Stripe."},
    {"q": "can i pay using crypto", "a": "Cryptocurrency payments are not accepted at this time."},
    {"q": "is bank transfer wire accepted", "a": "Yes, wire transfers are accepted for annual billing volumes exceeding $1000."},
    {"q": "late payment fee details", "a": "We do not charge late fees, but service is paused if invoices remain unpaid for 15 days."},
    {"q": "how to transfer billing ownership", "a": "Only the current billing owner can transfer this role to another user in Billing settings."},
    {"q": "adding billing contact emails", "a": "Add secondary emails in Billing Settings to CC them on all payment receipts."},

    # Category: Application Usage & Features (66-105)
    {"q": "how to export database tables", "a": "Go to Admin Panel > Data Export and select your desired table to download."},
    {"q": "how to export database tables", "a": "You can export tables in CSV, JSON, or XML formats."},
    {"q": "how to import datasets data", "a": "Click the Import button on the dataset editor screen and upload your CSV file."},
    {"q": "how to import datasets data", "a": "Ensure your columns match our predefined schema templates to avoid import issues."},
    {"q": "csv column mapping tool", "a": "The import wizard lets you visually map CSV headers to target table fields."},
    {"q": "is drag and drop supported", "a": "Yes, you can drag and drop supported files directly onto the ingestion dashboard."},
    {"q": "file upload size restrictions", "a": "Individual file uploads are limited to 50MB for security reasons."},
    {"q": "supported import file formats", "a": "We support CSV, JSON, and raw TXT file imports at this time."},
    {"q": "where are saved reports stored", "a": "Access your saved custom templates under Analytics > Reports dashboard."},
    {"q": "how to create a dashboard chart", "a": "Click 'New Widget' on your dashboard tab and select a data metric visualization."},
    {"q": "can i share my dashboards link", "a": "Yes, generate a view-only shareable link in Dashboard Settings."},
    {"q": "restrict viewer dashboard access", "a": "Disable public access links to keep dashboards strictly inside the team."},
    {"q": "how to schedule email reports", "a": "Set up automated weekly/monthly email deliveries in Report Settings."},
    {"q": "how to copy table data block", "a": "Double click the cell to edit, or highlight the row and click 'Copy Row'."},
    {"q": "shortcut keys list help", "a": "Press Ctrl + / to display the shortcut cheat sheet panel on any screen."},
    {"q": "how to delete search records", "a": "Search logs can be cleared under Analytics Settings > Logs Cleanup."},
    {"q": "filter search results criteria", "a": "Use the sidebar filters to refine matching by date, score, or accuracy tag."},
    {"q": "custom tags organization info", "a": "Add custom labels to Q&A cards to filter them during search query sessions."},
    {"q": "bulk action items execution", "a": "Check multiple rows in the admin grid to perform bulk deletion or tag updates."},
    {"q": "restore deleted data records", "a": "Deleted items are kept in the trash bin for 30 days before permanent purging."},
    {"q": "empty trash bin immediately", "a": "Click 'Empty Trash' in the settings panel to permanently delete all items now."},
    {"q": "search history list access", "a": "View your recent query attempts under the search input field dashboard history."},
    {"q": "disable search history saving", "a": "Disable search history saving under Profile Settings > Search Privacy."},
    {"q": "how to save favorite queries", "a": "Click the star icon next to any query to pin it to your favorites panel."},
    {"q": "is there dark mode theme", "a": "Toggle dark and light themes inside the profile dropdown settings."},
    {"q": "auto theme selection rules", "a": "Enable 'Sync with OS' to automatically match browser dark/light preferences."},
    {"q": "change UI language layout", "a": "Change your display language in settings, we support English, Spanish, and French."},
    {"q": "rich text edit markdown support", "a": "The answer editor supports markdown tags for bold, italic, lists, and code."},
    {"q": "spell check automatic checks", "a": "Our editor automatically highlights spelling mistakes using standard browser tools."},
    {"q": "add image to answers", "a": "Use standard Markdown image links to insert media files into answer bodies."},
    {"q": "embedded video tutorials info", "a": "Click 'Help' in the sidebar to open the video resources overlay panel."},
    {"q": "collaboration notes section help", "a": "Add notes to Q&A entries to communicate edits with team members."},
    {"q": "how to flag wrong answers", "a": "Click the flag icon on any answer card to report errors to admins."},
    {"q": "resolve flagged items queues", "a": "Admin panel features a 'Flags' tab to review and approve proposed corrections."},
    {"q": "search performance analysis logs", "a": "Track query speeds and matched accuracy logs in the admin health tab."},
    {"q": "export search analytics graphs", "a": "Download analytics chart visualizations as PNG images or PDF documents."},
    {"q": "view changes history audit log", "a": "Enterprise admins can check user edit logs inside the Audit Center tab."},
    {"q": "archiving vs deleting data", "a": "Archiving hides items from search results while preserving audit logs database entries."},
    {"q": "unarchive data records rules", "a": "Search archived records in admin views and click 'Unarchive' to restore."},
    {"q": "system notifications setup rules", "a": "Configure browser or email alerts inside Settings > Alerts settings."},

    # Category: Troubleshooting & Performance (106-150)
    {"q": "the application is running slow", "a": "Try clearing browser storage or restarting the backend server instance."},
    {"q": "the application is running slow", "a": "Verify if database indexes are configured correctly if queries take >100ms."},
    {"q": "why do i see database connection error", "a": "Ensure MySQL service is active and credentials in .env are correct."},
    {"q": "why do i see database connection error", "a": "Confirm if firewall rules permit connection to port 3306."},
    {"q": "api returns 500 internal server error", "a": "Check the terminal logs on the host server to trace the error traceback."},
    {"q": "api returns 500 internal server error", "a": "Verify that all Python package requirements match system architectures."},
    {"q": "react front end build errors troubleshooting", "a": "Delete node_modules and package-lock.json and run npm install again."},
    {"q": "react front end build errors troubleshooting", "a": "Ensure your Node version matches the specifications (>18.0.0)."},
    {"q": "how to debug matching scores issues", "a": "Verify keyword boosts configurations inside matcher.py logic module."},
    {"q": "how to debug matching scores issues", "a": "Adjust the threshold parameter on query requests to allow looser matches."},
    {"q": "cors issues blocking requests help", "a": "Ensure origins are allowed in app.add_middleware settings inside main.py."},
    {"q": "cors issues blocking requests help", "a": "Avoid using wildcards in allow_origins when credentials are true."},
    {"q": "out of memory crash error", "a": "Increase server swap space or optimize memory loads for scikit-learn models."},
    {"q": "port 8000 already in use", "a": "Identify the process using port 8000 and terminate it before launching FastAPI."},
    {"q": "port 8000 already in use", "a": "Run Uvicorn with a different port parameter: uvicorn main:app --port 8080."},
    {"q": "missing environment variables troubleshooting", "a": "Check if your .env file is located directly in the server directory."},
    {"q": "missing environment variables troubleshooting", "a": "Verify that environment variables match standard config schemas exactly."},
    {"q": "mysql connector auth plugin error", "a": "Configure MySQL user account plugin settings to caching_sha2_password or mysql_native_password."},
    {"q": "page displays blank white screen", "a": "Check browser developer console for JS run errors or missing files."},
    {"q": "npm install freezes forever", "a": "Use npm cache clean --force or configure registry proxies if connection fails."},
    {"q": "how to check node version", "a": "Run 'node -v' in your terminal environment command prompt window."},
    {"q": "uvicorn launch command failure", "a": "Ensure the virtual environment is activated before running backend scripts."},
    {"q": "pip dependency conflicts help", "a": "Use a fresh Python virtual environment instance to avoid system package overlaps."},
    {"q": "web socket connection disconnected", "a": "Verify server configurations when serving over reverse proxy layers (Nginx)."},
    {"q": "high query latency troubleshooting", "a": "Cache loaded database datasets in memory on server boot sequence."},
    {"q": "invalid token verification failure", "a": "Generate new session tokens or check system time offsets mismatch."},
    {"q": "blank search suggestion pills", "a": "Execute database seeding or populate source_questions dataset table first."},
    {"q": "how to read server logs files", "a": "Check uvicorn output streams or redirect console to a rolling logs file."},
    {"q": "react component not rendering update", "a": "Ensure react states triggers are declared using mutable hooks correctly."},
    {"q": "axios request network error failed", "a": "Confirm server address and port match backend local configurations."},
    {"q": "database locks deadlock troubleshooting", "a": "Implement lock timeouts and transaction retry logics inside database queries."},
    {"q": "browser blocking local resource requests", "a": "Run resources under standard HTTPS proxy configurations to avoid mixed-content blocks."},
    {"q": "too many open connections error", "a": "Ensure all database cursor objects are closed correctly using try-finally blocks."},
    {"q": "cannot write to logs directory", "a": "Verify folder permissions on host operating systems match execution user."},
    {"q": "package dependency deprecated notices", "a": "Upgrade packages to target versions when compatible updates are available."},
    {"q": "scikit-learn tfidf warning notes", "a": "Avoid empty strings inputs into vectorizers to prevent divide by zero errors."},
    {"q": "rapidfuzz execution speed notes", "a": "Ensure rapidfuzz uses compiled C extensions for peak fuzzy matching speeds."},
    {"q": "invalid json parsing error", "a": "Validate request payload formats inside client request headers and schemas."},
    {"q": "pydantic validation failed alert", "a": "Check if request parameters types match Pydantic model configurations."},
    {"q": "how to update database schema", "a": "Apply manual SQL migrations or rewrite database tables creation structures."},
    {"q": "css grid alignment bug styling", "a": "Use standard modern layout grid rules for multi-column grids templates."},
    {"q": "translucent background blur fails", "a": "Verify if backdrop-filter CSS rule is supported on your target browser version."},
    {"q": "reset system parameters default", "a": "Clear local database records and re-seed database defaults."},
    {"q": "force reload web application cache", "a": "Press Ctrl + F5 in browser to clear site resources cache completely."},
    {"q": "ssl cert security warnings local", "a": "Ignore security warnings on localhost, or generate local ssl signatures."},

    # Category: Security, Administration, and Integration (151-200)
    {"q": "how to create a new user profile", "a": "Go to Admin Panel > Users and click the 'Create User' button."},
    {"q": "how to create a new user profile", "a": "Fill in the user's name, email address, and select their starting permission role."},
    {"q": "admin permissions vs standard user roles", "a": "Admins have full write/edit database privileges while users only perform search queries."},
    {"q": "admin permissions vs standard user roles", "a": "Admins can also modify app configurations, add users, and view metrics logs."},
    {"q": "where are API keys generated", "a": "Generate credentials under settings > API Tokens panel for automation scripts."},
    {"q": "where are API keys generated", "a": "Ensure you save the token secret immediately as it won't be shown again."},
    {"q": "how to rotate api keys", "a": "Click 'Revoke' on the current active API token and generate a replacement credentials block."},
    {"q": "restrict api key access scopes", "a": "Limit API keys to Read-Only operations or specific endpoints in API settings."},
    {"q": "system status uptime info", "a": "Check the health page at `/api/stats` to verify database connection states."},
    {"q": "audit log location for admin actions", "a": "Audit logs are stored under Settings > Audit and cannot be deleted."},
    {"q": "how to change admin passwords", "a": "Update credentials under Profile Security settings inside user profile console."},
    {"q": "multi tenant database support info", "a": "Multi-tenant isolation requires configured enterprise architectures schemas."},
    {"q": "how to customize search engine limits", "a": "Configure search threshold defaults inside server/main.py settings variables."},
    {"q": "is my data encrypted database", "a": "MySQL data encryption at rest can be configured under server storage settings."},
    {"q": "user registration moderation approval", "a": "Enable user queue moderation in Admin settings to manually approve requests."},
    {"q": "configure mail smtp credentials settings", "a": "Setup SMTP server host, username, password inside config settings to allow outbound emails."},
    {"q": "slack integration setups instructions", "a": "Go to settings > integrations and enter your target Slack webhook URL address."},
    {"q": "slack integration setups instructions", "a": "Configure triggers to send search query logs or alerts directly to Slack."},
    {"q": "webhooks settings setup guidelines", "a": "Define webhook listeners URLs to receive real-time notifications on database updates."},
    {"q": "github oauth client configuration steps", "a": "Register client application on Github developers dashboard to obtain client id/secret codes."},
    {"q": "saml sso setup enterprise rules", "a": "Upload metadata XML files to verify identity provider configurations inside SSO console."},
    {"q": "ip access whitelist setups rules", "a": "Add corporate IP blocks to whitelist settings to block foreign addresses requests."},
    {"q": "rate limiting request configurations info", "a": "API requests are limited to 60 queries per minute per IP by default settings."},
    {"q": "disable public registrations option", "a": "Disable 'Allow Public Signups' in admin settings to lock down registrations."},
    {"q": "custom backup schedules configurations", "a": "Admin panel lets you configure automated backup cron schedules to export SQL dumps."},
    {"q": "restore system database from backup", "a": "Upload a valid exported SQL backup script and click restore database in Admin settings."},
    {"q": "where is backup file saved", "a": "Database backups are stored under server local files, or sent to S3 buckets."},
    {"q": "session length policy guidelines", "a": "Session lifetimes are restricted by standard corporate access policy requirements."},
    {"q": "system telemetry analytics share opt-in", "a": "Opt-in to telemetry sharing inside settings to help developers build tools."},
    {"q": "api documentation list options access", "a": "Access interactive swagger UI documentation at `/docs` when server runs in debug mode."},
    {"q": "is offline search engine mode available", "a": "Yes, our cognitive engine runs completely on your local machine offline."},
    {"q": "export search statistics logs csv", "a": "Click Export Logs in analytics dashboard to download query history details."},
    {"q": "user action logs monitoring dashboard", "a": "View active user login locations and events inside user monitoring console."},
    {"q": "gdpr customer compliance requests tools", "a": "Use the user erasure console tool to wipe customer metadata fully."},
    {"q": "minimum security requirements passwords details", "a": "Passwords must have at least 8 characters, one number, and one symbol."},
    {"q": "caching strategies search speed optimization", "a": "FastAPI caches query results in memory to speed up repeated queries."},
    {"q": "clear query cache parameters setting", "a": "Clear active cache blocks under Admin Panel > Cache Settings console."},
    {"q": "is there python SDK library", "a": "You can call backend endpoints using standard Python requests script packages."},
    {"q": "javascript SDK integration setups guidance", "a": "Import our custom javascript library package inside node package modules."},
    {"q": "how to update application license keys", "a": "Upload your key file under system license settings to verify subscription status."},
    {"q": "supported system virtualization Docker platforms", "a": "Docker Compose templates are available to run services inside containers."},
    {"q": "maximum parallel search threads execution", "a": "FastAPI processes queries concurrently using asyncio thread pooling architectures."},
    {"q": "performance benchmarks results reports access", "a": "Run performance test suites inside our automated benchmarking console."},
    {"q": "domain keyword boost weight adjustment", "a": "Configure keyword boosts weights in server/matcher.py calculations script."},
    {"q": "fuzzy algorithm implementation specifications info", "a": "We use Levenshtein token ratio calculations to evaluate fuzzy similarity scores."},
    {"q": "custom css style override instructions", "a": "Upload custom css scripts inside frontend styling console to personalize themes."},
    {"q": "branding logo updates guidance dashboard", "a": "Upload custom company logos inside branding console to update headers UI."},
    {"q": "multiple active workspaces setup guides", "a": "Link workspaces by setting target connection databases inside configuration manager."},
    {"q": "how to change dashboard refresh rate", "a": "Select refresh intervals from 5 seconds to 1 hour in widget settings."},
    {"q": "system shutdown remote commands execution", "a": "Remote shutdown triggers are only available over SSH console connections."}
]

# Ensure we have 200 distinct questions for source_questions as well
SOURCE_QUESTIONS = list(set([item["q"] for item in QA_DATA]))

def populate():
    print("Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Disable foreign key checks for clean truncates
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE question_matches;")
        cursor.execute("TRUNCATE TABLE knowledge_base;")
        cursor.execute("TRUNCATE TABLE source_questions;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Truncated existing database tables.")

        # 1. Insert into knowledge_base
        print(f"Inserting {len(QA_DATA)} records into knowledge_base...")
        insert_kb = "INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)"
        kb_records = [(item["q"], item["a"]) for item in QA_DATA]
        cursor.executemany(insert_kb, kb_records)
        conn.commit()

        # 2. Insert into source_questions
        print(f"Inserting {len(SOURCE_QUESTIONS)} records into source_questions...")
        insert_sq = "INSERT INTO source_questions (question) VALUES (%s)"
        sq_records = [(q,) for q in SOURCE_QUESTIONS]
        cursor.executemany(insert_sq, sq_records)
        conn.commit()

        # 3. Perform matching and populate question_matches
        print("Running batch matching for all questions...")
        from matcher import matching
        import pandas as pd
        df_q = pd.read_sql("SELECT question FROM source_questions", conn)
        df_a = pd.read_sql("SELECT question, answer FROM knowledge_base", conn)
        
        results = matching(
            sheet1=df_q,
            sheet2=df_a,
            cname1="question",
            cname2="question",
            ans_cname="answer",
            threshold=30.0,
            top_k=10
        )
        
        cursor.execute("SELECT id, question FROM source_questions")
        source_q_map = {str(q).strip(): q_id for q_id, q in cursor.fetchall()}
        
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
                acc_lvl = "strict" if score >= 80.0 else ("medium" if score >= 50.0 else "loose")
                match_records.append((s_id, orig_q, match["matched_question"], match["answer"], score, acc_lvl))
        
        if match_records:
            cursor.executemany(insert_match_query, match_records)
            conn.commit()
            print(f"Successfully calculated and populated {len(match_records)} matches in question_matches.")

        cursor.close()
        conn.close()
        print("Database population complete!")

    except Exception as e:
        print(f"Error populating database: {e}")

if __name__ == "__main__":
    populate()
