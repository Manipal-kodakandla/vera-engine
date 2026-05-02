# decision.py

def decide(context):
    category = context["category"]
    merchant = context["merchant"]
    trigger = context["trigger"]

    decision = {}

    kind = trigger.get("kind", "")

    # 🔥 CASE 1 — Performance Drop
    if kind == "perf_dip":
        decision["reason"] = "Merchant performance is below peer average"
        decision["goal"] = "increase traffic"
        decision["tone"] = "urgent"
        decision["angle"] = "discount"
        decision["urgency"] = "high"
        

    # 🔥 CASE 2 — Research Insight
    elif kind == "research_digest":
        decision["reason"] = "New research insight relevant to merchant"
        decision["goal"] = "educate"
        decision["tone"] = "professional"
        decision["angle"] = "insight"
        decision["urgency"] = "medium"
        decision["time_hint"] = "this week"

    # 🔥 CASE 3 — Customer Recall
    elif kind == "recall_due":
        decision["reason"] = "Customer is likely due for return visit"
        decision["goal"] = "conversion"
        decision["tone"] = "personalized"
        decision["angle"] = "reminder"
        decision["urgency"] = "high"

    # 🔥 DEFAULT
    else:
        decision["reason"] = "General engagement opportunity"
        decision["goal"] = "engagement"
        decision["tone"] = "neutral"
        decision["angle"] = "general"
        decision["urgency"] = "low"

    return decision