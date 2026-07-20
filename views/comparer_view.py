import streamlit as st
from services.document_service import (
    generate_docx_from_data,
    generate_plain_text,
    generate_styled_resume_html,
    process_resume_data_highlights
)
from utils.ui_components import render_resume_paper_view, render_header_banner

def render_comparer_view():
    render_header_banner(
        title="Before & After Comparison",
        subtitle="Review optimized enhancements made directly to your resume without altering layout, contact details, or work history."
    )

    if not st.session_state.get("is_optimized") or not st.session_state.get("optimized_resume"):
        st.warning("Please upload a resume and job description on the Dashboard to view the Side-by-Side comparison.")
        return

    original_data = st.session_state.get("original_resume", {})
    optimized_data = st.session_state.get("optimized_resume", {})
    resume_name = st.session_state.get("resume_name", "Resume")

    # Toolbar Row
    st.markdown('<div class="resumatch-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 2])

    with c1:
        show_added = st.checkbox("🟢 Added Keywords", value=True, key="chk_show_added")
    with c2:
        show_optimized = st.checkbox("🟠 Optimized Bullets", value=True, key="chk_show_optimized")

    processed_opt = process_resume_data_highlights(optimized_data, original_data, show_added, show_optimized)

    with c3:
        txt_content = generate_plain_text(processed_opt, original_data, show_added, show_optimized)
        st.download_button(
            label="📄 Export Plain Text",
            data=txt_content,
            file_name=f"{resume_name.split('.')[0]}_Optimized.txt",
            mime="text/plain",
            use_container_width=True
        )

    with c4:
        docx_bytes = generate_docx_from_data(processed_opt)
        st.download_button(
            label="📝 Download DOCX",
            data=docx_bytes,
            file_name=f"{resume_name.split('.')[0]}_Optimized.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )

    # Print-ready HTML Download
    html_content = generate_styled_resume_html(processed_opt, include_highlights=False)
    st.download_button(
        label="🖨️ Download Print-Ready PDF (HTML)",
        data=html_content,
        file_name=f"{resume_name.split('.')[0]}_Optimized.html",
        mime="text/html",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Side by side paper views
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 15px; color: #94a3b8;">Original Resume</span>
            <span style="font-size: 12px; color: #64748b;">📄 Raw Import</span>
        </div>
        """, unsafe_allow_html=True)
        render_resume_paper_view(original_data)

    with col_right:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 15px; color: #10b981;">Optimized Resume</span>
            <span style="font-size: 12px; color: #10b981;">✓ AI Enhanced</span>
        </div>
        """, unsafe_allow_html=True)
        render_resume_paper_view(optimized_data, original_data=original_data, show_added=show_added, show_optimized=show_optimized)
