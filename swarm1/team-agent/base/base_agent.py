class BaseAgent:
    def __init__(self, name, id, capabilities, policy):
        self.name = name
        self.id = id
        self.capabilities = capabilities
        self.policy = policy

    def evaluate_intent(self, intent):
        # Implement compliance checks for the intent
        pass

    def act(self, intent):
        # Execute or refuse the given intent
        pass

    def record(self, event):
        # Log actions taken by the agent
        pass

    def describe(self):
        # Provide metadata about the agent
        return {
            "name": self.name,
            "id": self.id,
            "capabilities": self.capabilities,
            "policy": self.policy
        }