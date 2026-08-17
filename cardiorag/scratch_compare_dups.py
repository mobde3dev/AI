import json
from difflib import SequenceMatcher

with open('data/processed/nice3_chunks.fixed.json', 'r', encoding='utf-8') as f:
    chunks = {c['chunk_id']: c for c in json.load(f)}

for c1_id, c2_id in [
    ('NICE3_1.7_IMPACT_001', 'NICE3_1.7_IMPACT_002'),
    ('NICE3_1.7_RATIONALE_001', 'NICE3_1.7_RATIONALE_004'),
    ('NICE3_1.7_RATIONALE_002', 'NICE3_1.7_RATIONALE_004'),
]:
    if c1_id in chunks and c2_id in chunks:
        t1 = chunks[c1_id]['text']
        t2 = chunks[c2_id]['text']
        ratio = SequenceMatcher(None, t1, t2).ratio()
        print(f"Similarity {c1_id} vs {c2_id}: {ratio:.2f}")
        print(f"--- {c1_id} (len={len(t1)}) ---")
        print(t1[:200])
        print(f"--- {c2_id} (len={len(t2)}) ---")
        print(t2[:200])
        print("="*60)
