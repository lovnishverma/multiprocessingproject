#with multiprocessing
#pip install pathos
#pip install PyMuPDF

import fitz
import os
from pathos.multiprocessing import ProcessingPool as Pool
import time

def split_and_save_page(args):
    input_pdf, output_directory, page_num = args
    pdf_document = fitz.open(input_pdf)
    page = pdf_document.load_page(page_num)
    output_path = os.path.join(output_directory, f"page_{page_num + 1}.pdf")
    page = pdf_document[page_num]
    new_document = fitz.open()
    new_document.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
    new_document.save(output_path)
    new_document.close()

if __name__ == "__main__":
    # Provide the path to your multi-page PDF file
    input_pdf = "merged.pdf"

    # Create a directory to save the individual PDF pages
    output_directory = "output_pageswithm"
    os.makedirs(output_directory, exist_ok=True)

    # Get the number of available CPU cores
    num_cores = os.cpu_count()

    # Record the start time
    start_time = time.time()

    # Create a Pool with the number of available CPU cores
    with Pool(num_cores) as pool:
        # Prepare arguments for split_and_save_page
        page_numbers = list(range(fitz.open(input_pdf).page_count))
        args = [(input_pdf, output_directory, page_num) for page_num in page_numbers]

        pool.map(split_and_save_page, args)

    # Calculate and print the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Splitting complete. Elapsed time: {elapsed_time:.2f} seconds")
