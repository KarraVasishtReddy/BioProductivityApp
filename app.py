import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION & MOCK DATABASE ---
st.set_page_config(page_title="Oxidate Auth", layout="wide")

# Mock User Database (Username: {password, role})
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "password123", "role": "user", "is_pro": False},
    "user2": {"password": "password456", "role": "user", "is_pro": True}
}

FOOD_DB = {
    "🫐 Blueberries": 15, "🍵 Green Tea": 12, "🥗 Spinach": 10,
    "🍔 Fried Food": -20, "🥤 Sugary Soda": -15, "🍺 Alcohol": -25
}

# --- 2. AUTHENTICATION LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
if 'balance' not in st.session_state:
    st.session_state.balance = 0
if 'history' not in st.session_state:
    st.session_state.history = []

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# --- 3. LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🔐 Oxidate Secure Login")
    with st.form("login_form"):
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if user_input in USERS and USERS[user_input]["password"] == pass_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.session_state.role = USERS[user_input]["role"]
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()

# --- 4. NAVIGATION & SIDEBAR ---
st.sidebar.title(f"Welcome, {st.session_state.username}")
st.sidebar.write(f"Role: **{st.session_state.role.upper()}**")

if st.sidebar.button("Log Out"):
    logout()

# --- 5. ADMIN AUTHORIZATION VIEW ---
if st.session_state.role == "admin":
    st.title("🛠️ Admin Command Center")
    st.info("You have full access to global system metrics.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", "1,240", "+12%")
    col2.metric("Pro Subscribers", "450", "36%")
    col3.metric("Revenue (Monthly)", "$4,050", "+$200")

    st.subheader("User Activity Monitor")
    # Mock data for admin to see
    admin_data = pd.DataFrame({
        "User": ["user1", "user2", "guest_99"],
        "Last Balance": [15, -10, 45],
        "Account": ["Free", "Pro", "Free"]
    })
    st.table(admin_data)
    
    st.subheader("Manage System Ads")
    st.text_area("Update Global Sidebar Ad", "Buy 'Pure-Antiox' Supplements now! 20% OFF")
    if st.button("Push Ad Update"):
        st.success("Ad campaign updated across all Free accounts.")

# --- 6. USER AUTHORIZATION VIEW ---
else:
    st.title("🧪 Your Oxidate Balance")
    
    # Check if this specific user is Pro in our mock DB
    is_pro = USERS[st.session_state.username].get("is_pro", False)
    
    if not is_pro:
        st.sidebar.warning("📢 AD: Upgrade to PRO for $9 to remove ads.")
    else:
        st.sidebar.success("💎 PRO Active: No Ads")

    # App Logic
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Internal Balance", st.session_state.balance)
    
    selected_food = st.selectbox("Log Intake", list(FOOD_DB.keys()))
    if st.button("Log Item"):
        st.session_state.balance += FOOD_DB[selected_food]
        st.session_state.history.append({"Item": selected_food, "Impact": FOOD_DB[selected_food]})
        st.rerun()

    # Restricted "Pro" Data
    if is_pro:
        st.subheader("💎 Pro Insights")
        st.write("Your cellular oxidation trend is improving. Keep it up!")
        st.line_chart([x['Impact'] for x in st.session_state.history])
    else:
        st.info("💡 Upgrade to Pro to see your energy trend charts.")
