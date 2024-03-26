import streamlit as st
import pandas as pd
import snowflake.connector
import json
import os

from streamlit_extras.switch_page_button import switch_page
from session_state import get_session_state
from session_state_manager import get_session_id, save_session_state, load_session_state

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
    for fl_field_name, field_type, field_options in form_fields_list:
        if fl_field_name in form_fields_data:
            values = form_fields_data[fl_field_name]
            if isinstance(values, list):
                # If the values are in a list, create a separate field for each value
                for i, value in enumerate(values):
                    # Use the index to create a unique key for each field
                    key = f"{fl_field_name}_{i}"
                    if field_type == "text_input":
                        st.text_input(
                            fl_field_name, value=value, disabled=True, key=key
                        )
            else:
                # If there's only a single value, display it as is
                st.text_input(fl_field_name, value=values, disabled=True)
        else:
            st.text_input(
                fl_field_name, value="", disabled=True, key=f"{fl_field_name}"
            )
            st.warning(f"Field '{fl_field_name}' not found in the data.")


def app(form_fields_list, form_fields_data):
    st.markdown(
        "<h1 style='text-align: center;'>FILER INFORMATION</h1>", unsafe_allow_html=True
    )
    state = get_session_state()
    submission_type = state.submission_type if hasattr(state, "submission_type") else ""

    with st.form("13F_Form"):
        st.text_input("Submission Type", value=submission_type, disabled=True)
        filer_cik = st.text_input("Filer CIK")

        if st.form_submit_button("PROCESS"):
            if not filer_cik:
                st.error("Please enter a valid Filer CIK.")
                return

            COMPANY_ID = st.session_state["username"]
            st.session_state["filer_cik"] = filer_cik

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

            form_fields = {}

            for column_info in filtered_json_data:
                column_name = column_info["Column"].strip()
                sql_query = construct_query([column_info], filer_cik)
                results = execute_dynamic_query(sql_query)

                if results:  # Ensure results is not None before iterating
                    for row in results:
                        for key, value in row.items():
                            if key not in form_fields:
                                form_fields[key] = [value]
                            else:
                                form_fields[key].append(value)

            state.form_fields = form_fields

            create_form(form_fields_list, form_fields)

            st.session_state["process_button_clicked"] = True
            st.success("Success")

        if (
            "process_button_clicked" in st.session_state
            and st.session_state["process_button_clicked"]
        ):
            if st.form_submit_button("Cover Page"):
                switch_page("coverPage")
                save_session_state(session_id, st.session_state)


if __name__ == "__main__":
    cover_page_form_fields_list = [
        ("FL.2 Filer CIK", "text_input", None),
        ("FL.3 Filer CCC", "text_input", None),
        ("FL.4 REPORT_DATE", "text_input", None),
        ("FL.5 DEADLINE_DATE", "text_input", None),
        ("FL.6 Would you like a Return Copy?", "text_input", None),
        (
            "FL.7 Is this an electronic copy of an official filing submitted in paper format?",
            "text_input",
            None,
        ),
        ("FL.8 Notify via Filing Website only?", "text_input", None),
        ("FL.9 Notification Email", "text_input", None),
        ("EMAIL", "text_input", None),
        ("FL.10 Ticker or Other Identifier for Fund", "text_input", None),
    ]
    app(cover_page_form_fields_list, {})

cur.close()
conn.close()

