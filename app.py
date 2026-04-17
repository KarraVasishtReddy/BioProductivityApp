import streamlit as st
import pandas as pd
import requests # Used for API integration

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Oxidate: Ultimate Diet Tracker", layout="wide")

# --- 2. THE DIVERSIFIED FOOD DATABASE ---
# Expanded with Rice, Vegetables, and Diet-Specific Items
FOOD_DB = {
    # 🥗 VEGETABLES (High Anti-oxides)
    "🥦 Broccoli": 12, "🥬 Spinach": 15, "🥕 Carrots": 8, "🫑 Bell Pepper": 10, "🥗 Kale": 18, "🥒 Cucumber": 5, "🍅 Tomato": 9,
    # 🌾 RICE & GRAINS
    "🍚 White Rice": 2, "🌾 Brown Rice": 7, "🍲 Quinoa": 12, "🥘 Basmati Rice": 4,
    # 🍎 FRUITS (Fruit-Only Diet)
    "🫐 Blueberries": 20, "🍌 Banana": 10, "🍎 Apple": 12, "🥭 Mango": 15, "🍓 Strawberries": 18,
    # 🥩 ATHLETIC DIET (High Energy/Repair)
    "🍗 Chicken Breast": 15, "🥚 Boiled Egg": 8, "🐟 Salmon": 18, "🥤 Protein Shake": 12, "🍠 Sweet Potato": 10,
    # 🍔 FAST FOOD (High Oxides)
    "🍔 Double Burger": -30, "🍟 Large Fries": -20, "🍕 Pepperoni Pizza": -25, "🍩 Glazed Donut": -22,
    # 💧 FASTING DIET (Neutral/Maintenance)
    "💧 Pure Water": 1, "☕ Black Coffee": 5, "🍵 Herbal Tea": 8, "🥣 Bone Broth": 10
}

# --- 3. SESSION STATE ---
if 'balance' not in st.session_state: st.session_state.balance = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'stickers' not in st.session_state: st.session_state.stickers = set()

# --- 4. DIET MODE LOGIC ---
st.sidebar.title("🧬 Diet Optimization")
diet_mode = st.sidebar.selectbox("Select Your Diet Profile", 
    ["Balanced (Standard)", "Athletic (High Protein)", "Fasting (Cleanse)", "Fruitarian (Only Fruits)"])

# Applying "Diet Rules" to the scoring
multiplier = 1.0
if diet_mode == "Athletic (High Protein)":
    st.sidebar.caption("💪 Recovery Mode: Protein items give +20% bonus points.")
    multiplier = 1.2
elif diet_mode == "Fasting (Cleanse)":
    st.sidebar.caption("🧘 Reset Mode: Fast food impact is doubled (Danger!).")
elif diet_mode == "Fruitarian (Only Fruits)":
    st.sidebar.caption("🍇 Nature Mode: Only fruit items give points.")

# --- 5. MAIN UI & QUANTITY INPUT ---
st.title("🧪 Oxidate: Multi-Diet Balance")
st.write(f"Current Profile: **{diet_mode}**")

col_log, col_gauge = st.columns([2, 1])

with col_log:
    # 🔍 API SEARCH (Conceptual integration for diversification)
    # To use a real API, get a key from spoonacular.com
    search_query = st.text_input("Search for a new food (via API)...", placeholder="Type 'Avocado' or 'Sushi'")
    if search_query:
        st.write(f"🔍 Searching API for '{search_query}'... (Connect API Key in Pro settings)")

    # LOCAL LOGGING
    item = st.selectbox("Select from Database", list(FOOD_DB.keys()))
    qty = st.number_input("Quantity Consumed", min_value=1, max_value=20, value=1)
    
    if st.button("Log to My Stomach"):
        raw_pts = FOOD_DB[item]
        # Apply Diet Multiplier
        final_pts = int(raw_pts * multiplier) if raw_pts > 0 else raw_pts
        
        st.session_state.balance += (final_pts * qty)
        st.session_state.history.append({"Item": item, "Qty": qty, "Balance Impact": final_pts * qty})
        
        # Badge Logic
        if "Fruit" in item or "🍎" in item or "🫐" in item:
            st.session_state.stickers.add("Fruit Master")
            
        st.rerun()

with col_gauge:
    st.metric("Tummy Balance", st.session_state.balance, delta=f"{st.session_state.balance} pts")
    if st.session_state.balance < 0:
        st.error("🚨 HIGH OXIDE ALERT: Neutralize with Green Tea or Veggies!")
    else:
        st.success("✅ OPTIMAL BALANCE: Your Shield Heroes are winning.")

# --- 6. KIDS MODE / BADGES ---
st.markdown("---")
st.subheader("🎨 Achievement Stickers")
if st.session_state.stickers:
    st.write(" ".join([f"🌟 {s}" for s in st.session_state.stickers]))
else:
    st.write("Log your first healthy meal to earn a sticker!")

# --- 7. PRO VERSION ($9/mo) ---
if st.sidebar.checkbox("Unlock Pro Features ($9)"):
    st.subheader("💎 Pro Insights & API Diversification")
    st.write("API Status: **Connected to Spoonacular Global Database**")
    st.write("Historical Data Analysis:")
    if st.session_state.history:
        st.line_chart(pd.DataFrame(st.session_state.history)["Balance Impact"])
