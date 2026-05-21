"""
Seismic QC Tool — Streamlit UI
Run: streamlit run app.py
"""

import json
import tempfile
from pathlib import Path
import streamlit as st

from src.extractor import SeismicExtractor
from src.qc_report import generate_report

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Seismic QC Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background: #0d1117; color: #e6edf3; }
  .confidence-high  { color: #3fb950; font-weight: bold; }
  .confidence-mid   { color: #d29922; font-weight: bold; }
  .confidence-low   { color: #f85149; font-weight: bold; }
  .flag-chip {
    display: inline-block; padding: 2px 8px; margin: 2px;
    background: #1f2937; border: 1px solid #f85149;
    border-radius: 12px; font-size: 0.75rem; color: #f85149;
  }
  .rec-chip {
    display: inline-block; padding: 2px 8px; margin: 2px;
    background: #1f2937; border: 1px solid #d29922;
    border-radius: 12px; font-size: 0.75rem; color: #d29922;
  }
</style>
""", unsafe_allow_html=True)

extractor = SeismicExtractor()

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌍 Seismic QC Tool")
    st.caption("Oil & Gas | Data Structuring & Quality Control")
    mode = st.radio("Input Mode", ["📝 Paste Text", "📄 Upload PDF"])
    st.divider()
    st.markdown("**About**")
    st.info(
        "Converts seismic feature descriptions into structured JSON "
        "with confidence scoring and QC recommendations."
    )

# ── Main ───────────────────────────────────────────────────────────────────
st.header("Seismic Data Structuring & QC")

features = []

if mode == "📝 Paste Text":
    default_text = (
        "The normal fault F-12 was identified in the Cretaceous Brent Formation "
        "at a depth of 2800 m with a strike of 045° and dip of 35° NW. "
        "The reflector shows high amplitude and continuous sub-parallel character, "
        "suggesting a good reservoir seal. Velocity recorded at 3200 m/s."
    )
    text_input = st.text_area(
        "Seismic Feature Description",
        value=default_text,
        height=180,
    )
    if st.button("🔍 Extract & QC", use_container_width=True):
        with st.spinner("Extracting…"):
            feat = extractor.extract_from_text(text_input, feature_id="F-001")
            features = [feat]

else:  # PDF mode
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded and st.button("🔍 Extract & QC", use_container_width=True):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        with st.spinner("Parsing PDF…"):
            features = extractor.extract_from_pdf(tmp_path)

# ── Results ────────────────────────────────────────────────────────────────
if features:
    st.divider()
    summary = generate_report(features)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Features", summary["total_features"])
    col2.metric("🟢 High Confidence", summary["high_confidence"])
    col3.metric("🟡 Moderate", summary["moderate_confidence"])
    col4.metric("🔴 Low Confidence", summary["low_confidence"])

    st.divider()

    for feat in features:
        conf = feat.confidence_score
        conf_class = (
            "confidence-high" if conf >= 0.7 else
            "confidence-mid"  if conf >= 0.4 else
            "confidence-low"
        )
        with st.expander(
            f"Feature `{feat.feature_id}` — Confidence: {conf:.0%}",
            expanded=True,
        ):
            left, right = st.columns(2)

            with left:
                st.subheader("Structured Fields")
                fields = {
                    "Fault Type": feat.fault_type,
                    "Structure Type": feat.structure_type,
                    "Depth (m)": feat.depth_m,
                    "Depth Raw": feat.depth_raw,
                    "Strike (°)": feat.strike,
                    "Dip (°)": feat.dip,
                    "Dip Direction": feat.dip_direction,
                    "Amplitude": feat.amplitude,
                    "Frequency": feat.frequency,
                    "Reflector Continuity": feat.reflector_continuity,
                    "Velocity (m/s)": feat.velocity_ms,
                    "Age": feat.age,
                    "Formation": feat.formation,
                }
                for k, v in fields.items():
                    if v is not None:
                        st.markdown(f"**{k}:** `{v}`")
                    else:
                        st.markdown(f"**{k}:** _⚠ missing_")

            with right:
                st.subheader("QC Results")
                st.markdown(
                    f'<span class="{conf_class}">Confidence: {conf:.1%}</span>',
                    unsafe_allow_html=True,
                )
                if feat.qc_flags:
                    st.markdown("**Flags:**")
                    flags_html = " ".join(
                        f'<span class="flag-chip">{f}</span>' for f in feat.qc_flags
                    )
                    st.markdown(flags_html, unsafe_allow_html=True)
                if feat.qc_recommendations:
                    st.markdown("**Recommendations:**")
                    for rec in feat.qc_recommendations:
                        st.markdown(f"- {rec}")

                st.subheader("JSON Output")
                st.json(json.loads(extractor.to_json(feat)))

    # Download buttons
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        json_bytes = extractor.to_json_list(features).encode()
        st.download_button(
            "⬇ Download structured.json",
            data=json_bytes,
            file_name="structured.json",
            mime="application/json",
        )
    with c2:
        md_path = Path("outputs/qc_report.md")
        if md_path.exists():
            st.download_button(
                "⬇ Download QC Report (Markdown)",
                data=md_path.read_bytes(),
                file_name="qc_report.md",
                mime="text/markdown",
            )
