# SmartJobMatch AI — Intelligent Resume-Based Job Discovery Platform

SmartJobMatch AI is a full-stack, AI-augmented job discovery and matching platform designed to analyze technical resumes, ingest and normalize job postings from LinkedIn (permitted/authorized methods and compliant mock adapter) and top ATS platforms (Greenhouse, Lever, Verified Feeds), calculate multi-factor compatibility scores (0–100%), automatically shortlist top-tier opportunities (70%+ default), and manage the application lifecycle through an intuitive Kanban pipeline.

---

## 🎯 Candidate Profile & Default Configuration

This deployment is pre-configured and seeded for **Akshay Sharma** (Full-Stack Software Engineer with 5+ years experience, ex-TCS, Accenture, Infosys):
- **Core Technical Stack:** Java, Spring Boot, Spring MVC, Microservices, REST APIs, ReactJS, JavaScript, SQL, MySQL, MongoDB, Kafka, AWS, Azure, Docker, Kubernetes, Jenkins, Terraform, CI/CD.
- **Default Location:** Bengaluru, Karnataka, India (with configurable Hybrid/Remote options).
- **Target Roles:**
  1. Senior Java Developer
  2. Java Backend Developer
  3. Java Software Engineer
  4. Spring Boot Developer
  5. Microservices Engineer
  6. Full-Stack Developer — Java + React
  7. Full-Stack Software Engineer
  8. Cloud-Native Java Engineer

---

## 🛠️ Architecture & Technology Stack

```
Resume Upload (PDF/DOCX)
  ↓ PyMuPDF / python-docx Text Extraction
Regex & NER Profile Parsing (Skills, Experience, Projects, Education)
  ↓
Job Source Adapters (LinkedIn Permitted/Mock, Greenhouse, Lever, Curated Feeds)
  ↓
Job Normalization & SHA-256 Content Deduplication
  ↓
Intelligent Matching Engine (Skills 35%, Semantic TF-IDF 25%, Exp 15%, Title 10%, Location 10%, Edu 5%)
  ↓
Automatic Shortlisting (Threshold ≥ 70%) & Pipeline Tracking
  ↓
React 19 + TypeScript + Vite + Tailwind CSS Dashboard
```

- **Backend:** Python 3.12+ / 3.14, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PyMuPDF, python-docx, APScheduler, Scikit-learn (TF-IDF & Cosine Similarity).
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, React Router v7, Axios, Lucide React, Recharts.
- **Database:** SQLite (local development zero-config) and PostgreSQL (production Docker Compose).
- **Testing:** Pytest (22 backend unit/integration tests) + Vitest (5 frontend component tests).

---

## 📁 Project Directory Structure

```
smartjobmatch-ai/
├── Full_Stack_Software_Engineer.pdf    # Candidate reference resume
├── docker-compose.yml                  # Full stack multi-container orchestration
├── README.md                           # Documentation and user guide
├── .gitignore                          # Standard gitignore
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application setup & lifecycle
│   │   ├── api/
│   │   │   ├── deps.py                 # Dependency injection (db, current user)
│   │   │   └── v1/
│   │   │       ├── health.py           # Health checks
│   │   │       ├── auth.py             # User registration & JWT auth
│   │   │       ├── resumes.py          # Upload, parse, edit, versioning
│   │   │       ├── jobs.py             # Search, filter, manual import
│   │   │       ├── matches.py          # Match calculation & analytics
│   │   │       ├── shortlist.py        # Shortlist lifecycle & notes
│   │   │       ├── applications.py     # Kanban pipeline tracking
│   │   │       └── preferences.py      # Target roles, weights & locations
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic BaseSettings
│   │   │   └── security.py             # Password hashing (PBKDF2/SHA256) & JWT
│   │   ├── db/
│   │   │   ├── session.py              # Engine & sessionmaker
│   │   │   ├── base.py                 # Declarative Base & model registry
│   │   │   └── init_db.py              # Auto-seeding default user & preferences
│   │   ├── models/                     # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── match.py
│   │   │   ├── shortlist.py
│   │   │   ├── application.py
│   │   │   └── preference.py
│   │   ├── schemas/                    # Pydantic v2 schemas
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── match.py
│   │   │   ├── shortlist.py
│   │   │   ├── application.py
│   │   │   └── preference.py
│   │   ├── services/
│   │   │   ├── resume_parser.py        # PDF/DOCX text & skill extraction
│   │   │   ├── job_normalizer.py       # Canonical normalization & content hashing
│   │   │   ├── deduplication.py        # Idempotent upsert & deduplication
│   │   │   ├── job_matcher.py          # 6-dimension scoring engine & explanations
│   │   │   ├── shortlist_service.py    # Auto-shortlisting & status updates
│   │   │   └── job_sync_service.py     # End-to-end multi-source synchronizer
│   │   ├── integrations/
│   │   │   ├── base.py                 # Abstract BaseJobSource
│   │   │   ├── linkedin.py             # LinkedIn compliant adapter & mock mode
│   │   │   ├── greenhouse.py           # Greenhouse Public Board API connector
│   │   │   ├── lever.py                # Lever Public Postings API connector
│   │   │   └── mock_data.py            # High-fidelity Bengaluru job fixtures
│   │   └── scheduler/
│   │       └── scheduler.py            # APScheduler background sync job
│   ├── alembic/                        # Database migration scripts
│   ├── tests/                          # 22 automated Pytest suites
│   ├── requirements.txt                # Python dependencies
│   ├── pytest.ini                      # Test runner configuration
│   ├── .env.example                    # Environment variable template
│   └── Dockerfile                      # Backend container definition
└── frontend/
    ├── src/
    │   ├── components/                 # Navbar, Sidebar, JobCard, JobDetailModal, ScoreBadge
    │   ├── pages/                      # Dashboard, Resume, JobSearch, Shortlist, Applications, Settings
    │   ├── services/                   # Axios API service client
    │   ├── types/                      # TypeScript domain models
    │   ├── App.tsx                     # React Router routes
    │   └── main.tsx                    # Entry point
    ├── package.json                    # Node dependencies
    ├── tsconfig.app.json               # TypeScript configuration
    ├── vite.config.ts                  # Vite + Tailwind + Vitest proxy config
    ├── nginx.conf                      # Production Nginx reverse proxy
    └── Dockerfile                      # Multi-stage production container
```

---

## 🚀 Quickstart Guide (Local Development)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment (Windows PowerShell)
py -3 -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
- **Backend API:** `http://localhost:8000`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Alternative ReDoc Documentation:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend

# Install Node modules
npm install

# Start Vite development server
npm run dev
```
- **Frontend Application:** `http://localhost:5173`

---

## 🧪 Test Execution & Verification

### Running Backend Tests (Pytest)
```bash
cd backend
.\venv\Scripts\pytest.exe -v
```
**Results (22 passing tests):**
- `test_resume_parser.py`: PDF extraction, contact regex, technical skills categorization, years of experience extraction, model validation, and live parsing of `Full_Stack_Software_Engineer.pdf`.
- `test_job_normalizer.py`: SHA-256 content hashing, skill extraction, experience range detection, work-mode inference.
- `test_deduplication.py`: Multi-source external ID matching, canonical URL matching, content-hash idempotency.
- `test_matching_engine.py`: High skill overlap scoring, missing required skill penalties, experience compatibility curves, and overall weighted calculation.
- `test_shortlist.py`: Automatic threshold filtering (≥70%), manual status transitions, and note persistence.
- `test_scheduled_sync.py`: Idempotent multi-source execution, new vs updated counting, and error resiliency.
- `test_api_endpoints.py`: Health check, JWT authentication, preferences update, and manual job import.

### Running Frontend Tests (Vitest)
```bash
cd frontend
npm test
```
**Results (5 passing tests):**
- `ScoreBadge.test.tsx`: Verifies color schemes, icons, and labels for Excellent (85%+), Strong (70-84%), Potential (55-69%), Low (<55%), and null scores.

---

## 📄 Importing Resumes

1. **Automatic Import (Built-in):**
   - On initial startup, if `Full_Stack_Software_Engineer.pdf` is present in the workspace, the backend automatically extracts and seeds the active profile for Akshay Sharma.
2. **Web Interface Upload:**
   - Navigate to `http://localhost:5173/resume`.
   - Click **Upload PDF / DOCX** to select any new resume document.
   - The parser extracts your full name, headline, contact info, total years of experience, technical skills grouped by category, employment history with highlights, projects, education, and certifications.
   - Click **Edit Extracted Details** to adjust or append custom skills, or switch between version histories.

---

## 🔌 Job Source Integrations & Credentials

### 1. LinkedIn Job Discovery (`linkedin.py`)
- **Compliance Guarantee:** The adapter strictly adheres to LinkedIn Terms of Service. It **never scrapes private pages**, bypasses bot protections, or uses unauthorized endpoints.
- **Operating Modes:**
  - **Permitted Mock Mode (Default):** Pre-configured with realistic Bengaluru & Remote Java opportunities (Target, Flipkart, Intuit, Cisco, Walmart). Tagged clearly as `linkedin_mock` to prevent false representation.
  - **Manual Import Mode:** Users can paste any LinkedIn job URL or job description directly from the Job Search page via the **Import Job Listing** dialog.
  - **Official LinkedIn Live API Mode:** If an enterprise LinkedIn Developer App is available:
    ```env
    LINKEDIN_CLIENT_ID=your_client_id
    LINKEDIN_CLIENT_SECRET=your_client_secret
    LINKEDIN_API_TOKEN=your_oauth_token
    ```
    Requires `r_jobs` or Talent Solutions Partner permission.

### 2. Greenhouse Job Boards (`greenhouse.py`)
- Connects to public job boards (e.g. `boards-api.greenhouse.io/v1/boards/{board_token}/jobs`).
- Configure `GREENHOUSE_BOARD_TOKEN` in `backend/.env`.

### 3. Lever Job Boards (`lever.py`)
- Connects to public Lever postings (e.g. `api.lever.co/v0/postings/{site_name}`).
- Configure `LEVER_SITE_NAME` in `backend/.env`.

### 4. Scheduled Synchronization (`APScheduler`)
- Runs automatically in the background every 6 hours (configurable in `Settings` or `SYNC_SCHEDULE_HOURS`).
- An instant **Sync Jobs** button is available in the top navigation bar.

---

## 🐳 Docker Deployment

To run the complete production stack (PostgreSQL + FastAPI + Nginx React Frontend):

```bash
docker-compose up --build -d
```
- Frontend: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

