"""
Seismic Data Extractor
Converts seismic feature descriptions (text/PDF) into structured JSON
with confidence scoring and QC recommendations.
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SeismicFeature:
    """Structured representation of a seismic feature."""
    # Identifiers
    feature_id: Optional[str] = None
    feature_name: Optional[str] = None

    # Fault / structure classification
    fault_type: Optional[str] = None          # normal, reverse, strike-slip, thrust…
    structure_type: Optional[str] = None      # anticline, syncline, dome, graben…

    # Spatial attributes
    depth_m: Optional[float] = None           # depth in metres
    depth_unit: Optional[str] = None          # m / ft / km
    depth_raw: Optional[str] = None           # original text excerpt

    strike: Optional[float] = None            # degrees
    dip: Optional[float] = None               # degrees
    dip_direction: Optional[str] = None

    # Seismic attributes
    amplitude: Optional[str] = None           # high / low / moderate / dim / bright
    frequency: Optional[str] = None
    reflector_continuity: Optional[str] = None
    velocity_ms: Optional[float] = None

    # Temporal / stratigraphic
    age: Optional[str] = None
    formation: Optional[str] = None
    horizon: Optional[str] = None

    # Confidence & QC
    confidence_score: float = 0.0             # 0–1
    missing_fields: list = field(default_factory=list)
    qc_flags: list = field(default_factory=list)
    qc_recommendations: list = field(default_factory=list)
    source_text: str = ""


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

FAULT_TYPES = ["normal", "reverse", "thrust", "strike-slip", "oblique", "listric",
               "growth", "blind", "flower", "tear", "detachment"]

STRUCTURE_TYPES = ["anticline", "syncline", "dome", "basin", "graben", "horst",
                   "half-graben", "rollover", "diapir", "salt", "mud volcano",
                   "fold", "monocline", "reef"]

AMPLITUDE_KEYWORDS = ["high amplitude", "low amplitude", "moderate amplitude",
                       "bright spot", "dim spot", "flat spot", "amplitude anomaly",
                       "strong reflector", "weak reflector"]

REQUIRED_FIELDS = ["fault_type", "depth_m", "strike", "dip", "formation"]


def _search(pattern: str, text: str, flags=re.IGNORECASE):
    return re.search(pattern, text, flags)


class SeismicExtractor:
    """Rule-based + regex extractor for seismic feature descriptions."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_from_text(self, text: str, feature_id: str = "F-001") -> SeismicFeature:
        feat = SeismicFeature(source_text=text, feature_id=feature_id)
        self._extract_fault_type(text, feat)
        self._extract_structure_type(text, feat)
        self._extract_depth(text, feat)
        self._extract_strike_dip(text, feat)
        self._extract_amplitude(text, feat)
        self._extract_frequency(text, feat)
        self._extract_reflector_continuity(text, feat)
        self._extract_velocity(text, feat)
        self._extract_age(text, feat)
        self._extract_formation(text, feat)
        self._extract_feature_name(text, feat)
        self._compute_confidence(feat)
        self._generate_qc(feat)
        return feat

    def extract_from_pdf(self, pdf_path: str) -> list[SeismicFeature]:
        """Parse a PDF and extract one feature per paragraph-like block."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("Install pdfplumber: pip install pdfplumber")

        results = []
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

        blocks = self._split_into_blocks(full_text)
        for i, block in enumerate(blocks, start=1):
            if len(block.strip()) > 30:
                feat = self.extract_from_text(block.strip(), feature_id=f"F-{i:03d}")
                results.append(feat)
        return results

    def to_json(self, feature: SeismicFeature, indent: int = 2) -> str:
        return json.dumps(asdict(feature), indent=indent, default=str)

    def to_json_list(self, features: list[SeismicFeature], indent: int = 2) -> str:
        return json.dumps([asdict(f) for f in features], indent=indent, default=str)

    # ------------------------------------------------------------------
    # Private extraction helpers
    # ------------------------------------------------------------------

    def _extract_fault_type(self, text: str, feat: SeismicFeature):
        for ft in FAULT_TYPES:
            if re.search(rf"\b{re.escape(ft)}\b", text, re.IGNORECASE):
                feat.fault_type = ft
                return
        # generic "fault" mention
        if _search(r"\bfault\b", text):
            feat.fault_type = "unclassified"

    def _extract_structure_type(self, text: str, feat: SeismicFeature):
        for st in STRUCTURE_TYPES:
            if re.search(rf"\b{re.escape(st)}\b", text, re.IGNORECASE):
                feat.structure_type = st
                return

    def _extract_depth(self, text: str, feat: SeismicFeature):
        # e.g. "depth of 2500 m", "at 3.2 km", "~4000 ft"
        patterns = [
            (r"depth[^\d]{0,20}([\d,\.]+)\s*(m\b|metres?|meters?)", "m"),
            (r"depth[^\d]{0,20}([\d,\.]+)\s*(km\b|kilometres?|kilometers?)", "km"),
            (r"depth[^\d]{0,20}([\d,\.]+)\s*(ft\b|feet|foot)", "ft"),
            (r"([\d,\.]+)\s*(m\b|metres?|meters?)\s*(depth|deep|bsl|tvd)", "m"),
            (r"([\d,\.]+)\s*(km)\s*(depth|deep|bsl)", "km"),
            (r"~?([\d,\.]+)\s*(m|ft|km)\b", None),  # loose match
        ]
        for pat, unit in patterns:
            m = _search(pat, text)
            if m:
                raw_val = m.group(1).replace(",", "")
                try:
                    val = float(raw_val)
                    detected_unit = unit or m.group(2).lower()
                    # normalise to metres
                    if detected_unit in ("km", "kilometres", "kilometers"):
                        feat.depth_m = val * 1000
                    elif detected_unit in ("ft", "feet", "foot"):
                        feat.depth_m = round(val * 0.3048, 1)
                    else:
                        feat.depth_m = val
                    feat.depth_unit = detected_unit
                    feat.depth_raw = m.group(0)
                    return
                except ValueError:
                    continue

    def _extract_strike_dip(self, text: str, feat: SeismicFeature):
        # Strike: "strike 045°", "striking N45E", "azimuth 270"
        m = _search(r"strik(?:e|ing)[^\d]{0,15}(\d{1,3})\s*[°\u00b0]?", text)
        if m:
            feat.strike = float(m.group(1))

        # Dip: "dip 30°", "dipping 45° NE", "dip angle 15"
        m = _search(r"dip(?:ping)?[^\d]{0,15}(\d{1,2})\s*[°\u00b0]?", text)
        if m:
            feat.dip = float(m.group(1))

        # Dip direction
        m = _search(
            r"dip(?:ping)?\s+\d+[°\u00b0]?\s+(N|S|E|W|NE|NW|SE|SW|NNE|NNW|SSE|SSW|ENE|ESE|WNW|WSW)",
            text,
        )
        if m:
            feat.dip_direction = m.group(1)

    def _extract_amplitude(self, text: str, feat: SeismicFeature):
        for kw in AMPLITUDE_KEYWORDS:
            if re.search(re.escape(kw), text, re.IGNORECASE):
                feat.amplitude = kw
                return
        m = _search(r"(high|low|moderate|strong|weak|bright|dim)\s+amplitude", text)
        if m:
            feat.amplitude = m.group(0).lower()

    def _extract_frequency(self, text: str, feat: SeismicFeature):
        m = _search(r"(\d+)\s*Hz\b", text)
        if m:
            feat.frequency = f"{m.group(1)} Hz"
            return
        m = _search(r"(high|low|dominant|dominant\s+frequency)[- ]frequency", text)
        if m:
            feat.frequency = m.group(0).lower()

    def _extract_reflector_continuity(self, text: str, feat: SeismicFeature):
        for kw in ["continuous", "discontinuous", "disrupted", "chaotic",
                   "parallel", "sub-parallel", "divergent", "convergent"]:
            if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
                feat.reflector_continuity = kw
                return

    def _extract_velocity(self, text: str, feat: SeismicFeature):
        m = _search(r"velocity[^\d]{0,10}([\d,\.]+)\s*m/s", text)
        if m:
            feat.velocity_ms = float(m.group(1).replace(",", ""))

    def _extract_age(self, text: str, feat: SeismicFeature):
        ages = ["cretaceous", "jurassic", "triassic", "permian", "carboniferous",
                "devonian", "miocene", "oligocene", "eocene", "paleocene",
                "pleistocene", "holocene", "neogene", "paleogene", "mesozoic",
                "cenozoic", "paleozoic"]
        for age in ages:
            if re.search(rf"\b{age}\b", text, re.IGNORECASE):
                feat.age = age.capitalize()
                return

    def _extract_formation(self, text: str, feat: SeismicFeature):
        m = _search(
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+(formation|member|group|horizon|unit|sand|shale|limestone)\b",
            text,
        )
        if m:
            feat.formation = m.group(0)
            feat.horizon = feat.formation

    def _extract_feature_name(self, text: str, feat: SeismicFeature):
        m = _search(r"(?:feature|structure|fault|horizon)[:\s]+([A-Z][A-Za-z0-9\-_]+)", text)
        if m:
            feat.feature_name = m.group(1)

    # ------------------------------------------------------------------
    # Confidence & QC
    # ------------------------------------------------------------------

    def _compute_confidence(self, feat: SeismicFeature):
        """Score 0–1 based on how many important fields are populated."""
        weights = {
            "fault_type": 0.20,
            "depth_m": 0.20,
            "strike": 0.10,
            "dip": 0.10,
            "formation": 0.15,
            "amplitude": 0.10,
            "age": 0.08,
            "reflector_continuity": 0.07,
        }
        score = sum(
            w for attr, w in weights.items() if getattr(feat, attr) is not None
        )
        feat.confidence_score = round(min(score, 1.0), 3)
        feat.missing_fields = [
            attr for attr in REQUIRED_FIELDS if getattr(feat, attr) is None
        ]

    def _generate_qc(self, feat: SeismicFeature):
        flags = []
        recs = []

        if feat.depth_m is None:
            flags.append("MISSING_DEPTH")
            recs.append("Provide depth measurement (TWT or TVD) in metres or feet.")

        if feat.fault_type is None:
            flags.append("MISSING_FAULT_TYPE")
            recs.append("Classify fault type (normal, reverse, strike-slip, thrust, etc.).")

        if feat.dip is None:
            flags.append("MISSING_DIP")
            recs.append("Add dip angle and direction for structural analysis.")

        if feat.strike is None:
            flags.append("MISSING_STRIKE")
            recs.append("Add strike azimuth for fault/structure orientation.")

        if feat.formation is None:
            flags.append("MISSING_FORMATION")
            recs.append("Link feature to a named stratigraphic formation or horizon.")

        if feat.amplitude is None:
            flags.append("MISSING_AMPLITUDE")
            recs.append("Include amplitude description for DHI (Direct Hydrocarbon Indicator) analysis.")

        if feat.depth_m is not None and feat.depth_m > 8000:
            flags.append("DEPTH_EXCEEDS_TYPICAL")
            recs.append("Depth > 8 000 m — verify units and confirm TWT-to-depth conversion.")

        if feat.dip is not None and feat.dip > 85:
            flags.append("NEAR_VERTICAL_DIP")
            recs.append("Dip > 85° — confirm measurement; may indicate overturned beds.")

        if feat.confidence_score < 0.3:
            flags.append("LOW_CONFIDENCE")
            recs.append("Confidence < 30% — description is sparse; enrich with additional attributes.")
        elif feat.confidence_score < 0.6:
            flags.append("MODERATE_CONFIDENCE")
            recs.append("Confidence < 60% — consider supplementing with seismic cross-sections or well-log ties.")

        feat.qc_flags = flags
        feat.qc_recommendations = recs

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _split_into_blocks(text: str) -> list[str]:
        """Split text into paragraph-like blocks."""
        blocks = re.split(r"\n{2,}", text)
        if len(blocks) == 1:
            # fallback: split on sentence boundaries
            blocks = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        return [b.strip() for b in blocks if b.strip()]
