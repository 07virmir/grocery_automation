import os, base64, requests, datetime, json, math
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from splitwise import Splitwise
from splitwise.expense import Expense, ExpenseUser

def post_order_script(table, tax, savings):
    """
    Calulates the totals and posts the order to Splitwise
    """

    items_per_person = {"Viren": {}, "Rishi": {}, "Siddharth": {}, "Rohan": {}, "Christopher": {}}
    totals_per_person = {}

    for _, row in table.iterrows():

        item_cost = float(row["price"]) * int(row["quantity"])

        viren_included, rishi_included, sid_included, rohan_included, chris_included = row["Viren"], row["Rishi"], row["Siddharth"], row["Rohan"], row["Christopher"]
        boolean_list = [viren_included, rishi_included, sid_included, rohan_included, chris_included]

        split = sum([1 for name in boolean_list if name])

        amount = math.ceil((item_cost / split) * 100) / 100

        if viren_included:
            items_per_person["Viren"][row["name"]] = amount
        if rishi_included:
            items_per_person["Rishi"][row["name"]] = amount
        if sid_included:
            items_per_person["Siddharth"][row["name"]] = amount
        if rohan_included:
            items_per_person["Rohan"][row["name"]] = amount
        if chris_included:
            items_per_person["Christopher"][row["name"]] = amount

    for person in items_per_person:
        totals_per_person[person] = sum(items_per_person[person].values())

    total = sum(totals_per_person.values())

    for person in totals_per_person:
        tax_added = (totals_per_person[person] / total) * float(tax)
        savings_subtracted = (totals_per_person[person] / total) * float(savings)
        totals_per_person[person] += tax_added
        totals_per_person[person] -= savings_subtracted
        totals_per_person[person] = math.ceil(totals_per_person[person] * 100) / 100

    print("\n")
    for person in items_per_person:
        print(f"{person}: {items_per_person[person]}" + "\n")

    print(f"Totals: {totals_per_person}" + "\n")

    make_splitwise_request(totals_per_person)


def make_splitwise_request(totals_per_person: dict):
        """
        Makes a request to the Splitwise API to create a new expense
        """
        load_dotenv()
        s_obj = Splitwise(os.environ.get("SPLITWISE_CONSUMER_KEY"),os.environ.get("SPLITWISE_CONSUMER_SECRET"),api_key=os.environ.get("SPLITWISE_API_KEY"))
        user_ids = {"Viren": s_obj.getCurrentUser().getId()}
        friends = s_obj.getFriends()
        for friend in friends:
            name = friend.getFirstName()
            if name == "Rishi":
                user_ids["Rishi"] = friend.getId()
            elif name == "Siddharth":
                user_ids["Siddharth"] = friend.getId()
            elif name == "Rohan":
                user_ids["Rohan"] = friend.getId()
            elif name == "Christopher":
                user_ids["Christopher"] = friend.getId()
            
        for person in user_ids:
            if person == "Viren":
                continue
            expense = Expense()
            expense.setCost(totals_per_person[person])
            expense.setDescription("Groceries " + str(datetime.datetime.now().date()))

            requester = ExpenseUser()
            requester.setId(user_ids["Viren"])
            requester.setPaidShare(totals_per_person[person])
            requester.setOwedShare(0)

            payer = ExpenseUser()
            payer.setId(user_ids[person])
            payer.setPaidShare(0)
            payer.setOwedShare(totals_per_person[person])

            expense.addUser(requester)
            expense.addUser(payer)
            s_obj.createExpense(expense)

            print(f"Created expense for {person} for ${totals_per_person[person]}")


def get_kroger_access_token():
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
            return response.json()
        else:
            return None


def make_df(items, members):
    ''' Formats the data for streamlit to display 
    Args:
        items : list[{id: str, name: str, price: int, split_by: list[str]}]
        members: list[str]
    Returns: 
        pd.Dataframe: with item id as index column. Forces use of hide_index in st.data_editor
    '''
    additional_cols = 4
    member_to_idx = {name: i + additional_cols for i,
                     name in enumerate(members)}
    table = np.zeros(shape=(len(items), len(members) +
                     additional_cols), dtype=object)
    table[additional_cols:] = table[additional_cols:] != 0
    for i, item in enumerate(items):
        table[i][:4] = item['id'], item['name'], item['price'], item['quantity']
        for member in members:
            idx = member_to_idx[member]
            if member in item['split_by']:
                table[i][idx] = True
            else:
                table[i][idx] = False

    return pd.DataFrame(table, columns=['id', 'name', 'price', 'quantity'] + members)

def save_data(table, location_id):
    """
    Saves the data to the backend
    """

    data = []
    for i, (_, row) in enumerate(table.iterrows()):
        data.append({})
        data[i]['split_by'] = []
        for j, (val, col_name) in enumerate(zip(row, table.columns.tolist())):
            if j < 4:
                data[i][col_name] = val
            else:
                if val:
                    data[i]['split_by'].append(col_name)
    info = {"data": data, "locationId": location_id}
    headers = {"Content-Type": "application/json"}
    requests.post("http://127.0.0.1:8000/save_changes", data=json.dumps(info), headers=headers)
     