import streamlit as st
import requests, json
from utils import make_df, save_data, add_to_cart_script, post_order_script

items = requests.get("http://127.0.0.1:5000/get_items").json()
df = make_df(items["data"], items["members"])
title = st.markdown(body="<h1 style='text-align: center; color: white;'>Groceries</h1>", unsafe_allow_html=True)
table = st.data_editor(df, num_rows='dynamic', use_container_width=True, hide_index=True, column_config={
    "Viren": st.column_config.CheckboxColumn(default=False),
    "Rishi": st.column_config.CheckboxColumn(default=False),
    "Siddharth": st.column_config.CheckboxColumn(default=False),
    "Rohan": st.column_config.CheckboxColumn(default=False),
    "Christopher": st.column_config.CheckboxColumn(default=False)
})

save = st.button(label='Save Changes', on_click=save_data, args=(table,))
add_to_cart = st.button(label='Add to Cart', on_click=add_to_cart_script, args=(table,))

tax = st.text_input("Tax")

if tax:
    second_button = st.button("Calculate Totals and Add to Splitwise", on_click=post_order_script, args=(table,tax,))


