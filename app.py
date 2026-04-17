import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime

# --- 1. CONFIGURATION & API ---
# Get a free API key at https://spoonacular.com/food-api
API_KEY = "YOUR_SPOONACULAR_API_KEY" 

def get_calories_api(query):
    """Fetches real calorie data per 100g using Spoonacular API."""
    try:
        url = f"https://api.spoonacular.com/food/ingredients/search?query={query}&apiKey={API_KEY}"
        res = requests.get(url).json()
        if res['results']:
            id = res['results'][0]['id']
            info = requests.get(f"https://api.spoonacular.com/food/ingredients/{id}/information?amount=100&unit=grams&apiKey={API_KEY}").json()
            return info['nutrition']['nutrients'][0]['amount'] # Returns kcal
    except:
        return None # Fallback if API fails or key is missing

# --- 2. BACKEND SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_ultimate.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, email TEXT, password TEXT, allergies TEXT, is_pro BOOLEAN, icon TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- 4. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.title("🧪 Oxidate: Balance & Calories")
    auth = st.tabs(["Login", "Sign Up"])
    with auth[1]:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        e = st.text_input("Email")
        allg = st.text_input("Allergies")
        if st.button("Create Account"):
            conn = sqlite3.connect('oxidate_ultimate.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (u, e, hashlib.sha256(p.encode()).hexdigest(), allg, False, "🐣"))
            conn.commit()
            st.success("Welcome Hero! Now Login.")
    with auth[0]:
        u_log = st.text_input("Username")
        p_log = st.text_input("Password", type="password")
        if st.button("Login"):
            conn = sqlite3.connect('oxidate_ultimate.db')
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username=?", (u_log,))
            res = c.fetchone()
            if res and res[0] == hashlib.sha256(p_log.encode()).hexdigest():
                st.session_state.logged_in = True
                st.session_state.user = u_log
                st.rerun()
    st.stop()

# --- 5. APP CORE ---
conn = sqlite3.connect('oxidate_ultimate.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,))
user_info = c.fetchone() # (u, e, p, all, pro, icon)

# Sidebar
st.sidebar.title(f"{user_info[5]} {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "Log Food", "Profile"])
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- 6. DASHBOARD (The Purpose) ---
if menu == "Dashboard":
    st.title("🚀 Hero Command Center")
    
    # Purpose Section
    with st.expander("📖 Why are we here? (The Purpose)", expanded=True):
        col_a, col_k = st.columns(2)
        col_a.markdown("### 🧑‍🔬 For Adults\n**Goal:** Neutralize Oxidative Stress.\nEvery time you eat, your body creates 'Free Radicals' (Oxides). If you have too many, they damage your DNA. We track **Antioxidants** to stop that damage.")
        col_k.markdown("### 🛡️ For Kids\n**Goal:** Defeat the Trash Monsters!\nJunk food creates monsters in your tummy. Healthy food sends in **Shield Heroes**. Keep your score green to stay a Superhero!")

    # Stats
    c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,))
    stats = c.fetchone()
    bal, cals = stats[0] or 0, stats[1] or 0
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Oxidate Balance", f"{bal:.1f} pts", delta="Healthy" if bal >=0 else "Oxidized")
    c2.metric("Total Calories", f"{int(cals)} kcal")

# --- 7. LOG FOOD (API Integration) ---
elif menu == "Log Food":
    st.title("⚖️ Precision Intake & Calorie Tracker")
    food_search = st.text_input("Search food (e.g., 'Blueberries' or 'Pizza')")
    grams = st.number_input("Weight (Grams)", 1, 1000, 100)
    
    if food_search:
        # Check Allergy
        if user_info[3] and user_info[3].lower() in food_search.lower():
            st.error(f"🚨 WARNING: {food_search} triggers your {user_info[3]} allergy!")
        
        # Calculate Scores
        cal_per_100 = get_calories_api(food_search) or 150 # Fallback 150 if no API key
        oxide_base = 15 if "fruit" in food_search or "veg" in food_search else -20 # Simple logic
        
        total_cals = (cal_per_100 / 100) * grams
        total_impact = (oxide_base / 100) * grams
        
        st.write(f"📊 **Analysis:** {total_cals:.0f} Calories | {total_impact:+.1f} Oxide Score")
        
        if st.button("Log to Backend"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_search, grams, total_impact, total_cals, datetime.now()))
            conn.commit()
            st.success("Saved to your history!")

# --- 8. PROFILE (Badge System) ---
elif menu == "Profile":
    st.title("👤 Hero Profile")
    st.write(f"Email: {user_info[1]}")
    
    # Badge Logic
    c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,))
    b = c.fetchone()[0] or 0
    badges = {"🐣":0, "🛡️":100, "⚔️":300, "👑":500}
    
    selected_icon = st.selectbox("Select Earned Badge", [k for k,v in badges.items() if b >= v])
    if st.button("Update Profile Photo"):
        c.execute("UPDATE users SET icon=? WHERE username=?", (selected_icon, st.session_state.user))
        conn.commit()
        st.rerun()

    if not user_info[4]:
        if st.button("Upgrade to PRO ($9)"):
            c.execute("UPDATE users SET is_pro=1 WHERE username=?", (st.session_state.user,))
            conn.commit()
            st.balloons()
            st.rerun()

conn.close()
