import os
import tempfile
import json
import streamlit as st
from models.database import SessionLocal
from models.db_models import Resume, JobDescription, ATSReport, OptimizedResume
from services.parser_service import extract_text_from_pdf, extract_text_from_docx, parse_resume_text_via_llm, parse_resume_text_to_structure
from services.ats_service import calculate_ats_metrics, extract_keywords_from_text
from services.optimizer_service import optimize_resume_data
from services.storage_service import upload_file_to_supabase
from services.sample_data import SAMPLE_JDS, SAMPLE_RESUMES
from utils.ui_components import render_header_banner, clean_markdown_html

def render_dashboard_view():
    render_header_banner(
        title="Resume Optimizer",
        subtitle="Upload your resume and target job description to match keywords, fix gaps, and boost your ATS score."
    )

    def format_template_option(option: str) -> str:
        options_map = {
            "-- Custom Upload --": "📁 Custom Upload",
            "software_engineer": "💻 Software Engineer",
            "data_analyst": "📊 Data Analyst",
            "product_manager": "🚀 Product Manager",
            "marketing_specialist": "📢 Marketing Specialist"
        }
        return options_map.get(option, option)

    # Template profile loader bar
    col_t1, col_t2 = st.columns([2, 1])
    with col_t2:
        selected_template = st.selectbox(
            "Load Sample Candidate Profile:",
            options=["-- Custom Upload --", "software_engineer", "data_analyst", "product_manager", "marketing_specialist"],
            format_func=format_template_option,
            key="sample_profile_select"
        )

        if selected_template and selected_template != "-- Custom Upload --" and st.session_state.get("last_selected_template") != selected_template:
            st.session_state.last_selected_template = selected_template
            st.session_state.jd_text = SAMPLE_JDS.get(str(selected_template), "")
            st.session_state.original_resume = SAMPLE_RESUMES.get(str(selected_template), None)
            st.session_state.resume_name = f"{selected_template}_Sample_Resume.docx"
            st.session_state.is_optimized = False
            st.session_state.optimized_resume = None
            st.rerun()

    # Main Upload & JD Input Columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(clean_markdown_html("""
<div style="font-size: 16px; font-weight: 700; margin-bottom: 12px; color: #8b5cf6;">
    1. Upload Resume
</div>
"""), unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drag and drop your PDF, DOCX, or JSON resume",
            type=["pdf", "docx", "json"],
            key="resume_file_uploader"
        )

        if uploaded_file is not None:
            if st.session_state.get("uploaded_filename") != uploaded_file.name:
                st.session_state.uploaded_filename = uploaded_file.name
                with st.spinner("Processing document text & structuring sections..."):
                    file_bytes = uploaded_file.read()
                    filename = uploaded_file.name
                    ext = filename.split(".")[-1].lower()

                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                        tmp.write(file_bytes)
                        tmp_path = tmp.name

                    try:
                        if ext == "json":
                            structured_json = json.loads(file_bytes.decode("utf-8"))
                        else:
                            if ext == "pdf":
                                parsed_text = extract_text_from_pdf(tmp_path)
                            else:
                                parsed_text = extract_text_from_docx(tmp_path)

                            structured_json = parse_resume_text_via_llm(parsed_text)
                            if not structured_json:
                                structured_json = parse_resume_text_to_structure(parsed_text, filename)

                        resume_url = upload_file_to_supabase(file_bytes, filename)

                        db = SessionLocal()
                        try:
                            resume_rec = Resume(resume_url=resume_url, parsed_json=structured_json)
                            db.add(resume_rec)
                            db.commit()
                            db.refresh(resume_rec)
                            st.session_state.resume_id = resume_rec.id
                        finally:
                            db.close()

                        st.session_state.original_resume = structured_json
                        st.session_state.resume_name = filename
                        st.session_state.is_optimized = False
                        st.session_state.optimized_resume = None
                        st.success(f"Successfully loaded {filename}")
                    except Exception as e:
                        st.error(f"Error parsing resume: {e}")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

        if st.session_state.get("original_resume"):
            st.info(f"📄 Active Resume: **{st.session_state.get('resume_name', 'Loaded Resume')}**")

    with col2:
        st.markdown(clean_markdown_html("""
<div style="font-size: 16px; font-weight: 700; margin-bottom: 12px; color: #8b5cf6;">
    2. Target Job Description
</div>
"""), unsafe_allow_html=True)

        jd_input = st.text_area(
            "Paste target job description details here...",
            value=st.session_state.get("jd_text", ""),
            height=240,
            placeholder="Paste job details, required technical skills, experience requirements, and key competencies...",
            key="jd_textarea"
        )
        st.session_state.jd_text = jd_input

    # Action trigger button
    st.markdown("<br>", unsafe_allow_html=True)
    is_ready = bool(st.session_state.get("original_resume")) and len(st.session_state.get("jd_text", "").strip()) > 15

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("✨ Optimize Resume", disabled=not is_ready, use_container_width=True, type="primary"):
            with st.spinner("Analyzing Job Requirements & Running AI Optimizer..."):
                try:
                    db = SessionLocal()
                    try:
                        # 1. Save JD
                        jd_rec = JobDescription(jd_text=st.session_state.jd_text)
                        db.add(jd_rec)
                        db.commit()
                        db.refresh(jd_rec)

                        parsed_data = st.session_state.original_resume
                        resume_text = json.dumps(parsed_data)
                        jd_text = st.session_state.jd_text

                        # 2. Compute metrics
                        metrics = calculate_ats_metrics(resume_text, jd_text)

                        # 3. AI Optimization
                        optimized_json = optimize_resume_data(parsed_data, jd_text, metrics["missing_keywords"])

                        # 4. Save ATS Report
                        report_rec = ATSReport(
                            resume_id=st.session_state.get("resume_id", "sample"),
                            jd_id=jd_rec.id,
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
                        db.add(report_rec)
                        db.commit()
                        db.refresh(report_rec)

                        # 5. Save Optimized Resume
                        opt_rec = OptimizedResume(
                            report_id=report_rec.id,
                            original_resume=resume_text,
                            optimized_resume=json.dumps(optimized_json)
                        )
                        db.add(opt_rec)
                        db.commit()
                        db.refresh(opt_rec)

                        st.session_state.result_id = report_rec.id
                        st.session_state.original_score = metrics["original_score"]
                        st.session_state.optimized_score = metrics["potential_score"]
                        st.session_state.matched_keywords = metrics["matched_keywords"]
                        st.session_state.missing_keywords = metrics["missing_keywords"]
                        st.session_state.optimized_resume = optimized_json
                        st.session_state.sections_found = metrics["sections_found"]
                        st.session_state.section_score = metrics["section_score"]
                        st.session_state.formatting_issues = metrics["formatting_issues"]
                        st.session_state.is_optimized = True
                        st.session_state.current_tab = "analysis"
                        st.rerun()
                    finally:
                        db.close()
                except Exception as e:
                    st.error(f"Optimization failed: {e}")
