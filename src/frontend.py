import streamlit as st
from streamlit_extras.row import row
import requests
from utils import make_df, save_data, post_order_script, authenticate, add_row

items = requests.get("http://127.0.0.1:8000/get_items").json()
df = make_df(items["data"], items["members"])
title = st.markdown(body="<h1 style='text-align: center; color: white;'>Groceries</h1>", unsafe_allow_html=True)

row1col1, row1col2, row1col3 = st.columns(3)
with row1col1:
    location = st.text_input("Enter a zip code")
with row1col2:
    location_id = st.text_input("Enter a location ID", value=items["locationId"])
with row1col3:
    person = st.selectbox("Who is editing?", options=["Viren", "Rishi", "Siddharth", "Rohan", "Christopher"])

if location and not location_id:
    params = {
        "zip_code": location
    }
    locations = requests.get(url="http://127.0.0.1:8000/get_locations", params=params).json()
    length = len(locations)
    location_row1 = row(min(len(locations), 3), vertical_align="center")
    length -= 3
    if length > 0:
        location_row2 = row(length, vertical_align="center")
    for idx, key in enumerate(locations):
        box_html = f"""
        <div class="box" style="text-align: center;">
            <h5 class="box-title">{locations[key]['name']}</h2>
            <p class="box-address">{locations[key]['address']}</p>
            <p class="box-id">ID: {key}</p>
        </div>
        """
        if idx <= 2:
            location_row1.markdown(box_html, unsafe_allow_html=True)
        else:
            location_row2.markdown(box_html, unsafe_allow_html=True)

if location_id:
    row2col1, row2col2 = st.columns([3, 1], gap="medium")

    with row2col1:
        search = st.text_input("Enter an item")
    with row2col2:
        limit = st.number_input("Limit", min_value=1, max_value=12, value=6)
    if search:
        params = {
            "item": search,
            "locationId": location_id,
            "limit": limit
        }
        search_results = requests.get(url="http://127.0.0.1:8000/search_kroger", params=params).json()

        length = len(search_results)
        numRows = length // 3

        for i in range(numRows):
            item_row = row(3, vertical_align="center")
            buttons = st.columns([1, 2, 1, 1, 2, 1, 1, 2, 1])
            for j in range(3):
                loc = str(3 * i + j)
                id = search_results[loc]['id']
                price = search_results[loc]['price']
                description = search_results[loc]['description']
                size = search_results[loc]['size']
                item_html = f"""
                    <div class="item" style="text-align: center;">
                        <img src ="{search_results[loc]['image']}"/>
                        <p class="item-description">{description}</p>
                        <p class="item-price">${price} - {size}</p>
                    </div>
                    """
                item_row.markdown(item_html, unsafe_allow_html=True)
                with buttons[j * 3 + 1]:
                    st.button(f"Add Item {3 * i + j + 1}", on_click=add_row, args=(df,location_id,id,description,size,price,person,))
        if length % 3 > 0:
            item_row = row(length % 3, vertical_align="center")
            buttons = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 1])
            for i in range(length % 3):
                loc = str(3 * numRows + i)
                id = search_results[loc]['id']
                price = search_results[loc]['price']
                description = search_results[loc]['description']
                size = search_results[loc]['size']
                item_html = f"""
                    <div class="item" style="text-align: center;">
                        <img src ="{search_results[loc]['image']}"/>
                        <p class="item-description">{description}</p>
                        <p class="item-price">${price} - {size}</p>
                    </div>
                    """
                item_row.markdown(item_html, unsafe_allow_html=True)
                if length % 3 == 1:
                    with buttons[4]:
                        st.button(f"Add Item {3 * numRows + i + 1}", on_click=add_row, args=(df,location_id,id,description,size,price,person,))
                else:
                    with buttons[i * 4 + 2]:
                        st.button(f"Add Item {3 * numRows + i + 1}", on_click=add_row, args=(df,location_id,id,description,size,price,person,))

    table = st.data_editor(df, num_rows='dynamic', use_container_width=True, hide_index=True, column_config={
        "price": st.column_config.NumberColumn(format="%.2f"),
        "quantity": st.column_config.NumberColumn(default=1, min_value=1),
        "Viren": st.column_config.CheckboxColumn(disabled=False if person == 'Viren' else True, default=False),
        "Rishi": st.column_config.CheckboxColumn(disabled=False if person == 'Rishi' else True, default=False),
        "Siddharth": st.column_config.CheckboxColumn(disabled=False if person == 'Siddharth' else True, default=False),
        "Rohan": st.column_config.CheckboxColumn(disabled=False if person == 'Rohan' else True, default=False),
        "Christopher": st.column_config.CheckboxColumn(disabled=False if person == 'Christopher' else True, default=False)
    })

    row2 = row([6, 6, 6, 5, 5], gap="small", vertical_align="bottom")
    row2.button(label='Save Changes', on_click=save_data, args=(table,location_id,))

    if person == 'Viren':
        fees = row2.text_input("Fees")
        savings = row2.text_input("Savings")
        row2.button(label='Add to Cart', on_click=authenticate)

        if fees and savings:
            row2.button("To Splitwise", on_click=post_order_script, args=(table,fees,savings,True,))
    else:
        show_total = row2.button(label='Show Totals')
        if show_total:
            totals = post_order_script(table,0,0,False)
            st.write(totals)