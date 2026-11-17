
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


@st.cache_resource
def get_engine():
    config = st.secrets["postgresql"]

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=config["username"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
        database=config["database"]
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True
    )

    return engine


def test_connection():
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        return result.fetchone()
