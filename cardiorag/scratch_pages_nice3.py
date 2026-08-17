import sys
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

doc = pymupdf.open('data/raw/NICE3.pdf')
with open('scratch_pages_nice3.txt', 'w', encoding='utf-8') as out:
    for i in range(len(doc)):
        text = doc[i].get_text('text')
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        out.write(f"=== PAGE {i+1} ===\n")
        out.write("\n".join(lines[:6]) + "\n\n")

print(f"Dumped page summaries for {len(doc)} pages to scratch_pages_nice3.txt")
