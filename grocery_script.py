import gspread
from oauth2client.service_account import ServiceAccountCredentials
from splitwise import Splitwise
from splitwise.expense import Expense, ExpenseUser
import math, datetime, os
from dotenv import load_dotenv

def calculate_totals():
    """
    Calculates the total amount each person owes for the groceries
    """

    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('sheets_credentials.json', scope)
    client = gspread.authorize(credentials)

    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1pSb1irU-GRNh8PEHjCbcgc3bfW_WjxRm5XmYZ-bSdpI/edit#gid=0')
    worksheet = sheet.get_worksheet(0)

    items_per_person = {"Viren": {}, "Rishi": {}, "Siddharth": {}, "Rohan": {}, "Christopher": {}}
    totals_per_person = {}

    row_idx = 2

    while worksheet.acell(f"A{row_idx}").value is not None:

        item_cost = float(worksheet.acell(f"H{row_idx}").value)

        viren_included = worksheet.acell(f"B{row_idx}").value if worksheet.acell(f"B{row_idx}").value is not None else 0
        rishi_included = worksheet.acell(f"C{row_idx}").value if worksheet.acell(f"C{row_idx}").value is not None else 0
        sid_included = worksheet.acell(f"D{row_idx}").value if worksheet.acell(f"D{row_idx}").value is not None else 0
        rohan_included = worksheet.acell(f"E{row_idx}").value if worksheet.acell(f"E{row_idx}").value is not None else 0
        chris_included = worksheet.acell(f"F{row_idx}").value if worksheet.acell(f"F{row_idx}").value is not None else 0
        
        split = sum([int(viren_included), int(rishi_included), int(sid_included), int(rohan_included), int(chris_included)])

        amount = math.ceil((item_cost / split) * 100) / 100

        if viren_included:
            items_per_person["Viren"][worksheet.acell(f"A{row_idx}").value] = amount
        if rishi_included:
            items_per_person["Rishi"][worksheet.acell(f"A{row_idx}").value] = amount
        if sid_included:
            items_per_person["Siddharth"][worksheet.acell(f"A{row_idx}").value] = amount
        if rohan_included:
            items_per_person["Rohan"][worksheet.acell(f"A{row_idx}").value] = amount
        if chris_included:
            items_per_person["Christopher"][worksheet.acell(f"A{row_idx}").value] = amount

        row_idx += 1

    tax = float(worksheet.acell("I2").value)

    for person in items_per_person:
        totals_per_person[person] = sum(items_per_person[person].values())

    total = sum(totals_per_person.values())

    for person in totals_per_person:
        tax_added = (totals_per_person[person] / total) * tax
        totals_per_person[person] += tax_added
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
        s_obj = Splitwise(os.environ.get("CONSUMER_KEY"),os.environ.get("CONSUMER_SECRET"),api_key=os.environ.get("API_KEY"))
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
        
        print("\n")

if __name__ == "__main__":
    calculate_totals()