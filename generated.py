import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def main():
    # Set page config with icon
    st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
    
    # Sidebar for additional options
    with st.sidebar:
        st.subheader("Settings")
        selected_model = st.selectbox("Choose Model", ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"])
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        # Allow user to upload files
        uploaded_file = st.file_uploader("Upload a file (optional)")
        if uploaded_file:
            st.write("File uploaded:", uploaded_file.name)
    
    # Add header and initial instructions
    st.title("AI Assistant 🤖")
    st.write("Feel free to ask me anything, or upload a file to start!")

    # Initialize session state for chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input and error handling
    if prompt := st.chat_input("What's on your mind?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True
                )
                
                # Initialize empty response
                full_response = ""
                
                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                # Final response
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})

    # Delay to control rate limiting
    time.sleep(0.5)

if __name__ == "__main__":
    main()
