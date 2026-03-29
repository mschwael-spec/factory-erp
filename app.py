import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Factory ERP AI", layout="wide")

# ---------------- LOGIN ----------------
USERS = {
    "admin": {"password": "Admin", "role": "Admin"},
    "operator": {"password": "123", "role": "Operator"},
    "qc": {"password": "123", "role": "QC"}
}

# Initialize session safely
if "user" not in st.session_state:
    st.session_state["user"] = None

# ---------------- LOGIN SCREEN ----------------
if st.session_state["user"] is None:
    st.title("🔐 ERP Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state["user"] = USERS[u]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid login")

    st.stop()

# ---------------- SAFE ROLE ACCESS ----------------
role = st.session_state["user"].get("role", "Unknown")

# ---------------- FILES ----------------
FILES = {
    "production": "production.xlsx",
    "sales": "sales.xlsx",
    "oee": "oee.xlsx"
}

# ---------------- UTIL ----------------
def load(f):
    try:
        return pd.read_excel(f)
    except:
        return pd.DataFrame()

def save(df, f):
    df.to_excel(f, index=False)

# ---------------- HEADER ----------------
st.title(f"🏭 AI Factory ERP | {role}")

menu = st.sidebar.radio("Menu", [
    "Dashboard","AI Insights","Production","Sales","OEE","KPI"
])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    prod = load(FILES["production"])
    sales = load(FILES["sales"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Batches", len(prod))
    col2.metric("Total Output", int(prod["Qty"].sum()) if not prod.empty else 0)
    col3.metric("Revenue", int(sales["Revenue"].sum()) if not sales.empty else 0)

# ---------------- AI INSIGHTS ----------------
if menu == "AI Insights":
    st.subheader("🤖 Smart Insights")

    prod = load(FILES["production"])
    sales = load(FILES["sales"])

    if not prod.empty:
        avg = prod["Qty"].mean()
        st.info(f"Average production per batch: {round(avg,2)}")

    if not sales.empty:
        best = sales.groupby("Customer")["Profit"].sum().idxmax()
        st.success(f"Top customer: {best}")

    st.warning("💡 Suggestion: Increase production of high-profit batches")

# ---------------- PRODUCTION ----------------
if menu == "Production":
    df = load(FILES["production"])

    b = st.text_input("Batch")
    q = st.number_input("Qty")

    if st.button("Produce"):
        new = pd.DataFrame([[b,q,datetime.now()]], columns=["Batch","Qty","Date"])
        df = pd.concat([df,new])
        save(df, FILES["production"])

    st.dataframe(df)

# ---------------- SALES ----------------
if menu == "Sales":
    df = load(FILES["sales"])

    b = st.text_input("Batch")
    q = st.number_input("Qty")
    p = st.number_input("Price")

    if st.button("Sell"):
        revenue = q * p
        profit = revenue * 0.3

        new = pd.DataFrame([[b,q,p,revenue,profit]],
                           columns=["Batch","Qty","Price","Revenue","Profit"])

        df = pd.concat([df,new])
        save(df, FILES["sales"])

    st.dataframe(df)

# ---------------- OEE ----------------
if menu == "OEE":
    df = load(FILES["oee"])

    planned = st.number_input("Planned Time")
    actual = st.number_input("Actual Time")
    good = st.number_input("Good Units")
    total = st.number_input("Total Units")

    if st.button("Calc OEE"):
        A = actual/planned if planned else 0
        P = total/actual if actual else 0
        Q = good/total if total else 0
        oee = A*P*Q

        new = pd.DataFrame([[A,P,Q,oee]], columns=["A","P","Q","OEE"])
        df = pd.concat([df,new])
        save(df, FILES["oee"])

        st.success(f"OEE = {round(oee,2)}")

    st.dataframe(df)

# ---------------- KPI ----------------
if menu == "KPI":
    st.subheader("📊 KPI Dashboard")

    prod = load(FILES["production"])
    sales = load(FILES["sales"])

    if not prod.empty:
        st.metric("Avg Batch Size", round(prod["Qty"].mean(),2))

    if not sales.empty:
        st.metric("Total Profit", int(sales["Profit"].sum()))

    st.success("🔥 System Optimized")