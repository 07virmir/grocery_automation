import streamlit as st
from streamlit_extras.row import row
import requests, json
from utils import make_df, save_data, add_to_cart_script, post_order_script

items = requests.get("http://127.0.0.1:5000/get_items").json()
df = make_df(items["data"], items["members"])
title = st.markdown(body="<h1 style='text-align: center; color: white;'>Groceries</h1>", unsafe_allow_html=True)

row0 = row([4, 1], gap="medium", vertical_align="bottom")
location = row0.text_input("Enter a zip code")
if location:
    location_button = row0.button("Search")
    if location_button:
        st.text_input("Selected Location:", key="location-input")
        params = {
            "zip_code": location
        }
        locations = requests.get(url="http://127.0.0.1:5000/get_locations", params=params).json()
        row1 = row(len(locations), vertical_align="center")
        for key in locations:
            box_html = f"""
            <div class="box" style="text-align: center;">
                <h5 class="box-title">{locations[key]['name']}</h2>
                <p class="box-address">{locations[key]['address']}</p>
                <button class="box-button" onclick="removeBoxAndSetLocation({locations[key]['name']})">Select</button>
            </div>
            <script>
                function removeBoxAndSetLocation(selectedLocation) {{
                    var boxes = document.querySelectorAll(".box");
                    for (var i = 0; i < boxes.length; i++) {{
                        boxes[i].remove();
                    }}
                    document.querySelector("#location-input input").value = selectedLocation;
                }}
            </script>
            """
            row1.markdown(box_html, unsafe_allow_html=True)

# search = st.text_input("Enter an item")
# if search:
#     search_button = st.button("Search")
#     if search_button:
#         data = {
#             "item": search,
#             "locationId": locationId
#         }
#         search_results = requests.get(url="http://127.0.0.1:5000/search_kroger", data=data).json()
#         st.markdown("""
#         <div class="custom-slider">
#             <!-- Add your components here: images, titles, prices, etc. -->
#         </div>
#         """, unsafe_allow_html=True)

table = st.data_editor(df, num_rows='dynamic', use_container_width=True, hide_index=True, column_config={
    "Viren": st.column_config.CheckboxColumn(default=False),
    "Rishi": st.column_config.CheckboxColumn(default=False),
    "Siddharth": st.column_config.CheckboxColumn(default=False),
    "Rohan": st.column_config.CheckboxColumn(default=False),
    "Christopher": st.column_config.CheckboxColumn(default=False)
})

row2 = row([3, 2, 2, 2], gap="medium", vertical_align="bottom")
tax = row2.text_input("Tax")
row2.button(label='Save Changes', on_click=save_data, args=(table,))
row2.button(label='Add to Cart', on_click=add_to_cart_script, args=(table,))

if tax:
    row2.button("To Splitwise", on_click=post_order_script, args=(table,tax,))


