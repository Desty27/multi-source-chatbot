import streamlit as st
import tempfile
import os
from src.chatbot import ChatBot
from src.file_processor import process_uploaded_file

# App config
st.set_page_config(
    page_title="Multi-Source ChatBot",
    page_icon=":robot:",
    layout="wide"
)

def initialize_session():
    if 'bot' not in st.session_state:
        st.session_state.bot = ChatBot()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def handle_file_upload():
    uploaded_files = st.sidebar.file_uploader(
        "Upload files (PDF/Images)",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                content = process_uploaded_file(tmp.name)
                st.session_state.bot.add_context(content)
            st.sidebar.success(f"Processed {uploaded_file.name}")

def display_chat():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    initialize_session()
    
    st.title("Multi-Source ChatBot ")
    st.markdown("Upload files and ask questions!")
    
    handle_file_upload()
    display_chat()
    
    if question := st.chat_input("Ask your question..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.spinner("Thinking..."):
            response = st.session_state.bot.generate_response(question)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()