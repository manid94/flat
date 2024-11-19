
import requests
import time
from urllib.parse import parse_qs, urlparse
import hashlib
from automateLogin import autoLogin
from brokerapi import getflattradeapi

password = 'Deepak@94'
topt_key = 'QA622YDDQD2DXH7F27A25F6DWU33AR2V'
userid = 'FT053455'

# redirect to cloud
APIKEY = 'cb95baef93fa48bb8dd39642a77bb6bb'
secretKey = '2024.85e765b78b2c44a69214c05a2627ea96feffc49df6508f8a'
#     OR OR OR OR OR OR OR
# redirect to google .com
APIKEY = 'a3bc1c61a0a1487c89ad5f9175df42cd'
secretKey = '2024.a1f9bc716ad94557b074633e1b4c045ca0775ac48868ef4e'


def main():
    code = autoLogin(APIKEY)

    api_secret =APIKEY+code+secretKey

    api_secret = hashlib.sha256(api_secret.encode()).hexdigest()

    payload = {"api_key":APIKEY, "request_code":code, "api_secret":api_secret}
    print(payload)
    url3 = 'https://authapi.flattrade.in/trade/apitoken'

    res3 = requests.post(url3,json=payload)
    time.sleep(1)
    print(res3.json())

    token = res3.json()['token']
    print(token)
    api = getflattradeapi(token)
    print(api.searchscrip(exchange='NSE', searchtext='Nifty 50'))
main()




APIKEY = 'a3bc1c61a0a1487c89ad5f9175df42cd'
secretKey = '2024.a1f9bc716ad94557b074633e1b4c045ca0775ac48868ef4e'