import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. DATABASE & BACKEND SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_final.db')
    c = conn.cursor()
    # Users: profile_icon stores the badge name used as a photo
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, email TEXT, password TEXT, age INTEGER, 
                  allergies TEXT, is_pro BOOLEAN, profile_icon TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, time TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact_per_100g INTEGER)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('oxidate_final.db')

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. APP MASTER DATA ---
FOOD_DB_100G = {
    "🍎 Apple": 8, "🫐 Blueberries": 25, "🥦 Broccoli": 15, "🥬 Spinach": 18, 
    "🍚 White Rice": 2, "🌾 Brown Rice": 7, "🍗 Chicken Breast": 12,
    "🍔 Double Burger": -35, "🍟 Large Fries": -22, "🍕 Pizza": -28, "🥤 Soda": -18
}

BADGE_ICONS = {
    "Beginner": "🐣",
    "Shield Scout": "🛡️",
    "Berry Knight": "🫐",
    "Oxide Crusher": "⚔️",
    "Rainbow Master": "🌈",
    "Legendary Protector": "👑"
}

# --- 3. SESSION & STYLES ---
st.set_page_config(page_title="Oxidate Pro", page_icon="🧪", layout="wide")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- 4. AUTHENTICATION FLOW ---
if not st.session_state.logged_in:
    st.title("🧪 Oxidate: Balance Your Internal Chemistry")
    auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])

    with auth_tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Enter Tummy Town"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username=?", (u,))
            res = c.fetchone()
            if res and res[0] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Access Denied.")

    with auth_tab2:
        new_u = st.text_input("New Username")
        new_e = st.text_input("Email")
        new_p = st.text_input("New Password", type="password")
        new_all = st.text_area("Allergies (comma separated)")
        if st.button("Create Hero Account"):
            conn = get_db_connection()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", 
                          (new_u, new_e, hash_pass(new_p), 25, new_all, False, "Beginner"))
                conn.commit()
                st.success("Registration Successful!")
            except:
                st.error("Username taken.")
    st.stop()

# --- 5. MAIN NAVIGATION ---
conn = get_db_connection()
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,))
curr_user = c.fetchone() # (0:u, 1:e, 2:p, 3:age, 4:allergies, 5:pro, 6:icon)

st.sidebar.markdown(f"<h1 style='text-align: center;'>{BADGE_ICONS[curr_user[6]]}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h3 style='text-align: center;'>{st.session_state.user}</h3>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigate", ["Dashboard", "Log Food", "Profile", "Admin"])

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- 6. DASHBOARD ---
if menu == "Dashboard":
    st.title("🛡️ Shield Hero Dashboard")
    
    # Calculate Balance
    c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,))
    balance = c.fetchone()[0] or 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Hero Power (Balance)", f"{balance:.1f} pts")
        if balance < 0:
            st.warning("⚠️ Trash Monsters are attacking! Eat some fruit.")
        else:
            st.success("✅ Shield Heroes are holding the line!")

    with col2:
        st.subheader("Your Story")
        if balance >= 500:
            st.info("Story: You have reached the Shield Fortress! You are a Legend.")
        else:
            st.write(f"Keep eating healthy! You need {500 - balance:.1f} more points to reach the Fortress.")

# --- 7. LOG FOOD (Grams & Portions) ---
elif menu == "Log Food":
    st.title("⚖️ Precision Log")
    
    # Custom Food Add
    with st.expander("➕ Add Custom Food Type"):
        cf_name = st.text_input("Name")
        cf_score = st.number_input("Score per 100g", -50, 50, 0)
        if st.button("Save to My List"):
            c.execute("INSERT INTO custom_foods VALUES (?,?,?)", (st.session_state.user, cf_name, cf_score))
            conn.commit()
            st.rerun()

    # Log Intake
    c.execute("SELECT food_name, impact_per_100g FROM custom_foods WHERE username=?", (st.session_state.user,))
    customs = dict(c.fetchall())
    full_db = {**FOOD_DB_100G, **customs}
    
    item = st.selectbox("Select Food", list(full_db.keys()))
    grams = st.number_input("Grams (g)", 1, 1000, 100)
    
    # Allergy Check
    if curr_user[4] and any(a.strip().lower() in item.lower() for a in curr_user[4].split(',')):
        st.error(f"🚨 ALLERGY ALERT: This food contains {curr_user[4]}!")
    
    impact = (full_db[item] / 100) * grams
    st.write(f"Result: **{impact:+.1f} pts**")
    
    if st.button("Eat and Log"):
        c.execute("INSERT INTO history VALUES (?,?,?,?,?)", 
                  (st.session_state.user, item, grams, impact, datetime.now()))
        conn.commit()
        st.success("Logged to backend!")

# --- 8. PROFILE & BADGE EDIT ---
elif menu == "Profile":
    st.title("👤 User Profile")
    st.write(f"**Email:** {curr_user[1]}")
    st.write(f"**Allergies:** {curr_user[4]}")
    
    st.divider()
    st.subheader("Edit Profile Badge (Your Photo)")
    
    # Logic: Only show badges if balance allows
    c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,))
    bal = c.fetchone()[0] or 0
    
    available = ["Beginner"]
    if bal >= 50: available.append("Shield Scout")
    if bal >= 150: available.append("Berry Knight")
    if bal >= 300: available.append("Oxide Crusher")
    if bal >= 500: available.append("Rainbow Master")
    if curr_user[5]: available.append("Legendary Protector") # Pro only

    new_icon = st.selectbox("Equip Badge as Photo", available, index=available.index(curr_user[6]) if curr_user[6] in available else 0)
    
    if st.button("Update Profile Icon"):
        c.execute("UPDATE users SET profile_icon=? WHERE username=?", (new_icon, st.session_state.user))
        conn.commit()
        st.rerun()

    if not curr_user[5]:
        if st.button("Upgrade to Pro ($9)"):
            c.execute("UPDATE users SET is_pro=1 WHERE username=?", (st.session_state.user,))
            conn.commit()
            st.balloons()
            st.rerun()

# --- 9. ADMIN ---
elif menu == "Admin":
    if st.session_state.user == "admin":
        st.title("👑 Admin Command")
        users_df = pd.read_sql_query("SELECT username, email, is_pro, profile_icon FROM users", conn)
        st.table(users_df)
    else:
        st.error("Admin Only.")

conn.close()
