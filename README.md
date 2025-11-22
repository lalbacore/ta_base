# Instructions for VS Code Agent

## Mission
Scaffold the core framework of `team-agent`, a modular AI agent system using Python. The system should support standalone agents and composable teams.

## Step 1: Create Base Agent Class
- File: `base/base_agent.py`
- Class: `BaseAgent`
- Include:
  - `__init__()` with name, ID, capabilities, policy
  - `evaluate_intent(intent)` for compliance checks
  - `act(intent)` for executing or refusing
  - `record(event)` to log actions
  - `describe()` for agent metadata
- Support hooks for future integrations (e.g., Autogen, LangChain)

## Step 2: Create Role Map in Swarm Template
- File: `swarms/team_agent/roles.py`
- Define agent roles: architect, builder, critic, compliance, recorder
- Each should contain `intent`, `capabilities`, and `policy` example

## Step 3: Create README
- File: `README.md`
- Summary of mission, architecture, directory structure
- Credit founding idea: Intent → Capability → Governance triangle

## Bonus: Setup Dev Tools
- Create `.gitignore`, `.env.example`
- Add stub test under `utils/tests/test_base_agent.py`

## Output
File structure, working class in `base/base_agent.py`, and role map in `swarms/team_agent/roles.py`.