import pymupdf
from src.clean_text import clean_all_pages, detect_noise_patterns, _is_clinical_line, _is_boilerplate, _BOILERPLATE_PATTERNS

doc = pymupdf.open('data/raw/WHO03.pdf')
pages_raw = [(i+1, doc[i].get_text('text')) for i in range(len(doc))]
cleaned = clean_all_pages(pages_raw)

line = "GUIDELINE FOR THE PHARMACOLOGICAL TREATMENT OF HYPERTENSION IN ADULTS"
print("is_boilerplate:", _is_boilerplate(line))
print("is_clinical_line:", _is_clinical_line(line))
for pat in _BOILERPLATE_PATTERNS:
    if pat.search(line):
        print("Matched boilerplate pattern:", pat.pattern)

# Check what page 24 cleaned text looks like
print("=== CLEANED PAGE 24 (first 200 chars) ===")
print(repr(cleaned[23][1][:200]))
