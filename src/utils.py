import os, base64, requests
from dotenv import load_dotenv

def get_access_token():
        """
        Gets the access token for the Kroger API
        """

        load_dotenv()
        CLIENT_ID = os.environ.get("KROGER_CLIENT_ID")
        CLIENT_SECRET = os.environ.get("KROGER_CLIENT_SECRET")

        url = "https://api.kroger.com/v1/connect/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()}"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "product.compact"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            access_token = response.json()["access_token"]
            return access_token
        else:
            return None