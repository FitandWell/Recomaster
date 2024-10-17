# signup.py (Streamlit Frontend)

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")  # Adjust if different

# Streamlit UI for Sign Up
st.title("Sign Up")

username = st.text_input("Enter your username")
email = st.text_input("Enter your email")
password = st.text_input("Enter your password", type="password")

if st.button("Sign Up"):
    if username and email and password:
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(f"{API_URL}/signup/", json=payload)
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.success("Sign up successful! You are now logged in.")
            st.session_state['token'] = token
            st.session_state['username'] = username
            # Optionally redirect to another page or display more info
        else:
            error = response.json().get("detail", "An error occurred.")
            st.error(f"Sign up failed: {error}")
    else:
        st.error("Please fill in all fields.")

# Link to the login page
st.write("Already have an account? [Log In here](login)")
