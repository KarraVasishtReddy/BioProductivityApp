import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. DATABASE & PERSISTENCE ---
def init_db():
    conn = sqlite3.connect('oxidate_pro_manual.db')
    c = conn.cursor()
    # Users: includes pet details and badge
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                  allergies TEXT, badge TEXT, hero_name TEXT, pet_level INTEGER)''')
    # History: saves every meal
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    # Custom Library
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact_per_100g REAL)''')
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect('oxidate_pro_manual.db')

# --- 2. MEDINDIA-POWERED REDOX ENGINE ---
def get_nutrition_data(food_name):
    """Sourced from Medindia & ORAC data for automatic differentiation."""
    kb = {
        "turmeric": {"cal": 312, "redox": 45}, "cloves": {"cal": 274, "redox": 50},
        "spinach": {"cal": 23, "redox": 22}, "pomegranate": {"cal": 83, "redox": 28},
        "apple": {"cal": 52, "redox": 12}, "blueberry": {"cal": 57, "redox": 25},
        "fries": {"cal": 312, "redox": -30}, "burger": {"cal": 250, "redox": -35},
        "pizza": {"cal": 266, "redox": -28}, "soda": {"cal": 40, "redox": -18}
    }
    name = food_name.lower()
    match = next((k for k in kb if k in name), "general")
    return kb.get(match, {"cal": 120, "redox": -5})

# --- 3. UI SETUP ---
st.set_page_config(page_title="Oxidate: Tummy Quest", page_icon="🛡️", layout="wide")
init_db()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    st.title("🛡️ OXIDATE: The Great Tummy Quest")
    t1, t2 = st.tabs(["Login", "Join the Heroes"])
    with t2:
        nu = st.text_input("Username")
        h_name = st.text_input("Name Your Pet (e.g. Sparky)")
        np = st.text_input("Password", type="password")
        ne = st.text_input("Email")
        na = st.text_input("Allergies")
        if st.button("Start My Quest"):
            conn = get_db()
            conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", 
                         (nu, hashlib.sha256(np.encode()).hexdigest(), ne, na, "🐣", h_name, 1))
            conn.commit()
            st.success("Hero Registered! Please Log In.")
    with t1:
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Enter Battle"):
            conn = get_db()
            res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
            if res and res[0] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied.")
    st.stop()

# --- 5. APP CORE DATA ---
conn = get_db()
c = conn.cursor()
user_data = c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,)).fetchone()

# Sidebar: Virtual Pet & Stats
st.sidebar.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{user_data[4]}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h3 style='text-align: center;'>{user_data[5]} (Lv. {user_data[6]})</h3>", unsafe_allow_html=True)
nav = st.sidebar.radio("Navigation", ["Dashboard & Map", "Log Battle Items", "Custom Food", "Profile & Badges"])

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# --- DASHBOARD: THE JOURNEY ---
if nav == "Dashboard & Map":
    st.title(f"🚀 {user_data[5]}'s Quest Status")
    res = c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,)).fetchone()
    score, cals = res[0] or 0, res[1] or 0
    
    # Visual Progress
    st.subheader("Your Progress to Shield Fortress")
    progress = min(1.0, score/500) if score > 0 else 0
    st.progress(progress)
    
    col1, col2 = st.columns(2)
    col1.metric("Hero Shield Power", f"{score:.1f} pts")
    col2.metric("Total Energy", f"{int(cals)} kcal")
    
    if score < 0:
        st.error("👾 **TRASH MONSTERS ARE ATTACKING!** Neutalize them with berries or tea.")
    else:
        st.success("🛡️ **SHIELD ACTIVE!** Your tummy is safe.")

# --- MANUAL LOGGING (No Camera Version) ---
elif nav == "Log Battle Items":
    st.title("⚖️ Log Food & Portion Control")
    food_input = st.text_input("Search Food (e.g. 'Pomegranate' or 'Pizza')")
    grams = st.number_input("Portion in Grams (g)", 1, 1000, 100)
    
    if food_input:
        # Allergy Check
        if user_data[3] and user_data[3].lower() in food_input.lower():
            st.error(f"🚨 DANGER! {user_data[5]} says this food triggers your {user_data[3]} allergy!")
        
        data = get_nutrition_data(food_input)
        total_impact = (data['redox'] / 100) * grams
        total_cals = (data['cal'] / 100) * grams
        
        st.subheader("Analysis Results")
        col_r1, col_r2 = st.columns(2)
        col_r1.write(f"🔥 Calories: **{int(total_cals)} kcal**")
        col_r2.write(f"🛡️ Redox Impact: **{total_impact:+.1f} pts**")

        if st.button("Confirm & Log Intake"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_input, grams, total_impact, total_cals, datetime.now()))
            conn.commit()
            st.balloons()
            st.rerun()

# --- CUSTOM FOOD ---
elif nav == "Custom Food":
    st.title("➕ Custom Hero Knowledge")
    with st.form("custom_form"):
        f_name = st.text_input("Food Name")
        f_val = st.number_input("Shield Score per 100g", -50, 50, 5)
        if st.form_submit_button("Save to Library"):
            c.execute("INSERT INTO custom_foods VALUES (?,?,?)", (st.session_state.user, f_name, f_val))
            conn.commit()
            st.success(f"Added {f_name} to your personal database!")

# --- PROFILE & BADGES ---
elif nav == "Profile & Badges":
    st.title("🏆 Trophy Room")
    res_bal = c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,)).fetchone()[0] or 0
    
    badges = {"🐣": 0, "🛡️": 100, "⚔️": 300, "👑": 500}
    eligible = [k for k,v in badges.items() if res_bal >= v]
    
    selected_badge = st.selectbox("Equip Badge", eligible, index=eligible.index(user_data[4]) if user_data[4] in eligible else 0)
    if st.button("Update Profile Photo"):
        c.execute("UPDATE users SET badge=? WHERE username=?", (selected_badge, st.session_state.user))
        conn.commit()
        st.rerun()

    st.subheader("Battle History")
    df = pd.read_sql_query(f"SELECT food, grams, impact, time FROM history WHERE username='{st.session_state.user}'", conn)
    st.table(df.tail(10))

conn.close()
