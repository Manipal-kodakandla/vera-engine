# evals.py

from store import Store
from decision import decide
from prompt import build_prompt
from composer import generate_message
import json


def run_test(name, trigger_data):
    print(f"\n🧪 TEST: {name}")

    store = Store()
    store.load_sample_data()

    # Override trigger
    store.trigger = trigger_data

    context = store.get_context()
    decision = decide(context)
    prompt = build_prompt(context, decision)
    output = generate_message(prompt)

    if not output:
        print("No output")
        return

    try:
        data = json.loads(output)
    except:
        print("Invalid JSON")
        return

    print("Output:", data)

    # 🔍 Top-tier evaluation checks
    if not data.get("body"):
        print("Missing body")

    if "%" not in data.get("body", ""):
        print("No specificity (no numbers)")

    if not data.get("cta"):
        print("Missing CTA")

    if "?" not in data.get("cta", ""):
        print("CTA may not be engaging")

    if "week" not in data.get("body", "").lower():
        print("Missing urgency signal")

    # 🏆 Top-tier specific checks
    has_metrics = "%" in data.get("body", "")
    has_trigger = any(word in data.get("body", "").lower() 
                     for word in ["research", "study", "recall", "dip", "improve", "increase"])
    
    if has_metrics and has_trigger:
        print("Signal combination present (TOP-TIER)")
    else:
        print("Missing signal combination (not top-tier)")

    # Check rationale quality
    rationale = data.get("rationale", "")
    if rationale:
        if "combine" in rationale.lower() or "connect" in rationale.lower():
            print("Strong rationale (TOP-TIER)")
        elif "performance" in rationale.lower() or "trigger" in rationale.lower():
            print("Good rationale")
        else:
            print("Weak rationale")
    else:
        print("Missing rationale")

    # Check suppression key specificity
    suppression_key = data.get("suppression_key", "")
    if suppression_key and "_" in suppression_key:
        print("Specific suppression key")
    elif suppression_key == "fallback_message":
        print("Generic suppression key")
    else:
        print("Poor suppression key")

    print("Done")


# ---------------- TEST CASES ---------------- #

tests = [
    {
        "name": "Research Trigger",
        "trigger": {
            "kind": "research_digest",
            "detail": "Study shows 27% increase in repeat visits"
        }
    },
    {
        "name": "Performance Dip",
        "trigger": {
            "kind": "perf_dip",
            "detail": "CTR dropped below peer average"
        }
    },
    {
        "name": "Recall Due",
        "trigger": {
            "kind": "recall_due",
            "detail": "Customer due for revisit"
        }
    }
]


if __name__ == "__main__":
    for t in tests:
        run_test(t["name"], t["trigger"])
