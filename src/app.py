from flask import Flask, jsonify, request, session
from datetime import datetime, timedelta
import firebase_admin, requests, os, sys
from firebase_admin import credentials, firestore
from utils import get_kroger_access_token
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'firebase_credentials.json')
# cred = credentials.Certificate(credentials_path)
# firebase_admin.initialize_app(cred)

# db = firestore.client()

access_token = None
expiry_time = None
data = []
members = ["Viren", "Rishi", "Siddharth", "Rohan", "Christopher"]

def set_access_token():
    global access_token, expiry_time
    api_result = get_kroger_access_token()
    access_token = api_result["access_token"]
    expiry_time = datetime.now() + timedelta(seconds=api_result["expires_in"])

@app.route("/refresh_token")
def init():
    """
    Initializes the token
    """
    global access_token, expiry_time
    if expiry_time is None or datetime.now() > expiry_time:
        set_access_token()

@app.route("/get_items", methods=['GET'])
def get_items():
    """
    Returns the list of items
    """
    info = {
        "data": data,
        "members": members
        }
    return jsonify(info)

@app.route("/save_changes", methods=['POST'])
def save_changes():
    """
    Saves the changes to the backend
    """
    global data
    data = request.get_json()["data"]
    
    return "", 204

@app.route("/search_kroger", methods=['GET'])
def search_kroger():
    """
    Searches the Kroger API for the item
    """

    access_token = get_kroger_access_token()

    item = request.args.get('item')
    locationId = session.get('locationId')

    url = f"https://api.kroger.com/v1/products?filter.term={item}&filter.locationId={locationId}&filter.fulfillment=csp&filter.limit=5"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response = response.json()
        item_info = {}

        for item in response["data"]:
            item_info[item["productId"]] = item["description"]
        return item_info


@app.route("/get_locations", methods=['GET'])
def get_locations():
        """
        Gets the nearest locations for the specified zip code
        """

        access_token = get_kroger_access_token()

        zip_code = request.args.get('zip_code')

        url = f"https://api.kroger.com/v1/locations?filter.zipCode.near={zip_code}&filter.limit=5"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response = response.json()
            location_info = {}

            for location in response["data"]:
                location_info[location["locationId"]] = location["address"]["addressLine1"] + ", " + location["address"]["city"] + ", " + location["address"]["state"] + " " + location["address"]["zipCode"]
            return location_info
        else: 
            return None

if __name__ == "__main__":
    app.run(port=5000)