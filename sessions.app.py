import pandas as pd
from datetime import datetime
import streamlit as st

# --- Config ---
excel_file = "sessions.xlsx"
cpt_fees = {
    "90837": 200,  # Fee for 90837
    "90791": 150   # Fee for 90791
}

# --- Load or create dataframe ---
try:
    df = pd.read_excel(excel_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "Client", "Date of Session", "CPT Code", "Session Fee",
        "Payment Received", "Date of Payment", "Outstanding",
        "Days Outstanding", "Aging Bucket"
    ])

# --- Helper functions ---
def calculate_outstanding(row):
    return max(row["Session Fee"] - row.get("Payment Received", 0), 0)

def calculate_days_outstanding(row):
    if pd.isna(row.get("Date of Payment")):
        days = (datetime.now() - pd.to_datetime(row["Date of Session"])).days
        return days
    return 0

def assign_aging_bucket(days):
    if days == 0:
        return "Paid"
    elif days <= 30:
        return "0-30"
    elif days <= 60:
        return "31-60"
    elif days <= 90:
        return "61-90"
    else:
        return "90+"

bucket_colors = {
    "Paid": "✅",
    "0-30": "🟡",
    "31-60": "🟠",
    "61-90": "🟣",
    "90+": "🔴"
}

# --- Streamlit UI ---
st.title("📊 Therapy Sessions Tracker")

st.sidebar.header("➕ Add a New Session")

with st.sidebar.form("session_form", clear_on_submit=True):
    client = st.text_input("Client Name")
    date_session = st.date_input("Date of Session")
    cpt_code = st.selectbox("CPT Code", ["90837", "90791"])
    payment_received = st.number_input("Payment Received", min_value=0.0, value=0.0, step=1.0)
    date_payment = st.date_input("Date of Payment (optional)", value=None)

    if st.form_submit_button("Add Session"):
        session_fee = cpt_fees[cpt_code]
        new_row = pd.DataFrame([{
            "Client": client,
            "Date of Session": pd.to_datetime(date_session),
            "CPT Code": cpt_code,
            "Session Fee": session_fee,
            "Payment Received": payment_received,
            "Date of Payment": pd.to_datetime(date_payment) if date_payment else pd.NaT
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        st.success("✅ Session added!")

# --- Calculations ---
if not df.empty:
    df["Outstanding"] = df.apply(calculate_outstanding, axis=1)
    df["Days Outstanding"] = df.apply(calculate_days_outstanding, axis=1)
    df["Aging Bucket"] = df["Days Outstanding"].apply(assign_aging_bucket)

    # Save to Excel
    df.to_excel(excel_file, index=False)

    # Show full table
    st.subheader("📑 Sessions Data")
    st.dataframe(df)

    # Show summary
    st.subheader("📌 Aging Summary")
    summary = df.groupby("Aging Bucket")["Outstanding"].sum().reset_index()
    summary["Bucket (with color)"] = summary["Aging Bucket"].map(bucket_colors) + " " + summary["Aging Bucket"]
    st.table(summary[["Bucket (with color)", "Outstanding"]])
else:
    st.info("No sessions yet. Add one using the sidebar ➡️")
