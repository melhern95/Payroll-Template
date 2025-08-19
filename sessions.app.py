import streamlit as st
import pandas as pd
import datetime
import io
from openpyxl.styles import PatternFill

# ---------- Initial Setup ----------
st.set_page_config(page_title="Session Tracker", layout="centered")

# ---------- Aging Bucket Function ----------
def aging_bucket(days):
    if days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "31-60 days"
    elif days <= 90:
        return "61-90 days"
    else:
        return "90+ days"

# ---------- Initialize DataFrame ----------
if "df" not in st.session_state:
    try:
        st.session_state.df = pd.read_excel("sessions.xlsx")
    except FileNotFoundError:
        st.session_state.df = pd.DataFrame(columns=[
            "Client Initials", "Date of Service", "CPT Code", "Session Fee",
            "Payment Received", "Date of Payment", "Outstanding",
            "Days Outstanding", "Aging Bucket"
        ])

df = st.session_state.df

# ---------- Excel Export with Color ----------
def export_colored_excel(df, file_name="sessions.xlsx"):
    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sessions")
        ws = writer.sheets["Sessions"]
        
        # Find the Aging Bucket column
        aging_col_idx = None
        for idx, cell in enumerate(ws[1], start=1):
            if cell.value == "Aging Bucket":
                aging_col_idx = idx
                break
        
        color_map = {
            "Paid": "00C6EFCE",      # light green
            "0-30 days": "00C6EFCE", # green
            "31-60 days": "00FFEB9C",# yellow
            "61-90 days": "00F4B084",# orange
            "90+ days": "00FF0000"   # red
        }
        
        if aging_col_idx:
            for row in ws.iter_rows(min_row=2, min_col=aging_col_idx, max_col=aging_col_idx):
                cell = row[0]
                fill_color = color_map.get(cell.value, None)
                if fill_color:
                    cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

# ---------- Input Form ----------
st.title("📊 Therapy Session Tracker")

with st.form("session_entry"):
    client_initials = st.text_input("Client Initials")
    date_of_service = st.date_input("Date of Service", datetime.date.today())
    cpt_code = st.selectbox("CPT Code", ["90837", "90791"])
    session_fee = st.number_input("Session Fee ($)", min_value=0.0, step=10.0)
    payment_received = st.number_input("Payment Received ($)", min_value=0.0, step=10.0)

    unpaid = st.checkbox("Unpaid?")
    if unpaid:
        date_of_payment = None
    else:
        date_of_payment = st.date_input("Date of Payment", datetime.date.today())

    submitted = st.form_submit_button("Add Session")

if submitted:
    outstanding = session_fee - payment_received
    if unpaid or not date_of_payment:
