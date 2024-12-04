import streamlit as st
from datetime import datetime
import pandas as pd

# Enigma Machine Implementation
class Plugboard:
    def __init__(self, connections=""):
        self.wiring = self.create_wiring(connections)

    def create_wiring(self, connections):
        wiring = {chr(i): chr(i) for i in range(65, 91)}  # A-Z mapping to itself initially
        for connection in connections.split():
            a, b = connection[0], connection[1]
            wiring[a], wiring[b] = b, a
        return wiring

    def encode(self, char):
        return self.wiring.get(char, char)

class Rotor:
    def __init__(self, rotor_no, position='A'):
        self.rotor_wirings = ["EKMFLGDQVZNTOWYHXUSPAIBRCJ", "AJDKSIRUXBLHWTMCQGZNPYFVOE", 
                              "BDFHJLCPRTXVZNYEIWGAKMUSQO", "GELUYASHMJDKWFIVNCZPQROXTB", 
                              "NMYXOQHAKREDVSITUPLJWBGZCF"]
        self.notch_position = ['Q', 'E', 'V', 'W', 'F']
        self.wiring = self.rotor_wirings[rotor_no]
        self.notch = self.notch_position[rotor_no]
        self.position = position

    def encode_forward(self, char):
        index = (ord(char) - 65 + ord(self.position) - 65) % 26
        return self.wiring[index]

    def encode_backward(self, char):
        index = self.wiring.index(char)
        index = (index - (ord(self.position) - 65)) % 26
        return chr(index + 65)

    def step(self):
        self.position = chr((ord(self.position) - 65 + 1) % 26 + 65)
        return self.position == self.notch

class Reflector:
    def __init__(self):
        self.wiring = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

    def reflect(self, char):
        index = ord(char) - 65
        return self.wiring[index]

class EnigmaMachine:
    def __init__(self, rotor_config, plugboard_config):
        self.rotors = [Rotor(rotor_no=key, position=value) for key, value in rotor_config.items()]
        self.reflector = Reflector()
        self.plugboard = Plugboard(plugboard_config)

    def encode(self, char):
        if char.isalpha():
            char = char.upper()
            char = self.plugboard.encode(char)

            for rotor in self.rotors:
                char = rotor.encode_forward(char)

            char = self.reflector.reflect(char)

            for rotor in reversed(self.rotors):
                char = rotor.encode_backward(char)

            char = self.plugboard.encode(char)

            for i in range(len(self.rotors)):
                if not self.rotors[i].step():
                    break

        return char

# Utility functions for encryption and decryption
def enigma_encrypt(rotor_config, plugboard_wiring, message):
    enigma = EnigmaMachine(rotor_config, plugboard_wiring)
    return "".join(enigma.encode(char) for char in message)

# Streamlit App
st.title("Enigma Messaging System")

DATA_FILE = "messages.csv"

try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Sender", "Timestamp", "Message"])
    df.to_csv(DATA_FILE, index=False)

tab1, tab2 = st.tabs(["Send Message", "View Messages"])

# Tab 1: Send Message
with tab1:
    st.header("Send a Message")

    sender = st.text_input("Your Name", placeholder="Enter your name")
    rotor_config = st.text_area("Rotor Config", placeholder="Enter as JSON (e.g., {0: 'A', 1: 'B', 2: 'C'})")
    plugboard_wiring = st.text_input("Plugboard Wiring", placeholder="Enter plugboard wiring (e.g., AB CD EF)")
    message = st.text_area("Message", placeholder="Enter the message to encrypt")

    if st.button("Send"):
        if sender and rotor_config and plugboard_wiring and message:
            try:
                rotor_config = eval(rotor_config)  # Convert input string to dictionary
                encrypted_message = enigma_encrypt(rotor_config, plugboard_wiring, message)
                new_entry = {"Sender": sender, 
                             "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                             "Message": encrypted_message}
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Message encrypted and sent successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill out all fields.")

# Tab 2: View Messages
with tab2:
    st.header("Messages")
    try:
        df = pd.read_csv(DATA_FILE)
        rotor_config = st.text_area("Rotor Config for Decryption", placeholder="Enter rotor config for decryption")
        plugboard_wiring = st.text_input("Plugboard Wiring for Decryption", 
                                         placeholder="Enter plugboard wiring for decryption")
        if rotor_config and plugboard_wiring:
            try:
                rotor_config = eval(rotor_config)  # Convert input string to dictionary
                for _, row in df.iterrows():
                    decrypted_message = enigma_encrypt(rotor_config, plugboard_wiring, row["Message"])
                    st.write(f"**{row['Sender']}** ({row['Timestamp']}):")
                    st.write(f"Decrypted Message: {decrypted_message}")
                    st.write("---")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Enter decryption keys to view decrypted messages.")
    except FileNotFoundError:
        st.error("No messages found yet!")

st.sidebar.markdown("### About")
st.sidebar.info("This is an Enigma Machine for encryption and decryption.")
