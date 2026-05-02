from store import Store
from decision import decide
from prompt import build_prompt
from composer import generate_message
import json


ddef tick(store):
    print("\nTICK TRIGGERED")

    context = store.get_context()

    print("\nCONTEXT:")
    print(context)

    # Decision
    decision = decide(context)

    print("\nDECISION:")
    print(decision)

    # Prompt
    prompt = build_prompt(context, decision)

    print("\nPROMPT:")
    print(prompt)

    # Generate
    output = generate_message(prompt)

    print("\nRAW OUTPUT:")
    print(output)

    if not output:
        print("No output from model")
        return

    # ✅ Parse FIRST
    try:
        data = json.loads(output)
    except Exception as e:
        print("\nJSON ERROR:", e)
        return

    # ✅ THEN apply fixes

    # Ensure number
    if not any(char.isdigit() for char in data.get("body", "")):
        data["body"] += " Acting now can improve results by up to 20%."

    # Ensure urgency
    if not any(word in data["body"].lower() for word in ["today", "week", "now"]):
        data["body"] += " Acting this week can help improve results."

    # Ensure CTA quality
    if "?" not in data.get("cta", ""):
        data["cta"] = "I can set this up for you today — want me to activate it?"

    print("\nFINAL OUTPUT:")
    print(json.dumps(data, indent=2))