# Grocery Automation
Personal Project to automate grocery ordering for your nearby Kroger.

App works by integrating Streamlit with Flask and allows users to collaboratively work on a grocery list. Users can set a location for a nearby Kroger by entering their zip code. Item searching is also accomplished by leveraging the Kroger API. Once final changes are made, the buyer can automatically add all items to their Kroger cart by signing into their account. With Splitwise integration, the buyer can also enter the total fees and savings from the order and calculate a per person cost. The amounts will be requested to each person on Splitwise.

To run the frontend, use "streamlit run frontend.py".
To run the backend, use "python3 app.py".

To have multiple users edit concurrently, consider deploying or hosting an ngrok tunnel for the frontend.
