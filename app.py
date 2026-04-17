import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. DATABASE & BACKEND SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_master_final.db')
    c = conn.cursor()
    # User accounts
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                  age INTEGER, allergies TEXT, badge TEXT)''')
    # Health History
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    # Custom Food Library - KEY TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact_per_100g REAL)''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('oxidate_master_final.db')

# --- 2. THE AI NEURAL VISION ENGINE ---
def ai_vision_engine(food_name, is_custom=False, custom_impact=0):
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
    
    # Use custom impact if it's a custom food, otherwise use KB
    redox_val = custom_impact if is_custom else kb.get(next((k for k in kb if k in name), "salad"), {"redox": -5})["redox"]
    cal_val = 150 if is_custom else kb.get(next((k for k in kb if k in name), "salad"), {"cal": 150})["cal"]
    
    size_factor = random.choice([0.7, 1.0, 1.5]) 
    weight = int(150 * size_factor)
    
    return {
        "weight": weight,
        "calories": int((cal_val / 100) * weight),
        "impact": round((redox_val / 100) * weight, 1),
        "size": "Small" if size_factor < 1 else ("Large" if size_factor > 1 else "Medium")
    }

# --- 3. APP SETUP ---
st.set_page_config(page_title="Oxidate Master", page_icon="🛡️", layout="wide")
init_db()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    st.title("🛡️ OXIDATE: AI Tummy Battle")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t2:
        nu = st.text_input("Username")
        np = st.text_input("Password", type="password")
        if st.button("Create Account"):
            conn = get_connection()
            try:
                conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user@mail.com", 25, "", "🐣"))
                conn.commit()
                st.success("Success! Login now.")
            except: st.error("Error creating account.")
    with t1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Login"):
            conn = get_connection()
            res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
            if res and res[0] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.rerun()
    st.stop()

# --- 5. DATA FETCHING ---
conn = get_connection()
c = conn.cursor()
user_info = c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,)).fetchone()

# Sidebar
st.sidebar.title(f"{user_info[5]} {st.session_state.user}")
nav = st.sidebar.radio("Navigation", ["Dashboard", "Log Food (AI Scanner)", "Add Custom Food", "Profile & History"])
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# --- 6. DASHBOARD ---
if nav == "Dashboard":
    st.title("🚀 Hero Dashboard")
    res = c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,)).fetchone()
    bal, cals = res[0] or 0, res[1] or 0
    c1, c2 = st.columns(2)
    c1.metric("Redox Balance", f"{bal:.1f} pts")
    c2.metric("Total Calories", f"{int(cals)} kcal")

# --- 7. LOG FOOD (INTEGRATED WITH CUSTOM ITEMS) ---
elif nav == "Log Food (AI Scanner)":
    st.title("📸 AI Plate Scanner")
    
    # FETCH CUSTOM FOODS EVERY TIME
    c.execute("SELECT food_name, impact_per_100g FROM custom_foods WHERE username=?", (st.session_state.user,))
    custom_list = dict(c.fetchall())
    
    base_foods = {"🍎 Apple": 12, "🥦 Broccoli": 18, "🍔 Burger": -35, "🍟 Fries": -30, "🫐 Blueberries": 25}
    # Merge both lists
    all_options = {**base_foods, **custom_list}
    
    selected_food = st.selectbox("Select or Search Food", list(all_options.keys()))
    
    if selected_food:
        # Determine if it's a custom food or base food
        is_custom = selected_food in custom_list
        impact_val = all_options[selected_food]
        
        # Run AI Vision Prediction
        scan = ai_vision_engine(selected_food, is_custom=is_custom, custom_impact=impact_val)
        
        st.subheader("AI Visual Prediction")
        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Size", scan['size'], f"{scan['weight']}g")
        col2.metric("Calories", f"{scan['calories']} kcal")
        col3.metric("Redox Impact", f"{scan['impact']:+.1f} pts")
        
        if st.button("Confirm & Log Intake"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, selected_food, scan['weight'], scan['impact'], scan['calories'], datetime.now()))
            conn.commit()
            st.balloons()
            st.rerun()

# --- 8. ADD CUSTOM FOOD (FIXED) ---
elif nav == "Add Custom Food":
    st.title("➕ Create Custom Knowledge")
    st.write("Add a new food to your personal library so the AI can track it.")
    
    with st.form("custom_food_form"):
        new_name = st.text_input("Food Name (e.g. Sushi)")
        new_impact = st.number_input("Oxide/Antioxide Score per 100g", -50, 50, 5)
        submitted = st.form_submit_button("Save to My Data")
        
        if submitted and new_name:
            # SAVE TO DATABASE
            c.execute("INSERT INTO custom_foods (username, food_name, impact_per_100g) VALUES (?,?,?)", 
                      (st.session_state.user, new_name, new_impact))
            conn.commit()
            st.success(f"✅ {new_name} is now saved to your data!")
            # NO st.rerun() inside form, but successful message shown. 
            # Navigating back to 'Log Food' will now show this item.

# --- 9. HISTORY ---
elif nav == "Profile & History":
    st.title("👤 Your History")
    df = pd.read_sql_query(f"SELECT food, grams, impact, calories, time FROM history WHERE username='{st.session_state.user}' ORDER BY time DESC", conn)
    st.dataframe(df, use_container_width=True)

conn.close()
