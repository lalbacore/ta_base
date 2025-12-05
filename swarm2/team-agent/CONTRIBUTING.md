# Contributing to Team Agent

Thank you for your interest in contributing to Team Agent! This document provides guidelines and standards for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful** - Treat everyone with respect and kindness
- **Be collaborative** - Work together to build better software
- **Be professional** - Keep discussions focused on the code and project
- **Be inclusive** - Welcome contributors from all backgrounds

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ta_base.git
cd ta_base/swarm2/team-agent
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-asyncio black flake8 mypy

# Verify installation
python -m pytest utils/tests/ -v
```

### 3. Create a Feature Branch

```bash
# Always branch from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description
```

---

## 🔄 Development Workflow

### Branch Naming

Use descriptive branch names with prefixes:

- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions or fixes
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

**Examples:**
```
feat/add-websocket-transport
fix/registry-race-condition
docs/improve-api-reference
test/add-integration-tests
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `test` - Adding/updating tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `chore` - Maintenance tasks

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

## 🎨 Code Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

#### Code Formatting

```python
# Use black for automatic formatting
black swarms/

# Check with flake8
flake8 swarms/

# Type checking with mypy
mypy swarms/
```

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

## 🧪 Testing Requirements

### Writing Tests

All new code must include tests. We aim for **80%+ code coverage**.

#### Test Structure

```python
# utils/tests/test_feature.py

import pytest
from swarms.team_agent.feature import FeatureClass


class TestFeatureClass:
    """Test suite for FeatureClass."""

    def test_basic_functionality(self):
        """Test basic feature functionality."""
        feature = FeatureClass()
        result = feature.do_something()
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test asynchronous operation."""
        feature = FeatureClass()
        result = await feature.async_operation()
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling."""
        feature = FeatureClass()
        with pytest.raises(ValueError):
            feature.invalid_operation()
```

### Running Tests

```bash
# Run all tests
python -m pytest utils/tests/ -v

# Run specific test file
python -m pytest utils/tests/test_a2a_system.py -v

# Run specific test
python -m pytest utils/tests/test_a2a_system.py::TestCapabilityRegistry::test_matching -v

# Run with coverage
python -m pytest utils/tests/ --cov=swarms/team_agent --cov-report=html

# Run async tests
python -m pytest utils/tests/ -v -k async
```

### Coverage Requirements

- **Minimum**: 70% overall coverage
- **Target**: 80%+ coverage
- **Critical paths**: 90%+ coverage (security, PKI, trust)

**Check coverage:**
```bash
python -m pytest utils/tests/test_a2a_system.py \
    --cov=swarms/team_agent/a2a \
    --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Run all tests locally:**
   ```bash
   python -m pytest utils/tests/ -v
   ```

2. **Check code coverage:**
   ```bash
   python -m pytest utils/tests/ --cov=swarms/team_agent --cov-report=term
   ```

3. **Format code:**
   ```bash
   black swarms/
   ```

4. **Check style:**
   ```bash
   flake8 swarms/
   ```

5. **Update documentation** if needed

### Creating Pull Request

1. **Push to your fork:**
   ```bash
   git push origin feat/your-feature
   ```

2. **Open PR on GitHub**:
   - Go to https://github.com/lalbacore/ta_base
   - Click "New Pull Request"
   - Select your branch

3. **Fill out PR template:**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] All tests passing
   - [ ] New tests added
   - [ ] Coverage maintained/improved

   ## Checklist
   - [ ] Code follows project style
   - [ ] Self-reviewed code
   - [ ] Commented complex code
   - [ ] Updated documentation
   - [ ] No new warnings
   ```

### PR Review Process

1. **Automated checks** must pass:
   - All tests passing
   - Code coverage ≥ 80%
   - No linting errors

2. **Code review** by maintainers:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations

3. **Approval and merge**:
   - At least 1 approval required
   - All comments resolved
   - CI/CD passing

---

## 📖 Documentation

### Documentation Structure

```
docs/
├── getting-started/     # Tutorials and quick starts
├── architecture/        # System design
├── features/            # Feature guides
├── development/         # Developer guides
├── api/                 # API reference
└── testing/             # Test documentation
```

### Adding Documentation

1. **Update existing docs** if changing functionality
2. **Add new docs** for new features
3. **Include examples** in all documentation
4. **Update DOCUMENTATION_INDEX.md** if adding new files

### Documentation Standards

- Use Markdown for all documentation
- Include code examples with output
- Add diagrams for complex concepts
- Link to related documentation
- Keep language clear and concise

---

## 🎯 Areas for Contribution

### High Priority

- **Network Transport**: Add HTTP/WebSocket/gRPC support for A2A
- **Performance**: Optimize capability matching for large registries
- **Monitoring**: Add metrics and observability
- **Documentation**: Improve API reference and examples

### Good First Issues

Look for issues labeled:
- `good-first-issue` - Beginner-friendly tasks
- `documentation` - Documentation improvements
- `testing` - Test additions

### Feature Ideas

- Advanced reputation algorithms (PageRank, EigenTrust)
- ML-based capability recommendation
- Distributed registry with consensus
- Smart contract integration
- MCP (Model Context Protocol) bridge

---

## 💬 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/lalbacore/ta_base/discussions)
- **Bugs**: Report via [GitHub Issues](https://github.com/lalbacore/ta_base/issues)
- **Documentation**: Check [docs/](docs/) folder
- **Code Examples**: See `demo_*.py` files

---

## 🙏 Thank You!

Every contribution makes Team Agent better. Whether it's:
- Fixing a typo
- Adding a test
- Implementing a feature
- Improving documentation

**Thank you for being part of the Team Agent community!**

---

<div align="center">

[Documentation](docs/DOCUMENTATION_INDEX.md) • [README](README.md) • [Code of Conduct](#code-of-conduct)

</div>
