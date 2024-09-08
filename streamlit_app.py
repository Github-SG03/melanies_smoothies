# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothiee :cup_with_straw:")
st.write(
   """
    Choose the fruits you want in your custom smoothiee!
   """
)

name_on_order = st.text_input('Name on smoothie:')
st.write('Name on smoothie will be', name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list = st.multiselect(
    'Choose upto five ingredients:',
    my_dataframe,
    max_selections=5
)
#st.write(ingredients_list)
#st.text(ingredients_list)

if ingredients_list:
    ingredients_string = ''
    
    # Concatenate the fruits with spaces between them
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
       # New section to display fruityvice nutrition information
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
    
    # Optionally strip the last space
    ingredients_string = ingredients_string.strip()

    #st.write(ingredients_string)

    my_insert_stmts = f"""insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string}','{name_on_order}')"""
    #st.write(my_insert_stmts)
    #st.stop()
    

    #st.write(my_insert_stmts)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmts).collect()
        st.success('Your Smoothie is ordered!', icon="✅")






      



        
