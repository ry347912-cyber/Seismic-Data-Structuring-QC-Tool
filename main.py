#!/usr/bin/env python3
"""
CLI for Seismic QC Tool
Usage:
  python main.py --text "Normal fault at depth 2500 m, strike 045°, dip 30° NW"
  python main.py --pdf data/samples/report.pdf
  python main.py --demo
"""

import argparse
import json
import sys
from pathlib import Path

from src.extractor import SeismicExtractor
from src.qc_report import generate_report

DEMO_TEXTS = [
    (
        "The reverse fault RF-07 was identified in the Jurassic Fulmar Formation at a depth of 3500 m. "
        "Strike is 090° with a dip of 45° SE. High amplitude bright spot anomaly observed. "
        "Reflectors are continuous and sub-parallel. Velocity approximately 3800 m/s."
    ),
    (
        "A normal fault trending NE-SW was mapped at approximately 1800 ft depth. "
        "No formation data available. Dip estimated around 60°. "
        "Amplitude character is low and discontinuous."
    ),
    (
        "Strike-slip fault zone observed in the Cretaceous section. "
        "Chaotic reflector pattern with moderate amplitude. "
        "Feature extends from surface to 4.2 km depth."
    ),
]


def main():
    parser = argparse.ArgumentParser(description="Seismic QC Tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--text", help="Single feature description string")
    group.add_argument("--pdf", help="Path to PDF file")
    group.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--out", default="outputs", help="Output directory")
    args = parser.parse_args()

    extractor = SeismicExtractor()
    features = []

    if args.demo or (not args.text and not args.pdf):
        print("Running in DEMO mode with sample seismic descriptions...\n")
        for i, txt in enumerate(DEMO_TEXTS, start=1):
            feat = extractor.extract_from_text(txt, feature_id=f"F-{i:03d}")
            features.append(feat)

    elif args.text:
        feat = extractor.extract_from_text(args.text, feature_id="F-001")
        features.append(feat)

    elif args.pdf:
        if not Path(args.pdf).exists():
            print(f"Error: PDF not found: {args.pdf}", file=sys.stderr)
            sys.exit(1)
        features = extractor.extract_from_pdf(args.pdf)

    # Print JSON to stdout
    print(extractor.to_json_list(features))

    # Write reports
    summary = generate_report(features, output_dir=args.out)
    print(f"\n✅ Done. {summary['total_features']} feature(s) processed.")
    print(f"   High confidence : {summary['high_confidence']}")
    print(f"   Moderate        : {summary['moderate_confidence']}")
    print(f"   Low confidence  : {summary['low_confidence']}")
    print(f"\n📁 Outputs in ./{args.out}/")


if __name__ == "__main__":
    main()
