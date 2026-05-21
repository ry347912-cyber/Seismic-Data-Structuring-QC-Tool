# 🌍 Seismic Data Structuring & QC Tool

> **HiDevs GenAI Internship — Oil & Gas Project**  
> Convert seismic feature descriptions (text / PDF) into structured JSON with confidence scoring and automated QC recommendations.

---

## 📌 Problem Statement

Seismic interpreters produce large volumes of free-text descriptions of geological features — faults, horizons, anticlines — that are difficult to query, analyse, or validate programmatically. This tool:

1. **Extracts** key attributes (fault type, depth, strike, dip, formation, amplitude…) from unstructured text or PDF reports.
2. **Structures** them into a validated JSON schema.
3. **Scores confidence** (0–100 %) based on attribute completeness.
4. **Flags** missing or suspicious fields and generates actionable QC recommendations.

---

## 🏗️ Architecture

```
Input (text / PDF)
      │
      ▼
┌─────────────────────────────────┐
│  Step 1 – Data Sources          │  pdfplumber, raw text
│  Step 2 – Data Preprocessing    │  cleaning, block splitting
│  Step 3 – Chunking              │  RecursiveCharacterTextSplitter
│  Step 4 – Embeddings + VectorDB │  all-MiniLM-L6-v2 + ChromaDB
│  Step 5 – Query + AI Engine     │  Groq / Llama3 + LangChain RAG
│  Step 6 – UI + Deployment       │  Streamlit + GitHub
│  Step 7 – Testing & Evaluation  │  LangChain Eval / DeepEval
└─────────────────────────────────┘
      │
      ▼
Structured JSON + Markdown QC Report
```

---

## 📂 Project Structure

```
seismic-qc/
├── app.py                  # Streamlit UI
├── main.py                 # CLI entry point
├── requirements.txt
├── .env.example            # API key template
├── src/
│   ├── extractor.py        # Core extraction engine
│   ├── rag_pipeline.py     # LangChain RAG (ChromaDB + Groq)
│   └── qc_report.py        # Markdown + JSON report generator
├── data/
│   └── samples/            # Sample seismic descriptions
└── outputs/                # Generated reports (git-ignored)
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/seismic-qc.git
cd seismic-qc
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at → https://console.groq.com

### 3. Run the CLI (no API key needed)

```bash
# Demo mode — uses built-in sample data
python main.py --demo

# Single description
python main.py --text "Normal fault at depth 2500 m, strike 045°, dip 30° NW, Brent Formation"

# PDF report
python main.py --pdf data/samples/my_report.pdf
```

Outputs are written to `outputs/structured.json` and `outputs/qc_report.md`.

### 4. Launch the Streamlit UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 📊 Output Schema

```json
{
  "feature_id": "F-001",
  "fault_type": "normal",
  "structure_type": null,
  "depth_m": 2800.0,
  "depth_unit": "m",
  "depth_raw": "depth of 2800 m",
  "strike": 45.0,
  "dip": 35.0,
  "dip_direction": "NW",
  "amplitude": "high amplitude bright spot",
  "frequency": null,
  "reflector_continuity": "continuous",
  "velocity_ms": 3200.0,
  "age": null,
  "formation": "Cretaceous Brent Formation",
  "confidence_score": 0.8,
  "missing_fields": ["age"],
  "qc_flags": ["MISSING_AMPLITUDE"],
  "qc_recommendations": [
    "Include amplitude description for DHI analysis."
  ],
  "source_text": "..."
}
```

---

## 🔍 Confidence Scoring

| Score | Label | Meaning |
|-------|-------|---------|
| ≥ 70 % | 🟢 High | Most required fields present |
| 40–69 % | 🟡 Moderate | Key fields missing; usable with caveats |
| < 40 % | 🔴 Low | Sparse description; enrich before use |

---

## 🤖 RAG Pipeline (Step 4–5)

The optional RAG pipeline (`src/rag_pipeline.py`) enables natural-language queries over a corpus of seismic documents:

```python
from src.rag_pipeline import build_rag_pipeline
chain = build_rag_pipeline("data/samples")
answer = chain.invoke({"question": "What is the depth of fault F-001?"})
```

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (free, HuggingFace)
- **Vector DB**: ChromaDB (local, no API key needed)
- **LLM**: Llama3-8b via Groq (free tier)

---

## 🧪 Testing & Evaluation (Step 7)

```bash
# LangChain string criteria evaluation
python -c "
from langchain.evaluation import load_evaluator
evaluator = load_evaluator('criteria', criteria='correctness')
result = evaluator.evaluate_strings(
    prediction='Normal fault at 2800 m',
    input='What type and depth is fault F-001?'
)
print(result)
"
```

Optional tools: **TruLens**, **DeepEval**, **Promptfoo** — see `requirements.txt` comments.

---

## 🚀 Deployment

### Streamlit Cloud (free)
1. Push to GitHub
2. Go to https://share.streamlit.io → New app → select `app.py`
3. Add `GROQ_API_KEY` in Secrets

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 🛠️ Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| PDF Parsing | pdfplumber | Free |
| Chunking | LangChain RecursiveCharacterTextSplitter | Free |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | Free |
| Vector DB | ChromaDB | Free / Open-source |
| LLM | Llama3 via Groq | Free (developer tier) |
| UI | Streamlit | Free |
| Version Control | GitHub | Free |

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

## 👤 Author

Built as part of the **HiDevs 100-Day GenAI Internship**.
