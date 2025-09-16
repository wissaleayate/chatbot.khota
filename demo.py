import streamlit as st
import fitz  
import requests

# === CONFIG ===
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"  
FAQ = {
    "hello": "👋 Hello! How can I help you today?",
    "hello there": "👋 Hello! How can I help you today?",
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
    result = response.json()
    print(result)  # يخرجلك الرد كامل من API

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    elif "error" in result:
        return f"⚠️ API Error: {result['error'].get('message', 'Unknown error')}"
    else:
        return f"⚠️ Unexpected API response: {result}"

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
