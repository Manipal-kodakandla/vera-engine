from fastapi import FastAPI
from store import Store
from decision import decide
from prompt import build_prompt
from composer import generate_message
import json
import logging
import re

logger = logging.getLogger("vera")

app = FastAPI()
store = Store()
@app.get("/v1/healthz")
def health():
    return {"status": "ok"}


@app.get("/v1/metadata")
def metadata():
    return {
        "name": "Vera Message Engine",
        "version": "1.0",
        "description": "Context-aware AI system that generates merchant messages using decision-driven reasoning"
    }

@app.post("/v1/context")
def set_context(data: dict):
    payload = data.get("payload", {})

    store.category = payload.get("category", {})
    store.merchant = payload.get("identity") or payload.get("merchant", {})
    store.trigger = payload.get("trigger", {})
    store.customer = payload.get("customer", None)

    logger.info(f"Context set - merchant: {store.merchant}, trigger: {store.trigger}")

    return {"accepted": True}

@app.post("/v1/tick")
def tick():
    context = store.get_context()

    # ✅ Robust extraction — handle both "identity" and "merchant" keys
    merchant = context.get("merchant", {})
    metrics = merchant.get("metric", {})

    ctr = metrics.get("ctr")
    peer_ctr = metrics.get("peer_ctr")
    name = merchant.get("name", "Merchant")

    trigger_detail = context.get("trigger", {}).get("detail", "")
    trigger_kind = context.get("trigger", {}).get("kind", "")
    category_name = context.get("category", {}).get("name", "").lower()

    # Category-aware context word
    if "dentist" in category_name or "clinic" in category_name or "doctor" in category_name:
        context_word = "patient traffic"
    elif "salon" in category_name or "beauty" in category_name or "spa" in category_name:
        context_word = "customer visits"
    elif "restaurant" in category_name or "cafe" in category_name:
        context_word = "foot traffic"
    else:
        context_word = "performance"

    logger.info(f"Tick - name={name}, ctr={ctr}, peer_ctr={peer_ctr}, trigger={trigger_kind}, category={category_name}")

    # 🔥 STEP 1: Determine performance mode
    if ctr is not None and peer_ctr is not None:
        if ctr < peer_ctr:
            mode = "underperform"
        else:
            mode = "overperform"
    else:
        mode = "unknown"

    # 🔥 STEP 2: Build message body (Decision Engine = Primary)
    if mode == "underperform":
        body = f"{name}, your CTR is {ctr}% vs peers {peer_ctr}% — this gap is reducing {context_word} right now."
    elif mode == "overperform":
        body = f"{name}, your CTR is {ctr}% vs peers {peer_ctr}% — you're outperforming peers, with a chance to convert more high-intent {context_word} into repeat visits this week."
    else:
        body = f"{name}, we noticed an opportunity to improve {context_word} this week based on recent trends."

    # 🔥 STEP 3: Trigger Fusion (ALWAYS include trigger insight)
    if trigger_detail:
        if mode == "underperform":
            body += f" {trigger_detail}, which can help recover this gap."
        elif mode == "overperform":
            body += f" {trigger_detail}, which can help leverage this momentum."
        else:
            body += f" {trigger_detail}, which can help drive better results."

    # 🔥 STEP 4: Smart CTA with trigger-detail personalization
    detail_numbers = re.findall(r'\d+', trigger_detail) if trigger_detail else []

    if "recall" in trigger_kind and detail_numbers:
        noun = "customers" if "customer" in trigger_detail.lower() else "users"
        cta = f"I can send recall messages to these {detail_numbers[0]} {noun} today — want me to activate it?"
    elif "recall" in trigger_kind:
        cta = "I can send recall messages based on this opportunity today — want me to activate it?"
    elif "research" in trigger_kind:
        cta = "I can apply this strategy today — want me to activate it?"
    elif "perf" in trigger_kind:
        cta = "I can set up a performance boost today — want me to activate it?"
    else:
        cta = "I can set this up for you today — want me to activate it?"

    # 🔥 STEP 5: Smart suppression key
    if mode == "overperform" and trigger_kind:
        suppression_key = f"{trigger_kind}_high_performance"
    elif mode == "underperform" and trigger_kind:
        suppression_key = f"ctr_gap_{trigger_kind}"
    elif mode == "overperform":
        suppression_key = "high_performance_only"
    elif mode == "underperform":
        suppression_key = "ctr_gap_only"
    else:
        suppression_key = "general_opportunity"

    # 🔥 STEP 6: Causal rationale
    if mode == "underperform" and trigger_kind:
        rationale = f"Combines performance gap ({ctr}% vs {peer_ctr}%) with trigger insight ({trigger_kind}) to drive immediate action"
    elif mode == "overperform" and trigger_kind:
        rationale = f"Leverages strong performance ({ctr}% vs {peer_ctr}%) and trigger insight ({trigger_kind}) to maximize opportunity"
    elif mode == "underperform":
        rationale = f"Uses performance gap ({ctr}% vs {peer_ctr}%) to drive recovery action"
    elif mode == "overperform":
        rationale = f"Leverages strong performance ({ctr}% vs {peer_ctr}%) to maximize growth"
    else:
        rationale = "General engagement opportunity based on recent trends"

    # Build the decision-engine result (this IS the primary output)
    result = {
        "body": body,
        "cta": cta,
        "send_as": "vera",
        "suppression_key": suppression_key,
        "rationale": rationale
    }

    # 🔥 STEP 7: Try LLM as optional enhancer
    decision = decide(context)
    prompt = build_prompt(context, decision)
    output = generate_message(prompt)

    if not output:
        logger.info("LLM unavailable — using decision engine output")
        return result

    # LLM succeeded — parse and enhance with our signal combination logic
    try:
        data = json.loads(output)
    except:
        logger.info("LLM output invalid JSON — using decision engine output")
        return result

    # Post-process LLM output with our performance-aware logic
    # Ensure suppression key reflects performance direction
    if mode == "overperform" and trigger_kind:
        data["suppression_key"] = f"{trigger_kind}_high_performance"
    elif mode == "underperform" and trigger_kind:
        data["suppression_key"] = f"ctr_gap_{trigger_kind}"
    elif trigger_kind:
        data["suppression_key"] = trigger_kind
    else:
        data["suppression_key"] = "general_message"

    # Ensure rationale reflects performance direction
    if mode == "overperform" and ctr and peer_ctr:
        data["rationale"] = f"Leverages strong performance ({ctr}% vs {peer_ctr}%) and trigger insight ({trigger_kind}) to maximize opportunity"
    elif mode == "underperform" and ctr and peer_ctr:
        data["rationale"] = f"Combines performance gap ({ctr}% vs {peer_ctr}%) with trigger insight ({trigger_kind}) to drive immediate action"

    # Ensure number in body
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
        data["cta"] = cta

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
