from xml.etree.ElementTree import Element, SubElement, tostring
import streamlit as st
import pandas as pd
import snowflake.connector
import json
from streamlit_extras.switch_page_button import switch_page
from session_state import get_session_state
import os
import xml.etree.ElementTree as ET
import datetime
import shutil
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from xml.etree.ElementTree import Element, SubElement, tostring


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
    table = ", ".join([f'"{table_info["Table"].strip()}"' for table_info in json_data])
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

        st.error(f"An error occurred during query execution: {e}")

        return pd.DataFrame()


# Function to create a form with dynamic fields


def create_form(form_fields_list, form_fields_data, form_prefix=""):

    for sp_field_name, field_type, field_options in form_fields_list:

        if sp_field_name in form_fields_data:

            if field_type == "text_input":

                unique_key = f"{form_prefix}_{sp_field_name}"

                if sp_field_name == "Number of Other Included Managers":

                    default_value = st.session_state.get(
                        "num_managers", form_fields_data[sp_field_name]
                    )

                elif sp_field_name == "Form 13F Information table Value Total":

                    default_value = st.session_state.get(
                        "total_it_5_values", form_fields_data[sp_field_name]
                    )

                else:

                    default_value = form_fields_data[sp_field_name]

                # Create the text input field with the determined default value

                st.text_input(
                    sp_field_name, value=default_value, disabled=True, key=unique_key
                )

        else:

            st.warning(f"Field '{sp_field_name}' not found in the data.")

            st.text_input(
                sp_field_name, value="", disabled=True, key=f"{sp_field_name}"
            )

    from xml.etree.ElementTree import Element, SubElement, tostring


# Main form selection function
def form_Selection(form_fields_list, form_fields_data):
    st.markdown(
        "<h1 style='text-align: center;'> Summary Page </h1>", unsafe_allow_html=True
    )
    state = get_session_state()
    submission_type = state.submission_type if hasattr(state, "submission_type") else ""

    with st.form("13F_Form"):
        # Display the submission_type in a non-editable text input
        st.text_input("Submission Type", value=submission_type, disabled=True)
        filer_cik = st.session_state["filer_cik"]

        # Submit button for filer_cik
        if filer_cik:
            COMPANY_ID = st.session_state["username"]
            try:
                json_data = fetch_json_data(COMPANY_ID)
            except ValueError as e:
                st.error(e)
                return

            # Filter the json_data to only include the relevant columns
            relevant_columns = [field[0] for field in form_fields_list]
            filtered_json_data = [
                column_info
                for column_info in json_data
                if column_info["Column"].strip() in relevant_columns
            ]
            # print(relevant_columns)
            form_fields = {}
            form_fields1 = {}
            form_fields2 = {}
            form_fields3 = {}
            form_fields4 = {}
            manager_data = [
                {
                    "CP.14.1 cik": form_fields1.get("CP.14.1 cik"),
                    "CP.14.2 Name": form_fields1.get("CP.14.2 Name"),
                    "CP.14.3 CRD Number": form_fields1.get("CP.14.3 CRD Number"),
                    "CP.14.4 SEC File Number": form_fields1.get(
                        "CP.14.4 SEC File Number"
                    ),
                    "CP.14.5 Form 13F File Number": form_fields1.get(
                        "CP.14.5 Form 13F File Number"
                    ),
                }
            ]

            # Loop through each column in the filtered json_data and execute a query for each
            for column_info in filtered_json_data:
                column_name = column_info["Column"].strip()
                sql_query = construct_query([column_info], filer_cik)
                df = execute_dynamic_query(sql_query)
                # print(df)
                if not df.empty:
                    # Convert the DataFrame to a dictionary
                    row_dict = df.iloc[0].to_dict()

                    # Add the column values to the form_fields dictionary
                    form_fields.update(row_dict)
                    form_fields1.update(row_dict)
                    form_fields2.update(row_dict)
                    form_fields3.update(row_dict)

                    form_fields4.update(row_dict)
                state.form_fields4 = form_fields3

            create_form(form_fields_list, form_fields)
            st.success("Success")
            cols = st.columns(2)
            if cols[0].form_submit_button("SIGNATURE"):
                switch_page("signatureBlock")
                save_session_state(session_id, st.session_state)
            if cols[1].form_submit_button("SUMMARY(MANAGER)"):
                switch_page("Summary_Other_Manager")
                save_session_state(session_id, st.session_state)


options = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]
cover_page_form_fields_list = [
    ("SP.1 Confidential information has been omitted", "text_input", None),
    ("Number of Other Included Managers", "text_input", None),
    ("Form 13F Information table Entry Total", "text_input", None),
    ("Form 13F Information table Value Total", "text_input", None),
    ("SP.2.1 Sequence Number", "text_input", None),
    ("SP.2.2 CIK", "text_input", None),
    ("SP.2.3 CRD Number", "text_input", None),
    ("SP.2.4 SEC File Number", "text_input", None),
    # ("SP.2.5 File Number", "text_input", None),
    # ("SP.2.6 Name", "text_input", None)
]

form_Selection(cover_page_form_fields_list, {})

# Close the cursor and connection
cur.close()
conn.close()
