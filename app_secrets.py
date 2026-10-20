"""Look up a secret from the environment or Streamlit secrets without triggering Streamlit's red banner."""
import os

import streamlit as st


def get_secret(name, section=None, field=None):
    """Environment variable `name`, else st.secrets[name], else st.secrets[section][field]. None if not set."""
    if os.environ.get(name):
        return os.environ[name]
    paths = [os.path.expanduser("~/.streamlit/secrets.toml"), os.path.join(os.getcwd(), ".streamlit", "secrets.toml")]
    if not any(os.path.exists(p) for p in paths):
        return None  # touching st.secrets with no file would render an error banner
    try:
        s = st.secrets
        if name in s:
            return s[name]
        if section and field and section in s and field in s[section]:
            return s[section][field]
    except Exception:
        pass
    return None
