import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhonePe Transaction Insights",
    page_icon="📱",
    layout="wide"
)

# ── DB Connection ────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine("postgresql+psycopg2://postgres:ashish123@localhost/phonepe_pulse")

engine = get_engine()

@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("📱 PhonePe Insights")
page = st.sidebar.radio("Navigate", ["Overview", "Transactions", "Users", "Insurance"])

years = load_data('SELECT DISTINCT "Year" FROM aggregated_transaction ORDER BY "Year"')["Year"].tolist()
selected_year = st.sidebar.selectbox("Select Year", ["All"] + years)

year_filter = "" if selected_year == "All" else f'WHERE "Year" = {selected_year}'

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📱 PhonePe Transaction Insights Dashboard")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
kpi = load_data(f'SELECT SUM("Transaction_amount") AS amt, SUM("Transaction_count") AS cnt FROM aggregated_transaction {year_filter}')
users = load_data(f'SELECT SUM("Registered_users") AS total_users FROM map_user {year_filter}')

c1, c2, c3 = st.columns(3)
c1.metric("💰 Total Transaction Amount", f"₹ {kpi['amt'][0]/1e12:.2f} T")
c2.metric("🔢 Total Transactions",        f"{kpi['cnt'][0]/1e9:.2f} B")
c3.metric("👥 Registered Users",          f"{users['total_users'][0]/1e6:.1f} M")

st.markdown("---")

# ── Overview Page ────────────────────────────────────────────────────────────
if page == "Overview":
    st.subheader("📈 Year-wise Transaction Trend")
    df = load_data('SELECT "Year", SUM("Transaction_amount") AS amt FROM aggregated_transaction GROUP BY "Year" ORDER BY "Year"')
    fig = px.line(df, x="Year", y="amt", markers=True,
                  color_discrete_sequence=["#5C4DE5"],
                  labels={"amt": "Transaction Amount (₹)"},height=400,width=800)
    st.plotly_chart(fig, use_container_width=False)

    st.subheader("🏆 Top 10 States by Transaction Amount")
    df2 = load_data(f'SELECT "State", SUM("Transaction_amount") AS amt FROM aggregated_transaction {year_filter} GROUP BY "State" ORDER BY amt DESC LIMIT 10')
    fig2 = px.bar(df2, x="amt", y="State", orientation="h",
                  color="amt", color_continuous_scale="Viridis",
                  labels={"amt": "Amount (₹)", "State": "State"},height=400,width=800)
    st.plotly_chart(fig2, use_container_width=False)

# ── Transactions Page ─────────────────────────────────────────────────────────
elif page == "Transactions":
    st.subheader("💳 Payment Category Breakdown")
    df = load_data(f'SELECT "Transaction_type", SUM("Transaction_count") AS cnt FROM aggregated_transaction {year_filter} GROUP BY "Transaction_type"')
    fig = px.pie(df, names="Transaction_type", values="cnt",
                 hole=0.4, color_discrete_sequence=px.colors.sequential.Purples_r,height=400,width=800)
    st.plotly_chart(fig, use_container_width=False)

    st.subheader("🏙️ Top 10 Districts by Transaction Amount")
    df2 = load_data(f'SELECT "District", "State", SUM("Transaction_amount") AS amt FROM map_transaction {year_filter} GROUP BY "District", "State" ORDER BY amt DESC LIMIT 10')
    fig2 = px.bar(df2, x="amt", y="District", orientation="h",
                  color="amt", color_continuous_scale="Magma",
                  labels={"amt": "Amount (₹)"},height=400,width=800)
    st.plotly_chart(fig2, use_container_width=False)

# ── Users Page ───────────────────────────────────────────────────────────────
elif page == "Users":
    st.subheader("👥 Top 10 States by Registered Users")
    df = load_data(f'SELECT "State", SUM("Registered_users") AS users FROM map_user {year_filter} GROUP BY "State" ORDER BY users DESC LIMIT 10')
    fig = px.bar(df, x="users", y="State", orientation="h",
                 color="users", color_continuous_scale="Teal",
                 labels={"users": "Registered Users"},height=400,width=800)
    st.plotly_chart(fig, use_container_width=False)

    st.subheader("📱 Top Pincodes by Registered Users")
    df2 = load_data(f'SELECT "Pincode", "State", SUM("Registered_users") AS users FROM top_user_pincode {year_filter} GROUP BY "Pincode", "State" ORDER BY users DESC LIMIT 10')
    fig2 = px.bar(df2, x="users", y="Pincode", orientation="h",
                  color="users", color_continuous_scale="Blues",
                  labels={"users": "Registered Users"},height=400,width=800)
    st.plotly_chart(fig2, use_container_width=False)

# ── Insurance Page ────────────────────────────────────────────────────────────
elif page == "Insurance":
    st.subheader("🛡️ Top 10 Districts by Insurance Amount")
    df = load_data(f'SELECT "District", "State", SUM("Insurance_amount") AS amt FROM map_insurance {year_filter} GROUP BY "District", "State" ORDER BY amt DESC LIMIT 10')
    fig = px.bar(df, x="amt", y="District", orientation="h",
                 color="amt", color_continuous_scale="Oranges",
                 labels={"amt": "Insurance Amount (₹)"},height=400,width=800)
    st.plotly_chart(fig, use_container_width=False)

    st.subheader("📍 Top Pincodes by Insurance Amount")
    df2 = load_data(f'SELECT "Pincode", "State", SUM("Insurance_amount") AS amt FROM top_insurance_pincode {year_filter} GROUP BY "Pincode", "State" ORDER BY amt DESC LIMIT 10')
    fig2 = px.bar(df2, x="amt", y="Pincode", orientation="h",
                  color="amt", color_continuous_scale="Reds",
                  labels={"amt": "Insurance Amount (₹)"},height=400,width=800)
    st.plotly_chart(fig2, use_container_width=False)