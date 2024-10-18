import streamlit as st
import requests

# Streamlit UI for Sign Up
st.title("Sign Up")

username = st.text_input("Enter your username")
email = st.text_input("Enter your email")
password = st.text_input("Enter your password", type="password")

# FastAPI endpoint URL for signup
API_URL = "https://recommend-meal.osc-fr1.scalingo.io/signup"  # Update this if your FastAPI runs on a different URL

if st.button("Sign Up"):
    if username and email and password:
        payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        response = requests.post(API_URL, json=payload)

        if response.status_code == 201:
            st.success("Sign up successful! You can now log in.")
        else:
            st.error(response.json().get("detail", "An error occurred."))
    else:
        st.error("Please fill in all fields.")

# Link to the login page
st.write("Already have an account? [Log In here](../Login)")
