from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import os.path


class GmailHelper(object):
    def __init__(self, client_secret_path, store_path=None):
        # Setup the Gmail API
        SCOPES = 'https://www.googleapis.com/auth/gmail.compose'
        store = file.Storage(os.path.join(store_path or '/tmp/',
                                          'storage.json'))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(client_secret_path, SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()))

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        message = {'raw': base64.urlsafe_b64encode(message)}
        try:
            message = (self.service.users().messages()
                       .send(userId=user_id, body=message)
                       .execute())
            print('E-mail sent. Message Id: %s' % message['id'])
        except errors.HttpError, error:
            print('An error occurred: %s' % error)
