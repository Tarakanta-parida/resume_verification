import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

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
