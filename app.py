import os
import json
import streamlit as st
from groq import Groq
from tools import handle_tool_call
from dotenv import load_dotenv

# Load local .env only once
load_dotenv()

def get_secret(key):
    """
    Safely fetch secret from:
    1. Streamlit Cloud secrets
    2. Local environment (.env)
    """
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

groq_key = get_secret("GROQ_API_KEY")
monday_key = get_secret("MONDAY_API_KEY")

if not groq_key:
    st.error("Missing GROQ_API_KEY")
    st.stop()

if not monday_key:
    st.error("Missing MONDAY_API_KEY")
    st.stop()

client = Groq(api_key=groq_key)

st.set_page_config(page_title="Monday BI Agent", layout="wide")

st.title("📊 Monday.com Business Intelligence Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a Business Intelligence AI agent. Ask clarifying questions if required parameters are missing.\n"
                "When needed, call 'run_bi_query' with the appropriate sector.\n"
                "If the user asks follow-up questions (e.g., 'and for manufacturing?'), use the context of previous queries.\n"
                "All monetary values are in INR. Base answers strictly on tool outputs."
            )
        }
    ]

if "last_sector" not in st.session_state:
    st.session_state.last_sector = None

if "trace" not in st.session_state:
    st.session_state.trace = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a founder-level business question...")

if user_input:
    # Prepare context hint for the LLM
    context_hint = f" (Context: Last sector discussed was {st.session_state.last_sector})" if st.session_state.last_sector else ""
    
    st.session_state.messages.append({"role": "user", "content": user_input + context_hint})
    st.chat_message("user").write(user_input)
    
    tools = [
        {
            "type": "function",
            "function": 
                {
                    "name": "run_bi_query",
                    "description": "Run a business intelligence query across Deals and Work Orders boards.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sector": {
                                "type": "string",
                                "description": "The business sector to analyze"
                            },
                            "time_period": {
                                "type": "string",
                                "description": "Time filter like 'this quarter', 'last quarter', or 'Q2 2025'"
                            }
                        },
                        "required": ["sector"]
                    }
                }
        }
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            tools=tools,
            temperature=0
        )
    except Exception as e:
        st.error(f"LLM Error: {e}")
        st.stop()

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        # Store context
        if "sector" in args:
            st.session_state.last_sector = args["sector"]

        result = handle_tool_call(tool_name, args, st.session_state.trace)
        final_text = result["final_answer"]
    else:
        final_text = message.content

    st.session_state.messages.append({"role": "assistant", "content": final_text})
    st.chat_message("assistant").write(final_text)

# Sidebar Trace
st.sidebar.title("🔧 Tool Trace")
for log in st.session_state.trace:
    st.sidebar.write(log)
