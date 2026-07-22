import os
import re
import json
import logging
from typing import Dict, Any, Optional
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

import io
from typing import Dict, Any, Optional, Union

logger = logging.getLogger("ats-optimizer")

def extract_text_from_pdf(file_or_path: Union[str, io.BytesIO]) -> str:
    """Extracts text from a PDF file using pdfplumber."""
    if not pdfplumber:
        raise Exception("pdfplumber library is not installed in the current Python environment.")
    text = ""
    try:
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
        with pdfplumber.open(file_or_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
        raise Exception("Failed to extract text from PDF file.")
    return text


def extract_text_from_docx(file_or_path: Union[str, io.BytesIO]) -> str:
    """Extracts text from a DOCX file using python-docx."""
    if not docx:
        raise Exception("python-docx library is not installed in the current Python environment.")
    try:
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
        doc = docx.Document(file_or_path)
        text_runs = []
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text_runs.append(paragraph.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        text_runs.append(cell.text)
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
        return "\n".join(text_runs)
    except Exception as e:
        logger.error(f"python-docx extraction failed: {e}")
        raise Exception("Failed to extract text from DOCX file.")


def extract_links_from_document(file_or_path: Union[str, io.BytesIO], ext: str) -> list[str]:
    """Extracts embedded hyperlinks from PDF or DOCX without polluting raw text."""
    links = []
    try:
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
            
        if ext == "pdf":
            if not pdfplumber:
                return []
            with pdfplumber.open(file_or_path) as pdf:
                for page in pdf.pages:
                    if hasattr(page, "hyperlinks") and page.hyperlinks:
                        for hl in page.hyperlinks:
                            uri = hl.get("uri")
                            if uri:
                                links.append(uri)
        else: # docx
            if not docx:
                return []
            doc = docx.Document(file_or_path)
            if hasattr(doc, "part") and hasattr(doc.part, "rels"):
                for rel in doc.part.rels.values():
                    if hasattr(rel, "reltype") and "hyperlink" in rel.reltype and hasattr(rel, "target_ref"):
                        links.append(rel.target_ref)
                        
        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
    return links


PARSING_SYSTEM_INSTRUCTION = """
You are an expert resume parser. Your task is to parse the raw text of a resume into a structured JSON object.
Extract all details accurately without changing any wording, facts, or context. Do not add any new information, and do not use placeholders. If a section is missing, leave it as an empty list or empty string.

Return the response ONLY in a valid JSON object matching this exact schema:
{
  "personalInfo": {
    "name": "Full Name",
    "email": "Email Address",
    "phone": "Phone Number",
    "github": "Github URL (if present, else empty string)",
    "linkedin": "LinkedIn URL (if present, else empty string)",
    "portfolio": "Portfolio or personal website URL (if present, else empty string)"
  },
  "summary": "Professional Summary or Objective (if present, else empty string)",
  "skills": [
    "Exact line 1 from skills section (e.g. 'Programming Languages: Python, SQL' or 'Power BI - DAX, Data Modeling')",
    "Exact line 2 from skills section",
    ...
  ],
  "experience": [
    {
      "role": "Job Title",
      "company": "Company Name",
      "duration": "Dates of employment (e.g., Jun 2021 - Present)",
      "bullets": ["Bullet point 1", "Bullet point 2", ...]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Short description/tech stack (if present, else empty string)",
      "bullets": ["Bullet point 1", "Bullet point 2", ...]
    }
  ],
  "education": [
    {
      "degree": "Degree (e.g., Bachelor of Science in Computer Science)",
      "school": "University/School Name",
      "year": "Graduation Year (e.g., 2023)"
    }
  ]
}
"""

def parse_resume_text_via_llm(raw_text: str) -> Optional[Dict[str, Any]]:
    """Parses raw resume text into structured JSON using LLM APIs."""
    # 1. Try Gemini
    if genai and os.getenv("GEMINI_API_KEY"):
        try:
            logger.info("Using Google Gemini API for parsing...")
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=f"Raw Resume Text:\n{raw_text}",
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                    "system_instruction": PARSING_SYSTEM_INSTRUCTION
                }
            )
            return json.loads(response.text or "{}")
        except Exception as e:
            logger.error(f"Gemini parsing failed: {e}")

    # 2. Try OpenAI
    if OpenAI and os.getenv("OPENAI_API_KEY"):
        try:
            logger.info("Using OpenAI GPT API for parsing...")
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response: Any = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PARSING_SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"Raw Resume Text:\n{raw_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                stream=False
            )
            return json.loads(response.choices[0].message.content or "{}")
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}")

    # 3. Try Claude
    if Anthropic and os.getenv("CLAUDE_API_KEY"):
        try:
            logger.info("Using Anthropic Claude API for parsing...")
            client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
            response: Any = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=PARSING_SYSTEM_INSTRUCTION,
                messages=[
                    {"role": "user", "content": f"Raw Resume Text:\n{raw_text}"}
                ],
                temperature=0.1
            )
            content_text = response.content[0].text
            start = content_text.find('{')
            end = content_text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content_text[start:end])
            return json.loads(content_text)
        except Exception as e:
            logger.error(f"Claude parsing failed: {e}")

    return None


def parse_resume_text_to_structure(text: str, filename: str) -> Dict[str, Any]:
    """Fallback heuristic regex parser for raw resume text."""
    structure: Dict[str, Any] = {
        "personalInfo": {
            "name": filename.replace("_", " ").split(".")[0],
            "email": "",
            "phone": "",
            "github": "",
            "linkedin": "",
            "portfolio": ""
        },
        "summary": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": []
    }

    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phones = re.findall(r'\+?[0-9\s\-()]{7,18}', text)

    if emails:
        structure["personalInfo"]["email"] = emails[0]
    if phones:
        valid_phones = [p.strip() for p in phones if len(re.sub(r'[^0-9]', '', p)) >= 10]
        if valid_phones:
            structure["personalInfo"]["phone"] = valid_phones[0]

    # Extract LinkedIn URL
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-\/\.]+', text, re.IGNORECASE)
    if linkedin_match:
        structure["personalInfo"]["linkedin"] = linkedin_match.group(0).strip()

    # Extract GitHub URL
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-\/\.]+', text, re.IGNORECASE)
    if github_match:
        structure["personalInfo"]["github"] = github_match.group(0).strip()

    # Extract Portfolio URL (any other valid URL that isn't github/linkedin)
    urls = re.findall(r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[a-zA-Z0-9._%+-]*)*', text)
    for url in urls:
        lower_url = url.lower()
        if "linkedin" not in lower_url and "github" not in lower_url and "email" not in lower_url:
            # Simple validation to avoid matching file paths or extensions
            if not any(lower_url.endswith(ext) for ext in [".pdf", ".docx", ".doc", ".png", ".jpg"]):
                structure["personalInfo"]["portfolio"] = url.strip()
                break

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
            if re.search(r'(19|20)\d{2}', line) or "present" in lower_line:
                save_experience()
                temp_bullets = []
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
                structure["certifications"].append(cert_val)

    save_experience()

    if not structure["summary"]:
        structure["summary"] = "Dedicated specialist seeking target growth role."
    if not structure["skills"]:
        structure["skills"] = ["Problem Solving", "Collaboration", "Communication"]

    return structure
