from flask import Flask, render_template, jsonify, request, redirect, url_for
from pathos.multiprocessing import ProcessingPool as Pool
import os
import fitz
import time
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import csv
import random
import json
from tqdm import tqdm


app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'csv'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/rename')
def rename():
    return render_template('rename.html')

@app.route('/mail')
def mail():
    return render_template('mail.html')

@app.route('/split_pdf', methods=['POST'])
def split_pdf():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Create a directory to save the individual PDF pages
        output_directory = "output_pageswithm"
        os.makedirs(output_directory, exist_ok=True)

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

        # Get the number of available CPU cores
        num_cores = os.cpu_count()

        # Record the start time
        start_time = time.time()

        # Create a Pool with the number of available CPU cores
        with Pool(num_cores) as pool:
            # Prepare arguments for split_and_save_page
            page_numbers = list(range(fitz.open(filename).page_count))
            args = [(filename, output_directory, page_num) for page_num in page_numbers]

            pool.map(split_and_save_page, args)

        # Calculate and print the elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time

        return f"Splitting complete. Elapsed time: {elapsed_time:.2f} seconds"
    
@app.route('/rename_pdfs', methods=['POST'])
def rename_pdfs():
    if 'csv' not in request.files:
        return redirect(request.url)

    csv_file = request.files['csv']

    if csv_file.filename == '':
        return redirect(request.url)

    if csv_file and allowed_file(csv_file.filename, app.config['ALLOWED_EXTENSIONS']):
        csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
        csv_file.save(csv_filename)

        # Create a directory to save the renamed PDF files
        output_directory = "renamed_pdfs"
        os.makedirs(output_directory, exist_ok=True)

        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_filename)

        # Get the number of available CPU cores
        num_cores = os.cpu_count()

        def rename_pdf(args):
            input_pdf, output_directory, new_name = args
            pdf_document = fitz.open(input_pdf)
            output_path = os.path.join(output_directory, new_name)
            pdf_document.save(output_path)
            pdf_document.close()

        # Create a Pool with the number of available CPU cores
        with Pool(num_cores) as pool:
            # Prepare arguments for rename_pdf
            args = [(os.path.join("output_pageswithm", row["Current Name"]), output_directory, row["New Name"]) for index, row in df.iterrows()]

            pool.map(rename_pdf, args)

        return "Renaming complete. Renamed PDF files saved in the 'renamed_pdfs' directory."

@app.route('/send_emails', methods=['POST'])
def send_emails():
    if 'csv' not in request.files:
        print("No CSV file provided. Please go back and select a CSV file.")
        return "No CSV file provided. Please go back and select a CSV file."

    csv_file = request.files['csv']

    if csv_file.filename == '':
        print("Empty CSV file provided. Please go back and select a valid CSV file.")
        return "Empty CSV file provided. Please go back and select a valid CSV file."

    if not allowed_file(csv_file.filename, app.config['ALLOWED_EXTENSIONS']):
        print("Invalid file type. Please upload a CSV file.")
        return "Invalid file type. Please upload a CSV file."

    # Save the CSV file
    csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
    csv_file.save(csv_filename)

    # Set your email and password
    email = "nielitcertificates@gmail.com"
    password = "rbgy ecim txsi wwbl"

    # Create an SMTP session
    smtp = smtplib.SMTP('smtp.gmail.com', 587)

    # Start TLS for security
    smtp.starttls()

    # Login with your email and password
    smtp.login(email, password)

    # Read student data from the CSV file and store it in a list
    student_data = []
    with open(csv_filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            student_data.append({'Email': row['Email'], 'PDF File': row['PDF File']})

    # Initialize counters
    email_count = 0
    success_count = 0
    failed_count = 0

    results = []

    # Initialize timer and progress bar
    start_time = time.time()
    progress_bar = tqdm(total=len(student_data), desc="Sending Emails")

    for student_info in student_data:
        student_email = student_info['Email']
        pdf_filename = os.path.join("renamed_pdfs", student_info['PDF File'])

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = student_email
        msg['Subject'] = "Your Demo Test Certificate"

        # Add a message body
        message = "Dear Student, please find your Certificate Pdf attached."
        msg.attach(MIMEText(message, 'plain'))

        # Attach the PDF file
        with open(pdf_filename, "rb") as pdf_file:
            attach = MIMEApplication(pdf_file.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_filename))
            msg.attach(attach)

        try:
            # Send the email
            smtp.sendmail(email, student_email, msg.as_string())

            # Calculate and display the delay time when an email is sent successfully
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Email sent successfully ({email_count}): {student_email}")
            print(f"Delay before next email: {elapsed_time:.2f} seconds")

            # Random delay between 15 to 60 seconds
            delay_seconds = random.randint(15, 60)
            print(f"Random delay for the next email: {delay_seconds} seconds")

            # Use a non-blocking delay using time
            time.sleep(delay_seconds)

            # Reset the timer for the next email
            success_count += 1

        except Exception as e:
            failed_count += 1
            print(f"Failed to send email ({email_count}): {student_email}")
            print(f"Error: {str(e)}")

        # Update counters and progress bar
        email_count += 1
        progress_bar.update(1)

    # Close the SMTP session
    smtp.quit()

    # Print the summary
    print(f"\nTotal emails sent: {email_count}")
    print(f"Successful emails: {success_count}")
    print(f"Failed emails: {failed_count}")

    return "Email sending completed. Check the terminal for results."

if __name__ == '__main__':
    app.run(debug=True)