# CardioRAG — Medical Guideline PDF Parsing & Chunking Pipeline

A robust Python pipeline that converts clinical guideline documents into high-quality, medically meaningful RAG chunks with rich clinical metadata.

Supported Guidelines:
1. **NICE Guideline NG238** (Cardiovascular disease: risk assessment and reduction, including lipid modification, 14 December 2023)
2. **WHO Guideline 2021** (Pharmacological treatment of hypertension in adults)

---

## Overview

This pipeline is the **ingestion layer** for the CardioRAG medical RAG system. It is deterministic and rule-based, designed for high retrieval precision, medical safety, and zero clinical hallucination.

### Key Capabilities

1. **PDF Extraction**: Extracts text with page tracking (PyMuPDF) and structured tables (pdfplumber).
2. **Medical Cleaning**: Strips repetitive header/footer boilerplate while preserving units, lipid values, thresholds, doses, and comparison operators.
3. **Guideline Structure Detection**: Detects all major sections, subheadings, and committee rationale sections.
4. **Recommendation Parsing**: Extracts individual recommendation IDs (e.g. `1.7.1`, `1.6.7`), original/amended dates, and cross-references.
5. **Rich Medical Metadata**: Extracts populations, risk tools (QRISK3), lipid targets, drug doses, lab tests, and technology appraisals (TAs).
6. **Semantic Chunking**: Creates standalone recommendation chunks and separate committee rationale chunks with deterministic IDs.
7. **Validation & Medical Safety**: Automated checks for 15 validation rules, numerical integrity, and priority assignment.
8. **Multi-Format Output**: Emits JSON array, JSONL, markdown preview, and processing reports.

---

## Project Structure

```text
cardiorag/
├── data/
│   ├── raw/
│   │   ├── NICE3.pdf
│   │   └── WHO03.pdf
│   └── processed/
│       ├── nice3_chunks.json
│       ├── nice3_chunks.jsonl
│       ├── nice3_chunks_preview.md
│       ├── nice3_processing_report.json
│       ├── who03_chunks.json
│       ├── who03_chunks.jsonl
│       └── who03_chunks_preview.md
├── src/
│   ├── parse_nice3.py               # NICE3 PyMuPDF & table extractor
│   ├── parse_who03.py               # WHO03 PyMuPDF & table extractor
│   ├── clean_text.py                # Safe text cleaning & boilerplate stripping
│   ├── nice_section_parser.py       # NICE3 section hierarchy & heading detection
│   ├── section_parser.py            # WHO03 section parser
│   ├── nice_recommendation_parser.py# NICE recommendation ID & date parser
│   ├── nice_metadata_extractor.py   # NICE3 metadata schemas & clinical mapping
│   ├── metadata_extractor.py        # WHO03 metadata extractor
│   ├── chunk_nice3.py               # NICE3 semantic chunker
│   ├── chunk_who03.py               # WHO03 semantic chunker
│   ├── deduplicate.py               # Clinical-aware deduplication
│   ├── validate_chunks.py           # 15-rule validation & numerical integrity
│   ├── run_nice3_pipeline.py        # NICE3 pipeline orchestrator
│   └── run_pipeline.py              # WHO03 pipeline orchestrator
├── tests/
│   ├── test_nice3_chunking.py       # NICE3 test suite
│   └── test_who03_chunking.py       # WHO03 test suite
├── requirements.txt
└── README.md
```

---

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run NICE3 (NG238) Pipeline

```bash
python src/run_nice3_pipeline.py
```

### Run NICE3 Tests

```bash
pytest tests/test_nice3_chunking.py -v
```

---

## Chunk Format Example (NICE NG238)

```json
{
  "chunk_id": "NICE3_1.7.1_REC",
  "text": "Section: 1.7 Lipid-lowering treatment for secondary prevention of cardiovascular disease\nSubheading: Lipid target for people taking lipid-lowering treatments\nRecommendation: 1.7.1\n\n1.7.1 For secondary prevention of CVD, aim for LDL cholesterol levels of 2.0 mmol per litre or less, or non-HDL cholesterol levels of 2.6 mmol per litre or less. [December 2023]",
  "token_count": 78,
  "metadata": {
    "source_file": "NICE3.pdf",
    "organization": "NICE",
    "guideline_code": "NG238",
    "document_title": "Cardiovascular disease: risk assessment and reduction, including lipid modification",
    "original_publication_date": "2023-12-14",
    "pdf_page_start": 26,
    "pdf_page_end": 26,
    "section": "1.7 Lipid-lowering treatment for secondary prevention of cardiovascular disease",
    "subsection": "Lipid target for people taking lipid-lowering treatments",
    "recommendation_id": "1.7.1",
    "recommendation_original_date": "December 2023",
    "recommendation_amended_dates": [],
    "domain": "cardiovascular_disease",
    "topic": "lipid_lowering_treatment",
    "subtopic": "secondary_prevention_lipid_target",
    "content_type": "recommendation",
    "prevention_type": "secondary",
    "population": ["people_with_cvd"],
    "lipid_measure": ["LDL", "non-HDL"],
    "clinical_priority": 1,
    "historical_context": false,
    "requires_manual_review": false
  }
}
```

---

## Medical Safety Guarantee

- **No Paraphrasing**: Guideline recommendation texts are verbatim extracts from the official PDF.
- **No Model Inference**: Clinical thresholds, drug doses, and dates are never fabricated or rewritten by LLM knowledge.
- **Traceability**: Every chunk preserves PDF page provenance for verifiable medical citations.
