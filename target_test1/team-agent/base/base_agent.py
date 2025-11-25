class BaseAgent:
    def __init__(self, name, agent_id, capabilities, policy):
        self.name = name
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.policy = policy

    def evaluate_intent(self, intent):
        # Compliance checks for the given intent
        pass

    def act(self, intent):
        # Execute the intent or refuse it
        pass

    def record(self, event):
        # Log the actions taken by the agent
        pass

    def describe(self):
        # Return metadata about the agent
        return {
            "name": self.name,
            "id": self.agent_id,
            "capabilities": self.capabilities,
            "policy": self.policy
        }

    # Hooks for future integrations can be added here
    def integrate(self, integration_name):
        # Placeholder for integration logic
        pass