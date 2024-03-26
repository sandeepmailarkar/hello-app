import streamlit as st
import os
import json
import snowflake.connector
from streamlit_extras.switch_page_button import switch_page

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

# Function to register a new user
def register_user(username, password):
    # Load Snowflake configuration
    file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'snowflake_credentials.json')
    with open(file_path, 'r') as f:
        snowflake_config = json.load(f)
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()

    try:
        cursor.execute(f"INSERT INTO login (username, password) VALUES ('{username}', '{password}')")
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(e)
        cursor.close()
        return False

# Create a Streamlit registration page
def registration_page():
    st.markdown("<h1 style='text-align: center;'>REGISTER</h1>", unsafe_allow_html=True)

    with st.form("Registration Form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if password == confirm_password:
                if register_user(username, password):
                    st.success("Registered successfully!")
                    # Optionally, redirect the user to the login page after successful registration
                    switch_page("main")
                else:
                    st.error("Registration failed. Please try again.")
            else:
                st.error("Passwords do not match.")

if __name__ == "__main__":
    registration_page()




    import streamlit as st
import os
import json
import snowflake.connector
from streamlit_extras.switch_page_button import switch_page

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


# Function to register a new user
def register_user(username, password):
    # Load Snowflake configuration
    file_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        "snowflake_credentials.json",
    )
    with open(file_path, "r") as f:
        snowflake_config = json.load(f)
    conn = snowflake.connector.connect(**snowflake_config)
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"INSERT INTO login (username, password) VALUES ('{username}', '{password}')"
        )
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(e)
        cursor.close()
        return False


# Create a Streamlit registration page
def registration_page():
    st.markdown("<h1 style='text-align: center;'>REGISTER</h1>", unsafe_allow_html=True)

    with st.form("Registration Form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if password == confirm_password:
                if register_user(username, password):
                    st.success("Registered successfully!")
                    # Optionally, redirect the user to the login page after successful registration
                    switch_page("main")
                else:
                    st.error("Registration failed. Please try again.")
            else:
                st.error("Passwords do not match.")


if __name__ == "__main__":
    registration_page()

