import streamlit as st
import pandas as pd
import datetime
import io

# ---------- Initial Setup ----------
st.set_page_config(page_title="Session Tracker", layout="centered")

# Aging bucket function
def aging_bucket(days):
    if days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "31-60 days"
    elif days <= 90:
        return "61-90 days"
    else:
        return "90+ days"

# Initialize session state DataFrame if not already there
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "Client Initials", "Date of Service", "CPT Code", "Session Fee",
        "Payment Received", "Date of Payment", "Outstanding",
        "Days Outstanding", "Aging Bucket"
    ])

# Shortcut
df = st.session_state.df

# ---------- Input Form ----------
st.title("📊 Therapy Session Tracker")

with st.form("session_entry"):
    client_initials = st.text_input("Client Initials")
    date_of_service = st.date_input("Date of Service", datetime.date.today())
    cpt_code = st.selectbox("CPT Code", ["90837", "90791"])
    session_fee = st.number_input("Session Fee ($)", min_value=0.0, step=10.0)
    payment_received = st.number_input("Payment Received ($)", min_value=0.0, step=10.0)
    date_of_payment = st.date_input("Date of Payment (leave today if unpaid)", datetime.date.today())
    
    submitted = st.form_submit_button("Add Session")

if submitted:
    outstanding = session_fee - payment_received
    days_outstanding = (datetime.date.today() - date_of_payment).days if outstanding > 0 else 0
    bucket = aging_bucket(days_outstanding) if outstanding > 0 else "Paid"

    new_row = {
        "Client Initials": client_initials,
        "Date of Service": date_of_service,
        "CPT Code": cpt_code,
        "Session Fee": session_fee,
        "Payment Received": payment_received,
        "Date of Payment": date_of_payment,
        "Outstanding": outstanding,
        "Days Outstanding": days_outstanding,
        "Aging Bucket": bucket
    }

    # Add row to DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.df = df  # update stored dataframe

    # Auto-save to Excel (local)
    df.to_excel("sessions.xlsx", index=False)

    st.success("✅ Session added and saved!")

# ---------- Display Data ----------
st.subheader("📋 All Sessions")
st.dataframe(df, use_container_width=True)

# ---------- Aging Summary ----------
if not df.empty:
    st.subheader("📊 Aging Summary")

    summary = df.groupby("Aging Bucket")["Outstanding"].sum().reset_index()

    # Add colors for buckets
    color_map = {
        "0-30 days": "🟩",
        "31-60 days": "🟨",
        "61-90 days": "🟧",
        "90+ days": "🟥",
        "Paid": "✅"
    }
    summary["Status"] = summary["Aging Bucket"].map(color_map)

    st.table(summary[["Status", "Aging Bucket", "Outstanding"]])

# ---------- Download Excel ----------
st.subheader("⬇️ Download Data")
output = io.BytesIO()
df.to_excel(output, index=False, engine="openpyxl")
st.download_button(
    label="📥 Download Excel file",
    data=output.getvalue(),
    file_name="sessions.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
