import os
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_BOARD_ID = os.getenv("WORK_BOARD_ID")

MONDAY_URL = "https://api.monday.com/v2"

def fetch_board(board_id):

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
