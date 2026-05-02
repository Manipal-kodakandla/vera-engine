

def decide(context):
    category = context["category"]
    merchant = context["merchant"]
    trigger = context["trigger"]

    decision = {}

    kind = trigger.get("kind", "")

    if kind == "perf_dip":
        decision["reason"] = "Merchant performance is below peer average"
        decision["goal"] = "increase traffic"
        decision["tone"] = "urgent"
        decision["angle"] = "discount"
        decision["urgency"] = "high"
        decision["metric_focus"] = "ctr"
        decision["trigger_insight"] = trigger.get("detail", "")
        decision["expected_impact"] = "20-30%"
        

    elif kind == "research_digest":
        decision["reason"] = "New research insight relevant to merchant"
        decision["goal"] = "educate"
        decision["tone"] = "professional"
        decision["angle"] = "insight"
        decision["urgency"] = "medium"
        decision["time_hint"] = "this week"
        decision["metric_focus"] = "conversion"
        decision["trigger_insight"] = trigger.get("detail", "")
        decision["expected_impact"] = "27%"

    elif kind == "recall_due":
        decision["reason"] = "Customer is likely due for return visit"
        decision["goal"] = "conversion"
        decision["tone"] = "personalized"
        decision["angle"] = "reminder"
        decision["urgency"] = "high"
        decision["metric_focus"] = "retention"
        decision["trigger_insight"] = trigger.get("detail", "")
        decision["expected_impact"] = "35%"

    else:
        decision["reason"] = "General engagement opportunity"
        decision["goal"] = "engagement"
        decision["tone"] = "neutral"
        decision["angle"] = "general"
        decision["urgency"] = "low"
        decision["metric_focus"] = "general"
        decision["trigger_insight"] = trigger.get("detail", "")
        decision["expected_impact"] = "10-15%"

    return decision
