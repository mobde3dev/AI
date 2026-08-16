You are working on a medical RAG project called **CardioRAG**.

Your current task is NOT to build the full RAG system yet.

Your task is to build a robust **PDF parsing, cleaning, section detection, medical metadata extraction, and semantic chunking pipeline** specifically for the following document:

`WHO03.pdf`

Document:

**World Health Organization — Guideline for the pharmacological treatment of hypertension in adults — 2021**

The output of this task will later be embedded and stored in a vector database such as Qdrant or Chroma.

---

# 1. Main Goal

Create a Python pipeline that converts:

`WHO03.pdf`

into high-quality, medically meaningful RAG chunks.

Do NOT simply split the PDF every 500 characters or every N words.

The chunking must respect:

- document sections
- recommendations
- implementation remarks
- evidence and rationale
- evidence-to-decision considerations
- bullet lists
- algorithms
- tables
- special populations
- page numbers
- recommendation strength
- certainty of evidence

The final chunks must be suitable for a clinical guideline RAG system.

---

# 2. Project Structure

Create or update this structure:

```text
cardiorag/
│
├── data/
│   ├── raw/
│   │   └── WHO03.pdf
│   │
│   └── processed/
│       ├── who03_chunks.json
│       ├── who03_chunks.jsonl
│       └── who03_chunks_preview.md
│
├── src/
│   ├── parse_who03.py
│   ├── clean_text.py
│   ├── section_parser.py
│   ├── metadata_extractor.py
│   └── chunk_who03.py
│
├── tests/
│   └── test_who03_chunking.py
│
├── requirements.txt
│
└── README.md
```

If the project already has an equivalent structure, reuse it instead of unnecessarily duplicating files.

---

# 3. PDF Parsing

Use a reliable PDF text extraction library.

Prefer:

```text
PyMuPDF
```

but design the parser so another extractor can be substituted later.

For every extracted text block preserve:

```text
physical PDF page number
page label if detectable
raw text
cleaned text
```

Page numbers must NEVER be lost because citations will later depend on them.

Use 1-based page numbering for user-facing metadata.

Example:

```json
{
  "pdf_page": 23,
  "page_label": "11",
  "text": "..."
}
```

If a printed page number differs from the physical PDF page, retain both values.

---

# 4. Remove PDF Noise

Remove repetitive content that should not become RAG chunks.

Examples:

- repeated running headers
- repeated document titles
- page-number-only lines
- repeated footer text
- copyright lines
- ISBN information
- URLs repeated in page footers
- empty lines
- broken whitespace
- repeated boilerplate

BUT never remove meaningful clinical content.

Do not accidentally remove:

- drug names
- doses
- BP values
- recommendation numbers
- evidence grades
- bullets
- thresholds
- units
- clinical abbreviations

Preserve expressions such as:

```text
≥140 mmHg
130–139 mmHg
<130 mmHg
ACEi
ARB
CCB
CKD
CVD
SBP
DBP
```

---

# 5. Normalize Text Carefully

Normalize:

- excessive whitespace
- broken line wraps
- Unicode bullet characters
- hyphenation caused only by PDF line wrapping

Do NOT alter medical meaning.

For example:

Do not convert:

```text
130–139 mmHg
```

into:

```text
130139
```

Do not modify comparison operators:

```text
≥
≤
<
>
```

Do not automatically rewrite WHO wording.

The original recommendation wording must remain intact.

---

# 6. Detect WHO03 Document Structure

The system must recognize the important hierarchy of the guideline.

At minimum detect:

```text
1 Introduction

2 Method for developing the guideline

3 Recommendations

3.1 Blood pressure threshold for initiation of pharmacological treatment

3.2 Laboratory testing before and during pharmacological treatment

3.3 Cardiovascular disease risk assessment as guide to initiation of antihypertensive medications

3.4 Drug classes to be used as first-line agents

3.5 Combination therapy

3.6 Target blood pressure

3.7 Frequency of reassessment

3.8 Administration of treatment by nonphysician professionals

4 Special settings

4.1 Hypertension in disaster, humanitarian and emergency settings

4.2 COVID-19 and hypertension

4.3 Pregnancy and hypertension

5 Publication, implementation, evaluation and research gaps

6 Implementation tools

6.1 Guideline recommendations

6.2 Drug- and dose-specific protocols
```

Do not rely exclusively on page numbers.

Detect headings from textual structure and numbering.

---

# 7. Clinical Topic Mapping

Map sections to normalized RAG topics.

Use values similar to:

```text
domain = hypertension
```

For subsection 3.1:

```text
topic = treatment_initiation
```

3.2:

```text
topic = laboratory_testing
```

3.3:

```text
topic = cardiovascular_risk_assessment
```

3.4:

```text
topic = pharmacological_treatment
subtopic = first_line_agents
```

3.5:

```text
topic = combination_therapy
```

3.6:

```text
topic = blood_pressure_target
```

3.7:

```text
topic = follow_up
subtopic = reassessment_frequency
```

3.8:

```text
topic = healthcare_delivery
subtopic = nonphysician_management
```

Special settings should be classified appropriately:

```text
special_setting = disaster_or_humanitarian
special_setting = covid_19
special_setting = pregnancy
```

---

# 8. Recommendation-Aware Parsing

This is CRITICAL.

WHO recommendation blocks must be recognized separately from supporting evidence.

Detect structures such as:

```text
RECOMMENDATION ON ...
```

followed by:

```text
WHO recommends ...
```

or:

```text
WHO suggests ...
```

Then detect:

```text
Strong recommendation
Conditional recommendation
```

and evidence certainty such as:

```text
high-certainty evidence
moderate-certainty evidence
low-certainty evidence
moderate- to high-certainty evidence
```

Extract these into metadata.

Example:

```json
{
  "recommendation_strength": "strong",
  "evidence_certainty": "high"
}
```

Normalize metadata values but NEVER modify the recommendation's original text.

---

# 9. Content Types

Classify every chunk into one of these types where possible:

```text
recommendation
implementation_remark
evidence_rationale
evidence_to_decision
background
definition
clinical_threshold
drug_guidance
laboratory_guidance
risk_assessment
follow_up
special_setting
algorithm
table
research_methodology
other
```

This field will later be used during retrieval and reranking.

---

# 10. Recommendation Chunking Rule

A recommendation should normally be its OWN chunk.

For example:

```text
Section title

Recommendation title

WHO recommendation text

Recommendation strength

Evidence certainty
```

Keep all these together.

DO NOT split a recommendation from:

```text
Strong recommendation
```

or:

```text
Conditional recommendation
```

or its evidence-certainty statement.

---

# 11. Implementation Remarks

Implementation remarks should normally become a separate chunk.

However they must retain metadata linking them to the corresponding recommendation.

Example:

```json
{
  "content_type": "implementation_remark",
  "parent_recommendation": "3.1"
}
```

The text of the chunk should include enough context so it is understandable when retrieved independently.

Prefix the chunk text internally with contextual information if necessary:

```text
Section: 3.1 Blood pressure threshold for initiation of pharmacological treatment

Implementation remarks:
...
```

Do not change the source wording.

---

# 12. Evidence and Rationale

Do not mix a very large evidence section into the recommendation chunk.

Create separate evidence chunks.

For example:

```text
Section:
3.4 Drug classes to be used as first-line agents

Content type:
Evidence and rationale

[original evidence text]
```

Target approximately:

```text
400–750 tokens
```

per evidence chunk.

Maximum approximately:

```text
900 tokens
```

But section boundaries and semantic completeness are MORE important than token count.

Never split:

- a short bullet list
- a clinical comparison
- a dose
- a numerical result
- a sentence
- a recommendation statement

solely to meet a token target.

---

# 13. Chunk Overlap

Use minimal overlap.

For long evidence/rationale text:

```text
50–100 tokens overlap
```

Avoid excessive overlap because it creates duplicate search results.

Recommendations generally need NO overlap if they are self-contained.

---

# 14. Clinical Entity Metadata

Where clearly stated in the source, extract useful structured metadata.

Possible fields:

```text
population
condition
comorbidity
drug_class
drug_name
bp_threshold
target_bp
age_group
special_population
```

Examples of values:

```text
population = adults_with_confirmed_hypertension

comorbidity = cardiovascular_disease

comorbidity = diabetes_mellitus

comorbidity = chronic_kidney_disease

drug_class = thiazide_or_thiazide_like

drug_class = ace_inhibitor

drug_class = arb

drug_class = calcium_channel_blocker
```

Only assign metadata supported by the actual source text.

Do not infer medical facts from general model knowledge.

---

# 15. Source Metadata

Every final chunk MUST contain:

```json
{
  "source_file": "WHO03.pdf",
  "organization": "WHO",
  "document_title": "Guideline for the pharmacological treatment of hypertension in adults",
  "publication_year": 2021,
  "domain": "hypertension",
  "pdf_page_start": 0,
  "pdf_page_end": 0,
  "page_label_start": null,
  "page_label_end": null,
  "section": "",
  "subsection": "",
  "recommendation_id": null,
  "topic": "",
  "subtopic": null,
  "content_type": "",
  "recommendation_strength": null,
  "evidence_certainty": null,
  "population": null,
  "special_setting": null,
  "region_scope": "global",
  "clinical_priority": 1
}
```

Use `null` instead of inventing unavailable metadata.

---

# 16. Chunk IDs

Generate deterministic IDs.

Examples:

```text
WHO03_3.1_REC_001

WHO03_3.1_IMPL_001

WHO03_3.1_EVID_001

WHO03_3.4_REC_001

WHO03_3.4_EVID_001
```

If a section has multiple evidence chunks:

```text
WHO03_3.4_EVID_001
WHO03_3.4_EVID_002
WHO03_3.4_EVID_003
```

Chunk IDs should remain stable when the pipeline is rerun on the same document.

---

# 17. Tables

Do not flatten tables into meaningless text.

When possible convert a table into structured readable text.

Example:

```text
Table: [table title]

Column A | Column B | Column C
...

Source: WHO03
Section: ...
Page: ...
```

Preserve:

- drug names
- doses
- contraindications
- thresholds
- clinical categories

If reliable extraction is impossible, record the issue in a processing report instead of inventing table values.

---

# 18. Algorithms and Figures

The implementation section contains clinical algorithms.

Detect:

```text
Algorithm 1
Algorithm 2
```

and other clinically relevant figures.

Create dedicated chunks:

```text
content_type = algorithm
```

Preserve:

- algorithm title
- steps
- conditions
- thresholds
- medications
- doses if present
- page

If essential information is represented graphically and cannot be extracted reliably from text, flag that page for manual or image-based extraction.

Do NOT hallucinate missing nodes in a clinical algorithm.

---

# 19. Front Matter and Administrative Content

Do NOT include ordinary clinical RAG chunks for:

```text
copyright
ISBN
acknowledgements
contributor names
conflict-of-interest lists
contact information
general publishing boilerplate
```

Also do not index the full bibliography into the main clinical collection.

References may remain accessible separately if needed.

---

# 20. Research Methodology

Sections about:

```text
PICO
GRADE
systematic review methodology
guideline development
```

may be retained, but tag them:

```text
content_type = research_methodology
clinical_priority = 3
```

Clinical recommendations should normally have:

```text
clinical_priority = 1
```

Supporting evidence/rationale:

```text
clinical_priority = 2
```

Administrative or research methodology:

```text
clinical_priority = 3
```

---

# 21. Scope Safety

Do not convert WHO03 into a generic cardiology knowledge base.

Its primary domain is:

```text
pharmacological treatment of hypertension in adults
```

If content discusses another disease only as a:

- comorbidity
- risk factor
- outcome
- treatment consideration

preserve that context.

For example, mentioning heart failure in an evidence section does not automatically make that chunk a general heart-failure guideline.

---

# 22. Special Handling of Pregnancy

The general guideline targets adults with hypertension and the main recommendations are not intended to silently become pregnancy-management recommendations.

Any pregnancy-specific material must be clearly tagged:

```text
special_setting = pregnancy
```

Never allow pregnancy content to be indistinguishable from the general adult recommendations.

---

# 23. Duplicate Recommendation Handling

The document may repeat recommendations in:

- executive summary
- main recommendation sections
- implementation tools

Do NOT blindly create three identical high-priority chunks.

Prefer the detailed recommendation in the main recommendation section as the canonical clinical chunk.

For repeated summaries:

```text
is_duplicate = true
canonical_chunk_id = "..."
```

or exclude exact duplicates from the main retrieval collection.

Do not discard unique implementation information.

---

# 24. JSON Output Structure

Output:

`data/processed/who03_chunks.json`

as:

```json
[
  {
    "chunk_id": "WHO03_3.4_REC_001",
    "text": "...",
    "metadata": {
      "source_file": "WHO03.pdf",
      "organization": "WHO",
      "document_title": "Guideline for the pharmacological treatment of hypertension in adults",
      "publication_year": 2021,
      "pdf_page_start": 23,
      "pdf_page_end": 23,
      "page_label_start": "11",
      "page_label_end": "11",
      "section": "3 Recommendations",
      "subsection": "3.4 Drug classes to be used as first-line agents",
      "recommendation_id": "4",
      "domain": "hypertension",
      "topic": "pharmacological_treatment",
      "subtopic": "first_line_agents",
      "content_type": "recommendation",
      "recommendation_strength": "strong",
      "evidence_certainty": "high",
      "population": "adults_with_hypertension_requiring_pharmacological_treatment",
      "special_setting": null,
      "region_scope": "global",
      "clinical_priority": 1
    }
  }
]
```

Also output the same chunks as JSONL:

`data/processed/who03_chunks.jsonl`

One chunk per line.

---

# 25. Human-Readable Preview

Generate:

`data/processed/who03_chunks_preview.md`

For every chunk display:

```markdown
## WHO03_3.4_REC_001

**Pages:** 23
**Section:** 3.4 Drug classes to be used as first-line agents
**Topic:** pharmacological_treatment
**Subtopic:** first_line_agents
**Type:** recommendation
**Strength:** strong
**Evidence certainty:** high

### Text

...
```

I need this file to manually inspect chunk quality before embeddings are generated.

---

# 26. Processing Report

At the end of the script print a report like:

```text
WHO03 PROCESSING REPORT

PDF pages:
61

Pages parsed:
...

Total chunks:
...

Recommendation chunks:
...

Implementation remark chunks:
...

Evidence/rationale chunks:
...

Algorithm chunks:
...

Table chunks:
...

Research methodology chunks:
...

Skipped administrative pages/blocks:
...

Potential duplicate chunks:
...

Pages requiring manual review:
...
```

Also show:

```text
average chunk tokens
minimum chunk tokens
maximum chunk tokens
```

---

# 27. Validation

Build automated checks.

The pipeline should fail validation if:

1. a chunk has no source file
2. a chunk has no page number
3. a clinical chunk has empty text
4. duplicate chunk IDs exist
5. recommendations lose their strength classification when it was present in source
6. recommendations lose their evidence-certainty classification when present
7. chunks exceed approximately 1000 tokens without a documented reason
8. a chunk spans unrelated major sections
9. page references fall outside the PDF
10. administrative boilerplate dominates clinical chunks

---

# 28. Tests

Create tests verifying that the parser detects at minimum:

```text
3.1 treatment initiation
3.2 laboratory testing
3.3 cardiovascular risk assessment
3.4 first-line agents
3.5 combination therapy
3.6 target blood pressure
3.7 follow-up/reassessment
3.8 nonphysician treatment
```

Also test that:

```text
recommendation_strength
```

and:

```text
evidence_certainty
```

are extracted when available.

Add a test that confirms repeated page headers are not present in the final chunk text.

---

# 29. Important Medical RAG Rules

These requirements are mandatory:

1. Do not paraphrase recommendations during ingestion.
2. Do not use LLM knowledge to "correct" WHO.
3. Do not add newer medical recommendations.
4. Do not infer missing drug doses.
5. Do not change BP thresholds.
6. Do not merge unrelated recommendations.
7. Preserve units exactly.
8. Preserve page provenance.
9. Preserve recommendation strength.
10. Preserve certainty of evidence.
11. Never invent text when PDF extraction fails.
12. Flag extraction uncertainty instead.

---

# 30. Parser Design

Keep the pipeline modular.

Suggested flow:

```text
PDF
 ↓
page extraction
 ↓
text cleaning
 ↓
document structure detection
 ↓
section segmentation
 ↓
clinical block classification
 ↓
recommendation extraction
 ↓
metadata extraction
 ↓
semantic chunking
 ↓
deduplication
 ↓
validation
 ↓
JSON / JSONL / Markdown preview
```

Do not combine everything into one large script.

---

# 31. Token Counting

Use a tokenizer appropriate for modern LLM workflows if available.

If no model-specific tokenizer is configured, use a reasonable generic tokenizer.

Token counts are for chunk sizing only and must not alter source text.

Store:

```json
"token_count": 537
```

for each chunk.

---

# 32. Quality Over Quantity

Do not optimize for producing the maximum number of chunks.

Optimize for:

```text
clinical completeness
retrieval precision
source traceability
semantic coherence
citation reliability
```

A good recommendation chunk is more important than five arbitrary overlapping chunks.

---

# 33. Final Verification Examples

After processing, automatically search the resulting chunks for queries such as:

```text
When should pharmacological treatment for hypertension be initiated?
```

```text
What first-line drug classes does WHO recommend?
```

```text
What is the target blood pressure?
```

```text
What laboratory tests should be considered?
```

```text
How often should patients be followed up?
```

Print the top matching chunks using a simple lexical or temporary similarity test.

This is only for validating the chunk quality.

Do NOT build the final RAG system yet.

---

# 34. Deliverables

When finished, provide:

1. list of created files
2. number of extracted chunks
3. number of recommendation chunks
4. detected main sections
5. examples of 5 high-quality chunks
6. any parsing problems found
7. any pages requiring manual inspection
8. confirmation that no recommendation wording was intentionally altered
9. path to `who03_chunks.json`
10. path to `who03_chunks_preview.md`

Do not proceed to embeddings, Qdrant, Chroma, LangChain, Gemini, or OpenAI integration yet.

Stop after the validated parsing and chunking pipeline is complete.