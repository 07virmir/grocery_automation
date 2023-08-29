from flask import Flask, request, session
import firebase_admin, requests, os
from firebase_admin import credentials, firestore
from src.utils import get_access_token

app = Flask(__name__)

credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'firebase_credentials.json')
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def initialize():
    session['token'] = get_access_token()

@app.route("/load_data", methods=['GET'])
def load_data():
    """
    Loads the data from the database
    """

    doc_ref = db.collection('items').document('E9TdIqXvP936dlNmJBaO')
    doc = doc_ref.get()

@app.route("/update_data", methods=['POST'])
def update_data():
    """
    Updates the data in the database
    """

    doc_ref = db.collection('items').document('E9TdIqXvP936dlNmJBaO')
    doc = doc_ref.get()

    data = doc.to_dict()

    data['items']['bread'] = 1

    doc_ref.set(data)

@app.route("/search_kroger", methods=['GET'])
def search_kroger():
    """
    Searches the Kroger API for the item
    """

    access_token = get_access_token()

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

        access_token = get_access_token()

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

@app.route("/update_location", methods=['POST'])
def update_location():
        """
        Updates the location in the database
        """

        locationId = request.form.get('locationId')
        address = request.form.get('address')

        session['locationId'] = locationId

        doc_ref = db.collection('items').document('location')
        doc = doc_ref.get()

        data = doc.to_dict()

        data['locationInfo']['id'] = locationId
        data['locationInfo']['address'] = address

        doc_ref.set(data)

if __name__ == "__main__":
    app.run()