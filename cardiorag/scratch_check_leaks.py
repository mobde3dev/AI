import json
import re

for filename in ['data/processed/who03_chunks.fixed.json', 'data/processed/nice3_chunks.fixed.json']:
    with open(filename, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"=== Checking {filename} ({len(chunks)} chunks) ===")
    for c in chunks:
        cid = c['chunk_id']
        text = c['text']
        for pat in [
            r"GUIDELINE\s+FOR",
            r"PHARMACOLOGICAL\s+TREATMENT\s+OF\s+HYPERTENSION",
            r"Cardiovascular\s+disease:\s*risk\s+assessment",
            r"NG238",
            r"©\s*NICE",
            r"Notice\s+of\s+rights",
            r"Page\s+\d+\s+of",
            r"terms-and-conditions",
            r"conditions#notice-of-rights"
        ]:
            if re.search(pat, text, re.IGNORECASE):
                m = re.search(pat, text, re.IGNORECASE)
                snippet = text[max(0, m.start()-30): min(len(text), m.end()+50)].replace('\n', ' ')
                print(f"[{cid}] matched {pat}: ...{snippet}...")
