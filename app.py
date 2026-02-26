import os
import json
import streamlit as st
from groq import Groq
from tools import handle_tool_call
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Monday BI Agent", layout="wide")

st.title("📊 Monday.com Business Intelligence Agent")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a Business Intelligence AI agent. Ask clarifying questions if required parameters are missing. Call tools only when enough information is available.\n"
                "When needed, call the appropriate function tool.\n"
                "After receiving tool results, respond in plain English.\n"
                "Do not call any additional functions.\n"
                "All monetary values are in INR.\n"
                "Base answers strictly on tool outputs."
            )
        }
    ]

if "trace" not in st.session_state:
    st.session_state.trace = []

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a founder-level business question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
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
                    "sector": {"type": "string"},
                    "time_period": {"type": "string"},
                    "metric_type": {
                        "type": "string",
                        "enum": ["pipeline", "revenue", "work_orders", "summary"]
                    }
                    }
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
