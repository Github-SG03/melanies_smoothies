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
st.write('Name on smoothie will be', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark dataframe to pandas dataframe
pd_df = my_dataframe.to_pandas()

# Display the dataframe for debugging
st.dataframe(pd_df, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to five ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Convert to a list of fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Check if the fruit exists in the dataframe
        if fruit_chosen in pd_df['FRUIT_NAME'].values:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for', fruit_chosen, 'is', search_on, '.')
        else:
            st.write('The fruit', fruit_chosen, 'is not in the database.')
            search_on = 'Not Available'
        
        # Display fruityvice nutrition information
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.subheader(fruit_chosen + 'Nutrition Information')
            st.json(fv_data)
        else:
            st.write('No nutrition information found for', fruit_chosen)
    
    # Optionally strip the last space
    ingredients_string = ingredients_string.strip()

    my_insert_stmts = f"""insert into smoothies.public.orders(ingredients, name_on_order)
            values ('{ingredients_string}','{name_on_order}')"""
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmts).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
