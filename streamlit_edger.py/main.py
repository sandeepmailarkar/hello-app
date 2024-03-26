import streamlit as st
import os
import json
import snowflake.connector
from streamlit_extras.switch_page_button import switch_page
 
st.set_page_config(initial_sidebar_state="collapsed")
 
def main():
   
    custom_css = """
    <style>
        .stButton > button {
            padding:   10px   30px;
            margin-right:   20px;
            margin-left:   50px;
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
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>LOGIN </h1>", unsafe_allow_html=True)
 
    # Login form
    with st.form("Submission Form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        cols = st.columns(2)
        if cols[0].form_submit_button("Login"):
            if authenticate_user(username, password):
                st.success("Logged in successfully!")
                st.session_state['username'] = username # Store the username in the session state
                switch_page("Create_Form")
            else:
                st.error("Invalid username or password")
 
    # Create a row for the buttons
       
        # Add a registration button next to the login button
        if cols[1].form_submit_button("Register"):
            switch_page("Register")
 
# Authenticate user against Snowflake database
file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), 'snowflake_credentials.json')
with open(file_path, 'r') as f:
    snowflake_config = json.load(f)
conn = snowflake.connector.connect(**snowflake_config)
cur = conn.cursor()
 
def authenticate_user(username, password):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM login WHERE username='{username}' AND password='{password}'")
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True
    else:
        return False
 
# Run the Streamlit app
if __name__ == "__main__":
    main()