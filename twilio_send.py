import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]


class Twilio:
    def __init__(self, body, phone_from, phone_to, media_url=None):
        self.body = body
        self.phone_from = phone_from
        self.phone_to = phone_to
        self.media_url = media_url
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def send_twilio(self):
        message_params = {
            "to": self.phone_to,
            "from_": self.phone_from,
            "body": self.body
        }
        if self.media_url:
            message_params["media_url"] = self.media_url

        message = self.client.messages.create(**message_params)
        print(f"Twilio message SID: {message.sid}")
