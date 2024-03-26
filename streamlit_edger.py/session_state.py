# session_state.py
import streamlit as st

class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_session_state(**kwargs):
    if not hasattr(st.session_state, 'state'):
        st.session_state.state = SessionState(**kwargs)
    return st.session_state.state
