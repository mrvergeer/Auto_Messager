import os
from google.cloud import storage
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types


# --- Google Cloud Storage Configuration ---
GCP_STORAGE_BUCKET_NAME = os.getenv('GCP_BUCKET')

# --- Gemini API Key ---
API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY)
if not API_KEY:
    raise ValueError("GENAI_API_KEY environment variable not set.")
# client = genai.Client(api_key=API_KEY)


class GenerateImage:
    def __init__(self, name, notes, language, theme):
        self.name = name
        self.notes = notes
        self.language = language
        self.theme = theme

    def request_image(self):
        language_map = {
            "nl": "dutch",
            "ja": "japanese",
        }
        image_language = language_map.get(self.language, "english")

        contents = (f'Can you create a fun image with a {self.theme} theme? '
                    f'Create it in a cartoony studio Ghibli style in soft pastel colors.'
                    f'Write a {self.theme} message on it in the {image_language} language.')

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=f"{contents} Pick one solution only",
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"Gemini Image Text Response: {part.text}")
            elif part.inline_data is not None:
                image_bytes = BytesIO(part.inline_data.data)
                image = Image.open(image_bytes)
                return image
        return None


class ImageUploader:
    def __init__(self, bucket_name=None, project_id=None):
        """
        Initializes the ImageUploader with an optional GCS bucket name and project ID.
        """
        if not project_id:
            # Try to get project ID from environment or raise error
            project_id = os.environ.get("GCP_PROJECT_ID")
            if not project_id:
                raise EnvironmentError(
                    "GCP_PROJECT_ID environment variable not set and project_id not passed."
                )
            self.storage_client = storage.Client(project=project_id)
        else:
            self.storage_client = storage.Client(project=project_id)

        if bucket_name:
            self.bucket_name = bucket_name
        else:
            self.bucket_name = "birthday-manager-images"  # os.environ.get("GCP_STORAGE_BUCKET_NAME")
            if not self.bucket_name:
                raise ValueError("GCP_STORAGE_BUCKET_NAME environment variable not set or bucket_name not provided.")
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def upload_image_to_public_url(self, image_bytes, filename, folder="birthdays"):
        try:
            blob = self.bucket.blob(f"{folder}/{filename}")
            blob.upload_from_file(BytesIO(image_bytes), content_type="image/png")

            # Construct the correct public URL
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{folder}/{filename}"
            return public_url
        except Exception as e:
            print(f"Error uploading {filename} to GCS: {e}")
            return None
