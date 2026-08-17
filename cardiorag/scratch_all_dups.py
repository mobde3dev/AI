import json
from difflib import SequenceMatcher

def check_dups(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"=== Checking {filename} ({len(chunks)} chunks) ===")
    pairs = []
    for i in range(len(chunks)):
        c1 = chunks[i]
        t1 = c1['text']
        cid1 = c1['chunk_id']
        ct1 = c1['metadata'].get('content_type')
        for j in range(i+1, len(chunks)):
            c2 = chunks[j]
            t2 = c2['text']
            cid2 = c2['chunk_id']
            ct2 = c2['metadata'].get('content_type')
            
            # check length ratio first
            len_ratio = min(len(t1), len(t2)) / max(len(t1), len(t2))
            if len_ratio > 0.4:
                ratio = SequenceMatcher(None, t1[:1000], t2[:1000]).ratio()
                if ratio > 0.70:
                    pairs.append((ratio, cid1, cid2, ct1, ct2))
    
    pairs.sort(reverse=True)
    for r, cid1, cid2, ct1, ct2 in pairs:
        print(f"  Similarity {r:.2f}: {cid1} ({ct1}) <-> {cid2} ({ct2})")

check_dups('data/processed/nice3_chunks.fixed.json')
check_dups('data/processed/who03_chunks.fixed.json')
