import fitz

doc = fitz.open('data/raw/NICE3.pdf')
print('NICE3 page count:', len(doc))
for i in range(len(doc)):
    text = doc[i].get_text('text')
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    first_few = ' | '.join(lines[:3]) if lines else 'EMPTY'
    for phrase in ['Why the committee made', 'Rationale and impact', '1.7 Lipid', '1.7.1', 'How the recommendations might affect', 'Rationale']:
        if phrase.lower() in text.lower():
            print(f'Page {i+1}: contains "{phrase}"')
