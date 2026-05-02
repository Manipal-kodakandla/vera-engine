# evals.py

from app import tick
import json


def run_test(name, payload):
    print(f"\nTEST: {name}")

    result = tick(payload)

    if not result:
        print("No output")
        return

    print("Output:", json.dumps(result, indent=2))

    # 🔍 Top-tier evaluation checks
    if not result.get("body"):
        print("Missing body")

    if "%" not in result.get("body", ""):
        print("❌ No specificity (no numbers)")
    else:
        print("Has specificity (numbers/%)")

    if not result.get("cta"):
        print("Missing CTA")
    elif "?" not in result.get("cta", ""):
        print("CTA not engaging")
    else:
        print("Strong CTA")

    if not any(word in result.get("body", "").lower() for word in ["today", "week", "now", "right now"]):
        print("Missing urgency signal")
    else:
        print("Has urgency")

    # 🏆 Top-tier specific checks
    has_metrics = "%" in result.get("body", "")
    has_trigger = any(word in result.get("body", "").lower()
                     for word in ["research", "study", "recall", "dip", "improve", "increase", "due"])

    if has_metrics and has_trigger:
        print("Signal combination present (TOP-TIER)")
    else:
        print("Missing signal combination (not top-tier)")

    # Check rationale quality
    rationale = result.get("rationale", "")
    if rationale:
        if "combine" in rationale.lower() or "leverage" in rationale.lower():
            print("Strong rationale (TOP-TIER)")
        elif "performance" in rationale.lower() or "trigger" in rationale.lower():
            print("Good rationale")
        else:
            print("Weak rationale")
    else:
        print("Missing rationale")

    # Check suppression key specificity
    suppression_key = result.get("suppression_key", "")
    if suppression_key and "_" in suppression_key:
        print("Specific suppression key")
    elif suppression_key and suppression_key != "general_opportunity":
        print("Acceptable suppression key")
    else:
        print("Generic suppression key")

    # Check performance logic correctness
    body_lower = result.get("body", "").lower()
    if "outperform" in body_lower or "chance to convert" in body_lower:
        print("Overperform logic detected")
    elif "reducing" in body_lower or "gap" in body_lower:
        print("Underperform logic detected")

    print("Done")


# ---------------- TEST CASES ---------------- #

tests = [
    {
        "name": "Dentist Underperform + Research",
        "payload": {
            "category": {"name": "dentist", "tone": "professional"},
            "identity": {
                "name": "Dr. Meera Clinic",
                "metric": {"ctr": 2.1, "peer_ctr": 3.0}
            },
            "trigger": {
                "kind": "research_digest",
                "detail": "JIDA study shows WhatsApp recalls improve repeat visits by 27%"
            }
        }
    },
    {
        "name": "Salon Overperform + Recall",
        "payload": {
            "category": {"name": "salon", "tone": "friendly"},
            "identity": {
                "name": "Glow Beauty Studio",
                "metric": {"ctr": 3.2, "peer_ctr": 2.8}
            },
            "trigger": {
                "kind": "recall_due",
                "detail": "45 customers are due for 6-week touchup appointments"
            }
        }
    },
    {
        "name": "Performance Dip",
        "payload": {
            "category": {"name": "restaurant"},
            "identity": {
                "name": "Spice Kitchen",
                "metric": {"ctr": 1.8, "peer_ctr": 2.5}
            },
            "trigger": {
                "kind": "perf_dip",
                "detail": "CTR dropped below peer average this week"
            }
        }
    }
]


if __name__ == "__main__":
    for t in tests:
        run_test(t["name"], t["payload"])
