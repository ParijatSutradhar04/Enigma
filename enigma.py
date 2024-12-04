import streamlit as st
from datetime import datetime
import pandas as pd

# File to store messages (locally or in GitHub repo)
DATA_FILE = "messages.csv"

# Initialize the data file if it doesn't exist
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Sender", "Timestamp", "Message"])
    df.to_csv(DATA_FILE, index=False)

# App title
st.title("Enigma Messaging System")

# Tabs for "Send Message" and "View Messages"
tab1, tab2 = st.tabs(["Send Message", "View Messages"])

# Tab 1: Send Message
with tab1:
    st.header("Send a Message")
    sender = st.text_input("Your Name", placeholder="Enter your name")
    message = st.text_area("Encrypted Message", placeholder="Enter your encrypted message")
    if st.button("Send"):
        if sender and message:
            # Add new message to the data file
            new_entry = {"Sender": sender, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Message": message}
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Message sent successfully!")
        else:
            st.error("Please fill out both fields.")

# Tab 2: View Messages
with tab2:
    st.header("Messages")
    try:
        df = pd.read_csv(DATA_FILE)
        for _, row in df.iterrows():
            st.write(f"**{row['Sender']}** ({row['Timestamp']}):")
            st.write(f"{row['Message']}")
            st.write("---")
    except FileNotFoundError:
        st.error("No messages found yet!")

# Footer
st.sidebar.markdown("### About")
st.sidebar.info("This is a simple Enigma Messaging System built with Streamlit.")
