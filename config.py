import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Prevent Streamlit/Google GenAI from showing "GOOGLE_API_KEY is not configured" banner
if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "not-used"

class Settings:
    PROJECT_NAME: str = "ResuMatch AI - Resume Optimizer"
    
    # Database URL (Defaults to empty string to avoid connecting to unconfigured localhost in Cloud)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Use cross-platform writable temp directory for SQLite database fallback
    temp_dir = tempfile.gettempdir().replace("\\", "/")
    SQLITE_DATABASE_URL: str = f"sqlite:///{temp_dir}/local_ats.db"
    
    # Supabase Storage Configurations
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET_NAME: str = os.getenv("SUPABASE_BUCKET_NAME", "ats-resumes")

settings = Settings()
