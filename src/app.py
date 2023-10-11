from flask import Flask, jsonify, request, redirect, url_for
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import requests, base64, os
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore


app = Flask(__name__)
CORS(app)
app.secret_key = 'test'
load_dotenv()

cred = credentials.Certificate("../credentials/firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

oauth = OAuth(app)
oauth.register(
    name='kroger',
    client_id=os.environ.get("KROGER_CLIENT_ID"),
    client_secret=os.environ.get("KROGER_CLIENT_SECRET"),
    access_token_url='https://api.kroger.com/v1/connect/oauth2/token',
    access_token_params=None,
    authorize_url='https://api.kroger.com/v1/connect/oauth2/authorize',
    authorize_params=None,
    api_base_url='https://api.kroger.com/v1/',
    client_kwargs={'scope': 'product.compact profile.compact cart.basic:write'}
)

access_token = None
add_to_cart_token = None
expiry_time = None

def set_access_token():
    global access_token, expiry_time
    if expiry_time is None or datetime.now() > expiry_time:
        api_result = get_kroger_access_token()
        if api_result is not None:
            access_token = api_result["access_token"]
            expiry_time = datetime.now() + timedelta(seconds=api_result["expires_in"])

def add_to_cart_script():
    """
    Adds the items to the cart
    """
    items = {"items": []}
    data = list(db.collection("grocery_data").document("table_data").get().to_dict().values())
    for item in data:
        items["items"].append({
            "quantity": int(item["quantity"]),
            "upc": item["id"],
            "modality": "PICKUP"
        })

    url = f"https://api.kroger.com/v1/cart/add"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {add_to_cart_token}"
    }
    requests.put(url=url, headers=headers, json=items)

def get_kroger_access_token():
    """
    Gets the access token for the Kroger API
    """

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
        return response.json()
    else:
        return None

@app.route("/")
def home():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.kroger.authorize_redirect(redirect_uri=redirect_uri)

@app.route("/authorize")
def authorize():
    global add_to_cart_token
    add_to_cart_token = oauth.kroger.authorize_access_token()["access_token"]
    add_to_cart_script()
    return "Order added to cart"

@app.route("/get_items", methods=['GET'])
def get_items():
    """
    Returns the list of items
    """
    data = list(db.collection("grocery_data").document("table_data").get().to_dict().values())
    locationId = db.collection("grocery_data").document("location_id").get().to_dict()
    if not locationId:
        locationId = ""
    else:
        locationId = locationId["locationId"]
    members = ["Viren", "Rishi", "Siddharth", "Rohan", "Christopher"]

    info = {
        "data": data,
        "members": members,
        "locationId": locationId
        }
    return jsonify(info)

@app.route("/save_changes", methods=['POST'])
def save_changes():
    """
    Saves the changes to the backend
    """
    keys = set()
    for item in request.get_json()["data"]:
        db.collection("grocery_data").document("table_data").update({item["id"]: item})
        keys.add(item["id"])
    for key in db.collection("grocery_data").document("table_data").get().to_dict().keys():
        if key not in keys:
            db.collection("grocery_data").document("table_data").update({key: firestore.DELETE_FIELD})
    db.collection("grocery_data").document("location_id").update({"locationId": request.get_json()["locationId"]})
    
    return "", 204

@app.route("/search_kroger", methods=['GET'])
def search_kroger():
    """
    Searches the Kroger API for the item
    """

    set_access_token()

    if access_token is None:
            return "", 204

    item = request.args.get('item')
    locationId = request.args.get('locationId')
    limit = request.args.get('limit')

    url = f"https://api.kroger.com/v1/products"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    params = {
            "filter.term": item,
            "filter.locationId": locationId,
            "filter.fulfillment": "csp",
            "filter.limit": limit
        }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response = response.json()
        item_info = {}

        for idx, item in enumerate(response["data"]):
            item_info[idx] = {}
            item_info[idx]["id"] = item["upc"]
            item_info[idx]["description"] = item["description"]
            item_info[idx]["price"] = min(item["items"][0]["price"]["regular"], item["items"][0]["price"]["promo"]) if item["items"][0]["price"]["promo"] != 0 else item["items"][0]["price"]["regular"]
            item_info[idx]["image"] = item["images"][0]["sizes"][2]["url"]
            item_info[idx]["size"] = item["items"][0]["size"]
        return jsonify(item_info)
    else:
        return "", response.status_code

@app.route("/get_locations", methods=['GET'])
def get_locations():
        """
        Gets the nearest locations for the specified zip code
        """

        set_access_token()

        if access_token is None:
            return "", 204

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
            return "", response.status_code

if __name__ == "__main__":
    app.run(port=8000, debug=True)