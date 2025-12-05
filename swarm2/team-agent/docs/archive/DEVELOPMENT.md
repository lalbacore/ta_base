# Development Guide

## Setup

```bash
# Clone repository
git clone <repo-url>
cd team-agent

# Install dependencies
pip install -r requirements.txt

# Run tests
python examples/run_capability_tests.py
```

## Project Standards

### Code Style
- PEP 8 compliance
- Type hints on all public methods
- Docstrings for classes and public methods

### Commit Messages
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Example:
```
feat(capabilities): add medical HRT guide capability

- Implements BaseCapability for HRT clinical guides
- Registers in default capability set
- Includes comprehensive metadata

Closes #42
```

### Branch Strategy
- `main`: Stable release
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes

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

## Testing Checklist

Before submitting a PR:

- [ ] All tests pass: `python examples/run_capability_tests.py`
- [ ] New capability has unit tests
- [ ] Integration test added to `test_orchestrator_capabilities.py`
- [ ] Documentation updated (README, ARCHITECTURE if needed)
- [ ] Type hints added
- [ ] Docstrings complete

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
cat output/wf_*/wf_*_record.json | jq
```

### Clear Cache

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
```

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

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Merge to `main`
5. Tag release: `git tag v1.0.0`
6. Push tags: `git push --tags`

## Questions?

Open an issue or discussion on GitHub.