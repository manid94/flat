import functions_framework
import os
import json
import hashlib
import requests
import datetime
from google.cloud import storage
from flask import jsonify

BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'gcf-v2-sources-305592068735-us-central1')

password = 'Deepak@94'
topt_key = 'QA622YDDQD2DXH7F27A25F6DWU33AR2V'
APIKEY = 'cb95baef93fa48bb8dd39642a77bb6bb'
userid = 'FT053455'
secretKey = '2024.85e765b78b2c44a69214c05a2627ea96feffc49df6508f8a'

api_url = "https://auth.flattrade.in/?app_key=cb95baef93fa48bb8dd39642a77bb6bb"

# Sample data for the API
dummydata = {
    "items": [
        {"id": 1, "name": "item1", "description": "This is item 1"},
        {"id": 2, "name": "item2", "description": "This is item 2"},
        {"id": 3, "name": "item3", "description": "This is item 3"},
    ]
}

# File-path
file_name = 'token_file.txt'
sibling_dir_name = 'sibling_directory'

def get_today_date():
    return datetime.date.today().strftime('%Y-%m-%d')

def write_token_to_sibling(token):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    # Construct the blob (file) path
    blob = bucket.blob(f'{sibling_dir_name}/{file_name}')
    
    # Convert the dictionary to a JSON string
    data = {
        'date': get_today_date(),
        'token': token
    }
    json_data = json.dumps(data)
    
    # Write the content to the blob (overwrite if exists)
    blob.upload_from_string(json_data, content_type='application/json')

    print(f"File '{file_name}' written to the bucket '{BUCKET_NAME}' in directory '{sibling_dir_name}'.")
    return 'Token generated successfully and written in the file: ' + token


def generate_token(code):
    if code:
        api_secret = APIKEY + code + secretKey

        # Hash the api_secret
        api_secret = hashlib.sha256(api_secret.encode()).hexdigest()

        payload = {"api_key": APIKEY, "request_code": code, "api_secret": api_secret}

        url3 = 'https://authapi.flattrade.in/trade/apitoken'
        res3 = requests.post(url3, json=payload)

        if res3.status_code == 200:
            token = res3.json().get('token', None)
            if token:
                print('Token generated successfully: ' + token)
                return 'Token generated successfully: ' + token
            else:
                print("Token generation failed")
                return "Token generation failed"
        else:
            print("Failed to generate token, HTTP status code: " + str(res3.status_code))
            return "Failed to generate token, HTTP status code: " + str(res3.status_code)


def check_login_and_generate_login(reqCode):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(f'{sibling_dir_name}/{file_name}')

    # Check if the file exists
    if not blob.exists():
        print(f"File '{file_name}' does not exist. Creating a new one.")
        token = generate_token(reqCode)
        if 'fail' not in token:
            token = write_token_to_sibling(token)
        return 'notexist: ' + token

    json_data = blob.download_as_string()
    data = json.loads(json_data)
    token = generate_token(reqCode)
    if 'fail' not in token:
        token = write_token_to_sibling(token)
    
    if data.get('date') == get_today_date():
        print(f"Data is already updated for today: {data}")
        return 'Data is already updated for today: ' + data.get('token') + 'still updated new token' + token
    return 'update: ' + token


@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    # Handling 'name' in JSON or query args
    name = request_json.get('name') if request_json and 'name' in request_json else request_args.get('name', 'World')

    filtered_items = [item for item in dummydata["items"] if item["name"] == name]
    
    token = None  # Initialize token as None
    if 'code' in request_args:
        if 'type' in request_args and request_args['type'] == 'hard':
            token = generate_token(request_args['code'])
            if 'fail' not in token:
                token = write_token_to_sibling(token)
        else:
            token = check_login_and_generate_login(request_args['code'])

    return jsonify({
        'message': 'Hello {}'.format(name),
        'items': filtered_items,
        'token': token
    })