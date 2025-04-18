from google import genai
import os

API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY)


class GenerateMessage:
    LANGUAGE_MAP = {
        'ja': "japanese",
        'nl': "dutch"
    }

    def __init__(self, name, notes, language, theme, friend_type):
        self.name = name
        self.notes = notes
        self.language = language
        self.theme = theme
        self.friend_type = friend_type

    def _get_gemini_language(self):
        return self.LANGUAGE_MAP.get(self.language, "english")

    def _generate_content(self, content_request):
        language = self._get_gemini_language()
        if language:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{content_request}. Write this in {language}. Don't translate. Only in {language}."
                         f"Only provide 1 option that I can send out directly (no alternatives). Make sure to "
                         f"not include any variable fields that are not specified. Do not add any items in "
                         f"square brackets []. Make sure that the language used is culturally appropriate "
                         f"in relation to the {language} used. Make sure the message does not sound too American. "
            )
            return response.text
        else:
            return f"Error: Language '{self.language}' not supported."

    def request_response(self):
        formality = (self.friend_type, "personal")
        content_request = (f"Write a short {self.theme} message for {self.name}. {self.notes}. "
                           f"Do not use my name. For WhatsApp. Write one message. "
                           f"Make sure this is a {formality} message. ")
        return self._generate_content(content_request)

    # Section to create components for an email response.
    def email_request_subject(self):
        formality = (self.friend_type, "personal")
        content_request = (f"Write a short {self.theme} subject line for {self.name} for an email. "
                           f"Write one message. Make sure this is a {formality} message. "
                           f"Do not mention {formality} or {self.theme}. Do not start the line with 'Subject'. "
                           f"This should be a regular email subject line. Make sure to generate only one"
                           f"line, and do not include a newline character. Make sure to "
                           f"not include any variable fields that are not specified. Do not add any items in "
                           f"square brackets []. Make sure that the language used is culturally appropriate "
                           f"in relation to the language used. Make sure the message does not sound too American. ")
        return self._generate_content(content_request)

    def email_request_body(self):
        formality = (self.friend_type, "personal")
        language = self._get_gemini_language()
        content_request = (f"Write a {self.theme} message for {self.name} for an email. "
                           f"This is the body text. Write one message. "
                           f"Make sure this is a {formality} message. Do not mention {formality}. "
                           f"Add an opening and a closing in {language} with an empty line between each part. "
                           f"No variable fields. Do not include a subject line. Make sure to "
                           f"not include any variable fields that are not specified. Do not add any items in "
                           f"square brackets []. Make sure that the language used is culturally appropriate "
                           f"in relation to the {language} used. Make sure the message does not sound too American. ")
        if language:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{content_request}. Write this in {language}. Only in {language}. "
                         f"Translate any non-{language} words to {language}."
            )
            return response.text
        else:
            return f"Error: Language '{self.language}' not supported."
