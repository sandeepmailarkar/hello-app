import streamlit as st
import json
from snowflake.connector import connect
from streamlit_extras.switch_page_button import switch_page
import os
import snowflake.connector
from session_state import get_session_state


# Get the absolute path to the snowflake_credentials.json file
file_path = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "snowflake_credentials.json",
)

# Load Snowflake configuration from JSON file
with open(file_path, "r") as f:
    snowflake_config = json.load(f)

# Connect to Snowflake using the loaded credentials
conn = snowflake.connector.connect(**snowflake_config)
cur = conn.cursor()


# Function to fetch JSON data for a given COMPANY_ID
def fetch_json_data(COMPANY_ID, cur):
    cur.execute(
        """
        SELECT JSON_DATA
        FROM JSON_FILE_1
        WHERE COMPANY_ID = %s
    """,
        (COMPANY_ID,),
    )
    json_data_record = cur.fetchone()

    if json_data_record:
        json_data = json.loads(json_data_record[0])
        return json_data
    else:
        return None


# Main Streamlit app
def app():
    # Initialize the session state
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

    if "session_state" not in st.session_state:
        st.session_state["session_state"] = {}

    COMPANY_ID = st.session_state["username"]

    # Center the title using Markdown syntax
    st.markdown(
        "<h1 style='text-align: center;'>CREATE FORM </h1>", unsafe_allow_html=True
    )

    # Create a two-column layout
    col1, col2 = st.columns([1, 3])

    # Add components to the left column
    with col1:
        st.write("Submission Type :")
        st.write("Report Date :")
        st.write("Deadline Date :")
        st.write("Ticker or Other Identifier for Fund :")
        st.write("Additional Description For Fund :")

    # Add components to the right column
    with col2:
        submission_type = st.selectbox(
            "",
            ["", "13F", "13F-HR/A", "3F-CTR", "13F-CTR/A", "13F-NT", "13F-NT/A", ""],
            label_visibility="collapsed",
        )
        report_date = st.date_input(
            "Report Date",
            value=None,
            min_value=None,
            max_value=None,
            key="report_date",
            label_visibility="collapsed",
        )
        deadline_date = st.date_input(
            "Deadline Date",
            value=None,
            min_value=None,
            max_value=None,
            key="deadline_date",
            label_visibility="collapsed",
        )
        ticker = st.text_input("Ticker", key="ticker")
        description = st.text_input("Description", key="description")

    # Add submit button
    submit_button = st.button("Submit")

    # Handle submit action
    if submit_button:

        # Store the submission type in the session state
        state = get_session_state()
        state.submission_type = submission_type

        conn = snowflake.connector.connect(**snowflake_config)
        cur = conn.cursor()

        try:
            # Check if COMPANY_ID exists in the database and fetch JSON data
            json_data = fetch_json_data(COMPANY_ID, cur)

            if json_data is not None:
                st.success("Form created successfully!")
                switch_page("filerInfo")
            else:
                st.error("Mapping not found.")
                switch_page("Mapping")

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            cur.close()
            conn.close()


if __name__ == "__main__":
    app()
