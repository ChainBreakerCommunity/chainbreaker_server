
#https://www.youtube.com/watch?v=-rcRf7yswfM
from __future__ import print_function
import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.env import get_config
conf = get_config()

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)


def gmail_send_message(to: str):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds, _ = google.auth.default()

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content('This is automated draft mail')

        message['To'] = to
        message['From'] = conf["MAIL_USERNAME"]
        message['Subject'] = 'Weekly update'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        logger.info(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')
        send_message = None
    return send_message

if __name__ == '__main__':
    gmail_send_message()