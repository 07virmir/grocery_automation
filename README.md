# Grocery Automation
Personal Project to automate grocery ordering for your nearby Kroger.

App works by allowing users to collaboratively work on a grocery list. Users can set a location for a nearby Kroger by entering their zip code. Then, users can search for items with a limit parameter for the output and add them with a click of a button. Users can also select the quantity they want and split specific items amongst each other. Users can visualize their total expected cost at any point. Once final changes are made, the buyer can automatically add all items to their Kroger cart by signing into their account. With Splitwise integration, the buyer can also enter the total fees from the order and the per-person amounts will automatically be added as expenses on Splitwise.

## Tech Stack
- Streamlit
- Flask

## APIs Used
- Kroger API for location-based store selection, item search, automatic store selection
- Splitwise API for expense tracking

## Deployment
- Hosted the frontend using Streamlit Community Cloud
- Hosted the backend using Azure App Service and Key Vault

## Instructions
To run the frontend, use "streamlit run frontend.py".  
To run the backend, use "python3 app.py".

To have multiple users edit concurrently, consider deploying or hosting an ngrok tunnel for the frontend.
