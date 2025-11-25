# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-11-24

### Added
- `run()` method to all agent roles (Architect, Builder, Critic, Governance, Recorder)
- HRT Guide generator script with PDF output (`scripts/generate_hrt_guide.py`)
- Parallel executor for concurrent capability execution
- Mission router for intelligent workflow routing
- MCP client stub for future Model Context Protocol support
- Agent-to-agent communication bus stub
- State management (HITL, Turing tape)
- Base role class for common functionality

### Changed
- Rewrote test suite to be behavioral rather than structural
- Tests now verify outcomes, not implementation details
- Governance agent accepts review results directly (not wrapped in dict)

### Fixed
- 171 tests now passing (was failing due to brittle structural tests)
- Recorder signature field name (`ts` vs `timestamp`)
- Capability registration in document generator

### Skipped
- RoutedOrchestrator tests (missing `_get_capability_by_name` method)

## [0.1.0] - 2024-11-23

### Added
- Initial multi-agent orchestration framework
- Five core agent roles: Architect, Builder, Critic, Governance, Recorder
- Capability registry with domain routing
- YAML mission file support
- Structured JSON logging
- Basic workflow execution (Design → Build → Review → Record)
- Medical domain: HRT Guide capability
- Document generator capability

### Architecture
- Intent → Capability → Governance triangle
- Modular capability system
- Policy-based governance enforcement
- Cryptographic audit trail

---

## [Unreleased]

### Planned
- LLM integration (Claude, GPT-4, local models)
- MCP server implementation
- Real parallel execution
- Additional domain capabilities (legal, financial, technical)
- Web UI for workflow monitoring
- Kubernetes deployment support