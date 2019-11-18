__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "November 18, 2019"
__Description__ = '''A script for converting word files to LaTeX documents.'''

from docx import Document

document = Document("G:\data\MRL 332 (2019-2020)\Modeling Data Requirements for Gravity Analysis.docx")

# Unopacking info from document class
hold = document.paragraphs[0].style
hold.name

[item.style.name for item in document.paragraphs]
document.sections

prefix = list()
body = list()

# Collect and TeXify each paragraph according to paragraph type
for count, para in enumerate(document.paragraphs):
    print(count)
    # Determine context of the previous and following paragraph.
    if count != 0:
        previous_type = para.style.name
    else:
        previous_type = 'beginning_of_document'
    if count == len(document.paragraphs)-1:
         next_type = 'end_of_document'
    else:
        next_type = document.paragraphs[count+1].style.name

    if para.style.name == 'Title':
        prefix.append("\\title{" + para.text + "}")
    if para.style.name == 'Subtitle':
        prefix.append("\\author{"+para.text+'}')
    if para.style.name == "Heading 1":
        body.append("\\section*{" + para.text + '}')
    if para.style.name == 'Normal':
        body.append(para.text)
    if para.style.name == 'List Paragraph':
        if previous_type != 'List Paragraph':
            body.append('\\begin{enumerate}')
        body.append("\\item " + para.text)
        if next_type != 'List Paragraph':
            body.append('\\end{enumerate}')

# Write to a file
with open('other/test_tex.tex', 'w') as tex_doc:
    for line in prefix:
        tex_doc.write(line + '\n')
    for line in body:
        tex_doc.write(line + '\n')

print(prefix)
print(body)
