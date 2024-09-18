import streamlit as st
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

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose upto five ingredients:',
    pd_df['FRUIT_NAME'],  # Show only fruit names for selection
    max_selections=5
)

if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)
    ingredients_string = ' '.join(ingredients_list)  # Join fruits with a space

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')

        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            fruityvice_response.raise_for_status()  # Raise an error for bad responses
            fruityvice_data = fruityvice_response.json()

            if isinstance(fruityvice_data, dict):
                # Check if the response contains valid data
                fv_df = pd.DataFrame([fruityvice_data])  # Convert single dictionary to a DataFrame
            else:
                fv_df = pd.DataFrame(fruityvice_data)  # If it's a list of dictionaries, convert it to a DataFrame

            st.dataframe(fv_df, use_container_width=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")
        except ValueError as ve:
            st.error(f"Invalid data structure from API for {fruit_chosen}: {ve}")
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        insert_query = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values (%s, %s)
        """
        try:
            session.sql(insert_query, (ingredients_string, name_on_order)).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Failed to submit your order: {e}")
