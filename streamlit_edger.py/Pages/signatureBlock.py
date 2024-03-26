import streamlit as st
import pandas as pd
import snowflake.connector
import json
from streamlit_extras.switch_page_button import switch_page
from session_state import get_session_state
import json
from streamlit_extras.switch_page_button import switch_page
from session_state_manager import get_session_id
from session_state_manager import save_session_state
from session_state_manager import load_session_state
from session_state import get_session_state
import os
from cryptography.fernet import Fernet
import base64

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

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

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


# Function to fetch JSON data from Snowflake
def fetch_json_data(COMPANY_ID):
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
        raise ValueError("No JSON data found for the given COMPANY_ID.")


# Function to construct the query using the JSON data and Filer_Cik
def construct_query(json_data, Filer_Cik):
    # Extract the database, schema, and table names from the JSON data
    database = json_data[0]["Database"].strip()
    schema = json_data[0]["Schema"].strip()
    table = json_data[0]["Table"].strip()
    columns = ", ".join(
        [f'"{column_info["Column"].strip()}"' for column_info in json_data]
    )

    # Initialize the base query components
    base_query = f"SELECT {columns} FROM {database}.{schema}.{table}"

    # Construct the WHERE clause using the Filer_Cik provided by the user
    where_clause = f" WHERE FILER_CIK = '{Filer_Cik}'"

    full_query = base_query + where_clause

    return full_query


file_path01 = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "Client_Shared_creds.json",
)


with open(file_path01, "r") as f:

    snowflake_config01 = json.load(f)

conn01 = snowflake.connector.connect(**snowflake_config01)

cur01 = conn01.cursor()


def execute_dynamic_query(sql_query):

    try:

        cur01.execute(sql_query)

        result = cur01.fetchall()

        if result:

            df = pd.DataFrame(result, columns=[desc[0] for desc in cur01.description])

            return df

        else:

            return pd.DataFrame()

    except Exception as e:

        return pd.DataFrame()


# Function to create a form with dynamic fields
def create_form(form_fields_list, form_fields_data):
    for sg_field_name, field_type, field_options in form_fields_list:
        if sg_field_name in form_fields_data:
            if field_type == "text_input":
                st.text_input(
                    sg_field_name, value=form_fields_data[sg_field_name], disabled=True
                )
        else:
            st.warning(f"Field '{sg_field_name}' not found in the data.")
            st.text_input(
                sg_field_name, value="", disabled=True, key=f"{sg_field_name}"
            )


def encrypt_document(document):
    # Generate a key for encryption
    key = Fernet.generate_key()
    # Initialize Fernet with the key
    fernet = Fernet(key)
    # Encrypt the document
    encrypted_document = fernet.encrypt(document)  # Directly use the bytes object
    # Encode the encrypted document to base64
    encoded_document = base64.b64encode(encrypted_document).decode("utf-8")
    return encoded_document, key


# Main form selection function
def form_Selection(form_fields_list, form_fields_data):
    st.markdown(
        "<h1 style='text-align: center;'> SIGNATURE </h1>", unsafe_allow_html=True
    )
    state = get_session_state()
    submission_type = state.submission_type if hasattr(state, "submission_type") else ""

    with st.form("13F_Form"):
        # Display the submission_type in a non-editable text input
        st.text_input("Submission Type", value=submission_type, disabled=True)
        filer_cik = st.session_state["filer_cik"]

        if filer_cik:
            COMPANY_ID = st.session_state["username"]
            try:
                json_data = fetch_json_data(COMPANY_ID)
            except ValueError as e:
                st.error(e)
                return
            relevant_columns = [field[0] for field in form_fields_list]
            filtered_json_data = [
                column_info
                for column_info in json_data
                if column_info["Column"].strip() in relevant_columns
            ]
            form_fields3 = {}
            # Loop through each column in the filtered json_data and execute a query for each
            for column_info in filtered_json_data:
                column_name = column_info["Column"].strip()
                sql_query = construct_query([column_info], filer_cik)
                df = execute_dynamic_query(sql_query)
                if not df.empty:
                    # Convert the DataFrame to a dictionary
                    row_dict = df.iloc[0].to_dict()

                    # Add the column values to the form_fields dictionary
                    form_fields3.update(row_dict)
                state.form_fields3 = form_fields3

            # Call the create_form function with the form fields list and data
            create_form(form_fields_list, form_fields3)

            # Add a file uploader for the document
            uploaded_file = st.file_uploader(
                "Upload your document", type=["txt", "pdf", "docx"]
            )
            if uploaded_file is not None:
                # Directly use the bytes object returned by read()
                encrypted_document = encrypt_document(uploaded_file.read())
                st.session_state["encrypted_document"] = encrypted_document
                # print(encrypted_document)
                st.success("Document Uploaded.")

            st.success("Success")
        cols = st.columns(2)
        if cols[0].form_submit_button("INFORMATION TABLE"):
            switch_page("informationTable")
            save_session_state(session_id, st.session_state)
        if cols[1].form_submit_button("SUMMARY"):
            switch_page("summaryPage")
            save_session_state(session_id, st.session_state)


# Define the form fields list for the cover page
cover_page_form_fields_list = [
    ("S.1 Name", "text_input", None),
    ("S.2 Title", "text_input", None),
    ("S.3 Phone", "text_input", None),
    ("S.4 Signature", "text_input", None),
    ("S.5 City", "text_input", None),
    ("S.6 State or Country", "text_input", None),
    ("S.7 Date", "text_input", None),
]

# Call the form_Selection function with the cover page form fields list
form_Selection(cover_page_form_fields_list, {})

# Close the cursor and connection
cur.close()
conn.close()
