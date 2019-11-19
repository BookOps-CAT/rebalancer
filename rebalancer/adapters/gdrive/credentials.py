# getting access token

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def get_access_token():
    creds = None
    pickled_token = os.path.join(
        os.environ['USERPROFILE'],
        '.google/rebalancer-dev-token.pickle')
    if os.path.exists(pickled_token):
        print('exists')
        with open(pickled_token, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('refresh')
            creds.refresh(Request())
        else:
            print('new')
            creds_fh = os.path.join(
                os.environ['USERPROFILE'],
                '.google/rebalancer-dev-credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_fh,
                scopes=[
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets'])
            creds = flow.run_local_server(port=0)

        with open(pickled_token, 'wb') as token:
            pickle.dump(creds, token)

    return creds
