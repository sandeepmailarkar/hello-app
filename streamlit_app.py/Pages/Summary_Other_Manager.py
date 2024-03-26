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

# Custom CSS for Streamlit components
custom_css = """
<style>
    .stButton > button {
        padding:   10px   15px;
        margin-right:   5px;
        margin-left:   5px;
        width: fit-content;
        height:  50px; /* Adjust height as needed */
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
    h1 {
        text-align: center;
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
    Manager_fields = [
        ("SP.2.1 Sequence Number", "text_input", None),
        ("SP.2.2 CIK", "text_input", None),
        ("SP.2.3 CRD Number", "text_input", None),
        ("SP.2.4 SEC File Number", "text_input", None),
        # ("SP.2.5 File Number", "text_input", None),
        # ("SP.2.6 Name", "text_input", None),
    ]

    # num_managers = len(form_fields_data["CP.14.1 cik"])
    for i, manager_data in enumerate(
        zip(*[form_fields_data[field[0]] for field in Manager_fields]), start=1
    ):
        expander_label = f"SUMMARY MANAGER"

        with st.expander(label=expander_label):
            for manager_field, field_value in zip(Manager_fields, manager_data):
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
    # st.session_state['num_managers'] = num_managers


def generate_xml(
    filer_info_fields,
    cover_page_fields,
    information_table_fields,
    signature_fields,
    summary_page_fields,
):
    filer_info_root = Element("filerInfo")
    cover_page_root = Element("coverPage")
    information_table_root = Element("informationTable")
    signature_root = Element("signatureBlock")
    summary_page_root = Element("summaryPage ")
    named_documents_root = Element("documents")  # New root element for Named Documents

    hidden_information_table_fields = [
        "IT.1_Name_of_issuer","IT.2_Title_of_class","IT.3_CUSIP","IT.4_FIGI","IT.5_Value__in_Thousands_","IT.6_Shares_Principal_Amount","IT.7_Shares_Principal","IT.8_Put_Call","IT.9_Investment_Discretion","IT.10_Other_Manager","IT.11_Voting_Authority","IT.12_Sole","IT.13_Shared",
        "IT.14_None","CP.14.1_cik","CP.14.2_Name","CP.14.3_CRD_Number","CP.14.4_SEC_File_Number","CP.14.5_Form_13F_File_Number","SP.2.1 Sequence Number","text_input","SP.2.2 CIK","SP.2.3 CRD Number","SP.2.4 SEC File Number","SP.2.5 File Number","SP.2.6 Name",
    ]

    def handle_multiple_values(fields, parent_element):
        for field_name, field_value in fields.items():
            field_name = (
                field_name.replace(" ", "_")
                .replace("?", "_")
                .replace("(", "_")
                .replace(")", "_")
                .replace("/", "_")
            )


            if field_name in [
                "CP.4_Name",
                "CP.5_Street_1",
                "CP.6_Street_1",
                "CP.7_City",
                "CP.8_State_Or_Country",
                "CP.9_Zip_Code",
            ]:
                address_element = parent_element.find("address")
                if address_element is None:
                    address_element = SubElement(parent_element, "address")
                child_element = SubElement(address_element, field_name)
                # Check if field_value is a list and display only the first value
                if isinstance(field_value, list):
                    child_element.text = str(field_value[0]) if field_value else ""
                else:
                    child_element.text = str(field_value)

            elif field_name in ["FL.2_Filer_CIK", "FL.3_Filer_CCC"]:
                credentials_element = parent_element.find("credentials")
                if credentials_element is None:
                    credentials_element = SubElement(parent_element, "credentials")
                child_element = SubElement(credentials_element, field_name)
                # Check if field_value is a list and display only the first value
                if isinstance(field_value, list):
                    child_element.text = str(field_value[0]) if field_value else ""
                else:
                    child_element.text = str(field_value)

            elif field_name in [
                "FL.6_Would_you_like_a_Return_Copy_",
                "FL.7_Is_this_an_electronic_copy_of_an_official_filing_submitted_in_paper_format_",
                "FL.8_Notify_via_Filing_Website_only_",
            ]:
                flags_element = parent_element.find("flags")
                if flags_element is None:
                    flags_element = SubElement(parent_element, "flags")
                child_element = SubElement(flags_element, field_name)
                # Check if field_value is a list and display only the first value
                if isinstance(field_value, list):
                    child_element.text = str(field_value[0]) if field_value else ""
                else:
                    child_element.text = str(field_value)

            # Check if the field is in the list of hidden fields
            elif field_name in hidden_information_table_fields:
                continue  # Skip this field if it's in the list of hidden fields

            elif field_name == "EMAIL":
                notification_email_element = SubElement(parent_element, field_name)
                if isinstance(field_value, list):
                    for email in field_value:
                        email_element = SubElement(notification_email_element, "email")
                        email_element.text = str(email)
                else:
                    email_element = SubElement(notification_email_element, "email")
                    email_element.text = str(field_value)
            else:
                child_element = SubElement(parent_element, field_name)
                # Check if field_value is a list and display only the first value
                if isinstance(field_value, list):
                    child_element.text = str(field_value[0]) if field_value else ""
                else:
                    child_element.text = str(field_value)

    # Call handle_multiple_values for each group of fields
    handle_multiple_values(filer_info_fields, filer_info_root)
    handle_multiple_values(cover_page_fields, cover_page_root)
    handle_multiple_values(information_table_fields, information_table_root)
    handle_multiple_values(signature_fields, signature_root)
    handle_multiple_values(summary_page_fields, summary_page_root)

    if "encrypted_document" in st.session_state:
        encrypted_document, _ = st.session_state["encrypted_document"]

        # Check if encrypted_document is a bytes object
        if isinstance(encrypted_document, bytes):
            named_document_element = SubElement(named_documents_root, "document")
            named_document_element.text = encrypted_document.decode("utf-8").replace(
                "\n", " "
            )
        else:
            # If encrypted_document is already a string, directly use it
            named_document_element = SubElement(named_documents_root, "document")
            named_document_element.text = encrypted_document.replace("\n", " ")

    # Create Manager elements under the Cover_page root
    manager_fields_group = [
        ("CP.14.1 cik", "text_input", None),
        ("CP.14.2 Name", "text_input", None),
        ("CP.14.3 CRD Number", "text_input", None),
        ("CP.14.4 SEC File Number", "text_input", None),
        ("CP.14.5 Form 13F File Number", "text_input", None),
    ]

    # Extract manager data from cover_page_fields
    manager_data = {
        field[0]: cover_page_fields[field[0]] for field in manager_fields_group
    }

    # Find the position of CP.14 in cover_page_root
    cp_14_position = None
    for i, child in enumerate(cover_page_root):
        if child.tag == "CP.14":
            cp_14_position = i
            break

    # Iterate over each manager and create a Manager element
    for i, manager_info in enumerate(
        zip(*[manager_data[field[0]] for field in manager_fields_group]), start=1
    ):
        # Include the index in the Manager tag name
        manager_element_tag = f"manager"
        manager_element = SubElement(cover_page_root, manager_element_tag)
        for manager_field, field_value in zip(manager_fields_group, manager_info):
            field_name, field_type, field_options = manager_field
            # Replace '.' with '_' for XML tag names and include the index in the field name
            field_element_tag = field_name.replace(".", "_").replace(" ", "_")
            field_element = SubElement(manager_element, field_element_tag)
            field_element.text = str(field_value)

        # Insert the Manager element right after CP.14
        if cp_14_position is not None:
            cover_page_root.insert(cp_14_position + i, manager_element)

    information_fields_group = [
        ("IT.1 Name of issuer", "text_input", None),
        ("IT.2 Title of class", "date_input", None),
        ("IT.3 CUSIP", "date_input", None),
        ("IT.4 FIGI", "text_input", None),
        ("IT.5 Value (in Thousands)", "text_input", None),
        ("IT.6 Shares/Principal Amount", "text_input", None),
        ("IT.7 Shares/Principal", "text_input", None),
        ("IT.8 Put/Call", "text_input", None),
        ("IT.9 Investment Discretion", "text_input", None),
        ("IT.10 Other Manager", "text_input", None),
        ("IT.11 Voting Authority", "text_input", None),
        ("IT.12 Sole", "text_input", None),
        ("IT.13 Shared", "text_input", None),
        ("IT.14 None", "text_input", None),
    ]

    # Extract manager data from cover_page_fields
    information_data = {
        field[0]: information_table_fields[field[0]]
        for field in information_fields_group
    }

    # Find the position of CP.14 in cover_page_root
    it_1_position = None
    for i, child in enumerate(information_table_root):
        if child.tag == "IT.1":
            it_1_position = i
            break

    # Iterate over each manager and create a Manager element
    for i, information_info in enumerate(
        zip(*[information_data[field[0]] for field in information_fields_group]),
        start=1,
    ):
        # Include the index in the Information_Table tag name
        information_element_tag = f"infoTable"
        information_element = SubElement(
            information_table_root, information_element_tag
        )
        for information_field, field_value in zip(
            information_fields_group, information_info
        ):
            field_name, field_type, field_options = information_field
            # Replace '.' with '_' for XML tag names, replace spaces with '_', and handle other special characters for XML tag names
            field_element_tag = (
                field_name.replace(".", "_")
                .replace(" ", "_")
                .replace("(", "_")
                .replace(")", "_")
                .replace("/", "_")
            )
            field_element = SubElement(information_element, field_element_tag)
            field_element.text = str(field_value)

        # Insert the Manager element right after CP.14
        if it_1_position is not None:
            information_table_root.insert(it_1_position + i, information_element)

    summary_fields_group = [
        ("SP.2.1 Sequence Number", "text_input", None),
        ("SP.2.2 CIK", "text_input", None),
        ("SP.2.3 CRD Number", "text_input", None),
        ("SP.2.4 SEC File Number", "text_input", None),
        # ("SP.2.5 File Number", "text_input", None),
        # ("SP.2.6 Name", "text_input", None)
    ]

    # Extract manager data from cover_page_fields
    summary_data = {
        field[0]: [summary_page_fields[field[0]]] for field in summary_fields_group
    }

    # Find the position of CP.14 in cover_page_root
    SP_2_1_position = None
    for i, child in enumerate(summary_page_root):
        if child.tag == "SP.2.1":
            SP_2_1_position = i
            break

    # Iterate over each manager and create a Manager element
    for i, summary_info in enumerate(
        zip(*[summary_data[field[0]] for field in summary_fields_group]), start=1
    ):
        # Include the index in the Manager tag name
        summary_element_tag = f"manager"
        summary_element = SubElement(summary_page_root, summary_element_tag)
        for summary_field, field_value in zip(summary_fields_group, summary_info):
            field_name, field_type, field_options = summary_field
            # Replace '.' with '_' for XML tag names and include the index in the field name
            summary_field_element_tag = field_name.replace(".", "_").replace(" ", "_")
            summary_field_element = SubElement(
                summary_element, summary_field_element_tag
            )
            summary_field_element.text = str(field_value)

        # Insert the Manager element right after CP.14
        if SP_2_1_position is not None:
            summary_page_root.insert(SP_2_1_position + i, summary_element)

    # Create the root element for the entire XML document
    root = Element("form13F-HR")
    root.append(filer_info_root)
    root.append(cover_page_root)
    root.append(information_table_root)
    root.append(signature_root)
    root.append(summary_page_root)
    root.append(named_documents_root)

    # Convert the XML structure to a string with pretty printing
    xml_string = tostring(root, encoding="unicode")
    xml_string = xml_string.replace("><", ">\n\t<")
    xml_string = xml_string.replace("<filerInfo>", "<filerInfo>\n\t")
    xml_string = xml_string.replace("</filerInfo>", "\n\t</filerInfo>\n")
    xml_string = xml_string.replace("<coverPage>", "<coverPage>\n\t")
    xml_string = xml_string.replace("</coverPage>", "\n\t</coverPage>\n")
    xml_string = xml_string.replace("<informationTable>", "<informationTable>\n\t")
    xml_string = xml_string.replace("</informationTable>", "\n\t</informationTable>\n")
    xml_string = xml_string.replace("<signatureBlock>", "<signatureBlock>\n\t")
    xml_string = xml_string.replace("</signatureBlock>", "\n\t</signatureBlock>\n")
    xml_string = xml_string.replace("<summaryPage>", "<summaryPage>\n\t")
    xml_string = xml_string.replace("</summaryPage>", "\n\t</summaryPage>\n")
    xml_string = xml_string.replace("<documents>", "<documents>\n\t")
    xml_string = xml_string.replace("</documents>", "\n\t</documents>\n")

    # Return the pretty-printed XML string
    return xml_string


def upload_file_to_local_directory(filename):
    try:
        # Ensure the filename has the .xml extension
        if not filename.endswith(".xml"):
            filename += ".xml"

        home_directory = os.path.expanduser("~")

        local_directory = os.path.join(home_directory, "Downloads")
        os.makedirs(local_directory, exist_ok=True)

        full_path = os.path.join(local_directory, filename)
        shutil.copy(filename, full_path)

    except Exception as e:
        st.error(f"An error occurred while saving the file to the local directory: {e}")


def upload_file_to_snowflake_stage(filename):
    try:
        stage_location = f"@FilerInformation.Filer.Filer_info/{filename}"
        cur.execute(f"PUT file://{filename} {stage_location}")
    except Exception as e:
        st.error(f"An error occurred while uploading the file to Snowflake stage: {e}")


def form_Selection(form_fields_list, form_fields_data):
    st.markdown(
        "<h1 style='text-align: center;'>SUMMARY PAGE (MANAGER)</h1>",
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
            form_fields5 = {}
            # Loop through each column in the filtered json_data and execute a query for each
            for column_info in filtered_json_data:
                column_name = column_info["Column"].strip()
                sql_query = construct_query([column_info], filer_cik)
                results = execute_dynamic_query(sql_query)
                # print(results)

                if results:  # Ensure results is not None before iterating
                    for row in results:
                        for key, value in row.items():
                            if key not in form_fields5:
                                form_fields5[key] = [value]
                            else:
                                form_fields5[key].append(value)

            # state.form_fields5 = form_fields5
            # Call the create_form function with the form fields list and data
            create_form(form_fields_list, form_fields5)
        st.success("Success")
        cols = st.columns(5)  # Increase the number of columns to 4
        if cols[0].form_submit_button("SUMMARY PAGE"):
            switch_page("summaryPage")
        if cols[1].form_submit_button("EDIT MAPPING"):
            switch_page("Edit_Mapping")
        if cols[2].form_submit_button("GENERATE XML"):

            combined_form_fields = {
                **state.form_fields,
                **state.form_fields1,
                **state.form_fields2,
                **state.form_fields3,
                **state.form_fields4,
            }
            # Separate the fields into Filer Information and Cover Page fields
            filer_info_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields
            }
            cover_page_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields1
            }
            information_table_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields2
            }
            signature_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields3
            }
            summary_page_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields4
            }
            # xml_string = generate_xml(filer_info_fields, cover_page_fields,information_table_fields, signature_fields, summary_page_fields)
            import xml.etree.ElementTree as ET

            # Assuming xml_string is the XML string generated by your generate_xml function
            xml_string = generate_xml(
                filer_info_fields,
                cover_page_fields,
                information_table_fields,
                signature_fields,
                summary_page_fields,
            )

            # Parse the XML string into an ElementTree object
            root = ET.fromstring(xml_string)

            # Define a dictionary mapping old tag names to new tag names
            tag_name_mapping = {
                "FL.2_Filer_CIK": "cik",
                "FL.3_Filer_CCC": "ccc",
                "FL.4_REPORT_DATE": "periodOfReport",
                "FL.5_DEADLINE_DATE": "deadlineDate",
                "FL.6_Would_you_like_a_Return_Copy_": "returnCopyFlag",
                "FL.7_Is_this_an_electronic_copy_of_an_official_filing_submitted_in_paper_format_": "confirmingCopyFlag",
                "FL.8_Notify_via_Filing_Website_only_": "overrrideInternetFlag",
                "FL.9_Notification_Email": "notificationEmailAddress",
                "FL.10_Ticker_or_Other_Identifier_for_Fund": "tickerOrOtherIdentifier",
                "CP.1_Report_for_the_Calendar_Year_or_Quarter_Ended": "reportCalendarOrQuarter",
                "CP.2_Amendment_Info": "isAmendment",
                "CP.2.a_Amendment_Number": "amendmentNo",
                "CP.2.b_Amendment_Type": "amendmentType:",
                "CP.2.c.i_Reason_for_Non_Confidentiality": "reasonForNonConfidentiality",
                "CP.2.c.ii_Date_Denied_or_Expired": "confDeniedExpired",
                "CP.2.c.iii_Date_Reported": "dateReported",
                "CP.3_Institutional_Investment_Manager_Filing_this_Report": "name:",
                "CP.4_Name": "name",
                "CP.5_Street_1": "com:street1",
                "CP.6_Street_1": "com:street2",
                "CP.7_City": "com:city",
                "CP.8_State_Or_Country": "com:stateOrCountry",
                "CP.9_Zip_Code": "com:zipCode",
                "CP.11_Form_13F_File_Number": "form13FFileNumber",
                "CP.12_Do_you_wish_to_provide_information_pursuant_to_Special_Instruction_5_": "provideInfoForInstruction5",
                "CP.13_Additional_Information": "additionalInformation ",
                "CP_14_1_cik": "cik",
                "CP_14_2_Name": "name",
                "CP_14_3_CRD_Number": "crdNumber",
                "CP_14_4_SEC_File_Number": "secFileNumber",
                "CP_14_5_Form_13F_File_Number": "form13FFileNumber",
                "S.1_Name": "Name:",
                "S.2_Title": "title:",
                "S.3_Phone": "phone:",
                "S.4_Signature": "signature",
                "S.5_City": "city",
                "S.6_State_or_Country": " stateOrCountry",
                "S.7_Date": "signatureDate",
                "SP.1_Confidential_information_has_been_omitted": "confidentialOmitted?",
                "Number_of_Other_Included_Managers": "otherIncludedManagersCount",
                "Form_13F_Information_table_Entry_Total": "tableEntryTotal ",
                "Form_13F_Information_table_Value_Total": "tableValueTotal",
                "SP.2.1_Sequence_Number": "sequenceNumber",
                "SP.2.2_CIK": "cik",
                "SP.2.3_CRD_Number": "crdNumber",
                "SP.2.4_SEC_File_Number": "secFileNumber",
                "SP_2_1_Sequence_Number": "sequenceNumber.",
                "SP_2_2_CIK": "cik",
                "SP_2_3_CRD_Number": "crdNumber",
                "SP_2_4_SEC_File_Number": "secFileNumber",
                "IT_1_Name_of_issuer": "nameOfIssuer",
                "IT_2_Title_of_class": "titleOfClass",
                "IT_3_CUSIP": "cusip",
                "IT_4_FIGI": "figi",
                "IT_5_Value__in_Thousands_": "value",
                "IT_6_Shares_Principal_Amount": "shrsOrPrnAmt",
                "IT_7_Shares_Principal": "sshPrnamt",
                "IT_8_Put_Call": "putCall",
                "IT_9_Investment_Discretion": "investmentDiscretion",
                "IT_10_Other_Manager": "otherManager",
                "IT_11_Voting_Authority": "votingAuthority",
                "IT_12_Sole": "Sole",
                "IT_13_Shared": "Shared",
                "IT_14_None": "None",
            }

            def modify_tags(element, tag_name_mapping):
                """Recursively modify tag names based on the mapping."""
                if element.tag in tag_name_mapping:
                    element.tag = tag_name_mapping[element.tag]
                for child in element:
                    modify_tags(child, tag_name_mapping)

            # Call the function to modify tag names
            modify_tags(root, tag_name_mapping)

            # Save the modified XML document
            modified_xml_string = ET.tostring(root, encoding="unicode")

            # Now you can save modified_xml_string to a file or further process it
            with open("modified_xml_file.xml", "w", encoding="utf-8") as file:
                file.write(modified_xml_string)
            st.markdown("**<h1>Generated XML</h1>**", unsafe_allow_html=True)

            st.code(modified_xml_string, language="xml")
            pass

        if cols[3].form_submit_button("PREVIEW"):
            # Combine Filer Information and Cover Page form fields
            combined_form_fields = {
                **state.form_fields,
                **state.form_fields1,
                **state.form_fields2,
                **state.form_fields3,
                **state.form_fields4,
            }
            st.markdown("**<h1>Preview Form</h1>**", unsafe_allow_html=True)
            st.markdown(
                "<h2><u><strong>Filer Information</strong></u></h2>",
                unsafe_allow_html=True,
            )
            for field_name, field_value in state.form_fields.items():
                if isinstance(field_value, list):
                    for value in field_value:
                        st.markdown(
                            f"**{field_name}:** {value}", unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"**{field_name}:** {field_value}", unsafe_allow_html=True
                    )
            st.markdown(
                "<h2><u><strong>Cover Page</strong></u></h2>", unsafe_allow_html=True
            )
            for field_name, field_value in state.form_fields1.items():
                if isinstance(field_value, list):
                    for value in field_value:
                        st.markdown(
                            f"**{field_name}:** {value}", unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"**{field_name}:** {field_value}", unsafe_allow_html=True
                    )
            st.markdown(
                "<h2><u><strong>Information Table</strong></u></h2>",
                unsafe_allow_html=True,
            )
            for field_name, field_value in state.form_fields2.items():
                if isinstance(field_value, list):
                    for value in field_value:
                        st.markdown(
                            f"**{field_name}:** {value}", unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"**{field_name}:** {field_value}", unsafe_allow_html=True
                    )
            st.markdown(
                "<h2><u><strong>Signature</strong></u></h2>", unsafe_allow_html=True
            )
            for field_name, field_value in state.form_fields3.items():
                if isinstance(field_value, list):
                    for value in field_value:
                        st.markdown(
                            f"**{field_name}:** {value}", unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"**{field_name}:** {field_value}", unsafe_allow_html=True
                    )
            st.markdown(
                "<h2><u><strong>Summary Page</strong></u></h2>", unsafe_allow_html=True
            )
            for field_name, field_value in state.form_fields4.items():
                if isinstance(field_value, list):
                    for value in field_value:
                        st.markdown(
                            f"**{field_name}:** {value}", unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"**{field_name}:** {field_value}", unsafe_allow_html=True
                    )

        if cols[4].form_submit_button("DOWNLOAD"):
            # Combine Filer Information and Cover Page form fields
            combined_form_fields = {
                **state.form_fields,
                **state.form_fields1,
                **state.form_fields2,
                **state.form_fields3,
                **state.form_fields4,
            }
            # Separate the fields into Filer Information and Cover Page fields
            filer_info_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields
            }
            cover_page_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields1
            }
            information_table_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields2
            }

            signature_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields3
            }
            summary_page_fields = {
                k: v for k, v in combined_form_fields.items() if k in state.form_fields4
            }
            xml_string = generate_xml(
                filer_info_fields,
                cover_page_fields,
                information_table_fields,
                signature_fields,
                summary_page_fields,
            )
            import xml.etree.ElementTree as ET

            root = ET.fromstring(xml_string)
            namespace_uri = "http://example.com/com"
            namespace_prefix = "com"
            # Define a dictionary mapping old tag names to new tag names
            tag_name_mapping = {
                "FL.2_Filer_CIK": "cik",
                "FL.3_Filer_CCC": "ccc",
                "FL.4_REPORT_DATE": "periodOfReport",
                "FL.5_DEADLINE_DATE": "deadlineDate",
                "FL.6_Would_you_like_a_Return_Copy_": "returnCopyFlag",
                "FL.7_Is_this_an_electronic_copy_of_an_official_filing_submitted_in_paper_format_": "confirmingCopyFlag",
                "FL.8_Notify_via_Filing_Website_only_": "overrrideInternetFlag",
                "FL.9_Notification_Email": "notificationEmailAddress",
                "FL.10_Ticker_or_Other_Identifier_for_Fund": "tickerOrOtherIdentifier",
                "CP.1_Report_for_the_Calendar_Year_or_Quarter_Ended": "reportCalendarOrQuarter",
                "CP.2_Amendment_Info": "isAmendment",
                "CP.2.a_Amendment_Number": "amendmentNo",
                "CP.2.b_Amendment_Type": "amendmentType",
                "CP.2.c.i_Reason_for_Non_Confidentiality": "reasonForNonConfidentiality",
                "CP.2.c.ii_Date_Denied_or_Expired": "confDeniedExpired",
                "CP.2.c.iii_Date_Reported": "dateReported",
                "CP.3_Institutional_Investment_Manager_Filing_this_Report": "name",
                "CP.4_Name": "name",
                "CP.5_Street_1": "com:street1",
                "CP.6_Street_1": "com:street2",
                "CP.7_City": "com:city",
                "CP.8_State_Or_Country": "com:stateOrCountry",
                "CP.9_Zip_Code": "com:zipCode",
                "CP.11_Form_13F_File_Number": "form13FFileNumber",
                "CP.12_Do_you_wish_to_provide_information_pursuant_to_Special_Instruction_5_": "provideInfoForInstruction5",
                "CP.13_Additional_Information": "additionalInformation ",
                "CP_14_1_cik": "cik",
                "CP_14_2_Name": "name",
                "CP_14_3_CRD_Number": "crdNumber",
                "CP_14_4_SEC_File_Number": "secFileNumber",
                "CP_14_5_Form_13F_File_Number": "form13FFileNumber",
                "S.1_Name": "name",
                "S.2_Title": "title",
                "S.3_Phone": "phone",
                "S.4_Signature": "signature",
                "S.5_City": "city",
                "S.6_State_or_Country": "stateOrCountry",
                "S.7_Date": "signatureDate",
                "SP.1_Confidential_information_has_been_omitted": "confidentialOmitted",
                "Number_of_Other_Included_Managers": "otherIncludedManagersCount",
                "Form_13F_Information_table_Entry_Total": "tableEntryTotal ",
                "Form_13F_Information_table_Value_Total": "tableValueTotal",
                "SP.2.1_Sequence_Number": "sequenceNumber",
                "SP.2.2_CIK": "cik",
                "SP.2.3_CRD_Number": "crdNumber",
                "SP.2.4_SEC_File_Number": "secFileNumber",
                "SP_2_1_Sequence_Number": "sequenceNumber.",
                "SP_2_2_CIK": "cik",
                "SP_2_3_CRD_Number": "crdNumber",
                "SP_2_4_SEC_File_Number": "secFileNumber",
                "IT_1_Name_of_issuer": "nameOfIssuer",
                "IT_2_Title_of_class": "titleOfClass",
                "IT_3_CUSIP": "cusip",
                "IT_4_FIGI": "figi",
                "IT_5_Value__in_Thousands_": "value",
                "IT_6_Shares_Principal_Amount": "shrsOrPrnAmt",
                "IT_7_Shares_Principal": "sshPrnamt",
                "IT_8_Put_Call": "putCall",
                "IT_9_Investment_Discretion": "investmentDiscretion",
                "IT_10_Other_Manager": "otherManager",
                "IT_11_Voting_Authority": "votingAuthority",
                "IT_12_Sole": "Sole",
                "IT_13_Shared": "Shared",
                "IT_14_None": "None",
            }

            def modify_tags(element, tag_name_mapping):
                """Recursively modify tag names based on the mapping."""
                if element.tag in tag_name_mapping:
                    element.tag = tag_name_mapping[element.tag]
                for child in element:
                    modify_tags(child, tag_name_mapping)

            # Save the modified XML document
            root = ET.fromstring(xml_string)

            modify_tags(root, tag_name_mapping)

            # Add the namespace declaration to the root element
            root.set(f"xmlns:{namespace_prefix}", namespace_uri)

            # Convert the modified XML tree back to a string
            modified_xml_string = ET.tostring(root, encoding="unicode")

            # Save the modified XML document to a file
            with open("modified_xml_file.xml", "w", encoding="utf-8") as file:
                file.write(modified_xml_string)
            pass

            filer_ccc = filer_info_fields.get("FL.2_Filer_CIK_1", "Form")
            date_part = datetime.datetime.now().strftime("%Y%m%d%H%M")
            filename = f"13F_{filer_ccc}_{date_part}.xml"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(modified_xml_string)
            st.success(f"XMLFILE'{filename}' has been downloaded.")
            upload_file_to_local_directory(filename)
            upload_file_to_snowflake_stage(filename)


cover_page_form_fields_list = [
    ("SP.2.1 Sequence Number", "text_input", None),
    ("SP.2.2 CIK", "text_input", None),
    ("SP.2.3 CRD Number", "text_input", None),
    ("SP.2.4 SEC File Number", "text_input", None),
    ("SP.2.5 File Number", "text_input", None),
    ("SP.2.6 Name", "text_input", None),
]

form_Selection(cover_page_form_fields_list, {})

# Close the cursor and connection
cur.close()
conn.close()
