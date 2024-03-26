# session_state_manager.py
import json
import os
import uuid
import streamlit as st

def get_session_id():
    """Generate or retrieve a unique session ID."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def save_session_state(session_id, state_data):
    """Save session state to a file."""
    # Convert the session state data to a serializable format
    serializable_state_data = {k: v for k, v in state_data.items() if isinstance(v, (int, float, str, list, dict, bool))}
    
    file_path = f"session_states/{session_id}.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(serializable_state_data, f)


def load_session_state(session_id):
    """Load session state from a file, handling errors gracefully."""
    file_path = f"session_states/{session_id}.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle the case where the file contains invalid JSON
            print(f"Warning: Invalid JSON data in {file_path}.")
            return {}  # Return an empty dictionary as a fallback
    else:
        # File does not exist, return an empty dictionary
        return {}
