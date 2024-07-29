import streamlit as st
import sklearn as sc
from streamlit_navigation_bar import st_navbar
from streamlit_supabase_auth import login_form, logout_button
from streamlit_antd_components.widgets import steps
from supabase import create_client, Client
import joblib as joblib 
import os
import datetime
import pandas as pd
#from model import FraudDetectionPipeline  # Import the class from model.py

# Supabase credentials
#os.environ["SUPABASE_URL"] 
#os.environ["SUPABASE_KEY"] 
st.set_page_config(layout="wide", page_title="Fraud Detection")

# Add custom CSS for styling
st.markdown("""
  <style>
  body {
  font-family: 'Arial', sans-serif;
  }
  .stButton > button {
  background-color: #2c3e50;
  color: #ecf0f1;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  transition: background-color 0.3s ease;
  }
  .stButton > button:hover {
  background-color: #34495e;
  }
  .stTextInput > div > input {
  border: 2px solid #2c3e50;
  border-radius: 0.5rem;
  padding: 0.75rem;
  font-size: 1rem;
  }
  .stFormSubmitButton > button {
  background-color: #16a085;
  color: #ecf0f1;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  transition: background-color 0.3s ease;
  }
  .stFormSubmitButton > button:hover {
  background-color: #1abc9c;
  }
  </style>
""", unsafe_allow_html=True)

# Session state management
if "btn_ready" not in st.session_state:
  st.session_state["btn_ready"] = False
if "user" not in st.session_state:
  st.session_state["user"] = None
if "login_success" not in st.session_state:
  st.session_state["login_success"] = False
if "access_pages" not in st.session_state:
  st.session_state["access_pages"] = False
if "payment_provider" not in st.session_state:
  st.session_state["payment_provider"] = "Select"
if "details_filled" not in st.session_state:
  st.session_state["details_filled"] = False
if "transaction_filled" not in st.session_state:
  st.session_state["transaction_filled"] = False
if "name_filled" not in st.session_state:
  st.session_state["name_filled"] = False

# Define pages
pages = ["Home", "Details", "Transaction", "Predict", "User Profile"]
style = {
  "nav": {
      "background-color": "#2c3e50", 
      "display": "flex",
      "justify-content": "left",
      "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.1)"  
  },
  "div": {
      "max-width": "auto", 
  },
  "span": {
      "border-radius": "0.5rem",
      "color": "#ecf0f1",  
      "padding": "0.75rem 1rem", 
      "font-family": "Arial, sans-serif", 
      "transition": "background-color 0.3s ease"  
  },
  "active": {
      "background-color": "rgba(255, 255, 255, 0.2)",  
  },
  "hover": {
      "background-color": "rgba(255, 255, 255, 0.1)",  
  },
}
options = {
  "show_menu": False,
  "show_sidebar": False,
  "use_padding": False
}

# Define country codes
country_codes = {
  "Kenya": "+254",
  "United States": "+1",
  "United Kingdom": "+44",
  "Canada": "+1",
  "Australia": "+61",
  "India": "+91"
  # Add more countries and codes as needed
}

# Define payment providers
payment_providers = [
  "JCB 16 digit", 
  "VISA 13 digit", 
  "Diner Club", 
  "MasterCard", 
  "Maestro", 
  "Voyager", 
  "Discover", 
  "VISA 16 digit", 
  "American Express"
]

def show_login_form():
  st.header("Fraud Detection")
  step = steps(items=["Welcome", "Register", "Login", "Ready"], size="md", variant="default")

  if step == "Welcome":
      st.markdown(open("welcome.html").read(), unsafe_allow_html=True)

  if step == "Register":
      session = login_form(url=os.environ["SUPABASE_URL"], apiKey=os.environ["SUPABASE_KEY"], providers=None)
      if session:
          st.toast("Check your email confirmation message")
  if step == "Login":
      session = login_form(url=os.environ["SUPABASE_URL"], apiKey=os.environ["SUPABASE_KEY"])
      if session:
          st.session_state["login_success"] = True
          st.write("Logged in successfully")
#if session
  if step == "Ready":
      if st.session_state["login_success"] == True:
          #if st.session_state["login_success"]:
          st.write("Ready and continue")
          if st.button(label="Continue", type="primary", key="continue_button"):
              st.session_state["access_pages"] = True
      else:
          st.warning("Please log in or register and click continue to proceed.")

intro = st.empty()
with intro.container():
  show_login_form()

if st.session_state["access_pages"]:
  intro.empty()
  page = st_navbar(pages, styles=style, options=options)
  
  # Define functionality for each page
  if page == "Home":
      current_hour = datetime.datetime.now().hour
      greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
      st.header(f"{greeting}! Welcome to the Fraud Detection System.")
      st.markdown(open("welcome.html").read(), unsafe_allow_html=True)
  
  elif page == "Details":
      st.header("Customer Details")
      with st.form(key="details_form"):
          customer_email = st.text_input("Customer Email:", placeholder="Enter customer email")
          country = st.selectbox("Country:", list(country_codes.keys()))
          phone_number = st.text_input("Phone Number:", placeholder="Enter phone number")
          customer_phone = f"{country_codes[country]} {phone_number}"
          customer_device = st.text_input("Customer Device (Serial Number):", placeholder="Enter customer device serial number")
          customer_ip = st.text_input("Customer IP Address:", placeholder="Enter customer IP address")
          customer_billing_address = st.text_input("Customer Billing Address:", placeholder="Enter customer billing address")
          no_of_transactions = st.number_input("Number of Transactions:", min_value=0)
          no_of_orders = st.number_input("Number of Orders:", min_value=0)
          no_of_payments = st.number_input("Number of Payments:", min_value=0)
          submit_button = st.form_submit_button(label="Submit")
          if submit_button:
              if not customer_email or not phone_number or not customer_device or not customer_ip or not customer_billing_address:
                  st.error("Please fill out all the required fields.")
              else:
                  st.session_state["customer_email"] = customer_email
                  st.session_state["customer_phone"] = customer_phone
                  st.session_state["details_filled"] = True
                  st.success("Customer details saved successfully.")
                  customer_data = {
                      "customerEmail": customer_email,
                      "customerPhone": customer_phone,
                      "customerDevice": customer_device,
                      "customerIpAddress": customer_ip,
                      "customerBillingAddress": customer_billing_address,
                      "No_Transactions": no_of_transactions,
                      "No_Orders": no_of_orders,
                      "No_Payments": no_of_payments,
                  }
                  pd.DataFrame(customer_data, index=[1]).to_csv("customer_submitted.csv")
  
  elif page == "Transaction":
      st.header("Transaction Details")
      with st.form(key="transaction_form"):
          customer_email = st.text_input("Customer Email:", placeholder="Enter customer email")
          transaction_id = st.text_input("Transaction ID:", placeholder="Enter transaction ID")
          order_id = st.text_input("Order ID:", placeholder="Enter order ID")
          payment_method_id = st.text_input("Payment Method ID:", placeholder="Enter payment method ID")
          payment_method_registration_failure = st.selectbox("Payment Method Registration Failure:", ["Yes", "No"])
          payment_method_type = st.selectbox("Payment Method Type:", ["Card", "Bitcoin", "Apple Pay", "PayPal"])
          payment_method_provider = st.selectbox("Payment Method Provider:", payment_providers)
          transaction_amount = st.number_input("Transaction Amount:", min_value=0.0)
          payment_failed = st.selectbox("Payment Failed:", ["Yes", "No"])
          order_state = st.selectbox("Order State:", ["Fulfilled", "Pending"])
          submit_button = st.form_submit_button(label="Submit")
          if submit_button:
              if not customer_email or not transaction_id or not order_id or not payment_method_id or not payment_method_type or not payment_method_provider:
                  st.error("Please fill out all the required fields.")
              else:
                  st.session_state["customer_email"] = customer_email
                  st.session_state["transaction_filled"] = True
                  st.success("Transaction details saved successfully.")
                  transaction_data = {
                      "customerEmail": customer_email,
                      "transactionId": transaction_id,
                      "orderId": order_id,
                      "paymentMethodId": payment_method_id,
                      "paymentMethodRegistrationFailure": payment_method_registration_failure,
                      "paymentMethodType": payment_method_type,
                      "paymentMethodProvider": payment_method_provider,
                      "transactionAmount": transaction_amount,
                      "paymentFailed": payment_failed,
                      "orderState": order_state,
                  }
                  pd.DataFrame(transaction_data, index=[1]).to_csv("transaction_submitted.csv")
  
  elif page == "Predict":
      st.header("Fraud Prediction")
      try:
          # Load customer and transaction details
          customer_details = pd.read_csv("customer_submitted.csv")
          transaction_details = pd.read_csv("transaction_submitted.csv")
          
          # Initialize the fraud detection pipeline
          pipeline = FraudDetectionPipeline(customer_details, transaction_details)
          
          # Preprocess the data and make predictions
          preprocessed_data = pipeline.preprocess_data()
          predictions = pipeline.predict_fraud(preprocessed_data)
          
          st.write("Fraud Prediction Results:")
          st.write(predictions)
      except FileNotFoundError as e:
          st.error(f"Error: {e}")
  
  elif page == "User Profile":
      st.header("User Profile")
      customer_email = st.session_state.get("customer_email", "")
      user_email = st.session_state.get("user", "")
      if st.session_state["details_filled"] and st.session_state["transaction_filled"]:
          if not customer_email:
              st.error("No customer email found. Please fill out the details and transaction pages.")
          else:
              if customer_email != user_email:
                  st.error("Fraudulent activity detected: The customer email does not match the registered email.")
              else:
                  st.write(f"Customer Email: {customer_email}")
                  st.write("User Profile Information:")
                  # Display other user profile information here
      else:
          st.warning("Please fill out the details and transaction pages before viewing the user profile.")
      if st.button("Logout"):
          st.session_state.clear()  # Clear session state
          st.experimental_rerun()   # Redirect to the welcome page