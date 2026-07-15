import os
import sys

# Add the current directory to sys.path to allow absolute imports of the 'app' package
# when running locally from the workspace root or on Vercel.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import shutil
import re
from typing import Any, cast
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
import io
import logging
from backend.app.core.config import settings
from backend.app.core.database import get_db, init_db
from backend.app.core.models import Resume, JobDescription, ATSReport, OptimizedResume
from backend.app.engine.pdf_parser import extract_text_from_pdf
from backend.app.engine.docx_parser import extract_text_from_docx
from backend.app.engine.ats_scorer import calculate_ats_metrics, extract_keywords_from_text
from backend.app.engine.prompt_layer import optimize_resume_data
from backend.app.engine.pdf_generator import generate_styled_resume_html
from backend.app.engine.docx_generator import generate_docx_from_data
from backend.app.engine.supabase_storage import upload_file_to_supabase

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ats-optimizer")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown (nothing needed for now)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Check
@app.get("/")
def read_root():
    return {"status": "running", "service": settings.PROJECT_NAME}

# Helper: Parse raw text into structured JSON sections (analogous to JS logic)
def parse_resume_text_to_structure(text: str, filename: str) -> dict:
    structure: dict[str, Any] = {
        "personalInfo": {
            "name": filename.replace("_", " ").split(".")[0],
            "email": "info@domain.com",
            "phone": "+1 (555) 000-0000",
            "github": "github.com/user",
            "linkedin": "linkedin.com/in/user"
        },
        "summary": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": []
    }

    # Regex search for Email & Phone
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phones = re.findall(r'\+?[0-9\s\-()]{7,18}', text)

    if emails:
        structure["personalInfo"]["email"] = emails[0]
    if phones:
        valid_phones = [p.strip() for p in phones if len(re.sub(r'[^0-9]', '', p)) >= 10]
        if valid_phones:
            structure["personalInfo"]["phone"] = valid_phones[0]

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        structure["personalInfo"]["name"] = lines[0]

    current_section = ""
    temp_bullets = []
    temp_company = ""
    temp_role = ""
    temp_duration = ""

    def save_experience():
        nonlocal temp_role, temp_company, temp_duration, temp_bullets
        if temp_role or temp_company or temp_bullets:
            structure["experience"].append({
                "role": temp_role or "Specialist",
                "company": temp_company or "Company Inc",
                "duration": temp_duration or "Present",
                "bullets": temp_bullets if temp_bullets else ["Assisted in daily team deliverables."]
            })

    for line in lines[1:]:
        lower_line = line.lower()
        is_header = len(line) < 40

        # Section Triggers
        if is_header and any(x in lower_line for x in ["summary", "profile", "objective", "professional summary", "career objective"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "summary"
            continue
        elif is_header and any(x in lower_line for x in ["skills", "competencies", "technologies", "key skills", "core competencies", "expertise", "skills & tools", "technical skills"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "skills"
            continue
        elif is_header and any(x in lower_line for x in ["experience", "employment", "work history", "professional experience", "employment history", "career history", "work experience"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "experience"
            continue
        elif is_header and any(x in lower_line for x in ["projects", "accomplishments", "key projects", "technical projects", "academic projects"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "projects"
            continue
        elif is_header and any(x in lower_line for x in ["education", "academic", "qualifications", "academic background", "credentials"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "education"
            continue
        elif is_header and any(x in lower_line for x in ["certifications", "licenses", "courses", "credentials"]):
            save_experience()
            temp_role, temp_company, temp_duration, temp_bullets = "", "", "", []
            current_section = "certifications"
            continue

        if current_section == "summary":
            structure["summary"] += (" " if structure["summary"] else "") + line
        elif current_section == "skills":
            skills = [s.strip() for s in re.split(r'[,|•\t]', line) if s.strip()]
            structure["skills"].extend(skills)
        elif current_section == "experience":
            # Check for year / duration signature
            if re.search(r'(19|20)\d{2}', line) or "present" in lower_line:
                save_experience()
                temp_bullets = []
                # Extract duration
                duration_match = re.search(r'((19|20)\d{2}\s*-\s*(present|(19|20)\d{2}))', line, re.IGNORECASE)
                temp_duration = duration_match.group(0) if duration_match else "Present"
                cleaned_line = line.replace(temp_duration, "").strip()
                headers = [h.strip() for h in re.split(r'[,|•\t-]', cleaned_line) if h.strip()]
                temp_role = headers[0] if len(headers) > 0 else "Engineer"
                temp_company = headers[1] if len(headers) > 1 else "Corporation"
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                temp_bullets.append(re.sub(r'^[•\-\*\s]+', '', line))
            else:
                if temp_bullets:
                    temp_bullets[-1] += " " + line
                else:
                    temp_bullets.append(line)
        elif current_section == "projects":
            if line.startswith("•") or line.startswith("-") or line.startswith("*"):
                if structure["projects"]:
                    structure["projects"][-1]["bullets"].append(re.sub(r'^[•\-\*\s]+', '', line))
            else:
                is_new_project = ("|" in line) or (not structure["projects"]) or (structure["projects"] and not structure["projects"][-1]["bullets"])
                if is_new_project:
                    headers = [h.strip() for h in re.split(r'[,|•\t-]', line) if h.strip()]
                    structure["projects"].append({
                        "name": headers[0] if len(headers) > 0 else "Personal Project",
                        "description": headers[1] if len(headers) > 1 else "Project Description",
                        "bullets": []
                    })
                else:
                    if structure["projects"] and structure["projects"][-1]["bullets"]:
                        structure["projects"][-1]["bullets"][-1] += " " + line
        elif current_section == "education":
            edu_keywords = ["b.tech", "b.e.", "m.tech", "b.s.", "m.s.", "bachelor", "master", "ph.d", "degree", "12th", "10th", "hsc", "ssc", "diploma", "science", "commerce", "arts", "high school", "school", "intermediate", "matriculation"]
            is_new_edu = any(k in lower_line for k in edu_keywords)
            
            # Extract year range or single year if present
            year_match = re.search(r'\b((19|20)\d{2}\s*(-\s*(present|(19|20)\d{2}))?)\b', line, re.IGNORECASE)
            year_val = year_match.group(0) if year_match else ""
            
            cleaned_line = line
            if year_val:
                cleaned_line = re.sub(re.escape(year_val), '', cleaned_line).strip()
                cleaned_line = re.sub(r'^[•\-\*\s|–]+|[•\-\*\s|–]+$', '', cleaned_line).strip()
            
            if is_new_edu:
                structure["education"].append({
                    "degree": cleaned_line,
                    "school": "",
                    "year": year_val
                })
            else:
                if structure["education"]:
                    # Continuation of last education block (like school name or details)
                    if year_val and not structure["education"][-1]["year"]:
                        structure["education"][-1]["year"] = year_val
                    
                    if cleaned_line:
                        if not structure["education"][-1]["school"]:
                            structure["education"][-1]["school"] = cleaned_line
                        else:
                            structure["education"][-1]["school"] += " | " + cleaned_line
                else:
                    structure["education"].append({
                        "degree": cleaned_line,
                        "school": "University",
                        "year": year_val or "2023"
                    })
        elif current_section == "certifications":
            cert_val = re.sub(r'^[•\-\*\s]+', '', line)
            if cert_val:
                if "certifications" not in structure:
                    structure["certifications"] = []
                structure["certifications"].append(cert_val)

    save_experience()

    # Final fallbacks
    if not structure["summary"]:
        structure["summary"] = "Dedicated specialist seeking target growth role."
    if not structure["skills"]:
        structure["skills"] = ["Problem Solving", "Collaboration", "Communication"]
    if "certifications" not in structure:
        structure["certifications"] = []

    return structure


# Endpoint: Resume Upload & Extract Text
@app.post("/api/v1/resume/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Create a temp file path
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    filename = file.filename or "upload"
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        is_json = False
        try:
            with open(temp_path, "r", encoding="utf-8") as f:
                first_char = f.read(1)
                if first_char == '{':
                    is_json = True
        except:
            pass

        if is_json:
            import json
            with open(temp_path, "r", encoding="utf-8") as f:
                structured_json = json.load(f)
            parsed_text = json.dumps(structured_json)
        else:
            ext = filename.split(".")[-1].lower()
            if ext == "pdf":
                parsed_text = extract_text_from_pdf(temp_path)
            elif ext == "docx":
                parsed_text = extract_text_from_docx(temp_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX.")

            # Structure parsed text
            from backend.app.engine.prompt_layer import parse_resume_text_via_llm
            
            structured_json = parse_resume_text_via_llm(parsed_text)
            if not structured_json:
                logger.warning("LLM parsing failed or no keys found. Falling back to heuristic parser.")
                structured_json = parse_resume_text_to_structure(parsed_text, filename)
        
        # Read file bytes and upload to Supabase Storage
        with open(temp_path, "rb") as f:
            file_bytes = f.read()
        resume_url = upload_file_to_supabase(file_bytes, filename)
        
        # Save to DB
        resume_record = Resume(
            resume_url=resume_url,
            parsed_json=structured_json
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)

        return {
            "resume_id": resume_record.id,
            "filename": filename,
            "structured_json": resume_record.parsed_json
        }
    except Exception as e:
        logger.error(f"Upload and extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Endpoint: Analyze Job Description Text
@app.post("/api/v1/jd/analyze")
async def analyze_jd(raw_text: str = Form(...), db: Session = Depends(get_db)):
    try:
        keywords = list(extract_keywords_from_text(raw_text))
        
        jd_record = JobDescription(
            jd_text=raw_text
        )
        db.add(jd_record)
        db.commit()
        db.refresh(jd_record)

        return {
            "jd_id": jd_record.id,
            "keywords": keywords
        }
    except Exception as e:
        logger.error(f"JD analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Full ATS Scoring and Optimization Trigger
@app.post("/api/v1/optimize")
async def optimize_resume(resume_id: str = Form(...), jd_id: str = Form(...), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()

    if not resume or not jd:
        raise HTTPException(status_code=404, detail="Resume or Job Description record not found.")

    # Explicitly cast for type safety
    resume_obj = cast(Resume, resume)
    jd_obj = cast(JobDescription, jd)

    try:
        import json as _json
        # Defensively parse parsed_json if it comes back as string from DB
        parsed_data = resume_obj.parsed_json
        if isinstance(parsed_data, str):
            parsed_data = _json.loads(parsed_data)
        elif not parsed_data:
            parsed_data = {}

        resume_text = _json.dumps(parsed_data) if parsed_data else ""
        jd_text = str(jd_obj.jd_text)

        # 1. Calculate matching metrics
        metrics = calculate_ats_metrics(resume_text, jd_text)
        
        # 2. Optimize structured JSON using AI prompt engineering layer
        optimized_json = optimize_resume_data(
            cast(dict[str, Any], parsed_data), 
            jd_text, 
            metrics["missing_keywords"]
        )
        
        # Save ATS Report to DB
        report_record = ATSReport(
            resume_id=str(resume_obj.id),
            jd_id=str(jd_obj.id),
            ats_score=metrics["original_score"],
            match_score=metrics["potential_score"],
            report_json={
                "matched_keywords": metrics["matched_keywords"],
                "missing_keywords": metrics["missing_keywords"],
                "sections_found": metrics["sections_found"],
                "section_score": metrics["section_score"],
                "formatting_issues": metrics["formatting_issues"]
            }
        )
        db.add(report_record)
        db.commit()
        db.refresh(report_record)

        # Save Optimized Resume to DB
        opt_resume = OptimizedResume(
            report_id=str(report_record.id),
            original_resume=resume_text,
            optimized_resume=_json.dumps(optimized_json)
        )
        db.add(opt_resume)
        db.commit()
        db.refresh(opt_resume)

        return {
            "result_id": report_record.id,
            "original_score": report_record.ats_score,
            "optimized_score": report_record.match_score,
            "matched_keywords": metrics["matched_keywords"],
            "missing_keywords": metrics["missing_keywords"],
            "original_resume": parsed_data,
            "optimized_resume": optimized_json,
            "sections_found": metrics["sections_found"],
            "section_score": metrics["section_score"],
            "formatting_issues": metrics["formatting_issues"]
        }
    except Exception as e:
        logger.error(f"Optimization trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Export Optimized Resume PDF
# Helper function to process bullet text in backend
def process_bullet_text(text: str, show_added: bool, show_optimized: bool, revert_entire_string: bool = False) -> str:
    if not text:
        return text
    
    result = text
    
    # 1. Process optimized bullets (class="mod")
    if not show_optimized:
        if revert_entire_string:
            match = re.search(r'<mark\s+class="mod"\s+data-tooltip="Original:\s*([^"]+)"[^>]*>', result, flags=re.IGNORECASE)
            if not match:
                match = re.search(r'<mark\s+class="mod"\s+data-tooltip=\'Original:\s*([^\']+)\'[^>]*>', result, flags=re.IGNORECASE)
            if match:
                return match.group(1)
                
        # Inline replacement
        result = re.sub(r'<mark\s+class="mod"\s+data-tooltip="Original:\s*([^"]+)"[^>]*>.*?</mark>', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r'<mark\s+class="mod"\s+data-tooltip=\'Original:\s*([^\']+)\'[^>]*>.*?</mark>', r'\1', result, flags=re.IGNORECASE)
        
    # 2. Process added keywords (class="add")
    if not show_added:
        result = re.sub(r'<mark\s+class="add"[^>]*>.*?</mark>', '', result, flags=re.IGNORECASE)
        # Clean up punctuation spacing and double conjunctions
        result = re.sub(r'\s+and\s*([.,;!])', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r'\s+or\s*([.,;!])', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r',\s*and\s*([.,;!])', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r',\s*or\s*([.,;!])', r'\1', result, flags=re.IGNORECASE)
        result = re.sub(r'\s+,\s*', ', ', result)
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s+([.,;!])', r'\1', result)
        result = re.sub(r'\s*•\s*•\s*', ' • ', result)
        result = result.strip()
        
    return result

def process_resume_data_highlights(data: dict, original_data: dict, show_added: bool, show_optimized: bool) -> dict:
    import copy
    processed = copy.deepcopy(data)
    
    if "summary" in processed:
        summary_text = original_data.get("summary", "") if (not show_optimized and original_data) else processed["summary"]
        processed["summary"] = process_bullet_text(summary_text, show_added, show_optimized)
        
    if "skills" in processed and isinstance(processed["skills"], list):
        new_skills = []
        for s in processed["skills"]:
            p_s = process_bullet_text(s, show_added, show_optimized)
            if p_s.strip():
                new_skills.append(p_s)
        processed["skills"] = new_skills
        
    if "experience" in processed and isinstance(processed["experience"], list):
        orig_exp_list = original_data.get("experience", []) if original_data else []
        for i, exp in enumerate(processed["experience"]):
            if "role" in exp:
                exp["role"] = process_bullet_text(exp["role"], show_added, show_optimized)
            if "bullets" in exp and isinstance(exp["bullets"], list):
                new_bullets = []
                orig_bullets = orig_exp_list[i].get("bullets", []) if (i < len(orig_exp_list) and isinstance(orig_exp_list[i], dict)) else []
                for bIdx, b in enumerate(exp["bullets"]):
                    bullet_text = orig_bullets[bIdx] if (not show_optimized and bIdx < len(orig_bullets)) else b
                    new_bullets.append(process_bullet_text(bullet_text, show_added, show_optimized, revert_entire_string=True))
                exp["bullets"] = new_bullets
                
    if "projects" in processed and isinstance(processed["projects"], list):
        orig_proj_list = original_data.get("projects", []) if original_data else []
        for i, proj in enumerate(processed["projects"]):
            if "description" in proj:
                proj["description"] = process_bullet_text(proj["description"], show_added, show_optimized)
            if "bullets" in proj and isinstance(proj["bullets"], list):
                new_bullets = []
                orig_bullets = orig_proj_list[i].get("bullets", []) if (i < len(orig_proj_list) and isinstance(orig_proj_list[i], dict)) else []
                for bIdx, b in enumerate(proj["bullets"]):
                    bullet_text = orig_bullets[bIdx] if (not show_optimized and bIdx < len(orig_bullets)) else b
                    new_bullets.append(process_bullet_text(bullet_text, show_added, show_optimized, revert_entire_string=True))
                proj["bullets"] = new_bullets

    if "certifications" in processed and isinstance(processed["certifications"], list):
        new_certs = []
        orig_certs = original_data.get("certifications", []) if original_data else []
        for i, cert in enumerate(processed["certifications"]):
            cert_text = orig_certs[i] if (not show_optimized and i < len(orig_certs)) else cert
            new_certs.append(process_bullet_text(cert_text, show_added, show_optimized))
        processed["certifications"] = new_certs
                
    return processed


# Endpoint: Export Optimized Resume PDF
@app.get("/api/v1/optimize/{result_id}/download-pdf", response_class=HTMLResponse)
async def download_pdf(result_id: str, show_added: bool = True, show_optimized: bool = True, db: Session = Depends(get_db)):
    import json as _json
    report = db.query(ATSReport).filter(ATSReport.id == result_id).first()
    if not report or not report.optimized_resume:
        raise HTTPException(status_code=404, detail="Optimization record not found.")

    opt_resume_obj = cast(OptimizedResume, report.optimized_resume)
    
    # Load optimized data
    opt_val = opt_resume_obj.optimized_resume
    if isinstance(opt_val, str):
        opt_data = _json.loads(opt_val)
    else:
        opt_data = opt_val or {}

    # Load original data
    orig_val = opt_resume_obj.original_resume
    if isinstance(orig_val, str):
        orig_data = _json.loads(orig_val)
    else:
        orig_data = orig_val or {}

    processed_data = process_resume_data_highlights(cast(dict, opt_data), cast(dict, orig_data), show_added, show_optimized)
    html_content = generate_styled_resume_html(processed_data, include_highlights=False)
    return HTMLResponse(content=html_content, status_code=200)


# Endpoint: Export Optimized Resume DOCX (returns clean formatted docx file)
@app.get("/api/v1/optimize/{result_id}/download-docx")
async def download_docx(result_id: str, show_added: bool = True, show_optimized: bool = True, db: Session = Depends(get_db)):
    import json as _json
    report = db.query(ATSReport).filter(ATSReport.id == result_id).first()
    if not report or not report.optimized_resume:
        raise HTTPException(status_code=404, detail="Optimization record not found.")

    opt_resume_obj = cast(OptimizedResume, report.optimized_resume)
    
    # Load optimized data
    opt_val = opt_resume_obj.optimized_resume
    if isinstance(opt_val, str):
        opt_data = _json.loads(opt_val)
    else:
        opt_data = opt_val or {}

    # Load original data
    orig_val = opt_resume_obj.original_resume
    if isinstance(orig_val, str):
        orig_data = _json.loads(orig_val)
    else:
        orig_data = orig_val or {}
    
    processed_data = process_resume_data_highlights(cast(dict, opt_data), cast(dict, orig_data), show_added, show_optimized)
    file_stream = generate_docx_from_data(processed_data)
    
    return StreamingResponse(
        file_stream, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=Optimized_Resume.docx"}
    )
