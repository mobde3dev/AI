from src.clean_text import _CLINICAL_PATTERNS, MEDICAL_ABBREVIATIONS

line = "GUIDELINE FOR THE PHARMACOLOGICAL TREATMENT OF HYPERTENSION IN ADULTS"
for pat in _CLINICAL_PATTERNS:
    if pat.search(line):
        print("Matched clinical pattern:", pat.pattern)
for abbr in MEDICAL_ABBREVIATIONS:
    if abbr in line:
        print("Matched abbreviation:", abbr)
