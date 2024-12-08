import json
import datetime
import pyotp
from google.cloud import storage
from NorenRestApiPy.NorenApi import NorenApi
from automateLogin.generateToken import generateToken

# Credentials - define these variables
password = 'Deepak@94'
flatuserid = 'FT053455'

shoonyauser  = 'FA348190'
shoonyapwd     = 'Deepak@94'
factor2 = '262M3JU777Q5ZEM6KT266CF2V472QODA'
vc      = 'FA348190_U'
app_key = 'a3bc1c61a0a1487c89ad5f9175df42cd'
imei    = 'abc1234'

#URL to get session
api_url = "https://auth.flattrade.in/?app_key=a3bc1c61a0a1487c89ad5f9175df42cd"



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
        raise ValueError(token)
        return token

 
    json_data = blob.download_as_string()
    data = json.loads(json_data)
    if data.get('date') == get_today_date():
        print(f"Data is already updated for today: {data}")
        return data.get('token')
    else:
        token = 'token doesnot exist'
        raise ValueError(token)
        return token


def getflattradeapi():
    token = generateToken()

    class FlatTradeApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/', 
                            websocket='wss://piconnect.flattrade.in/PiConnectWSTp/')

    api = FlatTradeApiPy()
    api.set_session(userid=flatuserid, password=password, usertoken=token)  # Set UID and token here
    return api


def getshoonyatradeapi():
    from NorenRestApiPy.NorenApi import NorenApi

    class ShoonyaTradeApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self,  host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')

    # Create a TOTP object using the given secret key
    totp = pyotp.TOTP(factor2)

    # Generate the current TOTP code
    current_otp = totp.now()
    api = ShoonyaTradeApiPy()
    api.login(userid=shoonyauser, password=shoonyapwd, twoFA=current_otp, vendor_code=vc, api_secret=app_key, imei=imei)
    return api
