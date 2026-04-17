import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# --- 1. DATABASE SYSTEM (THE BACKEND) ---
def init_db():
    conn = sqlite3.connect('oxidate.db')
    c = conn.cursor()
    # User Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, email TEXT, password TEXT, age INTEGER, allergies TEXT, is_pro BOOLEAN)''')
    # Consumption History Table
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food_item TEXT, quantity INTEGER, impact INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    # Custom Food Table
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact INTEGER)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. CONFIGURATION & STATE ---
st.set_page_config(page_title="Oxidate Pro: Persistent Backend", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.title("🧪 Oxidate: Secure Login")
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            conn = sqlite3.connect('oxidate.db')
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username=?', (u,))
            result = c.fetchone()
            if result and result[0] == hash_password(p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with tab2:
        st.subheader("Join the Hero Squad")
        new_u = st.text_input("Choose Username")
        new_e = st.text_input("Email")
        new_p = st.text_input("Password ", type="password")
        new_age = st.number_input("Age", 1, 100, 25)
        new_allergies = st.text_area("Allergies (comma separated)")
        
        if st.button("Register"):
            try:
                conn = sqlite3.connect('oxidate.db')
                c = conn.cursor()
                c.execute('INSERT INTO users VALUES (?,?,?,?,?,?)', 
                          (new_u, new_e, hash_password(new_p), new_age, new_allergies, False))
                conn.commit()
                st.success("Account created! Go to Login tab.")
            except sqlite3.IntegrityError:
                st.error("Username already exists!")
    st.stop()

# --- 4. MAIN APP LOGIC ---
conn = sqlite3.connect('oxidate.db')
c = conn.cursor()

# Get User Info
c.execute('SELECT * FROM users WHERE username=?', (st.session_state.username,))
user_data = c.fetchone() # (user, email, pass, age, allergies, is_pro)

# Sidebar / Logout
st.sidebar.title(f"👋 Hi, {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# --- 5. FOOD DATABASE ---
base_foods = {"🍎 Apple": 10, "🥦 Broccoli": 12, "🍔 Burger": -25, "🥤 Soda": -15, "🫐 Blueberries": 20}

# Fetch Custom Foods from DB
c.execute('SELECT food_name, impact FROM custom_foods WHERE username=?', (st.session_state.username,))
custom_rows = c.fetchall()
combined_foods = {**base_foods, **dict(custom_rows)}

# --- 6. USER DASHBOARD ---
st.title("Your Oxidate Balance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Log Intake")
    selected_item = st.selectbox("Select Food", list(combined_foods.keys()))
    qty = st.number_input("Quantity", 1, 10, 1)
    
    # Allergy Check
    if user_data[4] and any(a.strip().lower() in selected_item.lower() for a in user_data[4].split(',')):
        st.error(f"🚨 DANGER: You are allergic to an ingredient in {selected_item}!")

    if st.button("Add to My Tummy"):
        impact = combined_foods[selected_item] * qty
        c.execute('INSERT INTO history (username, food_item, quantity, impact) VALUES (?,?,?,?)',
                  (st.session_state.username, selected_item, qty, impact))
        conn.commit()
        st.success("Logged!")
        st.rerun()

with col2:
    st.subheader("Add New Food to App")
    new_food_name = st.text_input("Food Name (e.g. Sushi)")
    new_food_impact = st.number_input("Health Score (-30 to +30)", -30, 30, 5)
    if st.button("Save New Food Type"):
        c.execute('INSERT INTO custom_foods VALUES (?,?,?)', (st.session_state.username, new_food_name, new_food_impact))
        conn.commit()
        st.success(f"{new_food_name} added to your personal list!")
        st.rerun()

# --- 7. HISTORY & SCORE ---
st.divider()
c.execute('SELECT SUM(impact) FROM history WHERE username=?', (st.session_state.username,))
total_balance = c.fetchone()[0] or 0

st.metric("Current Balance Score", total_balance)

st.subheader("Your Consumption Log (Saved in Backend)")
c.execute('SELECT food_item, quantity, impact, timestamp FROM history WHERE username=? ORDER BY timestamp DESC', (st.session_state.username,))
history_df = pd.DataFrame(c.fetchall(), columns=["Food", "Qty", "Impact", "Time"])
st.dataframe(history_df, use_container_width=True)

# --- 8. PRO VERSION ($9) ---
if not user_data[5]:
    if st.button("Unlock Pro for $9 (One-time)"):
        c.execute('UPDATE users SET is_pro=1 WHERE username=?', (st.session_state.username,))
        conn.commit()
        st.balloons()
        st.rerun()
else:
    st.sidebar.success("💎 PRO ACCOUNT ACTIVE")
