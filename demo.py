import streamlit as st
import fitz  
import requests

# === CONFIG ===
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"  
FAQ = {
    "hello": "👋 Hello! How can I help you today?",
    "who are you": "I'm an AI assistant made with Python and Streamlit by Wissale!",
    "how to upload file": "Click the 'Upload a PDF or TXT file' button above to add your file.",
    "bye": "Goodbye 👋, see you soon!"}

# === FUNCTIONS ===
def extract_text(file):
    if file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    else:
        return file.read().decode("utf-8")

def ask_question(context, question):

    q_lower = question.lower().strip()
    if q_lower in FAQ:
        return FAQ[q_lower]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "Python Student Demo App",
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Answer based only on the context provided."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# === STREAMLIT UI ===
st.set_page_config(page_title="AI File Q&A Chat")
st.title("📄 HIT File Q&A Chat")

uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

# Shared session state for chat and context
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = ""

if uploaded_file:
    context = extract_text(uploaded_file)
    st.session_state.context = context
    st.success("✅ File uploaded and context loaded!")

# Show previous chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_question = st.chat_input("Ask a question about the file")
if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_question(st.session_state.context, user_question)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
