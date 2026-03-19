# ai_advisor.py

def get_ai_advice(product, season, days):

    # Product insight
    if product == "Flight":
        product_insight = "Flights are highly seasonal and sensitive to demand changes."
    elif product == "Hotel":
        product_insight = "Hotels perform well during holidays and travel seasons."
    elif product == "Cruise":
        product_insight = "Cruises are premium offerings with higher commission potential."
    else:
        product_insight = "Product performance varies."

    # Season insight
    if season == "Low":
        season_insight = "Low season offers higher commission opportunities."
    else:
        season_insight = "Peak season has high demand but lower commission margins."

    # Speed insight
    if days <= 5:
        speed_insight = "Fast sales (≤5 days) qualify for bonus commission."
        speed_type = "Fast"
    else:
        speed_insight = "Slower sales reduce bonus earning opportunities."
        speed_type = "Slow"

    # Final recommendation
    if season == "Low" and days <= 5:
        final = "This is the BEST strategy for maximizing commission."
    elif season == "Low":
        final = "Good strategy, but faster sales can increase earnings."
    else:
        final = "Consider targeting low season for better commission."

    # Output formatting (🔥 THIS IS THE MAGIC)
    advice = f"""
📊 **Recommendation Analysis**

**Product:** {product}  
➡️ {product_insight}

**Season:** {season}  
➡️ {season_insight}

**Selling Speed:** {speed_type} ({days} days)  
➡️ {speed_insight}

---

💡 **Final Insight:**  
{final}

🚀 **Strategy Tip:**  
Focus on selecting the right product, selling during low-demand periods, and closing deals quickly to maximize commission.
"""

    return advice