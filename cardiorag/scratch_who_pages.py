import pymupdf

doc = pymupdf.open('data/raw/WHO03.pdf')
for p in [22, 23]:
    print(f"=== WHO03 PAGE {p+1} ===")
    print(doc[p].get_text('text'))
    print("-----------------------------------------")
