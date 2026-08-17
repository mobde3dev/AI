import json
import re

with open('data/processed/nice3_chunks.fixed.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} NICE3 chunks")
for c in chunks:
    cid = c['chunk_id']
    text = c['text']
    for pat in [
        r"©\s*NICE",
        r"All rights reserved",
        r"conditions#notice-of-rights",
        r"Page \d+ of",
        r"Cardiovascular disease: risk assessment and reduction",
        r"\(NG238\)",
        r"GUIDELINE FOR T"
    ]:
        if re.search(pat, text, re.IGNORECASE):
            print(f"[{cid}] Leaked: {pat}")
