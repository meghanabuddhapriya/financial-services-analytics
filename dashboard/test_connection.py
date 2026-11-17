import streamlit as st
from db_connection import test_connection

st.title("Financial Analytics - Database Test")

try:
    result = test_connection()

    st.success("PostgreSQL connection successful!")

    st.write("Database:", result[0])
    st.write("User:", result[1])

except Exception as e:
    st.error(f"Connection failed: {e}")
