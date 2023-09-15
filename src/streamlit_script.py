import streamlit as st
from streamlit_extras.row import row
import requests, json
from utils import make_df, save_data, add_to_cart_script, post_order_script

items = requests.get("http://127.0.0.1:5000/get_items").json()
df = make_df(items["data"], items["members"])
title = st.markdown(body="<h1 style='text-align: center; color: white;'>Groceries</h1>", unsafe_allow_html=True)

row0 = row([1, 1, 1], gap="medium", vertical_align="bottom")
location = row0.text_input("Enter a zip code")
location_id = row0.text_input("Enter a location ID")
person = row0.selectbox("Who is editing?", options=["Viren", "Rishi", "Siddharth", "Rohan", "Christopher"])
if location and not location_id:
    params = {
        "zip_code": location
    }
    locations = requests.get(url="http://127.0.0.1:5000/get_locations", params=params).json()
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
    search = st.text_input("Enter an item")
    if search:
        params = {
            "item": search,
            "locationId": location_id
        }
        search_results = requests.get(url="http://127.0.0.1:5000/search_kroger", params=params).json()
        length = len(search_results)
        item_row1 = row(min(len(search_results), 3), vertical_align="center")
        length -= 3
        if length > 0:
            item_row2 = row(length, vertical_align="center")

        for idx, key in enumerate(search_results):
            item_html = f"""
                <div class="item" style="text-align: center;">
                    <img src ="{search_results[key]['image']}"/>
                    <p class="item-description">{search_results[key]['description']}</p>
                    <p class="item-price">${search_results[key]['price']} - {search_results[key]['size']}</p>
                    <p class="item-id">ID: {key}</p>
                </div>
                """
            if idx <= 2:
                item_row1.markdown(item_html, unsafe_allow_html=True)
            else:
                item_row2.markdown(item_html, unsafe_allow_html=True)

    table = st.data_editor(df, num_rows='dynamic', use_container_width=True, hide_index=True, column_config={
        "Viren": st.column_config.CheckboxColumn(disabled=False if person == 'Viren' else True, default=False),
        "Rishi": st.column_config.CheckboxColumn(disabled=False if person == 'Rishi' else True, default=False),
        "Siddharth": st.column_config.CheckboxColumn(disabled=False if person == 'Siddharth' else True, default=False),
        "Rohan": st.column_config.CheckboxColumn(disabled=False if person == 'Rohan' else True, default=False),
        "Christopher": st.column_config.CheckboxColumn(disabled=False if person == 'Christopher' else True, default=False)
    })

    row2 = row([3, 2, 2, 2], gap="medium", vertical_align="bottom")
    tax = row2.text_input("Tax")
    row2.button(label='Save Changes', on_click=save_data, args=(table,))
    row2.button(label='Add to Cart', on_click=add_to_cart_script, args=(table,))

    if tax:
        row2.button("To Splitwise", on_click=post_order_script, args=(table,tax,))


