import streamlit as st
import pandas as pd

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Oxidate: Internal Balance", layout="centered")

# --- INITIALIZE STATE ---
# This keeps the data from disappearing when the app refreshes
if 'balance' not in st.session_state:
    st.session_state.balance = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- APP DATABASE ---
FOOD_DB = {
    "🫐 Blueberries (Antioxidant)": 15,
    "🍵 Green Tea (Antioxidant)": 12,
    "🥗 Spinach (Antioxidant)": 10,
    "💊 Vitamin C (Antioxidant)": 20,
    "🍔 Fried Food (Oxidant)": -20,
    "🥤 Sugary Soda (Oxidant)": -15,
    "🍺 Alcohol (Oxidant)": -25,
    "🚬 Environmental Toxins (Oxidant)": -30
}

# --- SIDEBAR: MONETIZATION & ADS ---
st.sidebar.title("Oxidate Settings")
is_pro = st.sidebar.checkbox("🚀 Activate Pro Version ($9/mo)")

st.sidebar.markdown("---")
if not is_pro:
    # AD SPACE FOR FREE USERS
    st.sidebar.info("📢 **ADVERTISEMENT**\n\nFeeling sluggish? Try *Alpha-Glow* Antioxidants! Click [here](#) to buy.")
    st.sidebar.warning("Upgrade to **PRO** to remove ads and unlock AI Health Insights.")
else:
    st.sidebar.success("💎 **PRO ACCOUNT ACTIVE**")
    st.sidebar.write("Ads Disabled. AI Scanning Active.")

# --- MAIN UI ---
st.title("🧪 Oxidate Balance Tracker")
st.subheader("Neutralize stomach oxides for peak health.")

# 1. THE BALANCE GAUGE
col1, col2 = st.columns(2)

with col1:
    color = "green" if st.session_state.balance >= 0 else "red"
    st.markdown(f"### Current Balance: :{color}[{st.session_state.balance}]")

with col2:
    if st.session_state.balance >= 0:
        st.write("✅ Your gut is in a **Neutral/Alkaline** state.")
    else:
        st.write("⚠️ High **Oxidative Stress** detected in stomach.")

# 2. LOGGING INTERFACE
st.markdown("---")
selected_food = st.selectbox("What did you consume?", list(FOOD_DB.keys()))

if st.button("Log Intake"):
    points = FOOD_DB[selected_food]
    st.session_state.balance += points
    st.session_state.history.append({"Item": selected_food, "Impact": points})
    st.rerun()

# 3. PRO FEATURES ($9/MO VALUE)
if is_pro:
    st.markdown("---")
    st.header("💎 Pro Insights (AI-Powered)")
    
    if st.session_state.balance < 0:
        st.error(f"Action Required: You are {abs(st.session_state.balance)} points in the red. Drink 250ml of Green Tea immediately to neutralize.")
    else:
        st.success("Analysis: Your oxidation levels are optimal. Your energy levels should be at 100%.")
    
    with st.expander("View Full Chemical History"):
        st.table(pd.DataFrame(st.session_state.history))
else:
    st.markdown("---")
    st.text("🔓 Pro features (AI Insights & History) are locked.")
    if st.button("Unlock Pro for $9"):
        st.balloons()
        st.write("Redirecting to Stripe Payment Gateway...")

# 4. RESET BUTTON (For Testing)
if st.sidebar.button("Reset Session"):
    st.session_state.balance = 0
    st.session_state.history = []
    st.rerun()
