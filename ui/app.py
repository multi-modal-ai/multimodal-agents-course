import requests
import streamlit as st

# Configure the page
st.set_page_config(page_title="Sport Assistant Chat", page_icon="🏃", layout="centered")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the chat title
st.title("Sport Assistant Chat 🏃")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about sports?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send request to FastAPI endpoint
    try:
        response = requests.post(
            "http://api:8000/chat",  # Changed from localhost to service name
            json={"message": prompt},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get assistant's response
        assistant_response = response.json()["response"]

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response}
        )

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
