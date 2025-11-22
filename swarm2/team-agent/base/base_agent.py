class BaseAgent:
    def __init__(self, name, id, capabilities, policy):
        self.name = name
        self.id = id
        self.capabilities = capabilities
        self.policy = policy

    def evaluate_intent(self, intent):
        return True

    def act(self, intent):
        if self.name == "Architect":
            return {"design": f"Design for {intent}"}
        elif self.name == "Builder":
            return {"build": f"Build based on {intent['design']}"}
        elif self.name == "Critic":
            return {"passed": True, "notes": "Looks good"}
        elif self.name == "Governance":
            return {"allowed": True}
        elif self.name == "Recorder":
            return {"status": "success", "score": 100, "log": intent}
        elif self.name == "TestAgent":
            return {"test_results": "All tests passed"}
        return None

    def record(self, event):
        pass

    def describe(self):
        return {
            "name": self.name,
            "id": self.id,
            "capabilities": self.capabilities,
            "policy": self.policy
        }