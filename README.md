# ResuMatch AI - Streamlit Resume & JD Optimizer

ResuMatch AI is a production-ready, pure Python Streamlit web application that optimizes resumes to pass Applicant Tracking Systems (ATS) and maximize job match scores.

It extracts keywords from target job descriptions, calculates ATS match metrics, rewords experience bullets using strong action verbs and quantitative metrics, and generates optimized resumes in PDF, DOCX, and Plain Text formats—all without altering document structure, contact details, or background history.

---

##  Key Features

- **Multi-Format Document Upload**: Supports PDF (`.pdf`), Word (`.docx`), and structured JSON (`.json`) resume files.
- **Pre-Loaded Sample Candidates**: Includes ready-to-test candidate profiles (Software Engineer, Data Analyst, Product Manager, Marketing Specialist).
- **ATS Match Scoring & Taxonomy Engine**: Categorizes keywords across Technical Skills, Analytics & Data, Management & Methodologies, and Marketing & Tools.
- **Multi-Provider AI Optimization**: Calls Google Gemini (`gemini-2.0-flash`), OpenAI (`gpt-4o-mini`), or Anthropic Claude (`claude-3-5-sonnet`), with a robust local rule-based fallback engine if no API keys are provided.
- **Side-by-Side Comparison**: Live visual comparison between original and optimized resumes with interactive highlight toggles (`Added Keywords`, `Optimized Bullets`).
- **Multi-Format Exporting**: Download clean, ATS-friendly resumes in **DOCX**, **Print-Ready PDF (HTML)**, and **Plain Text**.
- **ATS Audit Report**: Comprehensive breakdown of keyword densities, category alignment scores, and formatting health checks.
- **Modern UI**: Dark/Light mode theme switching, glassmorphic card styling, gauge score visualizers, and responsive layout.

---

## 📂 Folder Structure

```
streamlit/
├── app.py                     # Main Streamlit application entrypoint
├── config.py                  # Settings & environment variable configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Application documentation
├── models/
│   ├── database.py            # SQLAlchemy engine & session factory (PostgreSQL / SQLite fallback)
│   └── db_models.py           # Database ORM models (Resume, JobDescription, ATSReport, OptimizedResume)
├── services/
│   ├── parser_service.py      # PDF, DOCX, JSON text extraction & resume structuring
│   ├── ats_service.py         # Tech taxonomy keyword extractor & ATS scoring engine
│   ├── optimizer_service.py   # Multi-LLM provider prompt layer & local rule fallback
│   ├── document_service.py    # HTML/PDF, DOCX, Plain Text generation & highlight tag processing
│   ├── storage_service.py     # Supabase file storage upload helper
│   └── sample_data.py         # Sample candidate profiles & job descriptions
├── utils/
│   └── ui_components.py       # Custom CSS themes, score gauges, progress bars, paper viewer
└── views/
    ├── dashboard_view.py      # Resume upload, JD input, template loader, optimization trigger
    ├── analysis_view.py       # Verdict gauges, category match bars, missing vs matched keyword tabs
    ├── comparer_view.py       # Side-by-side original vs optimized resume viewer with download buttons
    └── report_view.py         # Comprehensive ATS audit report & keyword density analysis
```

---

## 🚀 Setup & Execution

### 1. Prerequisites
Ensure Python **3.10+** is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables (Optional)
Create a `.env` file in the root directory to enable LLM model APIs and cloud storage:

```env
# Optional LLM API Keys (Falls back to local rule-based engine if omitted)
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
CLAUDE_API_KEY="your-claude-api-key"

# Optional Database & Storage Configuration (Falls back to local SQLite if omitted)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ats_db"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-key"
SUPABASE_BUCKET_NAME="ats-resumes"
```

### 4. Launch Application
Run the Streamlit app:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
