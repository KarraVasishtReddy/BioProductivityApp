class BioProductivityApp:
    def __init__(self, user_name, subscription_tier="free"):
        """
        Initializes the app with user data and subscription status.
        Tiers: 'free' (with ads) or 'pro' ($9/mo).
        """
        self.user_name = user_name
        self.tier = subscription_tier.lower()
        self.antioxidant_log = []
        self.pro_oxidant_log = []
        
        # Scoring Constants [cite: 15, 16]
        self.FOOD_VALUES = {
            "blueberries": 10, "green tea": 8, "spinach": 7, "turmeric": 9, # Antioxidants
            "processed sugar": -10, "alcohol": -12, "charred meat": -8     # Pro-oxidants
        }

    def log_nutrition(self, item):
        """Logs food items and updates the Oxidate Balance Score[cite: 6, 7]."""
        item = item.lower()
        if item in self.FOOD_VALUES:
            value = self.FOOD_VALUES[item]
            if value > 0:
                self.antioxidant_log.append(value)
            else:
                self.pro_oxidant_log.append(abs(value))
            return f"Logged {item}. Current Balance Score: {self.get_oxidate_balance()}"
        return "Item not found in database."

    def get_oxidate_balance(self):
        """Calculates the Balance Score (B)[cite: 15]."""
        return sum(self.antioxidant_log) - sum(self.pro_oxidant_log)

    def calculate_peak_readiness(self, sleep_quality, circadian_phase):
        """
        Calculates the Peak Readiness Score (P)[cite: 41].
        S = sleep_quality (0-100)
        H = hydration/nutrition (mapped from oxidate balance)
        C = circadian_phase (0-100)
        """
        # Normalize hydration/nutrition (H) based on gut balance score [cite: 42]
        h_score = max(0, min(100, self.get_oxidate_balance() + 50)) 
        
        p_score = (sleep_quality * 0.4) + (h_score * 0.3) + (circadian_phase * 0.3)
        return round(p_score, 2)

    def get_dashboard_view(self, sleep, circadian):
        """Renders the UI data based on subscription tier[cite: 9, 13, 33, 39]."""
        p_score = self.calculate_peak_readiness(sleep, circadian)
        
        dashboard = {
            "user": self.user_name,
            "oxidate_balance": self.get_oxidate_balance(),
            "peak_readiness": p_score,
            "status": "Peak Window" if p_score > 75 else "Recovery Phase"
        }

        # Handle Ads and Premium Features 
        if self.tier == "free":
            dashboard["ad_space"] = "[AD]: Upgrade to Pro for $9 to remove ads and unlock AI Scheduling!"
            dashboard["ai_features"] = "Locked"
        else:
            dashboard["ad_space"] = None
            dashboard["ai_features"] = "AI Schedule Orchestrator Active: Tasks moved to peak energy windows."
            dashboard["profit_analytics"] = "Calculating increased hourly earnings..."

        return dashboard

# --- Example Execution ---
# Initialize a Pro User [cite: 35]
app = BioProductivityApp("Alex", subscription_tier="pro")

# Log daily activities [cite: 16, 42]
app.log_nutrition("blueberries")
app.log_nutrition("green tea")
app.log_nutrition("alcohol")

# Generate current dashboard status [cite: 44, 45]
current_status = app.get_dashboard_view(sleep=85, circadian=90)
print(f"Dashboard for {current_status['user']}:")
print(f"Readiness Score: {current_status['peak_readiness']}")
print(f"AI Status: {current_status['ai_features']}")
