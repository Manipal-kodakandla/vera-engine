from fastapi import FastAPI
from store import Store
from decision import decide
from prompt import build_prompt
from composer import generate_message
import json

app = FastAPI()
store = Store()
@app.get("/v1/healthz")
def health():
    return {"status": "ok"}


@app.get("/v1/metadata")
def metadata():
    return {
        "name": "Vera Message Engine",
        "version": "1.0"
    }

@app.post("/v1/context")
def set_context(data: dict):
    payload = data.get("payload", {})

    store.category = payload.get("category", {})
    store.merchant = payload.get("identity", {})
    store.trigger = payload.get("trigger", {})
    store.customer = payload.get("customer", None)

    return {"accepted": True}

@app.post("/v1/tick")
def tick():
    context = store.get_context()

    # ✅ Safe extraction
    merchant = context.get("merchant", {})
    metrics = merchant.get("metric", {})

    ctr = metrics.get("ctr")
    peer_ctr = metrics.get("peer_ctr")
    name = merchant.get("name", "Merchant")

    decision = decide(context)
    prompt = build_prompt(context, decision)

    output = generate_message(prompt)

    if not output:
        print("Using fallback message")
        
        # Get trigger details for signal combination
        trigger_detail = context.get("trigger", {}).get("detail", "")
        trigger_kind = context.get("trigger", {}).get("kind", "")
        
        if ctr is not None and peer_ctr is not None and trigger_detail:
            body = f"{name}, your CTR is {ctr}% vs peers {peer_ctr}% - {trigger_detail}. Acting this week can recover this gap."
            suppression_key = f"ctr_gap_{trigger_kind}"
            rationale = f"Combines performance gap ({ctr}% vs {peer_ctr}%) with trigger insight ({trigger_kind}) to drive immediate action"
        elif ctr is not None and peer_ctr is not None:
            body = f"{name}, your CTR is {ctr}% vs peers {peer_ctr}%. This gap is impacting performance this week."
            suppression_key = "ctr_gap_only"
            rationale = f"Uses performance gap ({ctr}% vs {peer_ctr}%) to drive action"
        else:
            body = f"{name}, we noticed an opportunity to improve performance this week based on recent trends."
            suppression_key = "general_opportunity"
            rationale = "General engagement opportunity based on recent trends"

        return {
            "body": body,
            "cta": "I can set this up for you today — want me to activate it?",
            "send_as": "vera",
            "suppression_key": suppression_key,
            "rationale": rationale
        }

    try:
        data = json.loads(output)
    except:
        return {"error": "invalid json"}

    # 🔥 Post-processing fixes with signal combination

    # Generate specific suppression key and rationale
    trigger_kind = context.get("trigger", {}).get("kind", "")
    trigger_detail = context.get("trigger", {}).get("detail", "")
    
    # Smart suppression key generation
    suppression_parts = []
    if ctr and peer_ctr:
        suppression_parts.append("ctr_gap")
    if trigger_kind:
        suppression_parts.append(trigger_kind)
    
    data["suppression_key"] = "_".join(suppression_parts) if suppression_parts else "general_message"
    
    # Generate meaningful rationale
    rationale_parts = []
    if ctr and peer_ctr:
        rationale_parts.append(f"performance gap ({ctr}% vs {peer_ctr}%)")
    if trigger_detail:
        rationale_parts.append(f"trigger insight ({trigger_kind})")
    
    if len(rationale_parts) > 1:
        data["rationale"] = f"Combines {', '.join(rationale_parts)} to drive immediate action"
    elif rationale_parts:
        data["rationale"] = f"Uses {rationale_parts[0]} to drive action"
    else:
        data["rationale"] = "General engagement message"

    # Ensure number
    if not any(char.isdigit() for char in data.get("body", "")):
        if ctr:
            data["body"] += f" Your CTR is {ctr}%."
        else:
            data["body"] += " Acting now can improve results by up to 20%."

    # Ensure urgency
    if not any(word in data["body"].lower() for word in ["today", "week", "now"]):
        data["body"] += " Acting this week can help improve results."

    # Ensure CTA
    if "?" not in data.get("cta", ""):
        data["cta"] = "I can set this up for you today — want me to activate it?"

    return data

@app.post("/v1/reply")
def reply(data: dict):
    msg = data.get("message", "").lower()

    if "yes" in msg:
        return {
            "body": "Great — I’ll set this up for you today and share results shortly.",
            "cta": "Done",
            "send_as": "vera"
        }

    if "no" in msg:
        return {
            "body": "No problem — I’ll pause this for now. Let me know anytime.",
            "cta": "Okay",
            "send_as": "vera"
        }

    return {
        "body": "Got it — can you share more details so I can help better?",
        "cta": "Reply",
        "send_as": "vera"
    }
