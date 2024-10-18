import streamlit as st
import requests

# URL of the FastAPI backend
API_URL = "https://recommend-meal.osc-fr1.scalingo.io/login/"

# Streamlit UI for Log In
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Log In")

    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Log In"):
        if username and password:
            # Send login request to FastAPI
            response = requests.post(API_URL, data={'username': username, 'password': password})

            if response.status_code == 200:
                token_data = response.json()
                st.session_state.logged_in = True
                st.session_state['access_token'] = token_data['access_token']  # Store access token
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Please fill in all fields.")

    # Link to the sign-up page
    st.write("Don't have an account? [Sign Up here](../Signup)")
    st.write("[Forgot Password?](../ForgotPassword)")

else:
    st.write("You are already logged in!")
    st.write("You can now access the Meal Recommendation page.")

    # Optional: Add a logout button
    if st.button("Log Out"):
        st.session_state.logged_in = False
        del st.session_state['access_token']  # Remove the token on logout
        st.success("You have been logged out.")
