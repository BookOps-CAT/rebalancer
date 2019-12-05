# method to obtain credentials
import json
import os


def get_sierra_creds():
    sierra_creds_fh = os.path.join(
        'c:\\Users', os.environ.get('USERNAME'), '.sierra\\test_creds.json')
    with open(sierra_creds_fh, 'r') as file:
        creds = json.load(file)
        base = creds['base_url']
        key = creds['key']
        secret = creds['secret']

        return (base, key, secret)
