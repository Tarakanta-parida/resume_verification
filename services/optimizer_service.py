import os
import json
import logging
from typing import Dict, Any, List
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

from services.ats_service import extract_keywords_from_text

logger = logging.getLogger("ats-optimizer")

SYSTEM_INSTRUCTION = """
You are an expert Applicant Tracking System (ATS) Resume Optimizer. 
Your task is to review a candidate's resume data and optimize it to align strictly with the target Job Description (JD).

RULES:
1. Inject missing keywords from the JD naturally into the "Summary", "Skills", and "Experience" sections.
2. CRITICAL: Do NOT remove, prune, or delete any skills, projects, certifications, work history, or bullet points from the candidate's original resume. Keep all original contents intact.
3. CRITICAL: Do NOT alter the layout, formatting, names, contact info (phone, email, github, linkedin, portfolio), companies, durations, degree titles, or graduation years. Keep them EXACTLY the same as in the original resume.
4. Do NOT rewrite paragraphs or bullets completely. Only modify existing sentences slightly to naturally embed the target missing keywords, or append new skills to the skills list.
5. Return the response ONLY in a valid JSON object matching the exact keys and structure provided in the input resume. Include HTML `<mark class="add" data-tooltip="Embedded keyword">WORD</mark>` tags for any added keywords and `<mark class="mod" data-tooltip="Optimized for ATS metrics">SENTENCE</mark>` for modified sentences.
"""

def optimize_resume_data(resume_structure: Dict[str, Any], jd_text: str, missing_keywords: List[str]) -> Dict[str, Any]:
    """
    Tries calling Gemini, Claude, or GPT models based on key availability,
    and falls back to a rule-based regex optimizer if no keys are found.
    """
    # 1. Check Gemini
    if genai and os.getenv("GEMINI_API_KEY"):
        try:
            logger.info("Using Google Gemini API for optimization...")
            return optimize_via_gemini(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"Gemini API failed: {e}")

    # 2. Check OpenAI
    if OpenAI and os.getenv("OPENAI_API_KEY"):
        try:
            logger.info("Using OpenAI GPT API for optimization...")
            return optimize_via_openai(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"OpenAI API failed: {e}")

    # 3. Check Anthropic
    if Anthropic and os.getenv("CLAUDE_API_KEY"):
        try:
            logger.info("Using Anthropic Claude API for optimization...")
            return optimize_via_claude(resume_structure, jd_text, missing_keywords)
        except Exception as e:
            logger.error(f"Claude API failed: {e}")

    # 4. Fallback: Local rule-based optimization
    logger.info("No LLM API keys found. Falling back to local rule-based optimization engine.")
    return local_rule_based_optimize(resume_structure, jd_text, missing_keywords)


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
    response: Any = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        stream=False
    )
    return json.loads(response.choices[0].message.content or "{}")


def optimize_via_claude(data: Dict[str, Any], jd: str, missing: List[str]) -> Dict[str, Any]:
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    prompt = f"Resume Data JSON:\n{json.dumps(data, indent=2)}\n\nJob Description:\n{jd}\n\nMissing Keywords:\n{missing}"
    response: Any = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        system=SYSTEM_INSTRUCTION,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    resp_text = "".join(getattr(block, "text", "") for block in response.content)
    return json.loads(resp_text)


def local_rule_based_optimize(data: Dict[str, Any], jd_text: str, missing: List[str]) -> Dict[str, Any]:
    """Performs dynamic rule-based replacements without removing original resume content."""
    optimized = {
        "personalInfo": data.get("personalInfo") or {},
        "summary": data.get("summary") or "",
        "skills": list(data.get("skills") or []),
        "experience": [],
        "projects": [],
        "education": data.get("education") or [],
        "certifications": list(data.get("certifications") or [])
    }

    # 1. Optimize summary (Inject first two missing keywords)
    sum_text = data.get("summary") or ""
    if missing:
        top_kws = missing[:2]
        kw_marks = " and ".join([f'<mark class="add" data-tooltip="Embedded target keyword">{k}</mark>' for k in top_kws])
        optimized["summary"] = f"{sum_text} (Expertise aligns with {kw_marks}.)"

    # 2. Append missing JD target skills without removing any existing ones
    for m in missing[:5]:
        if not any(m.lower() in str(sk).lower() for sk in optimized["skills"]):
            optimized["skills"].append(f'<mark class="add" data-tooltip="Added missing skill found in Job Description">{m}</mark>')

    # 3. Optimize experience: Inject missing keywords sequentially into experience bullets
    kw_idx = 0
    for exp in data.get("experience") or []:
        bullets = list(exp.get("bullets") or [])
        optimized_bullets = []
        for bullet in bullets:
            if kw_idx < len(missing):
                kw = missing[kw_idx]
                bullet_opt = f"{bullet} <mark class='mod' data-tooltip='Optimized for keywords'>Utilized <mark class='add' data-tooltip='Embedded keyword'>{kw}</mark> to improve delivery efficiency.</mark>"
                optimized_bullets.append(bullet_opt)
                kw_idx += 1
            else:
                optimized_bullets.append(bullet)
        optimized["experience"].append({
            "role": exp.get("role") or "",
            "company": exp.get("company") or "",
            "duration": exp.get("duration") or "",
            "bullets": optimized_bullets
        })

    # 4. Optimize projects: Inject missing keywords sequentially into project bullets
    for proj in data.get("projects") or []:
        bullets = list(proj.get("bullets") or [])
        optimized_bullets = []
        for bullet in bullets:
            if kw_idx < len(missing):
                kw = missing[kw_idx]
                bullet_opt = f"{bullet} <mark class='mod' data-tooltip='Optimized for keywords'>Implemented utilizing <mark class='add' data-tooltip='Embedded keyword'>{kw}</mark> methodologies.</mark>"
                optimized_bullets.append(bullet_opt)
                kw_idx += 1
            else:
                optimized_bullets.append(bullet)
        optimized["projects"].append({
            "name": proj.get("name") or "",
            "description": proj.get("description") or "",
            "bullets": optimized_bullets
        })

    return optimized
