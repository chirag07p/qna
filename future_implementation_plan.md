# Future Implementation Plan & TODO List

This document acts as a roadmap and architectural blueprint to upscale the **Q&A Search Assistant** into an enterprise-grade cognitive search platform under a **100% Free & Local-First** setup (zero cloud hosting, zero paid API keys).

---

## 🚀 Future Roadmap & TODO List

### Phase 1: Local Database & JWT Security
- [ ] Initialize standard SQLite database schema (`qna.db`) via SQLAlchemy.
- [ ] Build local user schemas and session tokens using `python-jose` and `bcrypt`.
- [ ] Setup API endpoints under `/api/auth` and implement token security middleware.
- [ ] Implement backend migrations to ingest preloaded spreadsheet answers into the database.

### Phase 2: Local Cognitive Vector Matcher
- [ ] Incorporate `sentence-transformers` library and cache `all-MiniLM-L6-v2` locally on server boot.
- [ ] Create a local file-based **FAISS** vector index.
- [ ] Upgrade `server/matcher.py` to support hybrid scoring:
  - **50% Semantic Score** (FAISS dense embeddings)
  - **30% TF-IDF / Token Score** (exact keywords)
  - **20% Levenshtein Ratio** (RapidFuzz string distance)
- [ ] Add domain keyword boosts dynamically during hybrid score construction.

### Phase 3: Drag & Drop Dataset Upload
- [ ] Build React drag-and-drop wizard components to upload `.xlsx` and `.csv` files.
- [ ] Configure dynamic CSV headers mapping to determine custom question/answer columns on upload.
- [ ] Implement background threads to compute embeddings and index newly uploaded spreadsheets dynamically.

### Phase 4: Glassmorphic Administrative Grid
- [ ] Build administrative tab panel showing virtualized data tables.
- [ ] Enable cell double-click edit, row additions, and deletions with instant database updates.
- [ ] Design search conflict manager flagging elements where scores overlap by <5%.
- [ ] Provide a download function to export any active database table back as an Excel file.

### Phase 5: Containerization & Deployment
- [ ] Create a secure, multi-stage server `Dockerfile`.
- [ ] Compile a `docker-compose.yml` defining unified backend and frontend orchestration.

---

## 🏗️ System Architecture (100% Free & Offline)

```mermaid
graph TD
    %% Styling
    classDef clientStyle fill:#eef2ff,stroke:#6366f1,stroke-width:2px,color:#1e1b4b;
    classDef serverStyle fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#14532d;
    classDef storageStyle fill:#fffbeb,stroke:#f59e0b,stroke-width:2px,color:#78350f;
    classDef engineStyle fill:#faf5ff,stroke:#a855f7,stroke-width:2px,color:#3b0764;

    %% Nodes
    subgraph Client ["🎨 Premium React Frontend (SPA - Local Server)"]
        UI_Search["Search Dashboard<br>(Glassmorphic UI)"]:::clientStyle
        UI_Admin["Knowledge Editor<br>(CRUD Spreadsheet Grid)"]:::clientStyle
        UI_Upload["Dynamic Excel/CSV Ingester<br>(Drag & Drop)"]:::clientStyle
        UI_Analytics["Analytics & Logs Viewer<br>(Performance Metrics)"]:::clientStyle
    end

    subgraph Server ["🖥️ Scalable FastAPI Backend (Local Dev/Docker)"]
        API_Auth["Auth Router<br>(Local JWT Validation)"]:::serverStyle
        API_Search["Search Router<br>(Hybrid Search Engine)"]:::serverStyle
        API_KB["Knowledge Base Router<br>(CRUD & Datasets)"]:::serverStyle
        IngestionPipeline["Chunker & Indexer Pipeline<br>(Background Threads)"]:::serverStyle
    end

    subgraph Storage ["📂 Storage Layer (0 Cost / Local File System)"]
        RelationalDB["SQLite File DB<br>- Datasets & Q&A Rows<br>- Local Users & Logs"]:::storageStyle
        VectorDB["FAISS File Index<br>- 384d Dense Vectors<br>- Local Binary Serialization"]:::storageStyle
    end

    subgraph AI_Engine ["🧠 Cognitive Matching Engines (100% Free & Local)"]
        DenseEmbed["SentenceTransformers<br>all-MiniLM-L6-v2<br>(Local CPU Embeddings)"]:::engineStyle
        FuzzyEngine["RapidFuzz Engine<br>(Fuzzy String Ratios)"]:::engineStyle
        KeywordEngine["Keyword Rule-Based Booster<br>(Regex Overlap Check)"]:::engineStyle
    end

    %% Flows
    UI_Search -->|1. Authenticated Query| API_Search
    UI_Admin -->|2. Manage Q&As / CRUD| API_KB
    UI_Upload -->|3. Upload CSV/Excel| API_KB
    
    API_KB -->|Store Metadata & Rows| RelationalDB
    API_KB -->|Trigger Ingestion Background Task| IngestionPipeline
    
    IngestionPipeline -->|Calculate Embeddings| DenseEmbed
    IngestionPipeline -->|Index Dense Vectors| VectorDB
    
    API_Search -->|Retrieve Matches| VectorDB
    API_Search -->|Retrieve Full Metadata & Answers| RelationalDB
    
    API_Search -->|Evaluate Similarity| DenseEmbed
    API_Search -->|Apply String Matching| FuzzyEngine
    API_Search -->|Domain Rule Scoring| KeywordEngine
    
    class UI_Search,UI_Admin,UI_Upload,UI_Analytics clientStyle;
    class API_Auth,API_Search,API_KB,IngestionPipeline serverStyle;
    class RelationalDB,VectorDB storageStyle;
    class DenseEmbed,FuzzyEngine,KeywordEngine engineStyle;
```

---

## 🛠️ Storage & Engine Architecture Choices

1. **Complete Local Isolation (0 Operating Cost)**:
   - Use **SentenceTransformers `all-MiniLM-L6-v2`** running locally on the CPU (RAM overhead: ~120MB, query latency: <10ms) to compute 384-dimensional dense semantic vectors. No external API keys needed.
2. **Database Engine**:
   - Use **SQLite** for relational tables (Datasets, Q&A rows, search analytics logs, local users). Zero memory overhead when idle, highly performant.
3. **Vector Storage**:
   - Use **FAISS (CPU variant)** written directly to a binary file index in the workspace to bypass paid vector databases.

---

## 🧪 Verification & Testing Plan

### Automated Coverage
* Validate local SQLite transactions using Python unit testing libraries.
* Verify vector calculations are returned with high precision under 15ms.
* Run API route suite: `python -m pytest server/test_main.py`

### Manual Verification
1. **Spreadsheet Upload Verification**: Test massive ingestions in `DatasetManager` using local mock spreadsheets (>1,000 rows).
2. **Deep Semantic Test**: Query using conceptual synonyms (e.g. query "How do I secure an account reset link?" versus target "What is the procedure for updating user credentials?").
3. **Responsive UI Audit**: Guarantee smooth transitions and glassmorphism renders perfectly on screens of all sizes (360px wide through 4K displays).
