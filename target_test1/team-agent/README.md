# Instructions for VS Code Agent

## Mission
Scaffold the core framework of `team-agent`, a modular AI agent system using Python. The system should support standalone agents and composable teams.

## Project Overview
The `team-agent` project is designed to create a modular AI agent system that can operate both as standalone agents and as part of composable teams. The architecture is built around the concept of agents that can evaluate intents, execute actions, and maintain compliance through defined capabilities and policies.

## Directory Structure
- **base/**: Contains the core agent class.
  - `base_agent.py`: Defines the `BaseAgent` class with essential methods for agent functionality.
  
- **swarms/**: Houses the agent roles and mission execution.
  - **team_agent/**: Contains role definitions and mission execution scripts.
    - `roles.py`: Defines various agent roles (architect, builder, critic, compliance, recorder) with examples of intent, capabilities, and policy.
    - `roles_v2.py`: Executes the mission to scaffold the team-agent framework using the Orchestrator and Mission classes.
  
- **workflow/**: Manages the execution of missions and workflows.
  - `orchestrator.py`: Contains the `Orchestrator` class for managing and executing missions.
  - `__init__.py`: Initializes the workflow package.
  
- **utils/**: Contains utility functions and tests.
  - **tests/**: Contains test files for the project.
    - `test_base_agent.py`: Stub tests for the `BaseAgent` class.

- **.env.example**: Provides an example of environment variables needed for the project.
- **.gitignore**: Specifies files and directories to be ignored by version control.
- **README.md**: Documentation for the project.

## Founding Idea
The project is built upon the foundational idea of the Intent → Capability → Governance triangle, which serves as a guiding principle for the design and implementation of the agent system.

## Conclusion
This README serves as a guide to understanding the structure and purpose of the `team-agent` project. It outlines the mission, architecture, and key components necessary for developing a modular AI agent system.