import streamlit as st
from db import init_db

st.set_page_config(page_title="AidLoop", page_icon="🔄", layout="centered")

# Initialise the database on first load
init_db()

pg = st.navigation(
    [
        st.Page("home.py", title="Home", default=True),
        st.Page("raise_requirement.py", title="🙋 Raise a Requirement"),
        st.Page("fulfill_requirement.py", title="🤝 Fulfill a Requirement"),
        st.Page("fulfilled.py", title="✅ Fulfilled Requirements"),
    ]
)
pg.run()