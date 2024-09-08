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
st.write('Name on smoothie will be', name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve the DataFrame from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Create the multiselect widget
ingredients_list = st.multiselect(
    'Choose up to five ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use list of fruit names for multiselect
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the "Search On" value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Display fruityvice nutrition information
        st.subheader(fruit_chosen + 'Nutrition Information')

        # Handle API request and potential errors
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
            fruityvice_response.raise_for_status()  # Raise an exception for HTTP errors
            fv_data = fruityvice_response.json()
            
            if isinstance(fv_data, dict):  # Check if the response is a dictionary
                fv_df = pd.DataFrame([fv_data])  # Convert the dictionary to a DataFrame
            else:
                fv_df = pd.DataFrame(fv_data)  # Convert the list to a DataFrame
            
            st.dataframe(data=fv_df, use_container_width=True)
        
        except requests.RequestException as e:
            st.error(f"An error occurred while fetching nutrition information for {fruit_chosen}: {e}")
        except ValueError as e:
            st.error(f"Error processing the nutrition information for {fruit_chosen}: {e}")
    
    # Optionally strip the last space
    ingredients_string = ingredients_string.strip()

    my_insert_stmts = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')"""

    # Submit order button
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmts).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while placing your order: {e}")
