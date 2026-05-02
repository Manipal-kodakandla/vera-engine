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
        print("❌ No output")
        return

    try:
        data = json.loads(output)
    except:
        print("❌ Invalid JSON")
        return

    print("✅ Output:", data)

    # 🔍 Simple checks
    if not data.get("body"):
        print("❌ Missing body")

    if "%" not in data.get("body", ""):
        print("⚠️ No specificity (no numbers)")

    if not data.get("cta"):
        print("❌ Missing CTA")

    if "?" not in data.get("cta", ""):
        print("⚠️ CTA may not be engaging")

    if "week" not in data.get("body", "").lower():
        print("⚠️ Missing urgency signal")

    print("🎯 Done")


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