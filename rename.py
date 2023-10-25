import fitz
import os
import pandas as pd
from pathos.multiprocessing import ProcessingPool as Pool

def rename_pdf(args):
    input_pdf, output_directory, new_name = args
    pdf_document = fitz.open(input_pdf)
    output_path = os.path.join(output_directory, new_name)
    pdf_document.save(output_path)
    pdf_document.close()

if __name__ == "__main__":
    # Provide the path to your multi-page PDF directory and the CSV file
    pdf_directory = "output_pageswithm"  # Change to your PDF directory
    csv_file = "renaming1.csv"  # Change to your CSV file

    # Create a directory to save the renamed PDF files
    output_directory = "renamed_pdfs"
    os.makedirs(output_directory, exist_ok=True)

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Get the number of available CPU cores
    num_cores = os.cpu_count()

    # Create a Pool with the number of available CPU cores
    with Pool(num_cores) as pool:
        # Prepare arguments for rename_pdf
        args = [(os.path.join(pdf_directory, row["Current Name"]), output_directory, row["New Name"]) for index, row in df.iterrows()]

        pool.map(rename_pdf, args)

    print("Renaming complete. Renamed PDF files saved in the 'renamed_pdfs' directory.")
