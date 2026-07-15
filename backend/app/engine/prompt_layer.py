import os
import json
import logging
from typing import Dict, Any, List
from google import genai
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger("ats-optimizer")

SYSTEM_INSTRUCTION = """
You are an expert Applicant Tracking System (ATS) Resume Optimizer. 
Your task is to review a candidate's resume data and optimize it to align with the target Job Description (JD).

RULES:
1. Inject missing keywords from the JD naturally into the "Summary", "Skills", and "Experience" sections.
2. Re-word bullet points in the "Experience" and "Projects" sections using strong action verbs (e.g., Spearheaded, Developed, Optimized) and add realistic quantitative metrics (e.g., "improving performance by 25%", "cutting API latency by 40%") where appropriate.
3. CRITICAL: Do NOT alter the layout, formatting, names, contact info, companies, durations, degree titles, or graduation years.
4. Do NOT hallucinate completely false jobs or credentials. Keep the core work history factual.
5. Return the response ONLY in a valid JSON object matching the exact keys provided in the input resume. Include HTML `<mark class="add" data-tooltip="Embedded keyword">WORD</mark>` tags for any added keywords and `<mark class="mod" data-tooltip="Optimized for ATS metrics">SENTENCE</mark>` for modified sentences.

Input JSON format:
{
  "personalInfo": { ... },
  "summary": "...",
  "skills": ["...", "..."],
  "experience": [{"role": "...", "company": "...", "duration": "...", "bullets": ["...", "..."]}],
  "projects": [{"name": "...", "description": "...", "bullets": ["...", "..."]}],
  "education": [{"degree": "...", "school": "...", "year": "..."}],
  "certifications": ["...", "..."]
}
"""

def optimize_resume_data(resume_structure: Dict[str, Any], jd_text: str, missing_keywords: List[str]) -> Dict[str, Any]:
    """
    Tries calling Gemini, Claude, or GPT models based on key availability,
    and falls back to a rule-based regex optimizer if no keys are found.
    """
    # 1. Check Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            logger.info("Using Google Gemini API for optimization...")
            return optimize_via_gemini(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"Gemini API failed: {e}")

    # 2. Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            logger.info("Using OpenAI GPT API for optimization...")
            return optimize_via_openai(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"OpenAI API failed: {e}")

    # 3. Check Anthropic
    if os.getenv("CLAUDE_API_KEY"):
        try:
            logger.info("Using Anthropic Claude API for optimization...")
            return optimize_via_claude(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"Claude API failed: {e}")

    # 4. Fallback: Local rule-based optimization
    logger.info("No LLM API keys found. Falling back to local rule-based optimization engine.")
    return local_rule_based_optimize(resume_structure, missing_keywords)


def optimize_via_gemini(data: Dict[str, Any], jd: str, missing: List[str]) -> Dict[str, Any]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"Resume Data JSON:\n{json.dumps(data, indent=2)}\n\nJob Description:\n{jd}\n\nMissing Keywords:\n{missing}"
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.2,
            "system_instruction": SYSTEM_INSTRUCTION
        }
    )
    return json.loads(response.text or "{}")


def optimize_via_openai(data: Dict[str, Any], jd: str, missing: List[str]) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Resume Data JSON:\n{json.dumps(data, indent=2)}\n\nJob Description:\n{jd}\n\nMissing Keywords:\n{missing}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        stream=False
    )
    return json.loads(response.choices[0].message.content or "{}")  # type: ignore


def optimize_via_claude(data: Dict[str, Any], jd: str, missing: List[str]) -> Dict[str, Any]:
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    prompt = f"Resume Data JSON:\n{json.dumps(data, indent=2)}\n\nJob Description:\n{jd}\n\nMissing Keywords:\n{missing}"
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        system=SYSTEM_INSTRUCTION,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    # Extracts JSON block if wrapped
    resp_text = "".join(getattr(block, "text", "") for block in response.content)  # type: ignore
    return json.loads(resp_text)


def local_rule_based_optimize(data: Dict[str, Any], missing: List[str]) -> Dict[str, Any]:
    """
    Performs dynamic rule-based replacements to simulate LLM optimizer output.
    """
    optimized = {
        "personalInfo": data.get("personalInfo") or {},
        "summary": data.get("summary") or "",
        "skills": list(data.get("skills") or []),
        "experience": [],
        "projects": [],
        "education": data.get("education") or [],
        "certifications": list(data.get("certifications") or [])
    }
    
    # 1. Optimize summary
    sum_text = optimized["summary"]
    if missing:
        top_kws = missing[:2]
        kw_marks = " and ".join([f'<mark class="add" data-tooltip="Embedded target keyword">{k}</mark>' for k in top_kws])
        optimized["summary"] = f"Results-driven professional expert in aligning operations with {kw_marks}. {sum_text}"
    else:
        optimized["summary"] = f"Results-driven specialist with a proven track record. {sum_text}"

    # 2. Append missing skills
    for m in missing[:5]:
        optimized["skills"].append(f'<mark class="add" data-tooltip="Added missing skill found in Job Description">{m}</mark>')

    # 3. Optimize experience
    for idx, exp in enumerate(data.get("experience") or []):
        bullets = list(exp.get("bullets") or [])
        if idx == 0 and len(bullets) > 0:
            # Preserve original first bullet and append keyword and metric
            orig_bullet_0 = bullets[0]
            kw_inject = ""
            if len(missing) > 2:
                kw_inject = f' utilizing <mark class="add" data-tooltip="Embedded keyword">{missing[2]}</mark>'
            bullets[0] = f'<mark class="mod" data-tooltip="Rephrased with action verbs and metrics">{orig_bullet_0}{kw_inject}, improving deliverables and boosting efficiency by <mark class="add" data-tooltip="Added quantitative business result">24%</mark>.</mark>'
            
            # Preserve original second bullet if exists and append keyword and metric
            if len(bullets) > 1:
                orig_bullet_1 = bullets[1]
                kw_inject2 = ""
                if len(missing) > 3:
                    kw_inject2 = f' integrating <mark class="add" data-tooltip="Embedded keyword">{missing[3]}</mark>'
                bullets[1] = f'<mark class="mod" data-tooltip="Optimized sentence structure for keywords">{orig_bullet_1}{kw_inject2}, increasing operational performance by <mark class="add" data-tooltip="Added measurable result">35%</mark>.</mark>'
                
        optimized["experience"].append({
            "role": exp.get("role") or "",
            "company": exp.get("company") or "",
            "duration": exp.get("duration") or "",
            "bullets": bullets
        })

    # 4. Optimize projects
    for proj in data.get("projects") or []:
        bullets = list(proj.get("bullets") or [])
        if len(bullets) > 0:
            bullets[0] = f'{bullets[0]} <mark class="mod" data-tooltip="Optimized for JD keyword density">using modern industry-aligned frameworks.</mark>'
        optimized["projects"].append({
            "name": proj.get("name") or "",
            "description": proj.get("description") or "",
            "bullets": bullets
        })
    return optimized


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
    "linkedin": "LinkedIn URL (if present, else empty string)"
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

def parse_resume_text_via_llm(raw_text: str) -> Dict[str, Any] | None:
    """
    Parses raw resume text into structured JSON using LLM.
    """
    # 1. Try Gemini
    if os.getenv("GEMINI_API_KEY"):
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
    if os.getenv("OPENAI_API_KEY"):
        try:
            logger.info("Using OpenAI GPT API for parsing...")
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PARSING_SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"Raw Resume Text:\n{raw_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                stream=False
            )
            return json.loads(response.choices[0].message.content or "{}")  # type: ignore
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}")

    # 3. Try Claude
    if os.getenv("CLAUDE_API_KEY"):
        try:
            logger.info("Using Anthropic Claude API for parsing...")
            client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=PARSING_SYSTEM_INSTRUCTION,
                messages=[
                    {"role": "user", "content": f"Raw Resume Text:\n{raw_text}"}
                ],
                temperature=0.1
            )
            content_text = response.content[0].text  # type: ignore
            # Simple JSON extractor
            start = content_text.find('{')
            end = content_text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content_text[start:end])
            return json.loads(content_text)
        except Exception as e:
            logger.error(f"Claude parsing failed: {e}")

    return None

