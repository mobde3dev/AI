You are working on a medical RAG project called **CardioRAG**.

The current task is NOT to build the complete RAG system.

Your task is to build a robust:

**PDF parsing → cleaning → NICE guideline structure detection → recommendation extraction → medical metadata extraction → semantic chunking → validation pipeline**

specifically for:

`NICE3.pdf`

Document:

**NICE Guideline NG238 — Cardiovascular disease: risk assessment and reduction, including lipid modification**

Original publication:

**14 December 2023**

The uploaded PDF may contain later minor maintenance updates. Preserve those distinctions in metadata.

The processed output will later be embedded and stored in a vector database such as Qdrant or Chroma.

---

# 1. Main Goal

Convert:

`NICE3.pdf`

into high-quality, medically meaningful chunks suitable for a cardiovascular clinical-guideline RAG system.

Do NOT use naive fixed-size chunking.

Do NOT simply split:

- every 500 words
- every 1000 characters
- every page
- every paragraph without considering guideline structure

The parser must understand NICE guideline structure.

The chunking must preserve:

- recommendation numbers
- recommendation wording
- recommendation dates
- amendment dates
- section hierarchy
- primary vs secondary prevention
- patient populations
- thresholds
- lipid values
- statin doses
- drug names
- QRISK3 references
- contraindications
- monitoring intervals
- specialist referral thresholds
- rationale
- evidence discussion
- implementation impact
- cross-references
- page provenance

The result must be optimized for:

- retrieval precision
- medical traceability
- citation reliability
- clinical completeness
- metadata filtering
- future reranking

---

# 2. Project Structure

Create or update:

```text
cardiorag/
│
├── data/
│   ├── raw/
│   │   └── NICE3.pdf
│   │
│   └── processed/
│       ├── nice3_chunks.json
│       ├── nice3_chunks.jsonl
│       ├── nice3_chunks_preview.md
│       └── nice3_processing_report.json
│
├── src/
│   ├── parse_nice3.py
│   ├── clean_text.py
│   ├── section_parser.py
│   ├── nice_recommendation_parser.py
│   ├── metadata_extractor.py
│   ├── chunk_nice3.py
│   ├── deduplicate.py
│   └── validate_chunks.py
│
├── tests/
│   └── test_nice3_chunking.py
│
├── requirements.txt
│
└── README.md
```

If equivalent project files already exist, reuse and extend them.

Do not duplicate architecture unnecessarily.

---

# 3. PDF Parsing

Prefer:

```text
PyMuPDF
```

for PDF extraction.

Design the parser modularly so another parser can be substituted later.

For every extracted block preserve:

```text
physical PDF page
printed page number if detectable
raw text
cleaned text
block order
```

Use 1-based PDF page numbers in user-facing metadata.

Example:

```json
{
  "pdf_page": 22,
  "printed_page": "22",
  "raw_text": "...",
  "cleaned_text": "..."
}
```

Never discard page provenance.

Page provenance will later be required for RAG citations.

---

# 4. Remove Repetitive PDF Noise

Detect and remove repeated page boilerplate such as:

```text
Cardiovascular disease: risk assessment and reduction, including lipid modification

(NG238)

© NICE ...

Page X of 52
```

Also remove when appropriate:

- repeated copyright lines
- navigation-only footer URLs
- blank lines
- page-number-only lines
- repeated title headers

Do NOT remove meaningful clinical content.

Do not remove:

```text
recommendation numbers
recommendation dates
drug names
drug doses
QRISK3
LDL
non-HDL
HDL
triglycerides
eGFR
CKD
CVD
BMI
HbA1c
creatine kinase
transaminases
numerical thresholds
units
technology appraisal IDs
```

---

# 5. Preserve Medical Symbols and Units

Do not corrupt expressions such as:

```text
10%
40%
2.0 mmol per litre
2.6 mmol per litre
7.5 mmol per litre
20 mmol per litre
atorvastatin 20 mg
atorvastatin 80 mg
eGFR 30 ml per minute per 1.73 m²
5 times the upper limit of normal
2 to 3 months
```

Preserve comparison operators:

```text
<
>
≤
≥
```

Preserve ranges accurately.

Never silently modify thresholds.

---

# 6. NICE Guideline Structure Detection

Detect at minimum:

```text
Recommendations

1.1 Identifying and assessing cardiovascular disease risk for people without established cardiovascular disease

1.2 Aspirin for primary prevention of cardiovascular disease

1.3 Lifestyle changes for the primary and secondary prevention of cardiovascular disease

1.4 Initial lipid measurement and referral for specialist review

1.5 Discussions and assessment before starting statins

1.6 Lipid-lowering treatment for primary prevention of cardiovascular disease

1.7 Lipid-lowering treatment for secondary prevention of cardiovascular disease

1.8 Statins for primary and secondary prevention of cardiovascular disease in people with chronic kidney disease

1.9 Optimising statin treatment

1.10 Treatment if statins are contraindicated or not tolerated

1.11 Assessing response to treatment

1.12 Lipid-lowering treatments that should not be used or not used routinely

Terms used in this guideline

Recommendations for research

Context

Finding more information and committee details

Update information
```

Use section numbering and headings.

Do NOT depend entirely on page boundaries.

---

# 7. Detect Lower-Level Subheadings

NICE3 contains clinically important subheadings within major sections.

Examples include:

```text
Full formal risk assessment

Communication about risk assessment, lifestyle changes and treatment

Cardioprotective diet

Physical activity

Weight management

Alcohol consumption

Smoking cessation

Plant stanols and sterols

Discuss risks and benefits of statins

Perform baseline blood tests and clinical assessment

Statins and pregnancy

Lipid target for people taking statins

Optimising lifestyle changes

Statin treatment for people with and without type 2 diabetes

Statin treatment for people with type 1 diabetes

Initial treatment

Escalating treatment for people on statins

Primary prevention of cardiovascular disease

Secondary prevention of cardiovascular disease

When to repeat blood tests

When to measure creatine kinase

Annual medication review
```

Preserve these in metadata.

---

# 8. Clinical Topic Mapping

Map NICE sections to normalized CardioRAG topics.

Use:

```text
domain = cardiovascular_disease
```

For section 1.1:

```text
topic = cardiovascular_risk_assessment
subtopic = primary_prevention
```

1.2:

```text
topic = antiplatelet_therapy
subtopic = aspirin_primary_prevention
```

1.3:

```text
topic = lifestyle
```

Possible subtopics:

```text
cardioprotective_diet
dietary_fat
physical_activity
weight_management
alcohol
smoking_cessation
plant_stanols_sterols
```

1.4:

```text
topic = lipid_assessment
```

Possible subtopics:

```text
initial_lipid_measurement
familial_lipid_disorder
secondary_dyslipidaemia
specialist_referral
hypertriglyceridaemia
```

1.5:

```text
topic = statin_pre_treatment_assessment
```

Subtopics:

```text
shared_decision_making
adverse_effects
drug_interactions
baseline_testing
creatine_kinase
pregnancy
```

1.6:

```text
topic = lipid_lowering_treatment
subtopic = primary_prevention
```

1.7:

```text
topic = lipid_lowering_treatment
subtopic = secondary_prevention
```

1.8:

```text
topic = lipid_lowering_treatment
subtopic = chronic_kidney_disease
```

1.9:

```text
topic = statin_optimization
```

1.10:

```text
topic = statin_intolerance
```

1.11:

```text
topic = treatment_monitoring
```

1.12:

```text
topic = treatments_not_recommended
```

---

# 9. NICE Recommendation Detection

This is CRITICAL.

Detect individual NICE recommendation IDs such as:

```text
1.1.7
1.2.1
1.3.2
1.4.5
1.5.5
1.6.7
1.7.1
1.7.2
1.8.1
1.9.2
1.10.3
1.11.1
```

A recommendation begins with a pattern such as:

```regex
^\d+\.\d+\.\d+
```

but build the implementation robustly enough to handle line wrapping.

Every recommendation should normally become its OWN chunk.

Example:

```text
Recommendation 1.6.7

Offer atorvastatin 20 mg for the primary prevention of CVD to people who have a 10-year QRISK3 score of 10% or more.

[May 2023]
```

Do not merge several independent recommendations just because they appear on the same page.

---

# 10. Recommendation Date Metadata

NICE recommendations frequently include markers such as:

```text
[2008]

[2014]

[May 2023]

[December 2023]

[2008, amended 2014]

[May 2023, amended December 2023]

[2014, amended May 2023 and December 2023]
```

Parse these carefully.

Store:

```json
{
  "recommendation_original_date": "May 2023",
  "recommendation_amended_dates": [
    "December 2023"
  ]
}
```

For multiple amendments:

```json
{
  "recommendation_original_date": "2014",
  "recommendation_amended_dates": [
    "May 2023",
    "December 2023"
  ]
}
```

Do NOT treat `[May 2023]` as publication year metadata for the entire document.

It applies to that recommendation.

---

# 11. Guideline Version Metadata

Use document-level metadata such as:

```json
{
  "organization": "NICE",
  "guideline_code": "NG238",
  "document_title": "Cardiovascular disease: risk assessment and reduction, including lipid modification",
  "original_publication_date": "2023-12-14",
  "region_scope": "England",
  "source_file": "NICE3.pdf"
}
```

The uploaded copy may contain later NICE maintenance changes.

Therefore also support:

```json
{
  "source_revision_notes_present": true
}
```

Do NOT rewrite all recommendation dates as 2026 simply because the PDF copyright footer says 2026.

---

# 12. Recommendation Chunk Structure

Recommendation chunk text should contain enough context to make sense independently.

For example:

```text
Section:
1.7 Lipid-lowering treatment for secondary prevention of cardiovascular disease

Subheading:
Lipid target for people taking lipid-lowering treatments

Recommendation:
1.7.1

For secondary prevention of CVD, aim for LDL cholesterol levels of 2.0 mmol per litre or less, or non-HDL cholesterol levels of 2.6 mmol per litre or less.

[December 2023]
```

Do NOT paraphrase.

Do NOT change wording.

Do NOT omit thresholds.

---

# 13. “Why the Committee Made These Recommendations”

NICE includes sections:

```text
Why the committee made these recommendations
```

These should NOT be merged into recommendation chunks by default.

Create separate chunks:

```text
content_type = committee_rationale
```

Link them to relevant recommendations.

Example metadata:

```json
{
  "related_recommendations": [
    "1.7.1"
  ]
}
```

If the rationale applies to multiple recommendations:

```json
{
  "related_recommendations": [
    "1.6.7",
    "1.6.8",
    "1.6.9"
  ]
}
```

Only assign relationships that can be reliably established from section structure.

If uncertain:

```json
{
  "related_recommendations": null
}
```

Do not guess.

---

# 14. “How the Recommendations Might Affect Practice”

Treat sections titled:

```text
How the recommendations might affect practice
```

as:

```text
content_type = implementation_impact
clinical_priority = 3
```

Keep them available for questions about:

- NHS implementation
- resource impact
- workload
- practice changes
- cost implications

But they should rank below direct clinical recommendations.

---

# 15. Evidence Review References

NICE often says:

```text
Full details of the evidence and the committee's discussion are in evidence review C...
```

Preserve this relationship in metadata when possible:

```json
{
  "evidence_review_reference": "Evidence review C: statins: efficacy and adverse effects"
}
```

Do not attempt to retrieve or reconstruct that evidence review unless the actual evidence-review document is provided.

Do not hallucinate its contents.

---

# 16. Cross-References to Other NICE Guidelines

NICE3 contains many references such as:

```text
see NICE's guideline on hypertension in adults

see NICE's guideline on chronic kidney disease

see NICE's guideline on familial hypercholesterolaemia
```

Preserve them.

Add metadata:

```json
{
  "external_guideline_reference": [
    "NICE hypertension in adults"
  ]
}
```

However:

DO NOT automatically import clinical recommendations from those external guidelines.

They are outside this PDF unless separately provided.

---

# 17. Technology Appraisal References

Detect references such as:

```text
TA385
TA393
TA394
TA694
TA733
```

Store them as structured metadata.

Example:

```json
{
  "technology_appraisal_refs": [
    "TA385"
  ]
}
```

or:

```json
{
  "technology_appraisal_refs": [
    "TA393",
    "TA394",
    "TA385",
    "TA733"
  ]
}
```

Do not expand their contents from model knowledge.

Only store what NICE3 explicitly states.

---

# 18. Clinical Content Types

Classify chunks into:

```text
recommendation
committee_rationale
implementation_impact
risk_assessment_guidance
lifestyle_guidance
drug_guidance
lipid_target
laboratory_guidance
monitoring_guidance
specialist_referral
contraindication
adverse_effect_guidance
pregnancy_guidance
definition
technology_appraisal_reference
research_recommendation
context
update_information
other
```

---

# 19. Clinical Priority

Assign:

```text
clinical_priority = 1
```

for:

```text
direct NICE recommendations
clinical thresholds
drug treatment recommendations
monitoring instructions
specialist referral recommendations
contraindications
```

Assign:

```text
clinical_priority = 2
```

for:

```text
committee rationale
clinical explanatory text
risk tool explanation
supporting evidence discussion
```

Assign:

```text
clinical_priority = 3
```

for:

```text
implementation impact
research recommendations
context
update notes
```

Administrative boilerplate should normally not enter the main clinical index.

---

# 20. Prevention Type Metadata

NICE3 clearly distinguishes prevention contexts.

Use:

```text
prevention_type = primary
```

or:

```text
prevention_type = secondary
```

or:

```text
prevention_type = primary_and_secondary
```

Examples:

Section 1.6:

```text
prevention_type = primary
```

Section 1.7:

```text
prevention_type = secondary
```

Section 1.3:

```text
prevention_type = primary_and_secondary
```

For content that does not clearly fit:

```text
prevention_type = null
```

---

# 21. Patient Population Metadata

Extract only when explicitly supported.

Possible values:

```text
people_without_established_cvd
people_with_cvd
people_at_high_cvd_risk
people_with_type_1_diabetes
people_with_type_2_diabetes
people_with_ckd
people_aged_85_or_older
people_with_statin_intolerance
people_with_statin_contraindication
people_with_acute_coronary_syndrome
people_taking_lipid_lowering_treatment
```

Allow arrays where appropriate.

Example:

```json
{
  "population": [
    "people_with_cvd",
    "secondary_prevention"
  ]
}
```

Do not infer populations from outside knowledge.

---

# 22. Risk Assessment Metadata

For CVD risk chunks support fields such as:

```text
risk_tool
risk_horizon
risk_threshold
age_min
age_max
```

Example:

```json
{
  "risk_tool": "QRISK3",
  "risk_horizon": "10 years",
  "age_min": 25,
  "age_max": 84
}
```

When a recommendation explicitly uses a threshold:

```json
{
  "risk_tool": "QRISK3",
  "risk_threshold": "10%"
}
```

Do not calculate a patient's QRISK3 score.

This ingestion pipeline only stores source guidance.

---

# 23. Special QRISK3 Safety Handling

Do NOT turn the RAG system into a QRISK3 calculator.

Store NICE's recommendations about when and for whom QRISK3 should be used.

Store caveats about populations in which risk tools may underestimate risk.

Do NOT recreate the QRISK3 mathematical algorithm unless an authoritative algorithm source is separately provided.

Do NOT invent missing QRISK inputs.

---

# 24. Lipid Metadata

Where explicitly stated extract:

```text
lipid_measure
lipid_threshold
lipid_target
```

Possible measures include:

```text
LDL
non-HDL
HDL
total cholesterol
triglycerides
```

Example:

```json
{
  "lipid_measure": "LDL",
  "lipid_target": "≤2.0 mmol/L"
}
```

or:

```json
{
  "lipid_measure": "non-HDL",
  "lipid_target": "≤2.6 mmol/L"
}
```

Preserve original text in the chunk even if metadata normalizes the unit notation.

---

# 25. Drug Metadata

Extract explicit drug information.

Possible fields:

```text
drug_name
drug_class
dose
treatment_role
```

Examples:

```json
{
  "drug_name": "atorvastatin",
  "dose": "20 mg",
  "treatment_role": "primary prevention"
}
```

```json
{
  "drug_name": "atorvastatin",
  "dose": "80 mg",
  "treatment_role": "secondary prevention"
}
```

Other explicitly mentioned drugs may include:

```text
ezetimibe
alirocumab
evolocumab
inclisiran
bempedoic acid
```

Only extract information found in the PDF.

---

# 26. Statin Intolerance Metadata

For section 1.9 and 1.10 support:

```text
statin_status
adverse_effect
alternative_treatment
```

Possible values:

```text
high_intensity_not_tolerated
statin_intolerant
statin_contraindicated
muscle_symptoms
```

Keep management steps intact.

Do not split a strategy bullet list into isolated contextless chunks.

---

# 27. Laboratory and Monitoring Metadata

Extract when explicit:

```text
test_name
test_timing
monitoring_frequency
threshold
```

Examples:

```text
full lipid profile
liver transaminase
creatine kinase
renal function
HbA1c
fasting glucose
thyroid-stimulating hormone
```

Example:

```json
{
  "test_name": [
    "full lipid profile",
    "liver transaminase"
  ],
  "test_timing": "2 to 3 months after starting or changing lipid-lowering treatment"
}
```

Do not infer laboratory intervals not present in the source.

---

# 28. Referral Metadata

For specialist review recommendations use:

```text
content_type = specialist_referral
```

Support metadata such as:

```text
referral_urgency
trigger
threshold
```

Example:

```json
{
  "referral_urgency": "urgent",
  "trigger": "triglycerides",
  "threshold": ">20 mmol/L"
}
```

Preserve the exact NICE recommendation wording.

---

# 29. Lifestyle Chunking

Do not merge all lifestyle recommendations into one huge chunk.

Use separate chunks for:

```text
cardioprotective diet
saturated fat
physical activity
weight management
alcohol
smoking
plant stanols and sterols
```

Keep individual recommendation IDs where present.

This is particularly important because users may ask:

```text
What does NICE recommend about smoking?
```

or:

```text
What does NICE recommend about saturated fat?
```

and retrieval should not return an unnecessarily large lifestyle block.

---

# 30. Dietary Cholesterol Handling

NICE3 contains discussion explaining the update regarding dietary cholesterol.

Preserve the distinction between:

```text
direct recommendation
```

and:

```text
committee rationale
```

Do not invent a dietary cholesterol limit.

Do not reintroduce older limits removed from the current guideline.

If the committee explanation discusses removal of previous dietary cholesterol restriction, preserve that as rationale with the correct section metadata.

---

# 31. Aspirin Handling

Section 1.2 should be indexed independently.

Tag:

```text
topic = antiplatelet_therapy
subtopic = aspirin_primary_prevention
prevention_type = primary
```

Do not merge aspirin guidance with statins or lipid-lowering therapy simply because both concern CVD prevention.

---

# 32. CKD Handling

Section 1.8 should be tagged clearly:

```text
special_population = chronic_kidney_disease
```

Preserve:

```text
eGFR thresholds
atorvastatin dose
renal specialist involvement
```

Do not allow CKD-specific recommendations to appear as unrestricted general-population advice.

---

# 33. Pregnancy Handling

Pregnancy-related statin guidance must use:

```text
special_population = pregnancy
```

and/or:

```text
content_type = pregnancy_guidance
```

Do not allow pregnancy-specific contraindication content to lose that context.

Preserve timing statements exactly.

---

# 34. Cross-Section Recommendation Links

Some NICE recommendations refer to other recommendation IDs:

```text
see recommendation 1.6.1
see recommendation 1.7.1
recommendations 1.9.2 and 1.9.3
```

Extract:

```json
{
  "related_recommendation_ids": [
    "1.9.2",
    "1.9.3"
  ]
}
```

This will later enable graph-like retrieval.

Do not duplicate the referenced recommendation text inside the current chunk.

---

# 35. Chunk Size Strategy

Use section-aware semantic chunking.

Recommended target for supporting narrative:

```text
350–700 tokens
```

Maximum:

```text
~900 tokens
```

Overlap for long committee-rationale sections:

```text
50–100 tokens
```

However:

**semantic completeness is more important than token count.**

Recommendations should generally remain individual chunks even when very short.

Do not artificially merge several recommendations just to reach 350 tokens.

---

# 36. Recommendation Chunks Need No Arbitrary Overlap

Example:

```text
NICE3_1.7.1_REC
```

should stand alone.

Do not repeat it inside neighboring recommendation chunks.

Instead use shared metadata:

```text
section
subsection
topic
prevention_type
```

to maintain context.

---

# 37. Long Committee Rationale

A long:

```text
Why the committee made these recommendations
```

section may be divided into multiple coherent chunks.

For example:

```text
NICE3_1.7_RATIONALE_LIPID_TARGET_001
NICE3_1.7_RATIONALE_EVIDENCE_001
NICE3_1.7_RATIONALE_ECONOMIC_001
```

Prefer semantic boundaries such as:

```text
clinical evidence
economic evidence
cost effectiveness
implementation reasoning
```

instead of arbitrary token boundaries.

---

# 38. Tables and Structured Content

If tables appear:

Do not flatten them into unreadable paragraphs.

Convert to structured text when extraction is reliable.

Example:

```text
Table: ...

Column A | Column B | Column C
...
```

Preserve:

```text
drug
dose
lipid value
threshold
category
```

If extraction is unreliable:

```json
{
  "requires_manual_review": true,
  "review_reason": "table extraction uncertain"
}
```

Never invent cells.

---

# 39. External Links

Remove raw URLs from normal chunk text if they are just navigation boilerplate.

However, preserve semantically important external reference metadata.

Example:

```json
{
  "external_reference_type": "NICE technology appraisal",
  "external_reference_id": "TA385"
}
```

The vector DB does not need repetitive URLs in every chunk.

---

# 40. Terms Used in This Guideline

The:

```text
Terms used in this guideline
```

section can be useful.

Index clinically meaningful definitions as:

```text
content_type = definition
clinical_priority = 2
```

Each distinct definition should preferably become a separate chunk.

Do not merge all glossary terms into one enormous chunk.

---

# 41. Recommendations for Research

Keep them separate from clinical recommendations.

Use:

```text
content_type = research_recommendation
clinical_priority = 3
```

Do NOT allow a research recommendation to be retrieved and presented as current clinical management guidance.

This distinction is mandatory.

---

# 42. Update Information

Keep the update-history section but index it separately:

```text
content_type = update_information
clinical_priority = 3
```

Extract structured update metadata where possible.

Example:

```json
{
  "update_date": "December 2023",
  "update_scope": "secondary prevention lipid target"
}
```

This is important for provenance but should not outrank clinical recommendations.

---

# 43. Current vs Historical Recommendation Wording

Do NOT create clinical chunks from superseded historical recommendation wording when the current NICE3 recommendation replaces it.

Historical discussion may appear inside committee rationale.

Tag that text appropriately as:

```text
historical_context = true
```

Do not allow old thresholds or previous recommendations to compete equally with current recommendations.

---

# 44. Off-Label Statements

When NICE explicitly says a use was:

```text
off-label
```

preserve that fact.

Metadata:

```json
{
  "off_label_statement_present": true
}
```

Do not infer current licensing status outside what this uploaded document says.

---

# 45. Source Metadata Schema

Every chunk should contain:

```json
{
  "source_file": "NICE3.pdf",

  "organization": "NICE",

  "guideline_code": "NG238",

  "document_title": "Cardiovascular disease: risk assessment and reduction, including lipid modification",

  "original_publication_date": "2023-12-14",

  "pdf_page_start": 0,
  "pdf_page_end": 0,

  "printed_page_start": null,
  "printed_page_end": null,

  "section": null,
  "subsection": null,

  "recommendation_id": null,

  "recommendation_original_date": null,
  "recommendation_amended_dates": [],

  "domain": "cardiovascular_disease",

  "topic": null,
  "subtopic": null,

  "content_type": null,

  "prevention_type": null,

  "population": [],

  "special_population": [],

  "risk_tool": null,
  "risk_threshold": null,

  "lipid_measure": [],
  "lipid_target": null,

  "drug_names": [],
  "dose": null,

  "test_names": [],
  "monitoring_interval": null,

  "external_guideline_references": [],
  "technology_appraisal_refs": [],
  "related_recommendation_ids": [],
  "evidence_review_reference": null,

  "region_scope": "England",

  "clinical_priority": 1,

  "historical_context": false,

  "off_label_statement_present": false,

  "requires_manual_review": false,

  "token_count": 0
}
```

Use `null` or empty arrays if unavailable.

Never fabricate metadata.

---

# 46. Deterministic Chunk IDs

Use stable IDs.

Examples:

```text
NICE3_1.1.7_REC

NICE3_1.2.1_REC

NICE3_1.3.2_REC

NICE3_1.5.5_REC

NICE3_1.6.7_REC

NICE3_1.7.1_REC

NICE3_1.7.2_REC

NICE3_1.8.1_REC

NICE3_1.9.2_REC

NICE3_1.10.3_REC

NICE3_1.11.1_REC
```

Committee rationale:

```text
NICE3_1.7_RATIONALE_001
```

Implementation impact:

```text
NICE3_1.7_IMPACT_001
```

Definitions:

```text
NICE3_TERM_STATIN_INTENSITY_001
```

IDs must be deterministic across repeated runs on the same PDF.

---

# 47. Example Final Recommendation Object

Example schema:

```json
{
  "chunk_id": "NICE3_1.7.1_REC",

  "text": "For secondary prevention of CVD, aim for LDL cholesterol levels of 2.0 mmol per litre or less, or non-HDL cholesterol levels of 2.6 mmol per litre or less. [December 2023]",

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

    "population": [
      "people_with_cvd"
    ],

    "lipid_measure": [
      "LDL",
      "non-HDL"
    ],

    "region_scope": "England",

    "clinical_priority": 1,

    "historical_context": false,

    "requires_manual_review": false
  }
}
```

---

# 48. Duplicate Handling

The guideline may repeat information through:

```text
cross-references
rationale sections
update notes
summary statements
```

Do not blindly deduplicate based on partial semantic similarity.

Two chunks discussing the same drug may have different roles:

```text
recommendation
rationale
monitoring
contraindication
```

Only remove:

```text
exact boilerplate duplicates
repeated headers
identical accidental extraction duplicates
```

Preserve legitimate clinical repetition when the context differs.

---

# 49. Do Not Import NICE1

NICE3 may refer to:

```text
evidence review B: dietary cholesterol strategies
```

Do NOT automatically load `NICE1.pdf` into this ingestion process.

This task is exclusively for `NICE3.pdf`.

If evidence-review documents are later added, they should form separate sources with their own metadata and retrieval priority.

---

# 50. Main Clinical Collection vs Supporting Collection

Prepare chunks so we can later optionally create two logical collections.

### Clinical recommendations

```text
clinical_priority = 1
```

Contains:

```text
recommendations
thresholds
drug guidance
monitoring guidance
referral guidance
contraindications
```

### Supporting material

```text
clinical_priority = 2 or 3
```

Contains:

```text
committee rationale
economic evidence
implementation impact
definitions
research recommendations
update history
```

For now, output them all in one JSON dataset with metadata allowing filtering.

---

# 51. Excluded Administrative Content

Do not index as clinical chunks:

```text
copyright notices
generic responsibility disclaimer
repeated page footer
generic NICE navigation instructions
ISBN
generic committee-navigation text
```

Preserve document metadata separately if useful.

---

# 52. Medical Safety Requirements

These are mandatory:

1. Do not paraphrase NICE recommendations during ingestion.
2. Do not update them using model knowledge.
3. Do not replace NICE wording with WHO wording.
4. Do not alter doses.
5. Do not alter lipid thresholds.
6. Do not alter QRISK thresholds.
7. Do not alter monitoring intervals.
8. Do not infer treatment recommendations.
9. Do not merge primary and secondary prevention.
10. Do not strip recommendation dates.
11. Do not confuse recommendation dates with document publication dates.
12. Do not present research recommendations as clinical guidance.
13. Do not treat committee rationale as a direct recommendation.
14. Do not import recommendations from external NICE guidelines.
15. Do not expand technology appraisals from model knowledge.
16. Never invent text when extraction fails.
17. Flag uncertain extraction for manual review.

---

# 53. Chunk Validation Rules

The pipeline should fail validation if:

1. duplicate `chunk_id` exists
2. a recommendation chunk has no `recommendation_id`
3. recommendation text is empty
4. page provenance is missing
5. a recommendation date visible in source was lost
6. a drug dose visible in the recommendation was corrupted
7. a numerical threshold was corrupted
8. a recommendation is merged with an unrelated recommendation
9. primary and secondary prevention are incorrectly merged
10. research recommendations are marked as clinical priority 1
11. committee rationale is incorrectly classified as a direct recommendation
12. chunk text contains excessive repeated footer boilerplate
13. chunk exceeds approximately 1000 tokens without a documented reason
14. page references fall outside the PDF
15. QRISK3 references lose their risk horizon or threshold when explicitly present

---

# 54. Numerical Integrity Checks

Add automated checks for patterns containing:

```text
mg
mmol
%
months
years
eGFR
ml per minute
upper limit of normal
```

For recommendation chunks, compare extracted normalized text against the source block.

Flag suspicious transformations.

Examples:

```text
20 mg → 20 mg
80 mg → 80 mg
10% → 10%
2.0 mmol → 2.0 mmol
2.6 mmol → 2.6 mmol
```

These values must never silently change.

---

# 55. Recommendation ID Integrity

Validate IDs against:

```regex
^1\.\d+\.\d+$
```

for standard NICE recommendations in this guideline.

Ensure:

```text
1.10.3
```

is not accidentally parsed as:

```text
1.1.03
```

or:

```text
10.3
```

---

# 56. Human-Readable Preview

Generate:

```text
data/processed/nice3_chunks_preview.md
```

For each chunk show:

```markdown
## NICE3_1.6.7_REC

**PDF page:** 22
**Section:** 1.6 Lipid-lowering treatment for primary prevention of cardiovascular disease
**Recommendation:** 1.6.7
**Date:** May 2023
**Topic:** lipid_lowering_treatment
**Subtopic:** primary_prevention
**Type:** recommendation
**Clinical priority:** 1
**Population:** ...
**Drug:** atorvastatin
**Dose:** 20 mg
**Risk tool:** QRISK3
**Risk threshold:** 10%

### Text

...
```

This file is essential for manual QA before embeddings.

---

# 57. JSON Output

Generate:

```text
data/processed/nice3_chunks.json
```

containing a JSON array.

Also generate:

```text
data/processed/nice3_chunks.jsonl
```

with one chunk per line.

---

# 58. Processing Report

Print and save a processing report.

Example:

```text
NICE3 PROCESSING REPORT

PDF pages:
52

Pages successfully parsed:
...

Total chunks:
...

Direct recommendation chunks:
...

Committee rationale chunks:
...

Implementation impact chunks:
...

Definition chunks:
...

Research recommendation chunks:
...

Update information chunks:
...

Primary prevention chunks:
...

Secondary prevention chunks:
...

CKD-specific chunks:
...

Statin intolerance chunks:
...

Monitoring chunks:
...

Technology appraisal references detected:
...

Cross-recommendation links detected:
...

Skipped boilerplate blocks:
...

Potential duplicate blocks:
...

Pages requiring manual review:
...

Average tokens per chunk:
...

Minimum tokens:
...

Maximum tokens:
...
```

---

# 59. Topic Distribution Report

Also print:

```text
CVD risk assessment: X
Aspirin: X
Lifestyle: X
Lipids: X
Statin baseline assessment: X
Primary prevention treatment: X
Secondary prevention treatment: X
CKD: X
Statin optimisation: X
Statin intolerance: X
Monitoring: X
Treatments not recommended: X
```

This helps verify no major guideline section was lost.

---

# 60. Tests

Create automated tests confirming detection of:

```text
1.1 CVD risk assessment

1.2 Aspirin primary prevention

1.3 Lifestyle

1.4 Lipid measurement/referral

1.5 Pre-statin assessment

1.6 Primary prevention lipid-lowering treatment

1.7 Secondary prevention lipid-lowering treatment

1.8 CKD

1.9 Statin optimisation

1.10 Statin contraindication/intolerance

1.11 Treatment monitoring

1.12 Treatments not recommended
```

---

# 61. Specific Recommendation Tests

At minimum verify successful extraction of representative recommendation IDs such as:

```text
1.1.7

1.2.1

1.3.2

1.4.5

1.5.5

1.6.7

1.7.1

1.7.2

1.8.1

1.9.2

1.10.3

1.11.1
```

Do not hardcode their clinical text into production code.

Tests may confirm the IDs exist and their source text was extracted.

---

# 62. Date Parsing Tests

Test at least:

```text
[May 2023]

[December 2023]

[May 2023, amended December 2023]

[2014, amended May 2023 and December 2023]
```

Verify date fields are parsed correctly.

---

# 63. Retrieval Sanity Tests

After creating the chunks, perform temporary local retrieval checks.

No final vector database yet.

Test queries such as:

```text
Who should have QRISK3 calculated?
```

```text
Should aspirin routinely be used for primary prevention?
```

```text
What does NICE recommend about saturated fat?
```

```text
When should someone be referred for very high triglycerides?
```

```text
What tests should be performed before starting a statin?
```

```text
When is atorvastatin 20 mg recommended for primary prevention?
```

```text
What LDL target is recommended for secondary prevention?
```

```text
What is the initial statin treatment for someone with established CVD?
```

```text
What statin is recommended for CKD?
```

```text
What should be done if a high-intensity statin is not tolerated?
```

```text
What alternatives are available if statins are contraindicated?
```

```text
When should lipids and liver transaminases be rechecked?
```

The top result should normally be the appropriate direct recommendation chunk, not committee rationale.

---

# 64. Retrieval Validation Scoring

For the sanity test queries report:

```text
query
top chunk ID
recommendation ID
content type
page
topic
retrieval score
```

Flag any case where:

```text
committee_rationale
implementation_impact
update_information
```

ranks above an obviously matching direct clinical recommendation.

---

# 65. Parser Workflow

Implement modularly:

```text
NICE3.pdf
   ↓
PDF page extraction
   ↓
header/footer detection
   ↓
safe text normalization
   ↓
section hierarchy detection
   ↓
subheading detection
   ↓
recommendation ID detection
   ↓
recommendation date parsing
   ↓
content-type classification
   ↓
medical metadata extraction
   ↓
cross-reference extraction
   ↓
semantic chunking
   ↓
deduplication
   ↓
clinical-priority assignment
   ↓
validation
   ↓
JSON + JSONL + Markdown preview
   ↓
processing report
```

Do not place the entire pipeline in one monolithic file.

---

# 66. Token Counting

Use a suitable tokenizer if available.

Store:

```json
{
  "token_count": 412
}
```

for each chunk.

Token counting is only for chunk-size QA.

It must not alter source text.

---

# 67. No LLM Requirement for Basic Parsing

The initial parser should rely primarily on:

```text
regex
document hierarchy
heading detection
rule-based metadata extraction
```

for deterministic fields such as:

```text
recommendation IDs
dates
section numbers
drug doses
thresholds
technology appraisal IDs
```

If an LLM is used for optional metadata classification, it must NEVER rewrite source text.

All LLM-derived metadata should be distinguishable from deterministic metadata.

Prefer deterministic extraction wherever possible.

---

# 68. Manual Review Flags

Flag chunks when:

```text
table structure is uncertain
page text is malformed
a numerical value appears corrupted
a recommendation spans pages ambiguously
recommendation date cannot be attached confidently
section hierarchy is uncertain
an image contains potentially important clinical information not represented in extracted text
```

Use:

```json
{
  "requires_manual_review": true,
  "review_reason": "..."
}
```

---

# 69. Quality Goal

Optimize for:

```text
clinical accuracy
recommendation-level retrieval
metadata-rich filtering
current-vs-historical distinction
page-level citation
primary-vs-secondary prevention distinction
patient-population distinction
minimal hallucination risk
```

Do NOT optimize simply for producing many chunks.

---

# 70. Final Deliverables

When finished, report:

1. files created
2. total PDF pages processed
3. total chunks
4. number of direct NICE recommendation chunks
5. number of rationale chunks
6. number of implementation-impact chunks
7. detected sections
8. recommendation IDs detected
9. recommendation dates detected
10. technology appraisal IDs detected
11. primary prevention chunk count
12. secondary prevention chunk count
13. examples of 8 high-quality chunks
14. any extraction problems
15. pages requiring manual inspection
16. numerical-integrity validation results
17. confirmation that recommendation wording was not intentionally modified
18. path to `nice3_chunks.json`
19. path to `nice3_chunks.jsonl`
20. path to `nice3_chunks_preview.md`

Do NOT proceed yet to:

```text
embeddings
Qdrant
Chroma
LangChain
Gemini
OpenAI
reranker APIs
production UI
```

Stop once the NICE3 parsing and chunking pipeline has been validated.