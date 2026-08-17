import pymupdf
import json
import re

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())).strip()

doc = pymupdf.open('data/raw/NICE3.pdf')
pdf_pages = [norm(doc[i].get_text('text')) for i in range(len(doc))]

with open('data/processed/nice3_chunks.fixed.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"Total NICE3 chunks: {len(chunks)}")
mismatches = []
for c in chunks:
    cid = c['chunk_id']
    m = c['metadata']
    cur_start = m.get('pdf_page_start')
    cur_end = m.get('pdf_page_end')
    
    # Extract substantive lines from chunk text
    text = c['text']
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Filter out header lines
    substantive = [
        l for l in lines 
        if not l.startswith('Section:') 
        and not l.startswith('Subheading:') 
        and not l.startswith('Recommendation:') 
        and not l.startswith('Why the committee')
        and not l.startswith('How the recommendations')
        and len(norm(l)) > 20
    ]
    
    if not substantive:
        substantive = [l for l in lines if len(norm(l)) > 15]
    
    # Find matching pages
    matched_pages = []
    for line in substantive[:5]:
        nline = norm(line)[:40]
        for p_idx, p_text in enumerate(pdf_pages):
            if nline in p_text and (p_idx + 1) not in matched_pages:
                matched_pages.append(p_idx + 1)
    
    if matched_pages:
        calc_start = min(matched_pages)
        calc_end = max(matched_pages)
        if calc_start != cur_start or calc_end != cur_end:
            mismatches.append((cid, cur_start, cur_end, calc_start, calc_end, substantive[0][:60] if substantive else ""))

print(f"Found {len(mismatches)} page mismatches in NICE3:")
for cid, cs, ce, calc_s, calc_e, sub in mismatches:
    print(f"  {cid:35s}: current=({cs}, {ce}) -> calculated=({calc_s}, {calc_e}) | sample: {sub}")
