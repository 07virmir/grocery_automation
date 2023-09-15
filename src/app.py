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

@app.route("/refresh_token", methods=['POST'])
def init():
    """
    Initializes the token
    """
    global access_token, expiry_time
    if expiry_time is None or datetime.now() > expiry_time:
        set_access_token()
    return "", 204

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

    requests.post("http://127.0.0.1:5000/refresh_token")

    item = request.args.get('item')
    locationId = request.args.get('locationId')

    url = f"https://api.kroger.com/v1/products"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    params = {
            "filter.term": item,
            "filter.locationId": locationId,
            "filter.fulfillment": "csp",
            "filter.limit": 6
        }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response = response.json()
        item_info = {}

        for item in response["data"]:
            item_info[item["productId"]] = {}
            item_info[item["productId"]]["description"] = item["description"]
            item_info[item["productId"]]["price"] = min(item["items"][0]["price"]["regular"], item["items"][0]["price"]["promo"]) if item["items"][0]["price"]["promo"] != 0 else item["items"][0]["price"]["regular"]
            item_info[item["productId"]]["image"] = item["images"][0]["sizes"][2]["url"]
            item_info[item["productId"]]["size"] = item["items"][0]["size"]
        return jsonify(item_info)
    else:
        return None

@app.route("/get_locations", methods=['GET'])
def get_locations():
        """
        Gets the nearest locations for the specified zip code
        """

        requests.post("http://127.0.0.1:5000/refresh_token")

        zip_code = request.args.get('zip_code')

        url = f"https://api.kroger.com/v1/locations"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "filter.zipCode.near": zip_code,
            "filter.limit": 6
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response = response.json()
            location_info = {}

            for location in response["data"]:
                location_info[location["locationId"]] = {}
                location_info[location["locationId"]]["address"] = location["address"]["addressLine1"] + ", " + location["address"]["city"] + ", " + location["address"]["state"] + " " + location["address"]["zipCode"]
                location_info[location["locationId"]]["name"] = location["name"]
            return jsonify(location_info)
        else: 
            return None

if __name__ == "__main__":
    app.run(port=5000, debug=True)