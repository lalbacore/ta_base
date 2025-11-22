# Instructions for VS Code Agent

## Mission
Scaffold the core framework of `team-agent`, a modular AI agent system using Python. The system should support standalone agents and composable teams.

## Architecture
The `team-agent` project is structured to facilitate the development of a modular AI agent system. The key components include:

- **Base Agent Class**: Located in `base/base_agent.py`, this class serves as the foundation for all agents within the system. It includes essential methods for agent functionality, such as intent evaluation, action execution, event logging, and metadata description.

- **Role Map**: Found in `swarms/team_agent/roles.py`, this file defines various roles that agents can assume, including architect, builder, critic, compliance, and recorder. Each role is characterized by its intent, capabilities, and governing policies.

- **Testing Framework**: The `utils/tests/test_base_agent.py` file contains stub tests for the BaseAgent class, ensuring that the core functionalities are validated as the project evolves.

## Directory Structure
```
team-agent
├── base
│   └── base_agent.py
├── swarms
│   └── team_agent
│       └── roles.py
├── utils
│   └── tests
│       └── test_base_agent.py
├── .env.example
├── .gitignore
└── README.md
```

## Founding Idea
The project is built upon the concept of the Intent → Capability → Governance triangle, which serves as the guiding principle for the design and functionality of the agents within the system.