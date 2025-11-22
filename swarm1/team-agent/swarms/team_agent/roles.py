# roles.py

class Role:
    def __init__(self, name, intent, capabilities, policy):
        self.name = name
        self.intent = intent
        self.capabilities = capabilities
        self.policy = policy

# Define agent roles
roles = {
    "architect": Role(
        name="architect",
        intent="Design the overall structure of the agent system.",
        capabilities=["system design", "architecture planning"],
        policy="Ensure all designs adhere to governance standards."
    ),
    "builder": Role(
        name="builder",
        intent="Implement the components of the agent system.",
        capabilities=["coding", "integration", "testing"],
        policy="Follow best practices in coding and documentation."
    ),
    "critic": Role(
        name="critic",
        intent="Evaluate the performance and effectiveness of agents.",
        capabilities=["analysis", "feedback", "reporting"],
        policy="Provide constructive feedback and suggestions for improvement."
    ),
    "compliance": Role(
        name="compliance",
        intent="Ensure all actions and intents comply with regulations.",
        capabilities=["regulatory knowledge", "audit"],
        policy="Maintain compliance with all relevant laws and guidelines."
    ),
    "recorder": Role(
        name="recorder",
        intent="Log actions and events for accountability.",
        capabilities=["data entry", "report generation"],
        policy="Ensure accurate and timely recording of all relevant events."
    )
}