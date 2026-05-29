import streamlit as st
import anthropic
st.set_page_config(page_title="AWS Architecture Assistant", page_icon="☁️")
st.title("☁️ AWS Architecture Assistant")
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert AWS solutions architect. 
You help customers design scalable, cost-effective AWS architectures.
Be concise but thorough. Ask clarifying questions when needed."""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = {"input": 0, "output": 0}

with st.sidebar:
    st.header("📊 Session Stats")
    st.metric("Input Tokens", st.session_state.total_tokens["input"])
    st.metric("Output Tokens", st.session_state.total_tokens["output"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.total_tokens = {"input": 0, "output": 0}
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about AWS architecture..."):

    # 1. Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 3. Keep only last 10 messages
    if len(st.session_state.messages) > 10:
        st.session_state.messages = st.session_state.messages[-10:]

    # 4. Call API and show response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=st.session_state.messages
            )
            assistant_message = response.content[0].text
            st.session_state.total_tokens["input"] += response.usage.input_tokens
            st.session_state.total_tokens["output"] += response.usage.output_tokens
            st.markdown(assistant_message)

    # 5. Add assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    # 6. Rerun to update sidebar token counts
    st.rerun()