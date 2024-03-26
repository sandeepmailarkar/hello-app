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

# Custom CSS for Streamlit components
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

# Load session state and Snowflake configuration
session_id = get_session_id()
loaded_state_data = load_session_state(session_id)
if loaded_state_data:
    st.session_state.update(loaded_state_data)

file_path = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "snowflake_credentials.json",
)
with open(file_path, "r") as f:
    snowflake_config = json.load(f)

conn = snowflake.connector.connect(**snowflake_config)
cur = conn.cursor()


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


def construct_query(json_data, Filer_Cik):
    database = json_data[0]["Database"].strip()
    schema = json_data[0]["Schema"].strip()
    table = json_data[0]["Table"].strip()
    columns = ", ".join(
        [f'"{column_info["Column"].strip()}"' for column_info in json_data]
    )
    where_clause = f" WHERE FILER_CIK = '{Filer_Cik}'"
    base_query = f"SELECT {columns} FROM {database}.{schema}.{table}"
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
            return df.to_dict("records")  # Returns a list of dictionaries
        else:
            return []
    except Exception as e:
        st.error(f"An error occurred during query execution: {e}")
        return []


def create_form(form_fields_list, form_fields_data):
    manager_fields_group = [
        ("CP.14.1 cik", "text_input", None),
        ("CP.14.2 Name", "text_input", None),
        ("CP.14.3 CRD Number", "text_input", None),
        ("CP.14.4 SEC File Number", "text_input", None),
        ("CP.14.5 Form 13F File Number", "text_input", None),
    ]

    num_managers = len(form_fields_data["CP.14.1 cik"])
    for i, manager_data in enumerate(
        zip(*[form_fields_data[field[0]] for field in manager_fields_group]), start=1
    ):
        expander_label = f"MANAGER"
        with st.expander(label=expander_label):
            for manager_field, field_value in zip(manager_fields_group, manager_data):
                field_name, field_type, field_options = manager_field
                if field_type == "text_input":
                    unique_identifier = hash(
                        manager_data
                    )  # Generate a unique hash for the data
                    st.text_input(
                        field_name,
                        value=field_value,
                        disabled=True,
                        key=f"{expander_label}_{field_name}_{unique_identifier}",
                    )
    st.session_state["num_managers"] = num_managers


def form_Selection(form_fields_list, form_fields_data):
    st.markdown(
        "<h1 style='text-align: center;'>COVER PAGE (MANAGER)</h1>",
        unsafe_allow_html=True,
    )
    state = get_session_state()
    submission_type = state.submission_type if hasattr(state, "submission_type") else ""

    with st.form("13F_Form_Cover_Page"):
        # Display the submission_type in a non-editable text input
        st.text_input("Submission Type", value=submission_type, disabled=True)
        filer_cik = st.session_state.get("filer_cik", "")

        # Fetch Filer Information and store it in state.form_fields
        if filer_cik:
            COMPANY_ID = st.session_state.get("username", "")
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

            form_fields1 = {}

            # Loop through each column in the filtered json_data and execute a query for each
            for column_info in filtered_json_data:
                column_name = column_info["Column"].strip()
                sql_query = construct_query([column_info], filer_cik)
                results = execute_dynamic_query(sql_query)
                # print(results)

                if results:  # Ensure results is not None before iterating
                    for row in results:
                        for key, value in row.items():
                            if key not in form_fields1:
                                form_fields1[key] = [value]
                            else:
                                form_fields1[key].append(value)

            state.form_fields1 = form_fields1
            # Call the create_form function with the form fields list and data
            create_form(form_fields_list, form_fields1)

            st.success("Success")
        cols = st.columns(2)
        if cols[0].form_submit_button("COVER PAGE"):
            switch_page("coverPage")
            save_session_state(session_id, st.session_state)
        if cols[1].form_submit_button("INFORMATION TABLE"):
            switch_page("informationTable")
            save_session_state(session_id, st.session_state)


cover_page_form_fields_list = [
    ("CP.1 Report for the Calendar Year or Quarter Ended", "text_input", None),
    ("CP.2 Amendment Info", "text_input", None),
    ("CP.2.a Amendment Number", "text_input", None),
    ("CP.2.b Amendment Type", "text_input", None),
    (
        "CP.2.c Does this filing list securities holdings reported on a form 13F filed pursuant to a request for confidential treatment and for which that request was denied or confidential treatment expired?",
        "text_input",
        None,
    ),
    ("CP.2.c.i Reason for Non Confidentiality", "text_input", None),
    ("CP.2.c.ii Date Denied or Expired", "text_input", None),
    ("CP.2.c.iii Date Reported", "text_input", None),
    ("CP.3 Institutional Investment Manager Filing this Report", "text_input", None),
    ("CP.4 Name", "text_input", None),
    ("CP.5 Street 1", "text_input", None),
    ("CP.6 Street 1", "text_input", None),
    ("CP.7 City", "text_input", None),
    ("CP.8 State Or Country", "text_input", None),
    ("CP.9 Zip Code", "text_input", None),
    ("CP.10 Report Type ", "text_input", None),
    ("CP.11 Form 13F File Number", "text_input", None),
    (
        "CP.12 Do you wish to provide information pursuant to Special Instruction 5?",
        "text_input",
        None,
    ),
    ("CP.13 Additional Information", "text_input", None),
    # ("CP.14 List of Other Managers Reporting for this Manager", "text_input", None),
    ("CP.14.1 cik", "text_input", None),  # present
    ("CP.14.2 Name", "text_input", None),
    ("CP.14.3 CRD Number", "text_input", None),  # present
    ("CP.14.4 SEC File Number", "text_input", None),  # present
    ("CP.14.5 Form 13F File Number", "text_input", None),
]

form_Selection(cover_page_form_fields_list, {})

# Close the cursor and connection
cur.close()
conn.close()
