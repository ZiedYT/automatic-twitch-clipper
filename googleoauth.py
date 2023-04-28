from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def main(name):
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    SAMPLE_RANGE_NAME = 'Class Data!A2:E'
    creds = None
    if(not "tokens/" in name):
        name="tokens/"+name
    if os.path.exists('{}.json'.format(name)):
        creds = Credentials.from_authorized_user_file('{}.json'.format(name), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('{}.json'.format(name), 'w') as token:
            token.write(creds.to_json())


if __name__ == '__main__':
    import sys
    name="tokens/token"
    if(len(sys.argv)>1):
        name= sys.argv[1]

    main(name)