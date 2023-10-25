import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import csv
import time
import random
from tqdm import tqdm

# Set your email and password
email = "technicalboyprince@gmail.com"
password = "sjkr liut ryek dcdy"

# Create an SMTP session
smtp = smtplib.SMTP('smtp.gmail.com', 587)

# Start TLS for security
smtp.starttls()

# Login with your email and password
smtp.login(email, password)

# Read student data from the CSV file and store it in a list
student_data = []
with open('filenameee.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        student_data.append({'Email': row['Email'], 'PDF File': row['PDF File']})

# Initialize counters
email_count = 0
success_count = 0
failed_count = 0

# Timer
start_time = time.time()

# Create a tqdm progress bar
progress_bar = tqdm(total=len(student_data), desc="Sending Emails")

# Loop through the email list
for student_info in student_data:
    student_email = student_info['Email']
    pdf_filename = student_info['PDF File']

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
        attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
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
        start_time = time.time()
        while time.time() - start_time < delay_seconds:
            pass

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
