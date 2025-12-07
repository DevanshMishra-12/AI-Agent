# app.py

import streamlit as st
import asyncio

# Import everything needed from your original file
# Make sure the filename matches: firecrawl_mcp_agent.py
from firecrawl_mcp_agent import (
    ClientSession,
    StdioServerParameters,
    stdio_client,
    load_mcp_tools,
    create_react_agent,
    model,
    server_params,
)

# -------------------------------------------------------------------
#                   AGENT CALL (REUSING ORIGINAL SETUP)
# -------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful assistant that can scrape websites, "
    "crawl pages, and extract data using firecrawls tools. "
    "Think step by step and use the tools when necessary."
)

def get_initial_messages():
    """Initial messages list with system prompt."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

async def _agent_call_async(messages):
    """
    Async function that:
    - Uses the SAME model and server_params from the original file
    - Starts the Firecrawl MCP server over stdio
    - Loads MCP tools
    - Creates a LangGraph ReAct agent
    - Returns the latest assistant message content
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            response = await agent.ainvoke({"messages": messages})
            return response["messages"][-1].content

def call_agent(messages):
    """
    Sync wrapper around the async agent call.
    Streamlit code is synchronous, so we use asyncio.run here.
    """
    return asyncio.run(_agent_call_async(messages))

# -------------------------------------------------------------------
#                          STREAMLIT UI
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Firecrawl MCP Web Agent",
    page_icon="🕷️",
    layout="wide"
)

# 🔹 Custom CSS for a clean dark chat UI
st.markdown(
    """
    <style>
    .main {
        background-color: #020617;
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
    .chat-header {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        background: linear-gradient(90deg, #38bdf8, #a855f7);
        -webkit-background-clip: text;
        color: transparent;
    }
    .chat-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 0.75rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🔹 Sidebar
with st.sidebar:
    st.title("🕷️ Firecrawl Agent")
    st.markdown(
        """
        This agent can:

        - 🌐 Scrape websites  
        - 🕸 Crawl multiple pages  
        - 📊 Extract structured data  

        **Tech stack:**
        - LangGraph ReAct Agent  
        - MCP (Firecrawl)  
        - OpenAI `gpt-4o-mini` (from original file)  
        - Streamlit frontend  
        """
    )
    st.markdown("---")
    st.markdown("💡 Try prompts like:")
    st.code("Scrape https://example.com and summarize it.")
    st.code("Crawl https://wikipedia.org and list internal links.")
    st.code("Extract all headings and links from this URL: ...")
    st.markdown("---")
    if st.button("🔁 Reset chat"):
        st.session_state.messages = get_initial_messages()
        st.session_state.display_messages = []
        st.success("Conversation reset!")

# 🔹 Session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = get_initial_messages()

if "display_messages" not in st.session_state:
    # Only user + assistant messages for displaying in chat
    st.session_state.display_messages = []

# 🔹 Header
st.markdown('<div class="chat-header">Firecrawl Web Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="chat-subtitle">Ask me to scrape, crawl, and extract data from any website using Firecrawl MCP tools.</div>',
    unsafe_allow_html=True
)

# 🔹 Show past chat messages
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🔹 Chat input
user_input = st.chat_input("What do you want me to scrape or crawl?")

if user_input:
    # 1. Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input[:175000]})
    st.session_state.display_messages.append({"role": "user", "content": user_input})

    # 2. Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # 3. Call the agent using original setup
    with st.chat_message("assistant"):
        with st.spinner("Thinking with Firecrawl tools..."):
            try:
                answer = call_agent(st.session_state.messages)
            except Exception as e:
                answer = f"⚠️ Error while calling agent: `{e}`"

            st.markdown(answer)

    # 4. Save assistant answer
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.display_messages.append({"role": "assistant", "content": answer})
