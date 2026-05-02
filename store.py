# store.py

class Store:
    def __init__(self):
        self.category = {}
        self.merchant = {}
        self.trigger = {}
        self.customer = {}

    def load_sample_data(self):
        # Category
        self.category = {
            "name": "dentist",
            "tone": "professional"
        }

        # Merchant
        self.merchant = {
            "name": "Dr. Meera Clinic",
            "metric": {
                "ctr": 2.1,
                "peer_ctr": 3.0
            }
        }

        # Trigger (MOST IMPORTANT)
        self.trigger = {
            "kind": "research_digest",
            "detail": "JIDA study shows WhatsApp recalls improve repeat visits by 27%"
        }

        # Customer (optional)
        self.customer = None

    def get_context(self):
        return {
            "category": self.category,
            "merchant": self.merchant,
            "trigger": self.trigger,
            "customer": self.customer
        }