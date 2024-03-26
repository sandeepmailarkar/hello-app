import streamlit as st
import pandas as pd
import snowflake.connector
import json
import os
from session_state import get_session_state
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

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>MAPPING </h1>", unsafe_allow_html=True)


def logout():
    st.session_state.clear()
    switch_page("main")
    if st.button("Logout"):
        logout()


# Get the absolute path to the snowflake_credentials.json file
file_path = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "snowflake_credentials.json",
)

# Load Snowflake configuration from JSON file
with open(file_path, "r") as f:
    snowflake_config = json.load(f)


# Function to connect to Snowflake
def connect_to_snowflake():
    try:
        conn = snowflake.connector.connect(**snowflake_config)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
        return None, None


# Initialize the scorecard DataFrame
scorecard = pd.DataFrame(
    columns=["Fields", "Database", "Schema", "Table", "Column", "Where_Clause"]
)


# CSV file upload
uploaded_file = st.file_uploader("Upload Mapping File", type="csv")

if uploaded_file is not None:
    # Read the file into a pandas DataFrame
    scorecard = pd.read_csv(uploaded_file)

    # Display the CSV data in a table format
    st.write("Original CSV:")
    st.dataframe(scorecard)

col1, col2 = st.columns([1, 1])

# Ask user if they want to proceed with storing the data in Snowflake
with col1:

    if st.button("SAVE"):
        try:
            # Your existing code to save data
            Company_id = st.session_state["username"]
            Form_no = "13F"
            json_string = scorecard.to_json(orient="records")
            json.loads(json_string)  # Validate JSON string
            conn, cursor = connect_to_snowflake()
            if conn is not None and cursor is not None:
                sql = """
                        INSERT INTO JSON_FILE_1 (JSON_DATA, COMPANY_ID, FORM_NO)
                        SELECT parse_json(%s), %s, %s
                    """
                params = (json_string, Company_id, Form_no)
                cursor.execute(sql, params)
                # Commit the changes
                conn.commit()
                st.success("Data inserted successfully!")
                # Set a session state variable to indicate the "SAVE" action has been completed
                st.session_state["save_completed"] = True
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Check if the "SAVE" action has been completed
    if "save_completed" in st.session_state and st.session_state["save_completed"]:
        if st.button("PREVIEW MAPPING"):
            # Switch to the EDIT_Mapping page
            switch_page("EDIT_Mapping")
with col2:

    if st.button("Filer Information"):
        switch_page("filerInfo")
# Rest of the existing Streamlit app code...
st.write("Insert Mapping Manually ")

input_data = pd.DataFrame(
    index=range(42),
    columns=["Fields", "Database", "Schema", "Table", "Column", "Where_Clause"],
)
input_data["Fields"] = [
    "FL.1_Filer_CIK",
    "FL.2_Filer_CCC",
    "FL.3_Report_Date",
    "FL.4_Deadline_Date",
    "FL.5_Return_Copy",
    "FL.6_Electronic_Copy",
    "FL.7_Notify_Filing_Website",
    "FL.8_Novo_Request",
    "FL.9_Email",
    "FL.10_Ticker_Or_Other_Identifier",
    "FL.11_Additional_Description",
    "CP.1_AMENDMENT_NUMBER",
    "CP.2_AMENDMENT_TYPE",
    "CP.3_DOES_FILING_LIST_SECURITIES_HOLDINGS_13F_REQUESTED_CONFIDENTIAL_TREATMENT_DENIED_EXPIRED",
    "CP.4_REASON_FOR_NON_CONFIDENTIALITY",
    "CP.5_DATE_DENIED_EXPIRED",
    "CP.6_DATE_REPORTED",
    "CP.7_NAME",
    "CP.8_STREET_1",
    "CP.9_STREET_2",
    "CP.10_CITY",
    "CP.11_STATE_OR_COUNTRY",
    "CP.12_ZIP_CODE",
    "CP.13_REPORT_TYPE",
    "CP.14_CRD_NUMBER",
    "CP.15_SEC_FILE_NUMBER",
    "CP.16_FORM_13F_FILE_NUMBER",
    "CP.17_PROVIDE_INFORMATION_PURSUANT_TO_SPECIAL_INSTRUCTION_5",
    "CP.18_ADDITIONAL_INFORMATION",
    "SGP.1_NAME",
    "SGP.2_TITLE",
    "SGP.3_PHONE",
    "SGP.4_SIGNATURE",
    "SGP.5_CITY",
    "SGP.6_STATE_OR_COUNTRY",
    "SGP.7_DATE",
    "SP.1_Confidential_Information_Omitted",
    "SP.2_Other_Included_Manager",
    "SP.3_Sequence_Number",
    "SP.4_CIK",
    "SP.5_File_Number",
    "SP.6_Name",
]
edited_data = st.data_editor(
    input_data[["Fields", "Database", "Schema", "Table", "Column", "Where_Clause"]]
)

if st.button("Submit"):
    # validations
    if edited_data.isnull().values.any():
        st.error(
            "All fields must be filled and contain only letters and spaces. No numbers or special characters are allowed."
        )
    else:
        # Define the order of columns
        column_order = [
            "Fields",
            "Database",
            "Schema",
            "Table",
            "Column",
            "Where_Clause",
        ]

        # Create a new DataFrame with user input using the defined order
        new_data = pd.DataFrame(
            {
                "Fields": input_data["Fields"],
                "Database": edited_data["Database"].astype(str).tolist(),
                "Schema": edited_data["Schema"].astype(str).tolist(),
                "Table": edited_data["Table"].astype(str).tolist(),
                "Column": edited_data["Column"].astype(str).tolist(),
                "Where_Clause": edited_data["Where_Clause"].astype(str).tolist(),
            },
            columns=column_order,
        )

        scorecard = pd.concat([scorecard, new_data], ignore_index=True)

        st.success("Data submitted successfully!")
        st.write("Updated Scorecard:")
        st.table(scorecard[column_order])

        conn, cursor = connect_to_snowflake()
        if conn is not None and cursor is not None:
            try:
                COMPANY_ID = st.session_state["username"]
                Form_no = "13F"
                json_string = scorecard[column_order].to_json(orient="records")
                json.loads(json_string)
                sql = """
                INSERT INTO JSON_FILE_1 (JSON_DATA, COMPANY_ID, FORM_NO)
                SELECT parse_json(%s), %s, %s
                """
                params = (json_string, COMPANY_ID, Form_no)
                cursor.execute(sql, params)

                # Commit the changes
                conn.commit()
                st.success("Data inserted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()

