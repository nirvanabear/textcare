# Standard library import
import logging

# Third-party imports
from twilio.rest import Client
import environ

env = environ.Env()
environ.Env.read_env()


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = f"{env('TWILIO_ACCOUNT_SID')}"
auth_token = f"{env('TWILIO_AUTH_TOKEN')}"
client = Client(account_sid, auth_token)
twilio_number = f"+1{env('TWILIO_PHONE')}"
to_number = f"+1{env('MY_PHONE')}"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message2(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")