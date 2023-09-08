from dotenv import load_dotenv
import os
import base64
from requests import post


load_dotenv()

# USER must create a .env file with their CLIENT_ID and CLIENT_SECRET after they've created an app
#   on developer.spotify.com
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_id = os.getenv("USER_ID")
app_secret = os.getenv("APP_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data= data)
    # json_result = json.loads(result.content)
    # token = json_result["access_token"]
    token = result.json()["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def spotify_user_id():
    return user_id