import streamlit as st
import streamlit.components.v1 as components
from services.document_service import process_bullet_text, clean_html_tags
import re

def clean_contact_value(val: str) -> str:
    if not val:
        return ""
    # Strip leading/trailing spaces, dashes, colons, vertical bars, bullets
    cleaned = re.sub(r'^[\s\-:|•·▪◦-]+|[\s\-:|•·▪◦-]+$', '', val)
    cleaned = cleaned.strip()
    # Hide default placeholders
    lower_val = cleaned.lower()
    if "linkedin.com/in/user" in lower_val or "github.com/user" in lower_val or "info@domain.com" in lower_val:
        return ""
    return cleaned

def clean_markdown_html(html_str: str) -> str:
    """Removes leading whitespace from each line to prevent Streamlit from treating lines with >=4 spaces as code blocks."""
    lines = [line.strip() for line in html_str.split("\n")]
    return "\n".join(lines)

def inject_custom_css(theme: str = "dark"):
    is_light = (theme == "light")
    
    bg_color = "#f8fafc" if is_light else "#020617"
    sidebar_bg = "#ffffff" if is_light else "#090d16"
    text_color = "#0f172a" if is_light else "#f8fafc"
    card_bg = "#ffffff" if is_light else "rgba(15, 23, 42, 0.6)"
    card_border = "#e2e8f0" if is_light else "rgba(255, 255, 255, 0.08)"
    sub_text = "#475569" if is_light else "#94a3b8"
    input_bg = "#ffffff" if is_light else "#090d16"
    input_border = "#cbd5e1" if is_light else "rgba(255, 255, 255, 0.12)"
    
    btn_sec_bg = "#ffffff" if is_light else "rgba(255, 255, 255, 0.05)"
    btn_sec_text = "#0f172a" if is_light else "#f8fafc"
    btn_sec_border = "#cbd5e1" if is_light else "rgba(255, 255, 255, 0.1)"
    btn_sec_hover_bg = "#f1f5f9" if is_light else "rgba(255, 255, 255, 0.1)"

    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root, [data-testid="stAppViewContainer"], .stApp {{
    --secondary-background-color: {input_bg} !important;
    --background-color: {bg_color} !important;
    --text-color: {text_color} !important;
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
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {card_border} !important;
}}

/* Cards */
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

/* Form Controls & Inputs */
.stTextArea textarea, .stTextInput input, 
div[data-testid="stSelectbox"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div {{
    background-color: {input_bg} !important;
    color: {text_color} !important;
    border: 1px solid {input_border} !important;
    border-radius: 10px !important;
}}

/* Strictly strip background, border, and box-shadow from all inner selectbox children */
div[data-testid="stSelectbox"] div,
div[data-testid="stSelectbox"] span,
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] button,
div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] button,
div[data-baseweb="icon"],
div[data-baseweb="icon"] * {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {text_color} !important;
    fill: {text_color} !important;
    -webkit-text-fill-color: {text_color} !important;
}}

div[data-testid="stSelectbox"] svg,
div[data-baseweb="select"] svg {{
    fill: {text_color} !important;
    color: {text_color} !important;
}}

/* BaseWeb Selectbox Dropdown Menu Popover */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
div[data-baseweb="menu"] > div,
ul[role="listbox"],
[data-testid="stSelectboxVirtualDropdown"] {{
    background-color: {card_bg} !important;
    color: {text_color} !important;
    border: 1px solid {card_border} !important;
    border-radius: 12px !important;
    box-shadow: {"0 10px 30px rgba(0,0,0,0.12)" if is_light else "0 10px 30px rgba(0,0,0,0.5)"} !important;
}}

div[data-baseweb="popover"] *,
div[data-baseweb="menu"] *,
ul[role="listbox"] *,
div[role="option"] {{
    background-color: {card_bg} !important;
    color: {text_color} !important;
    -webkit-text-fill-color: {text_color} !important;
}}

div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover,
ul[role="listbox"] [aria-selected="true"],
div[role="option"]:hover {{
    background-color: {btn_sec_hover_bg} !important;
}}

.stTextArea textarea::placeholder, .stTextInput input::placeholder {{
    color: #94a3b8 !important;
}}

/* File Uploader Dropzone */
[data-testid="stFileUploaderDropzone"], div[data-testid="stFileUploader"] > section {{
    background-color: {card_bg} !important;
    border: 1px dashed {input_border} !important;
    border-radius: 12px !important;
    color: {text_color} !important;
}}

[data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploaderDropzone"] span {{
    color: {text_color} !important;
}}

[data-testid="stFileUploaderDropzone"] button, section[data-testid="stFileUploaderDropzone"] button, button[data-testid="stBaseButton-secondary"] {{
    background-color: {btn_sec_bg} !important;
    color: {btn_sec_text} !important;
    border: 1px solid {btn_sec_border} !important;
}}

[data-testid="stFileUploaderDropzone"] button:hover {{
    background-color: {btn_sec_hover_bg} !important;
    border-color: #8b5cf6 !important;
    color: #8b5cf6 !important;
}}

/* Info Callout Banner */
div[data-testid="stInfo"] {{
    background-color: {"rgba(59, 130, 246, 0.08)" if is_light else "rgba(59, 130, 246, 0.12)"} !important;
    color: {"#1e40af" if is_light else "#60a5fa"} !important;
    border: 1px solid {"rgba(59, 130, 246, 0.25)" if is_light else "rgba(59, 130, 246, 0.3)"} !important;
    border-radius: 10px !important;
}}

div[data-testid="stInfo"] * {{
    color: {"#1e40af" if is_light else "#60a5fa"} !important;
}}

/* Checkbox & Labels */
div[data-testid="stCheckbox"] label span {{
    color: {text_color} !important;
    font-weight: 600 !important;
}}

div[data-testid="stCheckbox"] label > div,
div[data-baseweb="checkbox"] > div,
span[data-baseweb="checkbox"] {{
    border-radius: 6px !important;
}}

div[data-testid="stCheckbox"] input:checked + div,
div[data-baseweb="checkbox"] [aria-checked="true"] > div,
div[data-baseweb="checkbox"] > div[aria-checked="true"] {{
    background-color: #8b5cf6 !important;
    border-color: #8b5cf6 !important;
}}

div[data-testid="stCheckbox"] svg,
div[data-baseweb="checkbox"] svg {{
    fill: #ffffff !important;
    color: #ffffff !important;
    stroke: #ffffff !important;
}}

p:not(.resume-paper *), span:not(.resume-paper *), label:not(.resume-paper *), h1:not(.resume-paper *), h2:not(.resume-paper *), h3:not(.resume-paper *), h4:not(.resume-paper *), h5:not(.resume-paper *), h6:not(.resume-paper *) {{
    color: {text_color};
}}

.stMarkdown p:not(.resume-paper *) {{
    color: {text_color};
}}

/* Buttons Styling */
div.stButton > button {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}}

/* Secondary Buttons */
div.stButton > button[kind="secondary"] {{
    background-color: {btn_sec_bg} !important;
    color: {btn_sec_text} !important;
    border: 1px solid {btn_sec_border} !important;
    box-shadow: {"0 1px 3px rgba(0,0,0,0.05)" if is_light else "none"} !important;
}}

div.stButton > button[kind="secondary"]:hover {{
    background-color: {btn_sec_hover_bg} !important;
    border-color: #8b5cf6 !important;
    color: #8b5cf6 !important;
}}

/* Primary Buttons */
div.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
}}

div.stButton > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
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
    box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
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
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    font-size: 12px;
    line-height: 1.6;
    min-height: 650px;
}}

/* Force Resume Paper text to be visible (override global dark mode text colors) */
.resume-paper h1, .resume-paper h2, .resume-paper h3, .resume-paper h4, .resume-paper h5, .resume-paper h6 {{
    color: #0f172a !important;
    border-color: #0f172a !important;
}}
.resume-paper span, .resume-paper p, .resume-paper li, .resume-paper strong, .resume-paper a {{
    color: inherit !important;
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
    is_light = (st.session_state.get("theme") == "light")
    sub_color = "#475569" if is_light else "#94a3b8"

    html = f"""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 32px; font-weight: 800; tracking: -0.5px; margin-bottom: 6px;
               background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        {title}
    </h1>
    <p style="font-size: 14px; color: {sub_color}; max-width: 650px; margin: 0; font-weight: 500;">
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
    email = clean_contact_value(personal.get("email", ""))
    phone = clean_contact_value(personal.get("phone", ""))
    linkedin = clean_contact_value(personal.get("linkedin", ""))
    github = clean_contact_value(personal.get("github", ""))

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
    <div style="display: flex; justify-content: space-between; font-weight: 700; color: #0f172a !important;">
        <span>{role}</span>
        <span>{duration}</span>
    </div>
    <div style="font-style: italic; color: #64748b !important; font-size: 11px; margin-bottom: 4px;">
        {company}
    </div>
    <ul style="padding-left: 18px; margin: 0; color: #334155 !important;">
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
    <div style="font-weight: 700; color: #0f172a !important;">
        <span>{p_name}</span> {f'| <span style="font-weight: 400; font-style: italic; color: #64748b !important;">{p_desc}</span>' if p_desc else ''}
    </div>
    <ul style="padding-left: 18px; margin: 4px 0 0 0; color: #334155 !important;">
        {bullets_html}
    </ul>
</div>
""")
    proj_html = "\n".join(proj_html_blocks)

    edu_html_blocks = []
    for edu in data.get("education", []):
        edu_html_blocks.append(f"""
<div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
    <div><strong style="color: #0f172a !important;">{edu.get('degree', '')}</strong> — <span style="color: #64748b !important;">{edu.get('school', '')}</span></div>
    <div style="font-weight: 600; color: #0f172a !important;">{edu.get('year', '')}</div>
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

    portfolio = personal.get("portfolio", "")

    contacts = []
    if phone:
        contacts.append(f"Mobile: <a href='tel:{phone}' style='color: inherit !important; text-decoration: none;'>{phone}</a>")
    if email:
        contacts.append(f"Email: <a href='mailto:{email}' style='color: #0284c7 !important; text-decoration: underline;'>{email}</a>")
    if linkedin:
        li_url = linkedin if linkedin.startswith("http") else f"https://{linkedin}"
        contacts.append(f"<a href='{li_url}' target='_blank' style='color: #0284c7 !important; text-decoration: underline;'>LinkedIn</a>")
    if github:
        gh_url = github if github.startswith("http") else f"https://{github}"
        contacts.append(f"<a href='{gh_url}' target='_blank' style='color: #0284c7 !important; text-decoration: underline;'>GitHub</a>")
    if portfolio:
        port_url = portfolio if portfolio.startswith("http") else f"https://{portfolio}"
        contacts.append(f"<a href='{port_url}' target='_blank' style='color: #0284c7 !important; text-decoration: underline;'>Portfolio</a>")
    contacts_str = " | ".join(contacts)

    html = f"""
<div class="resume-paper">
    <h2 style="text-align: center; font-size: 22px; font-weight: 800; margin: 0 0 4px 0; color: #0f172a !important;">
        {name}
    </h2>
    <div style="text-align: center; font-size: 10px; font-weight: 600; color: #475569 !important; margin-bottom: 16px; border-bottom: 1px solid #cbd5e1; padding-bottom: 8px;">
        {contacts_str}
    </div>
    
    <h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">
        Career Objective
    </h3>
    <p style="margin: 0 0 12px 0; text-align: justify; color: #334155 !important;">
        {summary_html}
    </p>

    <h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">
        Technical Skills
    </h3>
    <div style="margin-bottom: 12px; color: #334155 !important;">
        {skills_html}
    </div>

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">Work Experience</h3>{exp_html}' if exp_html.strip() else ''}
    
    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">Technical Projects</h3>{proj_html}' if proj_html.strip() else ''}

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">Education</h3>{edu_html}' if edu_html.strip() else ''}

    {f'<h3 style="font-size: 13px; font-weight: 800; text-transform: uppercase; color: #0f172a !important; border-bottom: 1.5px solid #0f172a !important; padding-bottom: 2px; margin: 14px 0 6px 0;">Certifications</h3><ul style="padding-left: 18px; margin: 0; color: #334155 !important;">{cert_html}</ul>' if cert_html.strip() else ''}
</div>
"""
    st.markdown(clean_markdown_html(html), unsafe_allow_html=True)
