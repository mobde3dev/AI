import pymupdf

doc = pymupdf.open('data/raw/NICE3.pdf')
with open('scratch_pages_26_36.txt', 'w', encoding='utf-8') as out:
    for i in range(25, 36):
        out.write(f"================== PAGE {i+1} ==================\n")
        out.write(doc[i].get_text('text'))
        out.write("\n\n")

print("Dumped pages 26-36")
