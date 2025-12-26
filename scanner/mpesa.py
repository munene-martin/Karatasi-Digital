import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64

def initiate_stk_push(phone, amount):
    # 1. Your Credentials (Get these from Daraja)
    consumer_key = "7MORBUnhHKp25bedkwusY8GKI2wLttZq4NWpGZlDyekch8cM"
    consumer_secret = "BQhm3cKIAxNIwWLglwvpDfXR7rA2QNCF7oak8DoQ7bU52AqMhXoIhHfgxwSnuiIm"
    
    # 2. Get the Access Token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    res = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = res.json()['access_token']
    
    # 3. Setup the STK Push Parameters
    business_short_code = "174379" # Default Sandbox Shortcode
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Password must be base64 encoded
    data_to_encode = business_short_code + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    # 4. The Request Payload
    headers = {"Authorization": f"Bearer {access_token}"}
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    payload = {
    "BusinessShortCode": "174379",
    "Password": online_password,
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": phone,
    "PartyB": "174379",
    "PhoneNumber": phone,
    # --- UPDATE THIS LINE CAREFULLY ---
    "CallBackURL": "https://unabruptly-uneuphemistic-ora.ngrok-free.dev/mpesa-callback/",
    # ----------------------------------
    "AccountReference": "KaratasiDigital",
    "TransactionDesc": "Premium OCR Payment"
}
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()