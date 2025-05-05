import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


def send_email_with_inline_image(email_subject,
                                 email_body_plain,
                                 email_body_formatted,
                                 recipient_email,
                                 attachment_path):
    """Sends an email with HTML body containing an inline image."""
    port = 465  # For SSL
    smtp_server = os.environ.get("SMTP_SERVER")
    sender_email = os.environ.get("SMTP_USERNAME")
    sender_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_server or not sender_email or not sender_password:
        print("Error: SMTP_SERVER, SMTP_USERNAME, or SMTP_PASSWORD environment variables not set.")
        return False

    message = MIMEMultipart('related')  # 'related' for inline attachments
    message['Subject'] = email_subject
    message['From'] = sender_email
    message['To'] = recipient_email

    # Create the plain text part (for clients that don't support HTML)
    part1 = MIMEText(email_body_plain, 'plain')
    message.attach(part1)

    # Create the HTML part with the Content-ID reference
    part2 = MIMEText(email_body_formatted, 'html')
    message.attach(part2)

    # Attach the image
    if attachment_path:
        try:
            with open(attachment_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', '<birthday_image>')  # Unique Content-ID
                message.attach(img)
        except FileNotFoundError:
            print(f"Error: Image file not found at {attachment_path}")
            return False

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Email with inline image sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email with inline image to {recipient_email}: {e}")
        return False

