# Development Setup Guide

This guide helps you set up a local development environment for Team Agent.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: For version control
- **pip**: Python package manager

---

## Quick Setup

```bash
# Clone repository
git clone https://github.com/lalbacore/ta_base.git
cd ta_base/swarm2/team-agent

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-asyncio black flake8 mypy

# Verify installation
python -m pytest utils/tests/ -v
```

---

## Project Structure

```
team-agent/
├── swarms/team_agent/         # Core framework code
│   ├── a2a/                   # Agent-to-Agent system
│   │   ├── registry.py        # Capability registry
│   │   └── protocol.py        # A2A protocol
│   ├── crypto/                # PKI infrastructure
│   │   ├── pki.py             # Certificate authority
│   │   ├── signing.py         # Digital signatures
│   │   ├── trust.py           # Trust scoring
│   │   └── secrets.py         # Secrets management
│   ├── roles/                 # Agent roles
│   │   ├── base.py            # Base role class
│   │   ├── architect.py       # Architecture agent
│   │   ├── builder.py         # Implementation agent
│   │   └── critic.py          # Review agent
│   ├── orchestrator.py        # Workflow orchestrator
│   └── orchestrator_a2a.py    # A2A-enhanced orchestrator
│
├── utils/tests/               # Test suite
│   ├── test_pki.py            # PKI tests (107 tests)
│   ├── test_a2a_system.py     # A2A tests (20 tests)
│   ├── test_trust.py          # Trust scoring tests
│   └── test_orchestrator_capabilities.py
│
├── docs/                      # Documentation
├── examples/                  # Example scripts
└── demo_*.py                  # Demonstration scripts
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Always branch from main
git checkout main
git pull origin main

# Create feature branch with descriptive name
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming Conventions:**
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions or fixes
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

### 2. Make Changes

Follow the code standards outlined below.

### 3. Run Tests

```bash
# Run all tests
python -m pytest utils/tests/ -v

# Run specific test file
python -m pytest utils/tests/test_a2a_system.py -v

# Run with coverage
python -m pytest utils/tests/ --cov=swarms/team_agent --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 4. Format and Lint

```bash
# Format code with black
black swarms/

# Check style with flake8
flake8 swarms/

# Type check with mypy
mypy swarms/
```

### 5. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

**Example:**
```
feat(registry): add reputation decay over time

Implements time-based decay for capability reputation scores to
ensure recent performance is weighted more heavily than historical
data.

- Add decay_factor parameter to CapabilityRegistry
- Update reputation calculation to apply exponential decay
- Add tests for reputation decay scenarios

Closes #123
```

---

## Code Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

#### Type Hints

All public functions and methods must have type hints:

```python
def register_capability(
    self,
    provider_id: str,
    capability_type: CapabilityType,
    name: str,
    description: str,
    version: str = "1.0.0",
    **kwargs: Any
) -> Capability:
    """Register a new capability."""
    ...
```

#### Docstrings

Use Google-style docstrings for all public classes and functions:

```python
def match_capabilities(
    self,
    requirement: CapabilityRequirement,
    limit: int = 10
) -> List[CapabilityMatch]:
    """
    Find and rank capabilities that match a requirement.

    Args:
        requirement: Capability requirement specification
        limit: Maximum number of matches to return

    Returns:
        List of CapabilityMatch objects sorted by overall_score

    Raises:
        ValueError: If requirement.capability_type is invalid

    Example:
        >>> requirement = CapabilityRequirement(
        ...     capability_type=CapabilityType.CODE_GENERATION,
        ...     min_trust_score=80.0
        ... )
        >>> matches = registry.match_capabilities(requirement, limit=5)
        >>> print(matches[0].overall_score)
        95.5
    """
    ...
```

#### Naming Conventions

- **Classes**: `PascalCase` (e.g., `CapabilityRegistry`)
- **Functions/Methods**: `snake_case` (e.g., `match_capabilities`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private**: Prefix with `_` (e.g., `_calculate_score`)

#### Code Organization

```python
# 1. Standard library imports
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

# 2. Third-party imports
import pytest
from cryptography.hazmat.primitives import hashes

# 3. Local imports
from swarms.team_agent.crypto import PKIManager
from swarms.team_agent.a2a import CapabilityRegistry
```

---

## Adding a New Capability

### 1. Create Capability Class

```python
# swarms/team_agent/capabilities/your_domain/your_capability.py

from swarms.team_agent.capabilities.base_capability import BaseCapability

class YourCapability(BaseCapability):
    """Brief description."""

    def get_metadata(self):
        return {
            "name": "your_capability",
            "type": "code_generation",  # or document_generation
            "domains": ["your", "domains"],
            "description": "What this does",
            "version": "1.0.0"
        }

    def execute(self, context):
        mission = context.get("mission", "")
        # Your logic here
        return {
            "content": "...",
            "artifacts": [...],
            "metadata": self.metadata
        }
```

### 2. Write Tests

```python
# utils/tests/test_your_capability.py

def test_metadata():
    cap = YourCapability()
    meta = cap.get_metadata()
    assert meta["name"] == "your_capability"
    assert "your" in meta["domains"]

def test_execute():
    cap = YourCapability()
    result = cap.execute({"mission": "test mission"})
    assert "content" in result
    assert len(result["artifacts"]) > 0
```

### 3. Register in Orchestrator

```python
# swarms/team_agent/orchestrator.py

from swarms.team_agent.capabilities.your_domain.your_capability import YourCapability

class Orchestrator:
    def _register_default_capabilities(self):
        # ... existing capabilities
        self.capability_registry.register(YourCapability())
```

### 4. Update Exports

```python
# utils/capabilities/__init__.py

from swarms.team_agent.capabilities.your_domain.your_capability import YourCapability
__all__ = ["HRTGuideCapability", "YourCapability"]
```

---

## Common Development Tasks

### Running Demonstrations

```bash
# Capability registry demo
python demo_capability_registry.py

# A2A protocol demo
python demo_a2a_protocol.py

# Orchestrator demo
python demo_orchestrator_a2a.py

# Trust scoring demo
python demo_trust_system.py

# PKI integration test
python full_pki_integration_test.py
```

### Working with PKI

```bash
# View trust scores
python scripts/pki_trust_cli.py list

# Check specific agent
python scripts/pki_trust_cli.py show architect-agent

# System statistics
python scripts/pki_trust_cli.py stats
```

### Database Management

```bash
# View trust database
sqlite3 ~/.team_agent/trust.db

# View registry database
sqlite3 ~/.team_agent/registry.db

# View CRL database
sqlite3 ~/.team_agent/pki/crl.db
```

---

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

o = Orchestrator()
result = o.execute("your mission")
```

### Inspect Workflow Records

```bash
# View workflow record
cat output/wf_*/wf_*_record.json | jq

# Pretty print
python -m json.tool output/wf_*/wf_*_record.json
```

### Clear Cache

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf htmlcov/
```

---

## Common Issues

### `AttributeError: 'str' object has no attribute 'get'`

**Cause**: Agent received string instead of dict.

**Fix**: Ensure `_prepare_context()` is called before agent.run().

### `ValueError: Capability must have a name in metadata`

**Cause**: Capability metadata missing `"name"` field.

**Fix**: Add `"name": "capability_name"` to `get_metadata()`.

### `KeyError: 'artifacts'`

**Cause**: Builder result missing expected structure.

**Fix**: Ensure capability `execute()` returns dict with `"artifacts"` key.

### `CertificateRevokedException`

**Cause**: Agent's certificate has been revoked.

**Fix**: Issue new certificate or reinstate if temporarily suspended.

---

## Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

o = Orchestrator()
o.execute("mission")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## Testing Checklist

Before submitting a PR:

- [ ] All tests pass: `python -m pytest utils/tests/ -v`
- [ ] New capability has unit tests
- [ ] Integration test added if needed
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Code formatted with black
- [ ] No linting errors
- [ ] Coverage maintained/improved (target: 80%+)

---

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Merge to `main`
5. Tag release: `git tag v1.0.0`
6. Push tags: `git push --tags`

---

## Related Documentation

- [Contributing Guide](../../CONTRIBUTING.md) - Contribution guidelines
- [Architecture Overview](../architecture/overview.md) - System design
- [Testing Guide](testing.md) - Comprehensive testing guide
- [API Reference](../api/README.md) - API documentation

---

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/lalbacore/ta_base/discussions)
- **Bugs**: Report via [GitHub Issues](https://github.com/lalbacore/ta_base/issues)
- **Documentation**: Check [docs/](../) folder
- **Code Examples**: See `demo_*.py` files

---

**Last Updated**: 2025-12-04
