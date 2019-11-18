__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "November 18, 2019"
__Description__ = '''A script for converting word files to LaTeX documents.'''

from docx import Document
import os as os

document = Document("G:\data\MRL 332 (2019-2020)\Modeling Data Requirements for Gravity Analysis.docx")

opening_matter = " \\documentclass{article} \n " \
                 "\\usepackage[paperwidth=8.5in,left=.75in,right=.75in,top=1.0in, bottom=1.0in,paperheight=11.0in,textheight=9in]{geometry} \n " \
                 "\\geometry{letterpaper} \n " \
                 "\\usepackage{graphicx} \n " \
                 "\\usepackage[cp1251]{inputenc}"


prefix = list()
body = list()

prefix.append(opening_matter)

# Remove empty paragraphs
paragraph_list = [para for para in document.paragraphs if para.text != '']

# Collect and TeXify each paragraph according to paragraph type
for count, para in enumerate(paragraph_list):
    # Determine context of the previous and following paragraph.
    if count != 0:
        previous_type = paragraph_list[count - 1].style.name
    else:
        previous_type = 'beginning_of_document'
    if count == len(paragraph_list) - 1:
        next_type = 'end_of_document'
    else:
        next_type = paragraph_list[count + 1].style.name

    if para.style.name == 'Title':
        prefix.append("\\title{" + para.text + "}")
    if para.style.name == 'Subtitle':
        prefix.append("\\author{" + para.text + '}')
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

begin_doc = " \\begin{document} \n \\maketitle"
prefix.append(begin_doc)

# Write to a file
with open('other/test_tex.tex', 'w') as tex_doc:
    for line in prefix:
        tex_doc.write(line + '\n')
    for line in body:
        tex_doc.write(line + '\n')
    tex_doc.write('\\end{document}')

os.system("latex other/test_tex.tex")
os.system("pdflatex other/test_tex.tex")

# Todo: fix way that " and ' get encoded for UTF-8
