import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "ResuMatch AI - Resume Optimizer"
    
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ats_db")
    SQLITE_DATABASE_URL: str = (
        "sqlite:////tmp/local_ats.db"
        if os.getenv("VERCEL")
        else "sqlite:///./local_ats.db"
    )
    
    # Supabase Storage Configurations
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET_NAME: str = os.getenv("SUPABASE_BUCKET_NAME", "ats-resumes")

settings = Settings()
