import streamlit as st
import streamlit.components.v1 as components
from services.document_service import process_bullet_text, clean_html_tags

def clean_markdown_html(html_str: str) -> str:
    """Removes leading whitespace from each line to prevent Streamlit from treating lines with >=4 spaces as code blocks."""
    lines = [line.strip() for line in html_str.split("\n")]
    return "\n".join(lines)

def inject_custom_css(theme: str = "dark"):
    is_light = (theme == "light")
    
    bg_color = "#f8fafc" if is_light else "#020617"
    text_color = "#0f172a" if is_light else "#f8fafc"
    card_bg = "#ffffff" if is_light else "rgba(15, 23, 42, 0.6)"
    card_border = "rgba(0, 0, 0, 0.08)" if is_light else "rgba(255, 255, 255, 0.08)"
    sub_text = "#64748b" if is_light else "#94a3b8"
    input_bg = "#f1f5f9" if is_light else "#090d16"
    
    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

section[data-testid="stSidebar"] {{
    background-color: {"#ffffff" if is_light else "#090d16"} !important;
    border-right: 1px solid {card_border} !important;
}}

.resumatch-card {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 24px;
    box-shadow: {"0 4px 20px -2px rgba(0,0,0,0.05)" if is_light else "0 10px 30px -5px rgba(0,0,0,0.3)"};
    margin-bottom: 20px;
    transition: all 0.3s ease;
}}

.resumatch-card:hover {{
    border-color: rgba(139, 92, 246, 0.4);
}}

.gauge-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}

.gauge-circle {{
    width: 110px;
    height: 110px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: {input_bg};
    position: relative;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
}}

.gauge-value {{
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
}}

.gauge-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 8px;
    color: {sub_text};
}}

.badge-missing {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.25);
    margin: 4px;
}}

.badge-matched {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(16, 185, 129, 0.12);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.25);
    margin: 4px;
}}

mark.add {{
    background-color: rgba(16, 185, 129, 0.25) !important;
    color: #047857 !important;
    border-radius: 3px;
    padding: 1px 4px;
    font-weight: 600;
}}

mark.mod {{
    background-color: rgba(245, 158, 11, 0.25) !important;
    color: #b45309 !important;
    border-radius: 3px;
    padding: 1px 4px;
    font-weight: 600;
}}

.resume-paper {{
    background: #ffffff;
    color: #1e293b;
    padding: 36px;
    border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
    font-size: 12px;
    line-height: 1.6;
    min-height: 650px;
}}
</style>
"""
    st.markdown(clean_markdown_html(css), unsafe_allow_html=True)


def render_gauge(score: int, label: str, color: str = "#8b5cf6"):
    """Renders a visual metric gauge indicator."""
    html = f"""
<div class="gauge-container">
    <div class="gauge-circle" style="border: 4px solid {color};">
        <span class="gauge-value" style="color: {color};">{score}%</span>
    </div>
    <span class="gauge-label">{label}</span>
</div>
"""
    st.markdown(clean_markdown_html(html), unsafe_allow_html=True)


def render_header_banner(title: str, subtitle: str):
    """Renders the top title banner."""
    html = f"""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 32px; font-weight: 800; tracking: -0.5px; margin-bottom: 6px;
               background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        {title}
    </h1>
    <p style="font-size: 14px; color: #94a3b8; max-width: 650px; margin: 0;">
        {subtitle}
    </p>
</div>
"""
    st.markdown(clean_markdown_html(html), unsafe_allow_html=True)


def render_resume_paper_view(data: dict, original_data: dict | None = None, show_added: bool = True, show_optimized: bool = True):
    """Renders formatted resume paper view in HTML."""
    if not data:
        st.info("No resume data available.")
        return

    personal = data.get("personalInfo", {})
    name = personal.get("name", "Applicant Name")
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    linkedin = personal.get("linkedin", "")
    github = personal.get("github", "")

    summary_text = original_data.get("summary", "") if (not show_optimized and original_data) else data.get("summary", "")
    summary_html = process_bullet_text(str(summary_text or ""), show_added, show_optimized)

    skills_list = []
    for s in data.get("skills", []):
        p_s = process_bullet_text(str(s or ""), show_added, show_optimized)
        if p_s.strip():
            skills_list.append(p_s)
    skills_html = " • ".join(skills_list)

    exp_html_blocks = []
    for i, exp in enumerate(data.get("experience", [])):
        role = process_bullet_text(str(exp.get("role", "") or ""), show_added, show_optimized)
        company = exp.get("company", "")
        duration = exp.get("duration", "")
        
        bullets_html = ""
        orig_bullets = original_data.get("experience", [])[i].get("bullets", []) if (original_data and i < len(original_data.get("experience", []))) else []
        for bIdx, b in enumerate(exp.get("bullets", [])):
            bullet_text = orig_bullets[bIdx] if (not show_optimized and bIdx < len(orig_bullets)) else b
            b_proc = process_bullet_text(str(bullet_text or ""), show_added, show_optimized, revert_entire_string=True)
            bullets_html += f"<li style='margin-bottom: 4px;'>{b_proc}</li>"

        exp_html_blocks.append(f"""
<div style="margin-bottom: 12px;">
    <div style="display: flex; justify-content: space-between; font-weight: 700; color: #0f172a;">
        <span>{role}</span>
        <span>{duration}</span>
    </div>
    <div style="font-style: italic; color: #64748b; font-size: 11px; margin-bottom: 4px;">
        {company}
    </div>
    <ul style="padding-left: 18px; margin: 0; color: #334155;">
        {bullets_html}
    </ul>
</div>
""")
    exp_html = "\n".join(exp_html_blocks)

    proj_html_blocks = []
    for i, proj in enumerate(data.get("projects", [])):
        p_name = proj.get("name", "")
        p_desc = process_bullet_text(str(proj.get("description", "") or ""), show_added, show_optimized)
        
        bullets_html = ""
        orig_bullets = original_data.get("projects", [])[i].get("bullets", []) if (original_data and i < len(original_data.get("projects", []))) else []
        for bIdx, b in enumerate(proj.get("bullets", [])):
            bullet_text = orig_bullets[bIdx] if (not show_optimized and bIdx < len(orig_bullets)) else b
            b_proc = process_bullet_text(str(bullet_text or ""), show_added, show_optimized, revert_entire_string=True)
            bullets_html += f"<li style='margin-bottom: 4px;'>{b_proc}</li>"

        proj_html_blocks.append(f"""
<div style="margin-bottom: 12px;">
    <div style="font-weight: 700; color: #0f172a;">
        <span>{p_name}</span> {f'| <span style="font-weight: 400; font-style: italic; color: #64748b;">{p_desc}</span>' if p_desc else ''}
    </div>
    <ul style="padding-left: 18px; margin: 4px 0 0 0; color: #334155;">
        {bullets_html}
    </ul>
</div>
""")
    proj_html = "\n".join(proj_html_blocks)

    edu_html_blocks = []
    for edu in data.get("education", []):
        edu_html_blocks.append(f"""
<div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
    <div><strong style="color: #0f172a;">{edu.get('degree', '')}</strong> — <span style="color: #64748b;">{edu.get('school', '')}</span></div>
    <div style="font-weight: 600; color: #0f172a;">{edu.get('year', '')}</div>
</div>
""")
    edu_html = "\n".join(edu_html_blocks)

    cert_html_blocks = []
    orig_certs = original_data.get("certifications", []) if original_data else []
    for i, cert in enumerate(data.get("certifications", [])):
        c_val = orig_certs[i] if (not show_optimized and i < len(orig_certs)) else cert
        c_proc = process_bullet_text(str(c_val or ""), show_added, show_optimized)
        cert_html_blocks.append(f"<li>{c_proc}</li>")
    cert_html = "\n".join(cert_html_blocks)

    contacts = [f"Mobile: {phone}", f"Email: {email}"]
    if linkedin: contacts.append(f"LinkedIn: {linkedin}")
    if github: contacts.append(f"GitHub: {github}")
    contacts_str = " | ".join(contacts)

    html = f"""
<div class="resume-paper">
    <h2 style="text-align: center; font-size: 22px; font-weight: 800; margin: 0 0 4px 0; color: #0f172a;">
        {name}
    </h2>
    <div style="text-align: center; font-size: 10px; font-weight: 600; color: #475569; margin-bottom: 16px; border-bottom: 1px solid #cbd5e1; padding-bottom: 8px;">
        {contacts_str}
    </div>
    
    <h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">
        Career Objective
    </h3>
    <p style="margin: 0 0 12px 0; text-align: justify; color: #334155;">
        {summary_html}
    </p>

    <h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">
        Technical Skills
    </h3>
    <div style="margin-bottom: 12px; color: #334155;">
        {skills_html}
    </div>

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">Work Experience</h3>{exp_html}' if exp_html.strip() else ''}
    
    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">Technical Projects</h3>{proj_html}' if proj_html.strip() else ''}

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">Education</h3>{edu_html}' if edu_html.strip() else ''}

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a; border-bottom: 1.5px solid #0f172a; padding-bottom: 2px; margin: 14px 0 6px 0;">Certifications</h3><ul style="padding-left: 18px; margin: 0; color: #334155;">{cert_html}</ul>' if cert_html.strip() else ''}
</div>
"""
    st.markdown(clean_markdown_html(html), unsafe_allow_html=True)
