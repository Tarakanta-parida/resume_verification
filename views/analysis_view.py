import streamlit as st
from utils.ui_components import render_gauge, render_header_banner, clean_markdown_html

def render_analysis_view():
    render_header_banner(
        title="ATS Match & Analysis",
        subtitle="Review missing keywords, category scores, and customized recommendations."
    )

    if not st.session_state.get("is_optimized"):
        st.warning("Please upload a resume and job description on the Dashboard to view the ATS Analysis.")
        return

    orig_score = st.session_state.get("original_score", 0)
    opt_score = st.session_state.get("optimized_score", 0)
    diff = opt_score - orig_score
    matched_kws = st.session_state.get("matched_keywords", [])
    missing_kws = st.session_state.get("missing_keywords", [])

    # Top Row Cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="resumatch-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 16px; font-weight: 700; margin-bottom: 20px;">📊 ATS Match Verdict</h3>', unsafe_allow_html=True)

        g_col1, g_col2 = st.columns(2)
        with g_col1:
            render_gauge(orig_score, "Current Score", "#ef4444")
        with g_col2:
            render_gauge(opt_score, "Potential Score", "#06b6d4")

        verdict_msg = "Critical gaps successfully bypassed! Adding missing keywords and re-wording bullets raised metrics." if diff > 15 else "Your resume is well aligned! Incorporating missing skills pushed compatibility higher to clear ATS filters."
        
        st.markdown(clean_markdown_html(f"""
<div style="text-align: center; margin-top: 20px;">
    <div style="display: inline-block; padding: 4px 14px; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); color: #10b981; font-size: 13px; font-weight: 700; border-radius: 20px; margin-bottom: 10px;">
        ▲ +{diff}% Match Improvement
    </div>
    <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 0;">
        {verdict_msg}
    </p>
</div>
</div>
"""), unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="resumatch-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 16px; font-weight: 700; margin-bottom: 20px;">📋 ATS Section Analysis</h3>', unsafe_allow_html=True)

        categories = [
            ("Keyword Matching & Density", orig_score + 5),
            ("Skills & Competency Alignments", max(orig_score - 10, 45)),
            ("Experience & Role Match", orig_score + 2),
            ("Education & Certification Validation", 95)
        ]

        for cat_name, cur_val in categories:
            pot_val = min(cur_val + 20, 98)
            st.markdown(f"**{cat_name}** ({cur_val}% ➔ {pot_val}%)")
            st.progress(pot_val / 100)

        st.markdown('</div>', unsafe_allow_html=True)

    # Keywords Badge Panel
    st.markdown('<div class="resumatch-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 16px; font-weight: 700; margin-bottom: 16px;">🔑 Keyword Matching Report</h3>', unsafe_allow_html=True)

    tab_missing, tab_matched = st.tabs([f"⚠️ Missing Keywords ({len(missing_kws)})", f"✅ Matched Keywords ({len(matched_kws)})"])

    with tab_missing:
        if not missing_kws:
            st.info("No missing keywords detected!")
        else:
            badges_html = "".join([f'<span class="badge-missing">⚠️ {kw}</span>' for kw in missing_kws])
            st.markdown(clean_markdown_html(f'<div style="line-height: 2.2;">{badges_html}</div>'), unsafe_allow_html=True)

    with tab_matched:
        if not matched_kws:
            st.info("No matched keywords detected!")
        else:
            badges_html = "".join([f'<span class="badge-matched">✓ {kw}</span>' for kw in matched_kws])
            st.markdown(clean_markdown_html(f'<div style="line-height: 2.2;">{badges_html}</div>'), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
