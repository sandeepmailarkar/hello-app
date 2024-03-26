import streamlit as st
import pandas as pd
import snowflake.connector
import json
import os
from streamlit_extras.switch_page_button import switch_page
from session_state import get_session_state
from session_state_manager import get_session_id
from session_state_manager import save_session_state
from session_state_manager import load_session_state


# Custom CSS for Streamlit (if any)
custom_css = """
<style>
    /* Your custom CSS here */
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>EDIT MAPPING</h1>", unsafe_allow_html=True)

# Custom CSS for Streamlit
custom_css = """
<style>
    .stButton > button {
        padding:   10px   30px;
        margin-right:   5px;
        margin-left:   5px;
        border: none;
        cursor: pointer;
        font-size:   16px;
        background-color: #4CAF50; /* Default background color */
        color: white; /* White text */
        border-radius:   5px; /* Rounded corners */
    }
    .stButton > button[type="submit"]:nth-child(1) {
        background-color: #4CAF50; /* Green background */
    }
    .stButton > button[type="submit"]:nth-child(2) {
        background-color: #008CBA; /* Blue background */
    }
    .stButton > button:hover {
        opacity:   0.8;
    }
    .stButton > button:disabled {
        background-color: #cccccc; /* Gray background for disabled buttons */
    }
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)


def logout():
    st.session_state.clear()
    switch_page("main")
    if st.button("Logout"):
        logout()


# Function to connect to Snowflake
def connect_to_snowflake():
    # Get the absolute path to the snowflake_credentials.json file
    file_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        "snowflake_credentials.json",
    )

    # Load Snowflake configuration from JSON file
    with open(file_path, "r") as f:
        snowflake_config = json.load(f)

    try:
        # Connect to Snowflake using the loaded credentials
        conn = snowflake.connector.connect(**snowflake_config)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
        return None, None


def app():

    # Input company ID
    company_id = st.session_state["username"]

    if company_id:
        # Connect to Snowflake
        conn, cursor = connect_to_snowflake()

        if conn is not None and cursor is not None:
            try:
                # Retrieve JSON data from Snowflake
                sql = f"""
                SELECT JSON_DATA
                FROM JSON_FILE_1
                WHERE COMPANY_ID = '{company_id}'
                """
                cursor.execute(sql)
                result = cursor.fetchone()

                if result:
                    # Parse JSON data into a pandas DataFrame
                    json_data = result[0]
                    df = pd.read_json(json_data, orient="records")

                    # Allow the user to edit the DataFrame
                    edited_data = st.data_editor(df)
                    col1, col2 = st.columns([1, 1])

                    with col2:

                        if st.button("SAVE"):
                            # Validate the edited data
                            if edited_data.isnull().values.any():
                                st.error(
                                    "All fields must be filled and contain only letters and spaces. No numbers or special characters are allowed."
                                )
                            else:
                                # Update the JSON data in Snowflake
                                updated_json = edited_data.to_json(orient="records")
                                update_sql = f"""
                                UPDATE JSON_FILE_1
                                SET JSON_DATA = PARSE_JSON(%s)
                                WHERE COMPANY_ID = '{company_id}'
                                """
                                cursor.execute(update_sql, (updated_json,))

                                # Commit the changes
                                conn.commit()
                                st.success("Changes saved successfully!")
                else:
                    st.warning("No data found for the given COMPANY_ID.")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                if st.button("FILER INFORMATION"):
                    switch_page("filerInfo")
    else:
        st.info("Please enter a COMPANY_ID to load data.")


if __name__ == "__main__":
    app()
