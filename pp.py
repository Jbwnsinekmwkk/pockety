import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# BASIC PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Pocket Money Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Pocket Money Tracker")
st.write("Track your pocket money, savings, and daily expenses in a simple way.")


# -----------------------------
# INITIALIZE SESSION STATE
# -----------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Type", "Amount", "Category", "Note"]
    )

if "starting_balance" not in st.session_state:
    st.session_state.starting_balance = 0.0


# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------
st.sidebar.header("Settings")

# Starting Balance input
starting_balance = st.sidebar.number_input(
    "Starting Balance (₹)",
    min_value=0.0,
    value=float(st.session_state.starting_balance),
    step=50.0,
    help="Set how much money you started with."
)
st.session_state.starting_balance = starting_balance

# Upload existing CSV
st.sidebar.subheader("Upload Saved Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file with your transactions",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        # Basic validation
        required_cols = {"Date", "Type", "Amount", "Category", "Note"}
        if required_cols.issubset(set(df_uploaded.columns)):
            st.session_state.transactions = df_uploaded
            st.sidebar.success("Transactions loaded successfully!")
        else:
            st.sidebar.error("CSV does not have the required columns.")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")

# Reset data button
if st.sidebar.button("Reset All Data"):
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Type", "Amount", "Category", "Note"]
    )
    st.sidebar.success("All data cleared!")


# -----------------------------
# ADD NEW TRANSACTION
# -----------------------------
st.subheader("➕ Add New Entry")

with st.form("add_transaction_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    with col1:
        date = st.date_input("Date", value=datetime.today())
    with col2:
        t_type = st.selectbox("Type", ["Income (+)", "Expense (-)"])
    with col3:
        amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)
    with col4:
        category = st.text_input("Category (e.g. snacks, gift, tuition)")
    with col5:
        note = st.text_input("Note (optional)")

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if category.strip() == "":
            category = "Uncategorized"

        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Type": t_type,
            "Amount": amount,
            "Category": category,
            "Note": note,
        }

        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("Entry added!")


# -----------------------------
# SUMMARY & BALANCE
# -----------------------------
st.subheader("📊 Summary")

df = st.session_state.transactions.copy()

if not df.empty:
    # Convert Amount to numeric just in case
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    total_income = df.loc[df["Type"] == "Income (+)", "Amount"].sum()
    total_expense = df.loc[df["Type"] == "Expense (-)", "Amount"].sum()
    current_balance = st.session_state.starting_balance + total_income - total_expense
else:
    total_income = 0.0
    total_expense = 0.0
    current_balance = st.session_state.starting_balance

c1, c2, c3 = st.columns(3)
c1.metric("Total Income (₹)", f"{total_income:,.2f}")
c2.metric("Total Expense (₹)", f"{total_expense:,.2f}")
c3.metric("Current Balance (₹)", f"{current_balance:,.2f}")


# -----------------------------
# TRANSACTIONS TABLE
# -----------------------------
st.subheader("📒 All Transactions")

if df.empty:
    st.info("No transactions yet. Add your first entry above.")
else:
    # Sort by date
    df_display = df.copy()
    df_display["Date"] = pd.to_datetime(df_display["Date"])
    df_display = df_display.sort_values("Date", ascending=False)

    st.dataframe(df_display, use_container_width=True)

    # -------------------------
    # DOWNLOAD DATA AS CSV
    # -------------------------
    csv_data = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download as CSV",
        data=csv_data,
        file_name="pocket_money_transactions.csv",
        mime="text/csv",
    )


# -----------------------------
# SIMPLE ANALYTICS (OPTIONAL)
# -----------------------------
if not df.empty:
    st.subheader("📈 Simple Charts")

    # Ensure proper types
    df_chart = df.copy()
    df_chart["Date"] = pd.to_datetime(df_chart["Date"])
    df_chart["Signed_Amount"] = df_chart.apply(
        lambda row: row["Amount"] if row["Type"] == "Income (+)" else -row["Amount"],
        axis=1,
    )

    # Daily balance over time
    df_chart = df_chart.sort_values("Date")
    df_chart["Cumulative"] = (
        st.session_state.starting_balance + df_chart["Signed_Amount"].cumsum()
    )

    st.markdown("**Balance Over Time**")
    st.line_chart(df_chart.set_index("Date")["Cumulative"])

    # Spending by category (only expenses)
    df_exp = df[df["Type"] == "Expense (-)"]
    if not df_exp.empty:
        df_cat = df_exp.groupby("Category")["Amount"].sum().reset_index()
        st.markdown("**Expenses by Category**")
        st.bar_chart(df_cat.set_index("Category")["Amount"])
