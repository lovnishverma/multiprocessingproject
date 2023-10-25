#pip install docx2pdf

import docx2pdf

# Provide the path to your Word document
input_docx = "cert.docx"

# Convert the Word document to separate PDF files for each page
docx2pdf.convert(input_docx)

#python app.py
