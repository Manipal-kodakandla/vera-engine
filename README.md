## Vera Message Engine

A context-aware AI system that generates high-quality, decision-driven WhatsApp messages for merchants.

# Problem

Merchants receive generic, untimed messages that:

lack specificity
ignore business performance
fail to drive action

# Result: low engagement and missed growth opportunities

# Solution

This system composes messages using 4 input layers:

Category → tone & domain context
Merchant → performance metrics (CTR vs peers)
Trigger → why the message should be sent now
Customer → optional targeting
# Core Idea

Instead of relying on LLMs alone, this system uses a:

Deterministic Decision Engine + Optional LLM Enhancement

# Architecture
Input Context
      ↓
Decision Engine (PRIMARY)
  - Performance analysis
  - Trigger reasoning
  - Category adaptation
      ↓
Message Generation
      ↓
LLM Enhancement (optional)
      ↓
Final Output (guaranteed)
## Key Features
✅ Context-aware reasoning (not generic prompts)
✅ Performance-based messaging (underperform vs outperform)
✅ Trigger-driven decisions (why now matters)
✅ Strong, actionable CTAs
✅ Multimodel fallback (LLM optional)
✅ Stateless API design (evaluator-safe)
✅ Always returns valid structured output
# Example
Input
{
  "category": {"name": "dentist"},
  "identity": {
    "name": "Dr Meera Clinic",
    "metric": {"ctr": 2.1, "peer_ctr": 3.0}
  },
  "trigger": {
    "kind": "research_digest",
    "detail": "WhatsApp recalls improve repeat visits by 27%"
  }
}
Output
{
  "body": "Dr Meera Clinic, your CTR is 2.1% vs peers 3.0% — this gap is reducing patient traffic right now. WhatsApp recalls improve repeat visits by 27%, which can help recover this gap.",
  "cta": "I can apply this strategy today — want me to activate it?",
  "send_as": "vera"
}
## Design Decisions
Decision Engine first, LLM second
Explicit reasoning > black-box generation
Reliability over creativity
Context fusion is mandatory
# Evaluation

The system is tested on multiple scenarios:

Underperforming vs outperforming merchants
Different trigger types
Missing data cases

Each output is validated for:

specificity
urgency
actionability
signal combination
🔌 API Endpoints
GET /v1/healthz
GET /v1/metadata
POST /v1/tick (stateless)
POST /v1/reply
🚀 Deployment

## Hosted on Render:

link: https://vera-engine-bygs.onrender.com

## Final Note

This is not just a message generator —
it’s a decision system designed to reason about context, timing, and action, ensuring every message is relevant, specific, and actionable.
