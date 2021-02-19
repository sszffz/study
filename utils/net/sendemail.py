"""
Utilities method to send email

reference:
https://realpython.com/python-send-email/
https://stackoverflow.com/questions/23137012/535-5-7-8-username-and-password-not-accepted
"""
import smtplib
import ssl
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from security.email import get_email_account, get_email_password
from utils.log import log


def send_email(subject: str, body: str, attachment_file_path: str = None):
    account = get_email_account()
    password = get_email_password()

    if account is None or password is None:
        log("Invalid email account or password")
        return

    # subject = "An email with attachment from Python"
    # body = "This is an email with attachment sent from Python"
    # sender_email = "my@gmail.com"
    # receiver_email = "your@gmail.com"
    # password = input("Type your password and press enter:")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = account
    message["To"] = account
    message["Subject"] = subject
    message["Bcc"] = ""  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if attachment_file_path and os.path.isfile(attachment_file_path):
        filename = attachment_file_path  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(account, password)
        server.sendmail(account, account, text)


if __name__ == "__main__":
    send_email("test", "It is test")