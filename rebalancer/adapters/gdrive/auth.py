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

    if not creds and not creds.valid:
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
                scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']) # will this limit scopes enabled in creds??
            creds = flow.run_local_server(port=0)

        with open(pickled_token, 'wb') as token:
            pickle.dump(creds, token)

    return creds


if __name__ == '__main__':
    from googleapiclient.discovery import build

    creds = get_access_token()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        pageSize=10, fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])

    if not items:
        print('No files found')
    else:
        print('Files:')
        for item in items:
            print(f'{item["name"]}, {item["id"]}')
