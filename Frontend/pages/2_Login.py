# login.py (Streamlit Frontend)

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")  # Adjust if different

# Streamlit UI for Log In
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Log In")

    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Log In"):
        if username and password:
            payload = {
                "username": username,
                "password": password
            }
            response = requests.post(f"{API_URL}/login/", data=payload)
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.success(f"Welcome, {username}!")
                st.session_state['logged_in'] = True
                st.session_state['token'] = token
                st.session_state['username'] = username
                # Optionally redirect or reload the page
            else:
                error = response.json().get("detail", "An error occurred.")
                st.error(f"Login failed: {error}")
        else:
            st.error("Please fill in all fields.")

    # Link to the sign-up page
    st.write("Don't have an account? [Sign Up here](signup)")
    st.write("[Forgot Password?](forgot_password)")

else:
    st.write(f"Hello, {st.session_state['username']}! You are logged in.")
    st.write("You can now access the Meal Recommendation page.")
    # Optionally add a logout button
    if st.button("Log Out"):
        st.session_state['logged_in'] = False
        st.session_state['token'] = None
        st.session_state['username'] = None
        st.success("You have been logged out.")
