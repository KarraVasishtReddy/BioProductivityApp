import datetime

class OxidateApp:
    def __init__(self, username, is_pro=False):
        self.username = username
        self.is_pro = is_pro
        self.balance_score = 0
        self.logs = []
        
        # Database of values (Oxides vs Anti-oxides)
        self.values = {
            "blueberry": 15, "green tea": 10, "spinach": 12,  # Anti-oxides (+)
            "soda": -15, "fried food": -20, "alcohol": -25    # Oxides (-)
        }

    def log_item(self, item_name):
        item = item_name.lower()
        if item in self.values:
            points = self.values[item]
            self.balance_score += points
            self.logs.append(f"{datetime.datetime.now().strftime('%H:%M')} - {item_name} ({points} pts)")
            return f"✅ Logged {item_name}. New Balance: {self.balance_score}"
        else:
            return f"❌ '{item_name}' not found in database."

    def display_ui(self):
        print("\n" + "="*40)
        print(f" OXIDATE MVP - User: {self.username}")
        print(f" Status: {'💎 PRO' if self.is_pro else '🆓 FREE'}")
        print("="*40)
        
        # The Balance Meter
        status = "Healthy" if self.balance_score >= 0 else "Oxidized"
        print(f" CURRENT BALANCE: {self.balance_score} ({status})")
        
        # Pro Feature: Detailed Insights
        if self.is_pro:
            print("\n[PRO FEATURE] AI Health Insight:")
            if self.balance_score < 0:
                print(" > High stomach oxides detected. Suggesting 200ml Green Tea.")
            else:
                print(" > Internal chemistry is balanced. Peak performance active.")
        
        # Free Feature: Ads
        else:
            print("\n" + "-"*40)
            print(" [ AD SPACE ]")
            print(" Buy 'Pure-Antiox' Supplements now! 20% OFF")
            print(" Upgrade to PRO for $9 to remove these ads.")
            print("-"*40)

# --- EXECUTION BLOCK (The part that makes it run) ---

def run_app():
    # 1. Initialize a Free User (MVP Format)
    user_app = OxidateApp("GuestUser", is_pro=False)

    # 2. Simulate User Activity
    print(user_app.log_item("Blueberry"))
    print(user_app.log_item("Soda"))
    
    # 3. Show the UI
    user_app.display_ui()

    # 4. Show what a Pro User ($9/mo) sees
    print("\n\n--- SWITCHING TO PRO VERSION ($9/mo) ---")
    pro_app = OxidateApp("PowerUser", is_pro=True)
    pro_app.log_item("Green Tea")
    pro_app.display_ui()

if __name__ == "__main__":
    run_app()
