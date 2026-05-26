# Step-by-Step Developer TODO List (Beginner Friendly)

This document is a sequential, step-by-step guide to help you build the Excel Q&A Matching application. Each task includes explanations of **what to do**, **why we are doing it**, and the **exact command to run**.

---

## Folder Structure Map
Before we begin, this is how your workspace folders currently look:
```text
qna/
├── client/
│   ├── react-frontend/   <-- Your React frontend project (already created! ✅)
│   └── vite-frontend/    <-- (Unused Vite project)
├── server/               <-- Your Python FastAPI backend project (already created! ✅)
├── .venv/                <-- Your Python Virtual Environment sandbox (already created! ✅)
├── requirements.txt      <-- Python dependencies list (already created at root! ✅)
├── todo.md               <-- This checklist
└── implementation_plan.md <-- Your high-level design plan
```

---
## 🚀 PHASE 1: Backend Setup & Development (Python)

We will start with the backend because the frontend needs the backend APIs to send files and get matches.

---

### Step 0: Place your Excel Q&A Sheets
To make development and testing super convenient, we set up a local `data` directory in the backend containing your Excel sheets.
- [x] **Create a `data` folder:** Inside the `server/` directory, create a folder named `data`. *(Done! Created at `server/data/`)*
- [x] **Place your sheets:** Generate valid Excel sheets inside the `server/data/` folder using the automated Python command:
  ```powershell
  python -c "import pandas as pd; pd.DataFrame({'Question': ['i am facing issue in login', 'how to reset password', 'payment failed']}).to_excel('data/questions.xlsx', index=False); pd.DataFrame({'Question': ['login error occurred', 'password reset procedure', 'payment issue'], 'Answer': ['Please clear your browser cookies and cache.', 'Go to settings and click Reset Password.', 'Verify your card details and try again.']}).to_excel('data/answers.xlsx', index=False); print('Success: Created valid questions.xlsx and answers.xlsx!')"
  ```
  *(Done! Real Excel files generated successfully!)*
- [x] **Note their column names:** Check the column headers of the generated Excel sheets.
  * **Sheet 1 (questions.xlsx)**: `['Question']`
  * **Sheet 2 (answers.xlsx)**: `['Question', 'Answer']`
  *(Done! Verified successfully!)*

---

### Step 1: Create Backend Folder & Virtual Environment
A virtual environment (`.venv`) is a private sandbox for Python packages so they don't interfere with other projects on your computer.
- [x] **Create the backend folder:** Inside the main `qna` directory, create a folder named `server` (or `backend`). *(Done! You created `server`)*
- [x] **Open your terminal** and make sure you are in the `server` directory. *(Done! Your terminal is in `c:\Users\Chirag Pradhan\qna\server`)*
- [x] **Create the virtual environment:** Run: `python -m venv .venv` *(Done! Created at the root `qna/.venv`)*
- [x] **Activate the virtual environment:** This tells your terminal to use the sandbox. *(Done! You successfully activated it and saw `(.venv)` in the terminal!)*
  Since your virtual environment is in the root directory (`qna/.venv`) and you are in the `server` folder, run this exact command to activate it:
  ```powershell
  ..\.venv\Scripts\Activate.ps1
  ```
  *(Note: If you get a permission error in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first, then run the activation command above).*

---

### Step 2: Install Packages (Dependencies)
We need libraries for reading Excel files, running the web server, and doing the text similarity mapping.
- [x] **Create `requirements.txt`:** Create a file named `requirements.txt` containing the necessary packages. *(Done! Created at root `qna/requirements.txt` and `server/requirements.txt`)*
- [x] **Install the packages:** *(Done! You ran `pip install -r requirements.txt` inside your virtual environment)*
  ```powershell
  pip install -r requirements.txt
  ```

---

### Step 3: Write the Matching Engine (`matcher.py`)
This script contains the brain of our app—it compares questions and outputs the best answers.
- [x] **Create `matcher.py`:** Inside `server/`, create a file called `matcher.py`.
- [x] **Write the logic:**
  1. [x] Clean the text (lowercase it, remove extra spaces).
  2. [x] Write a function `calculate_fuzzy_score(q1, q2)` using `rapidfuzz` (e.g. `token_set_ratio`).
  3. [x] Write a function `calculate_tfidf_score(questions_list, queries_list)` using `scikit-learn`'s TF-IDF vectorizer, utilizing Natural Language Processing (NLP) and information retrieval to convert unstructured text into a format that machine learning algorithms can understand.
  4. [ ] Write a runner function `match_sheets(sheet1_df, sheet2_df, col1_name, col2_name, ans_col_name, threshold, top_k=3)` to pair rows, return the Top K matches for each query, and identify conflicts where multiple strong solutions exist.

---

### Step 4: Write the Server Web Routes (`main.py`)
FastAPI listens for requests sent by the browser (frontend), runs the matcher, and sends answers back.
- [ ] **Create `main.py`:** Inside `server/`, create a file called `main.py`.
- [ ] **Write these API Endpoints:**
  * `POST /api/upload`: Reads uploaded Excel files and returns their column names so the user can choose them.
  * `POST /api/match`: Takes the user's column choices, matching threshold, and `top_k` value, runs `matcher.py`, and returns results as an array of objects, each containing a list of matching solutions.
  * `POST /api/export`: Generates a styled Excel sheet with matched answers. Support export modes: "Best Match", "Multi-Column" (creates multiple columns for Top N answers), and "Concatenated" (merges multiple answers in one cell with bullets and confidence scores).
- [ ] **Add CORS middleware:** Configure it so your frontend (running on port `3000`) is allowed to talk to your backend (running on port `8000`).

---

### Step 5: Test the Backend
- [ ] **Start the backend server:** Run this in your backend terminal (within `server/`):
  ```powershell
  uvicorn main:app --reload
  ```
- [ ] **Verify it runs:** Open your browser and go to `http://localhost:8000/docs`. You should see an interactive Swagger documentation page where you can test your APIs!

---
---

## 🎨 PHASE 2: Frontend Setup & Development (React)

Your React frontend has already been created using `create-react-app` in `client/react-frontend/`. Now let's set it up to talk to the backend.

### Step 1: Install Frontend Packages
We need a library to send API requests (`axios`) and some modern icons (`lucide-react`).
- [ ] **Open a new terminal window** (keep the backend one running!).
- [ ] **Change directory into the React project:**
  ```powershell
  cd client/react-frontend
  ```
- [ ] **Install Axios and Lucide Icons:** Run:
  ```powershell
  npm install axios lucide-react
  ```

---

### Step 2: Configure Backend Proxy
To avoid running into networking cross-origin blockages (CORS), we tell React to redirect backend requests automatically.
- [ ] **Configure Proxy:** Open `package.json` inside `client/react-frontend/` and add this line near the top (above `"dependencies"`):
  ```json
  "proxy": "http://localhost:8000",
  ```

---

### Step 3: Build the UI Components
We want a beautiful UI, so we will build it in modern components.
- [ ] **Clean default files:** Open `src/App.js` and delete the default header content. Open `src/App.css` and delete default styles.
- [ ] **Create Component files:** Inside `client/react-frontend/src/`, create a folder named `components`.
- [ ] **Build `FileUpload.js`:** A drag-and-drop box for users to select Sheet 1 (questions) and Sheet 2 (answers).
- [ ] **Build `MatchConfig.js`:** Shows dropdown menus for choosing column names dynamically, along with a similarity percentage slider, a Top-K selector, and an Excel export format dropdown.
- [ ] **Build `ResultsTable.js`:** Displays rows of Sheet 1 with a "Conflicts/Multiple Solutions" badge where relevant. Allows expanding a row to reveal a slide drawer/expandable container showcasing all retrieved Top K alternative solutions as sleek cards. Users can click any alternative card to promote it to the primary answer (Click-to-Swap Override).
- [ ] **Build `DashboardStats.js`:** Displays numbers showing processed questions, average confidence, and a dedicated counter for "Multiple Solution Conflicts" to focus manual review.

---

### Step 4: Write Frontend Controller Logic (`App.js`)
Tie the components together using state variables.
- [ ] **Manage state in `src/App.js`:**
  * File state (`file1`, `file2`).
  * Mapping columns (`questionColumn1`, `questionColumn2`, `answerColumn2`).
  * Matching parameters (`threshold` value, `top_k` limit, and `exportMode`).
  * API states (`loading`, `error`, `results`).
- [ ] **Write HTTP triggers:**
  * Send uploaded files to `/api/upload` when selected to load column names.
  * Send matching configurations to `/api/match` (including `top_k`) when the user clicks "Start Matching".
  * Call `/api/export` (including selected `exportMode`) when the user clicks "Download Excel".

---

### Step 5: Design with Beautiful Styling (`App.css`)
- [ ] **Design custom glassmorphic rules:** Add smooth backgrounds, gradients, soft borders (`backdrop-filter: blur()`), glowing buttons, and hover animations to make the UI look premium.

---

### Step 6: Run and Test the Full Application
- [ ] **Start the React developer server:** Inside the `client/react-frontend` terminal, run:
  ```powershell
  npm start
  ```
- [ ] **Verify locally:** Your browser will open `http://localhost:3000`. 
- [ ] Upload two sample Excel sheets, select columns, click match, inspect results, adjust threshold, and download the finished sheet!
