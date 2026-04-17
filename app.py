import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Oxidate Pro MVP", layout="wide")

# --- 2. DATABASE INITIALIZATION ---
# Using session_state for USERS so new sign-ups work during the session
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "admin", "email": "admin@oxidate.com", "age": 30, "allergies": "", "is_pro": True},
        "user1": {"password": "password123", "role": "user", "email": "user@test.com", "age": 25, "allergies": "nuts", "is_pro": False}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if 'balance' not in st.session_state:
    st.session_state.balance = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. EXPANDED FOOD DATABASE ---
FOOD_DB = {
    # Fruits (High Anti-oxides)
    "🍎 Apple": 8, "🍊 Orange": 10, "🍓 Strawberries": 14, "🍇 Grapes": 9, "🍍 Pineapple": 11, "🍉 Watermelon": 7,
    # Fast Food Center (High Oxides)
    "🍔 Double Burger": -25, "🍟 Large Fries": -18, "🍕 Pepperoni Pizza": -22, "🌭 Hot Dog": -15, "🍗 Fried Chicken": -20, "🍩 Glazed Donut": -18,
    # Basics
    "🍵 Green Tea": 12, "🥤 Sugary Soda": -15, "🍺 Alcohol": -25
}

# --- 4. AUTHENTICATION & SIGN-UP ---
def login_user(u, p):
    if u in st.session_state.users and st.session_state.users[u]["password"] == p:
        st.session_state.logged_in = True
        st.session_state.username = u
        st.rerun()
    else:
        st.error("Invalid credentials")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        st.header("Login")
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            login_user(u, p)

    with tab2:
        st.header("New User Registration")
        new_u = st.text_input("Choose Username")
        new_e = st.text_input("Email Address")
        new_p = st.text_input("Choose Password", type="password")
        new_age = st.number_input("Age", min_value=1, max_value=120, value=25)
        new_allergies = st.text_area("List Allergies (e.g., nuts, dairy, berries)").lower()
        
        if st.button("Sign Up"):
            if new_u and new_p and new_e:
                st.session_state.users[new_u] = {
                    "password": new_p, "role": "user", "email": new_e, 
                    "age": new_age, "allergies": new_allergies, "is_pro": False
                }
                st.success("Account created! Please log in.")
            else:
                st.warning("Please fill in all fields.")
    st.stop()

# --- 5. APP INTERFACE ---
user_data = st.session_state.users[st.session_state.username]
st.sidebar.title(f"Hello, {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- ADMIN VIEW ---
if user_data["role"] == "admin":
    st.title("🛠️ Admin Dashboard")
    st.write("Total Registered Users:", len(st.session_state.users))
    st.dataframe(pd.DataFrame(st.session_state.users).T[['email', 'age', 'role', 'is_pro']])

# --- USER VIEW ---
else:
    st.title("🧪 Oxidate: Balance Your Stomach")
    
    # Allergy Alert System
    if user_data["allergies"]:
        st.warning(f"⚠️ Allergy Profile Active: Avoiding **{user_data['allergies']}**")

    # Layout Columns
    col_input, col_status = st.columns([2, 1])

    with col_input:
        st.subheader("Log Consumption")
        item = st.selectbox("Select Item", list(FOOD_DB.keys()))
        quantity = st.number_input("Quantity / Servings", min_value=1, max_value=10, value=1)
        
        # Check for allergy match
        allergy_found = any(word in item.lower() for word in user_data["allergies"].split(",")) if user_data["allergies"] else False
        
        if allergy_found:
            st.error(f"🚨 WARNING: This item may contain {user_data['allergies']}!")
        
        if st.button("Add to Balance"):
            impact = FOOD_DB[item] * quantity
            st.session_state.balance += impact
            st.session_state.history.append({"Item": item, "Qty": quantity, "Total Impact": impact})
            st.rerun()

    with col_status:
        st.subheader("Health Status")
        color = "green" if st.session_state.balance >= 0 else "red"
        st.metric("Net Balance Score", st.session_state.balance, delta=f"{st.session_state.balance} pts")
        
        if not user_data["is_pro"]:
            st.info("📢 AD: Buy Organic Fruits! \n\n Upgrade to PRO for $9/mo.")

    # --- PRO VERSION ($9 FEATURE) ---
    if user_data["is_pro"]:
        st.markdown("---")
        st.subheader("💎 Pro Insights: Chemical Trend")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.line_chart(df["Total Impact"])
        else:
            st.write("No data logged yet.")
    else:
        if st.button("Unlock Pro Analytics ($9)"):
            st.session_state.users[st.session_state.username]["is_pro"] = True
            st.balloons()
            st.rerun()
