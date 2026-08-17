import json

with open('data/processed/who03_chunks.fixed.json', 'r', encoding='utf-8') as f:
    chunks = {c['chunk_id']: c for c in json.load(f)}

for cid in ['WHO03_0_TBL_009', 'WHO03_0_TBL_010', 'WHO03_0_TBL_011', 'WHO03_0_TBL_012']:
    if cid in chunks:
        print(f"=== {cid} ===")
        print(chunks[cid]['text'][:300])
        print()
