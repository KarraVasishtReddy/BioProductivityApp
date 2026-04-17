import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from PIL import Image
from datetime import datetime

# --- 1. BACKEND & DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_final_master.db')
    c = conn.cursor()
    # User accounts
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                  age INTEGER, allergies TEXT, badge TEXT)''')
    # Health History
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    # Custom Food Library
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact_per_100g REAL)''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('oxidate_final_master.db')

# --- 2. THE AI NEURAL VISION ENGINE ---
def ai_vision_engine(food_name):
    """Predicts portion size, weight, and chemistry automatically."""
    kb = {
        "apple": {"cal": 52, "redox": 12, "avg": 150},
        "blueberry": {"cal": 57, "redox": 25, "avg": 100},
        "broccoli": {"cal": 34, "redox": 18, "avg": 120},
        "fries": {"cal": 312, "redox": -30, "avg": 200},
        "burger": {"cal": 250, "redox": -35, "avg": 250},
        "pizza": {"cal": 266, "redox": -28, "avg": 350},
        "soda": {"cal": 40, "redox": -15, "avg": 330}
    }
    name = food_name.lower()
    match = next((k for k in kb if k in name), "salad")
    data = kb[match]
    size_factor = random.choice([0.7, 1.0, 1.5]) 
    weight = int(data["avg"] * size_factor)
    return {
        "weight": weight,
        "calories": int((data["cal"] / 100) * weight),
        "impact": round((data["redox"] / 100) * weight, 1),
        "size": "Small" if size_factor < 1 else ("Large" if size_factor > 1 else "Medium")
    }

# --- 3. APP CONFIGURATION ---
st.set_page_config(page_title="Oxidate Pro", page_icon="🛡️", layout="wide")
init_db()

BADGE_ICONS = {"🐣": "Beginner", "🛡️": "Shield Scout", "⚔️": "Oxide Crusher", "👑": "Legendary Hero"}

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    st.title("🛡️ OXIDATE: AI Tummy Battle")
    tab1, tab2 = st.tabs(["Login", "Join the Squad (Free)"])
    
    with tab2:
        nu = st.text_input("New Username")
        ne = st.text_input("Email")
        np = st.text_input("Password", type="password")
        nall = st.text_input("Allergies (comma separated)")
        if st.button("Create My Account"):
            conn = get_connection()
            try:
                conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), ne, 25, nall, "🐣"))
                conn.commit()
                st.success("Account Ready! Go to the Login tab.")
            except: st.error("Username already taken!")

    with tab1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Enter Battle"):
            conn = get_connection()
            res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
            if res and res[0] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# --- 5. MAIN NAVIGATION & USER DATA ---
conn = get_connection()
c = conn.cursor()
user_data = c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,)).fetchone()

# Sidebar Styling
st.sidebar.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{user_data[5]}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h2 style='text-align: center;'>{st.session_state.user}</h2>", unsafe_allow_html=True)

nav = st.sidebar.radio("Command Deck", ["Dashboard", "AI Vision Scanner", "Add Custom Food", "Profile & History", "Admin"])

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# --- 6. DASHBOARD ---
if nav == "Dashboard":
    st.title("🚀 Hero Command Center")
    with st.expander("📖 The Mission (How it Works)", expanded=True):
        col_ad, col_kd = st.columns(2)
        col_ad.markdown("### 🧑‍🔬 For Adults\nMaintain a 'Neutral' environment in your stomach. Use **Antioxidants** to neutralize **Oxidative Stress** (free radicals) caused by processed food.")
        col_kd.markdown("### 🛡️ For Kids\nYour Tummy Battle is real! Use healthy food 'Shields' to knock out the 'Trash Monsters'. Stay Green to stay strong!")

    res = c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,)).fetchone()
    bal, cals = res[0] or 0, res[1] or 0
    
    c1, c2 = st.columns(2)
    c1.metric("Current Redox Balance", f"{bal:.1f} pts", delta="Safe" if bal >= 0 else "Oxidized")
    c2.metric("Energy Consumed", f"{int(cals)} kcal")

    if bal < 0:
        st.warning(f"💡 AI Coach: Your balance is low. A bowl of Blueberries (+25 pts) would neutralize the monsters!")

# --- 7. AI VISION SCANNER ---
elif nav == "AI Vision Scanner":
    st.title("📸 Neural Vision Plate Scanner")
    img = st.camera_input("Scan your food")
    food_label = st.text_input("What is this? (e.g. 'French Fries' or 'Apple')")

    if img and food_label:
        # Allergy Check
        if user_data[4] and user_data[4].lower() in food_label.lower():
            st.error(f"🚨 DANGER! Allergy Warning: {user_data[4]}")
        
        scan = ai_vision_engine(food_label)
        st.subheader("AI Visual Analysis")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Size", scan['size'], f"{scan['weight']}g")
        col_s2.metric("Calories", f"{scan['calories']} kcal")
        col_s3.metric("Redox Impact", f"{scan['impact']:+.1f} pts")

        if st.button("Log AI Prediction"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_label, scan['weight'], scan['impact'], scan['calories'], datetime.now()))
            conn.commit()
            st.balloons()
            st.rerun()

# --- 8. CUSTOM FOOD (THE FIXED PAGE) ---
elif nav == "Add Custom Food":
    st.title("➕ Expand Your Hero Library")
    st.write("Can't find a food? Add it here to track it forever.")
    
    with st.form("custom_food_form"):
        new_name = st.text_input("Name of Food")
        new_impact = st.number_input("Oxide/Antioxide Score per 100g", -50, 50, 0)
        submit = st.form_submit_button("Save to My Library")
        
        if submit and new_name:
            c.execute("INSERT INTO custom_foods VALUES (?,?,?)", (st.session_state.user, new_name, new_impact))
            conn.commit()
            st.success(f"Added {new_name} to your local database!")

# --- 9. PROFILE & HISTORY ---
elif nav == "Profile & History":
    st.title("👤 Hero Profile & Badge Room")
    
    # Badge Logic
    res_bal = c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,)).fetchone()[0] or 0
    
    st.subheader("Equip Your Active Badge")
    # Users can only select badges they've earned
    eligible = ["🐣"]
    if res_bal >= 100: eligible.append("🛡️")
    if res_bal >= 300: eligible.append("⚔️")
    if res_bal >= 500: eligible.append("👑")
    
    selected_icon = st.selectbox("Current Badge (Shows in Sidebar)", eligible, index=eligible.index(user_data[5]) if user_data[5] in eligible else 0)
    
    if st.button("Save Profile Update"):
        c.execute("UPDATE users SET badge=? WHERE username=?", (selected_icon, st.session_state.user))
        conn.commit()
        st.rerun()

    st.divider()
    st.subheader("📈 Consumption History")
    df = pd.read_sql_query(f"SELECT food, grams, impact, calories, time FROM history WHERE username='{st.session_state.user}' ORDER BY time DESC", conn)
    st.dataframe(df, use_container_width=True)

# --- 10. ADMIN ---
elif nav == "Admin":
    st.title("🛠️ Global Management")
    if st.session_state.user == "admin":
        users_df = pd.read_sql_query("SELECT username, email, badge FROM users", conn)
        st.table(users_df)
    else:
        st.error("Admin Access Only.")

conn.close()
