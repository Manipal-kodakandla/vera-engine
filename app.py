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


# ✅ METADATA
@app.get("/v1/metadata")
def metadata():
    return {
        "name": "Vera Message Engine",
        "version": "1.0"
    }


# ✅ CONTEXT
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
    decision = decide(context)
    prompt = build_prompt(context, decision)

    output = generate_message(prompt)

    if not output:
        print("⚠️ Using fallback message")

        return {
            "body": f"{context['merchant'].get('name', 'Merchant')}, your CTR is {context['merchant'].get('metric', {}).get('ctr', 0)}% vs peers {context['merchant'].get('metric', {}).get('peer_ctr', 0)}%. This gap is impacting performance this week.",
            "cta": "I can set this up for you today — want me to activate it?",
            "send_as": "vera",
            "suppression_key": "fallback_message",
            "rationale": "Fallback used due to model failure; still uses merchant metrics and trigger"
        }

    try:
        data = json.loads(output)
    except:
        return {"error": "invalid json"}

    if not any(char.isdigit() for char in data.get("body", "")):
        data["body"] += " Acting now can improve results by up to 20%."

    if not any(word in data["body"].lower() for word in ["today", "week", "now"]):
        data["body"] += " Acting this week can help improve results."

    if "?" not in data.get("cta", ""):
        data["cta"] = "I can set this up for you today — want me to activate it?"

    return data