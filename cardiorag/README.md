# CardioRAG — WHO03 PDF Parsing & Chunking Pipeline

A robust Python pipeline that converts **WHO03.pdf** (WHO Guideline for the Pharmacological Treatment of Hypertension in Adults, 2021) into high-quality, medically meaningful RAG chunks with rich clinical metadata.

## Overview

This pipeline is the **ingestion layer** for the CardioRAG medical RAG system. It does **not** include embeddings, vector databases, or LLM integration — those come later.

### What it does

1. **Extracts** text from the PDF (PyMuPDF) with page tracking
2. **Extracts** structured tables (pdfplumber)
3. **Detects** figures and clinical algorithms
4. **Cleans** text while preserving all medical content (drug names, BP values, units, operators)
5. **Detects** document structure using TOC + regex + font-size analysis
6. **Classifies** content into types (recommendation, evidence, implementation remark, etc.)
7. **Extracts** clinical metadata (drug classes, BP thresholds, comorbidities, recommendation strength, evidence certainty)
8. **Creates** semantic chunks respecting section boundaries and clinical context
9. **Deduplicates** repeated recommendations across sections
10. **Validates** output against 10 quality rules
11. **Outputs** JSON, JSONL, and human-readable Markdown preview

## Project Structure

```
cardiorag/
├── data/
│   ├── raw/
│   │   └── WHO03.pdf
│   └── processed/
│       ├── who03_chunks.json
│       ├── who03_chunks.jsonl
│       ├── who03_chunks_preview.md
│       ├── who03_stats.json
│       └── figures/
├── src/
│   ├── parse_who03.py          # PDF extraction (PyMuPDF + pdfplumber)
│   ├── clean_text.py           # Noise removal & medical-safe normalization
│   ├── section_parser.py       # Document structure detection (TOC-first)
│   ├── metadata_extractor.py   # Clinical metadata & recommendation parsing
│   ├── chunk_who03.py          # Semantic chunking engine
│   └── run_pipeline.py         # Pipeline orchestrator
├── tests/
│   └── test_who03_chunking.py
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Place `WHO03.pdf` in `data/raw/`.

## Usage

### Run the pipeline

```bash
python src/run_pipeline.py
```

Or with a custom PDF path:

```bash
python src/run_pipeline.py --pdf /path/to/WHO03.pdf
```

### Run tests

```bash
pytest tests/test_who03_chunking.py -v
```

## Output Format

Each chunk in `who03_chunks.json`:

```json
{
  "chunk_id": "WHO03_3.4_REC_001",
  "text": "...",
  "token_count": 537,
  "metadata": {
    "source_file": "WHO03.pdf",
    "organization": "WHO",
    "document_title": "Guideline for the pharmacological treatment of hypertension in adults",
    "publication_year": 2021,
    "domain": "hypertension",
    "pdf_page_start": 23,
    "pdf_page_end": 23,
    "section": "3 Recommendations",
    "subsection": "3.4 Drug classes to be used as first-line agents",
    "topic": "pharmacological_treatment",
    "subtopic": "first_line_agents",
    "content_type": "recommendation",
    "recommendation_strength": "strong",
    "evidence_certainty": "high",
    "clinical_priority": 1,
    "...": "..."
  }
}
```

## Medical Safety Rules

- No recommendation wording is paraphrased or altered during ingestion
- No LLM knowledge is used to "correct" WHO content
- All text is extracted directly from the source PDF
- Units, BP thresholds, and drug doses are preserved exactly
- Extraction uncertainty is flagged, never invented
