import functions_framework
import os
import json
import hashlib
import requests
import datetime
from google.cloud import storage

# file-path
file_name = 'token_file.txt'
sibling_dir_name = 'sibling_directory'


def get_today_date():
    return datetime.date.today().strftime('%Y-%m-%d')

def check_token():
    client = storage.Client()
    bucket = client.get_bucket('gcf-v2-sources-305592068735-us-central1')
    blob = bucket.blob(f'{sibling_dir_name}/{file_name}')
    
    # Check if the file exists
    if not blob.exists():
        print(f"File '{file_name}' does not exist. Creating a new one.")
        token = 'File {file_name} does not exist. Creating a new one.'
        return token

 
    json_data = blob.download_as_string()
    data = json.loads(json_data)
    if data.get('date') == get_today_date():
        print(f"Data is already updated for today: {data}")
        return data.get('token') + 'exist in file'
    else:
        token = 'token doesnot exist'
        return token


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'

    comments = check_token()
    return 'Hello {}!'.format(name) + comments
