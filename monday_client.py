import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

MONDAY_API_KEY = get_secret("MONDAY_API_KEY")
DEALS_BOARD_ID = get_secret("DEALS_BOARD_ID")
WORK_BOARD_ID = get_secret("WORK_BOARD_ID")

MONDAY_URL = "https://api.monday.com/v2"

def fetch_board(board_id):
    if not MONDAY_API_KEY:
        return {"errors": [{"message": "Missing MONDAY_API_KEY"}]}

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json",
    }

    query = f"""
    query {{
      boards(ids: {board_id}) {{
        id
        name
        columns {{
          id
          title
          type
        }}
        items_page(limit: 500) {{
          items {{
            id
            name
            column_values {{
              id
              text
              value
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(
        MONDAY_URL,
        headers=headers,
        json={"query": query},
    )

    return response.json()

def fetch_deals():
    return fetch_board(DEALS_BOARD_ID)

def fetch_work_orders():
    return fetch_board(WORK_BOARD_ID)
