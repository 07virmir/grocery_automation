from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore
import requests

app = Flask(__name__)

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection('items').document('E9TdIqXvP936dlNmJBaO')
doc = doc_ref.get()

if __name__ == "__main__":
    app.run()