# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom smoothie!
    """
)
name_on_order = st.text_input('Name on smoothie:')
st.write('Name on smoothie will be:', name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose upto five ingredients:',
    my_dataframe,
    max_selections=5

)
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    #st.write(ingredients_string)
    
    my_insert_stmts = f"""insert into smoothies.public.orders(ingredients,name_on_order)
           values ('{ingredients_string}','{name_on_order}')"""
    time_to_insert = st.button('Submit Order')
    
    #st.write(my_insert_stmts)
    #st.stop()
    
    if time_to_insert:
        session.sql(my_insert_stmts).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
