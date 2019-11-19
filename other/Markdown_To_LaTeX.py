__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "November 18, 2019"
__Description__ = ''' '''

import re

markdown_path = 'other/test_md_file.md'

with open(markdown_path) as md_doc:
    md_text = md_doc.read()

md_text = md_text.split('\n')
md_text = [para for para in md_text if para != '']
md_text = [para.strip() for para in md_text]


def special_format(text:str):
    bold_words = re.findall('\*{2}(.*?)\*{2}', text)
    for word in bold_words:
        md_word = "**{}**".format(word)
        tex_word = ("\\textbf{" + word + '}')
        text = text.replace(md_word, tex_word)

    emph_words = re.findall('\*{1}(.*?)\*{1}', text)
    for word in emph_words:
        md_word = "*{}*".format(word)
        tex_word = ("\\emph{" + word + '}')
        text = text.replace(md_word, tex_word)

    return text


tex_body = list()
classification = list()
for count, para in enumerate(md_text):
    special_types = list()

    heading_1_match = re.match('^#{1}[^#]', para)
    special_types.append(heading_1_match)
    if heading_1_match:
        new_text = para[1:].strip()
        new_text = special_format(new_text)
        tex_body.append('\\section*{' + new_text + '}')

    heading_2_match = re.match('^#{2}[^#]', para)
    special_types.append(heading_2_match)
    if heading_2_match:
        new_text = para[2:].strip()
        new_text = special_format(new_text)
        tex_body.append('\\subsection*{' + new_text + '}')

    heading_3_match = re.match('^#{3}[^#]', para)
    special_types.append(heading_3_match)
    if heading_3_match:
        new_text = para[3:].strip()
        new_text = special_format(new_text)
        tex_body.append('\\subsubsection*{' + new_text + '}')

    # ToDo: add handling for headers 4, 5, and 6.

    if not any(special_types):
        new_text = special_format(para)
        tex_body.append(new_text)

tex_body




# ToDo: add special formatting (e.g. bold, italic, etc) function to 'new_text' before adding section info.
class MarkdownToLatex(object):
    def __init__(self):
        pass

