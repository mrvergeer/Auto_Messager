import time
import os
import pandas as pd
from authentication_import import fetch_and_process_sheet
from datetime import datetime
from email_sender import send_email_with_inline_image
from friend_class import Friend
from gemini_text import GenerateMessage
from gemini_image import GenerateImage, ImageUploader
from io import BytesIO
from twilio_send import Twilio


# Define your credentials path, spreadsheet ID, and data range
credentials_file = os.getenv('CREDENTIALS_FILE')
spreadsheet_id = os.getenv('SPREADSHEET_ID')
data_range = SHEET_RANGE = os.getenv('SHEET_RANGE')

# Call the function to get the DataFrame
df = fetch_and_process_sheet(credentials_file, spreadsheet_id, data_range)

# Now you can work with the 'df' DataFrame in your main.py file
if not df.empty:
    # Continue with your data processing, including the birthday conversion
    if 'birthday' in df.columns:
        try:
            df['birthday'] = pd.to_datetime(df['birthday'], format='%d-%m', errors='coerce').dt.strftime('%d-%m')
        except Exception as e:
            print(f"\nError converting 'birthday' column: {e}")
else:
    print("No data received from Google Sheets.")
    exit()

today_dm = datetime.now().strftime('%d-%m')

image_uploader = ImageUploader(project_id="birthday-manager-456500")

for _, row in df[df['birthday'] == today_dm].iterrows():
    friend = Friend(**row.to_dict())

    send_media = False  # Initialize a flag for sending media
    public_image_url = None  # Initialize media URL
    generated_image = None  # Initialize generated_image to None
    local_image_path = None  # Initialize local_image_path

    if friend.meme_pref.lower() == 'y':
        image_generator = GenerateImage(
            name=friend.name,
            notes=friend.notes,
            language=friend.language,
            theme=friend.theme
        )

        generated_image = image_generator.request_image()

        if generated_image:
            image_buffer = BytesIO()
            generated_image.save(image_buffer, format="PNG")
            image_bytes = image_buffer.getvalue()

            image_filename = f"birthday_{friend.name.replace(' ', '_')}.png"
            public_image_url = image_uploader.upload_image_to_public_url(
                image_bytes, image_filename
            )
            local_image_path = f"/tmp/birthday_{friend.name.replace(' ', '_')}.png"
            generated_image.save(local_image_path)
            send_media = True
        else:
            print(f"Failed to generate image for {friend.name}. Sending text only.")
            local_image_path = None  # Explicitly set to None when no image
    elif friend.meme_pref.lower() == 'n':
        print(f"Meme preference is 'n' for {friend.name}. Sending text only.")
        local_image_path = None
    else:
        print(f"Unknown meme_pref '{friend.meme_pref}' for {friend.name}. Sending text only.")
        local_image_path = None

    # Generate the WhatsApp message
    gen_ai_message = GenerateMessage(
        name=friend.name,
        notes=friend.notes,
        language=friend.language,
        theme=friend.theme,
        friend_type=friend.friend_type
    )
    message_body = gen_ai_message.request_response()

    if friend.comms_pref.lower() == 'whatsapp':
        twilio_params = {
            "body": message_body,
            "phone_from": '+18337712335', #"whatsapp:+14155238886",  # Replace with your Twilio number
            "phone_to": f"{friend.phone}", #f"whatsapp:{friend.phone}",
        }
        if send_media and public_image_url:
            twilio_params["media_url"] = [public_image_url]

        # Send the WhatsApp message via Twilio
        twilio_client = Twilio(**twilio_params)
        try:
            twilio_client.send_twilio()
            print(f"WhatsApp message{' with image' if send_media and public_image_url else ''} sent to {friend.name}")

        except Exception as e:
            print(f"Error sending Twilio message to {friend.name}: {e}")
        time.sleep(5)
    elif friend.comms_pref.lower() == 'email':
        # Generate the message body for the email

        email_subject = gen_ai_message.email_request_subject()
        email_body_text = gen_ai_message.email_request_body()

        email_body_html = f"""
                <html>
                <body>
                    <img src="cid:birthday_image" alt="Birthday Image"><br><br>
                    
                </body>
                </html>
                """
        # You'll need to save the generated image locally to use its path here
        local_image_path = f"/tmp/birthday_{friend.name.replace(' ', '_')}.png"
        if generated_image:
            generated_image.save(local_image_path)
            send_email_with_inline_image(email_subject, email_body_text, email_body_html, friend.email,
                                         local_image_path)
            os.remove(local_image_path)  # Clean up the temporary file
            print(f"Birthday email sent to {friend.name} ({friend.email}) with inline image")
        else:
            send_email_with_inline_image(email_subject,
                                         email_body_text,
                                         f"<html><body><p>{email_body_text}</p></body></html>",
                                         friend.email,
                                         None)
            print(f"Birthday email sent to {friend.name} ({friend.email}) without image (image generation failed)")

    else:
        print(f"Unknown comms_pref '{friend.comms_pref}' for {friend.name}. Skipping WhatsApp.")
