#without multiprocessing
import fitz
import os
import time

# Provide the path to your multi-page PDF file
input_pdf = "cert.pdf"

# Record the start time
start_time = time.time()

# Open the multi-page PDF
pdf_document = fitz.open(input_pdf)

# Create a directory to save the individual PDF pages
output_directory = "output_pages_withoutm"
os.makedirs(output_directory, exist_ok=True)

# Extract and save each page as a separate PDF
for page_num in range(pdf_document.page_count):
    page = pdf_document.load_page(page_num)

    # Save each page with a unique name
    output_path = os.path.join(output_directory, f"page_{page_num + 1}.pdf")
    pdf_document.save(output_path, page_num, page_num)

# Calculate and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Splitting complete. Elapsed time: {elapsed_time:.2f} seconds")
