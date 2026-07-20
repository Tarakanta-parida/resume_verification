import streamlit as st
from models.database import init_db
from utils.ui_components import inject_custom_css, clean_markdown_html
from views.dashboard_view import render_dashboard_view
from views.analysis_view import render_analysis_view
from views.comparer_view import render_comparer_view
from views.report_view import render_report_view

# Initialize Streamlit Page Config
st.set_page_config(
    page_title="ResuMatch AI - Resume Optimizer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database tables
init_db()

# Session State Initialization
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "dashboard"
if "original_resume" not in st.session_state:
    st.session_state.original_resume = None
if "optimized_resume" not in st.session_state:
    st.session_state.optimized_resume = None
if "original_score" not in st.session_state:
    st.session_state.original_score = 0
if "optimized_score" not in st.session_state:
    st.session_state.optimized_score = 0
if "matched_keywords" not in st.session_state:
    st.session_state.matched_keywords = []
if "missing_keywords" not in st.session_state:
    st.session_state.missing_keywords = []
if "sections_found" not in st.session_state:
    st.session_state.sections_found = {}
if "section_score" not in st.session_state:
    st.session_state.section_score = 0
if "formatting_issues" not in st.session_state:
    st.session_state.formatting_issues = []
if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "resume_id" not in st.session_state:
    st.session_state.resume_id = None
if "result_id" not in st.session_state:
    st.session_state.result_id = None
if "is_optimized" not in st.session_state:
    st.session_state.is_optimized = False

# Inject Custom CSS Theme
inject_custom_css(st.session_state.theme)

# Render Sidebar Navigation
with st.sidebar:
    st.markdown(clean_markdown_html("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08);">
    <div style="width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%); display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 15px rgba(124,58,237,0.3);">
        ✨
    </div>
    <span style="font-size: 20px; font-weight: 800; tracking: -0.5px; background: linear-gradient(135deg, #c084fc 0%, #60a5fa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ResuMatch AI
    </span>
</div>
"""), unsafe_allow_html=True)

    # Navigation buttons
    is_opt = st.session_state.is_optimized

    nav_options = [
        ("dashboard", "📊 Dashboard", False),
        ("analysis", "📈 ATS Analysis", not is_opt),
        ("comparer", "↔️ Side-by-Side", not is_opt),
        ("report", "📋 ATS Audit Report", not is_opt)
    ]

    for tab_id, label, disabled in nav_options:
        is_active = (st.session_state.current_tab == tab_id)
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(label, key=f"nav_{tab_id}", disabled=disabled, use_container_width=True, type=btn_type):
            st.session_state.current_tab = tab_id
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)

    # Status pill indicator
    status_msg = "✓ Resume Optimized" if is_opt else ("📄 Ready to Optimize" if st.session_state.resume_name else "📁 Upload files to begin")
    status_color = "#10b981" if is_opt else ("#3b82f6" if st.session_state.resume_name else "#94a3b8")

    st.markdown(clean_markdown_html(f"""
<div style="display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: {status_color}; padding: 8px 12px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; margin-bottom: 16px;">
    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: {status_color};"></span>
    <span>{status_msg}</span>
</div>
"""), unsafe_allow_html=True)

    # Theme Toggle Switch
    current_theme_label = "🌙 Dark Mode" if st.session_state.theme == "dark" else "☀️ Light Mode"
    if st.button(f"Theme: {current_theme_label}", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    # Reset All Button
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.original_resume = None
        st.session_state.optimized_resume = None
        st.session_state.original_score = 0
        st.session_state.optimized_score = 0
        st.session_state.matched_keywords = []
        st.session_state.missing_keywords = []
        st.session_state.sections_found = {}
        st.session_state.section_score = 0
        st.session_state.formatting_issues = []
        st.session_state.resume_name = ""
        st.session_state.jd_text = ""
        st.session_state.resume_id = None
        st.session_state.result_id = None
        st.session_state.is_optimized = False
        st.session_state.current_tab = "dashboard"
        st.rerun()

# Render Active View
if st.session_state.current_tab == "dashboard":
    render_dashboard_view()
elif st.session_state.current_tab == "analysis":
    render_analysis_view()
elif st.session_state.current_tab == "comparer":
    render_comparer_view()
elif st.session_state.current_tab == "report":
    render_report_view()
else:
    render_dashboard_view()
