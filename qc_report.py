"""
QC Report Generator
Produces Markdown + JSON reports from extracted seismic features.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


def generate_report(features, output_dir: str = "outputs") -> dict:
    """
    Given a list of SeismicFeature objects, write:
      - outputs/qc_report.md   (human-readable)
      - outputs/structured.json (machine-readable)
    Returns summary dict.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    summary = {
        "total_features": len(features),
        "high_confidence": 0,
        "moderate_confidence": 0,
        "low_confidence": 0,
        "features_with_flags": 0,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    md_lines = [
        "# Seismic Data QC Report",
        f"_Generated: {summary['generated_at']}_",
        f"**Total features processed:** {len(features)}",
        "",
        "---",
        "",
    ]

    structured = []

    for feat in features:
        d = asdict(feat)
        structured.append(d)

        conf = feat.confidence_score
        conf_label = (
            "🟢 HIGH" if conf >= 0.7 else
            "🟡 MODERATE" if conf >= 0.4 else
            "🔴 LOW"
        )
        if conf >= 0.7:
            summary["high_confidence"] += 1
        elif conf >= 0.4:
            summary["moderate_confidence"] += 1
        else:
            summary["low_confidence"] += 1

        if feat.qc_flags:
            summary["features_with_flags"] += 1

        md_lines += [
            f"## Feature `{feat.feature_id}`",
            f"**Confidence:** {conf_label} ({conf:.1%})",
            "",
            "### Extracted Fields",
            "| Field | Value |",
            "| --- | --- |",
        ]

        display_fields = [
            ("Fault Type", feat.fault_type),
            ("Structure Type", feat.structure_type),
            ("Depth (m)", feat.depth_m),
            ("Depth (raw)", feat.depth_raw),
            ("Strike (°)", feat.strike),
            ("Dip (°)", feat.dip),
            ("Dip Direction", feat.dip_direction),
            ("Amplitude", feat.amplitude),
            ("Frequency", feat.frequency),
            ("Reflector Continuity", feat.reflector_continuity),
            ("Velocity (m/s)", feat.velocity_ms),
            ("Age", feat.age),
            ("Formation/Horizon", feat.formation),
        ]
        for label, val in display_fields:
            if val is not None:
                md_lines.append(f"| {label} | `{val}` |")
            else:
                md_lines.append(f"| {label} | ⚠ _missing_ |")

        md_lines += [""]

        if feat.missing_fields:
            md_lines.append(
                f"**Missing required fields:** {', '.join(f'`{f}`' for f in feat.missing_fields)}"
            )

        if feat.qc_flags:
            md_lines.append("")
            md_lines.append("### QC Flags")
            for flag in feat.qc_flags:
                md_lines.append(f"- ⚑ `{flag}`")

        if feat.qc_recommendations:
            md_lines.append("")
            md_lines.append("### Recommendations")
            for rec in feat.qc_recommendations:
                md_lines.append(f"- {rec}")

        md_lines += ["", "---", ""]

    # Summary section at top
    summary_block = [
        "## Summary",
        f"| Metric | Count |",
        f"| --- | --- |",
        f"| 🟢 High Confidence (≥70%) | {summary['high_confidence']} |",
        f"| 🟡 Moderate Confidence (40–69%) | {summary['moderate_confidence']} |",
        f"| 🔴 Low Confidence (<40%) | {summary['low_confidence']} |",
        f"| Features with QC Flags | {summary['features_with_flags']} |",
        "",
        "---",
        "",
    ]
    md_lines[5:5] = summary_block

    # Write files
    md_path = out / "qc_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    json_path = out / "structured.json"
    json_path.write_text(
        json.dumps(structured, indent=2, default=str), encoding="utf-8"
    )

    print(f"[QC] Report written to {md_path}")
    print(f"[QC] Structured JSON written to {json_path}")
    return summary
