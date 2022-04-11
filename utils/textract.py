import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
#
import hashlib
import textract
import PyPDF2
from pdfminer.high_level import extract_text
import pandas as pd

def extract_text_from_pdf(file):
    '''Opens and reads in a PDF file from path'''

    fileReader = PyPDF2.PdfFileReader(open(file, 'rb'))
    page_count = fileReader.getNumPages()
    text = [fileReader.getPage(i).extractText() for i in range(page_count)]

    return str(text).replace("\\n", "")


def extract_text_from_word(filepath):
    '''Opens en reads in a .txt, .doc or .docx file from path'''

    txt = textract.process(filepath, method='pdfminer').decode('utf-8')

    return txt.replace('\n', ' ').replace('\t', ' ')
