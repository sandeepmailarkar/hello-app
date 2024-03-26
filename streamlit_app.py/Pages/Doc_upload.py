import streamlit as st
import snowflake.connector
import os
import json

# Streamlit app title
st.title("Snowflake Document Upload")


# Function to upload file to Snowflake stage
def upload_to_snowflake(file, conn):
    cursor = conn.cursor()
    # Specify the full path to the stage in the PUT command
    put_command = f"PUT file://{file.name} @DOCUMENT_STAGE"
    cursor.execute(put_command)
    conn.commit()
    st.success("File uploaded to Snowflake stage successfully.")


# Function to establish a connection to Snowflake
def connect_to_snowflake():
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
    return conn


# Connect to Snowflake
conn = connect_to_snowflake()

# File uploader widget
uploaded_file = st.file_uploader("Choose a file to upload to Snowflake")

# Check if a file has been uploaded
if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Upload the file to Snowflake stage
    upload_to_snowflake(uploaded_file, conn)

    # Delete the temporary file
    os.remove(uploaded_file.name)

# Close the connection
conn.close()
