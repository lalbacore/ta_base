# Installation Guide

Complete installation instructions for Team Agent.

---

## System Requirements

### Minimum Requirements

- **Operating System**: macOS, Linux, or Windows (WSL recommended)
- **Python**: 3.11 or higher
- **Memory**: 2 GB RAM minimum
- **Disk Space**: 500 MB for installation and dependencies

### Recommended

- **Python**: 3.11.5+
- **Memory**: 4 GB RAM or higher
- **Disk Space**: 2 GB for development and testing

---

## Installation Methods

### Method 1: Standard Installation (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/lalbacore/ta_base.git
cd ta_base/swarm2/team-agent

# 2. Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -m pytest utils/tests/ -v
```

### Method 2: Development Installation

For contributors and developers:

```bash
# Follow steps 1-2 from Method 1, then:

# 3. Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio black flake8 mypy

# 4. Install in editable mode (optional)
pip install -e .

# 5. Verify installation
python -m pytest utils/tests/ -v --cov=swarms/team_agent
```

### Method 3: Docker Installation (Coming Soon)

```bash
# Pull image
docker pull teamagent/team-agent:latest

# Run container
docker run -it teamagent/team-agent:latest
```

---

## Dependencies

### Core Dependencies

Team Agent requires the following Python packages:

```
cryptography==41.0.7    # PKI infrastructure
```

All dependencies are listed in `requirements.txt`.

### Optional Dependencies

For development and testing:

```
pytest==7.4.0           # Testing framework
pytest-cov==4.1.0       # Code coverage
pytest-asyncio==0.21.0  # Async testing
black==23.7.0           # Code formatting
flake8==6.1.0           # Linting
mypy==1.5.0             # Type checking
```

---

## Configuration

### Initial Setup

After installation, initialize the PKI infrastructure:

```python
from swarms.team_agent.crypto import PKIManager

# Initialize PKI (creates certificate authority)
pki = PKIManager()
pki.initialize_pki()

# Certificates stored in: ~/.team_agent/pki/
```

### Directory Structure

Team Agent creates the following directories:

```
~/.team_agent/
├── pki/                    # PKI certificates
│   ├── root/
│   ├── government/
│   ├── execution/
│   └── logging/
├── trust.db                # Trust scoring database
├── registry.db             # Capability registry database
└── secrets/                # Encrypted secrets
```

### Environment Variables (Optional)

```bash
# Set custom PKI directory
export TEAM_AGENT_PKI_DIR="~/.team_agent/pki"

# Set custom database location
export TEAM_AGENT_DB_DIR="~/.team_agent"

# Enable debug logging
export TEAM_AGENT_DEBUG=1
```

---

## Verification

### Test Installation

Run the full test suite to verify everything works:

```bash
# All tests (should pass 163 tests)
python -m pytest utils/tests/ -v

# Specific component tests
python -m pytest utils/tests/test_pki.py -v          # PKI (107 tests)
python -m pytest utils/tests/test_a2a_system.py -v   # A2A (20 tests)
python -m pytest utils/tests/test_trust.py -v        # Trust (31 tests)
```

Expected output:
```
======================== 163 passed in 2.5s ========================
```

### Test PKI Infrastructure

```python
from swarms.team_agent.crypto import PKIManager, Signer, Verifier

# Initialize
pki = PKIManager()
pki.initialize_pki()

# Get certificate chain
cert_chain = pki.get_certificate_chain("execution")

# Create signer
signer = Signer(
    private_key_pem=cert_chain['key'],
    certificate_pem=cert_chain['cert'],
    signer_id="test-agent"
)

# Sign data
data = {"test": "data"}
signed = signer.sign_dict(data)

# Verify
verifier = Verifier(chain_pem=cert_chain['chain'])
is_valid = verifier.verify_dict(signed)
print(f"Signature valid: {is_valid}")  # Should print: True
```

### Test A2A System

```bash
# Run capability registry demo
python demo_capability_registry.py

# Expected output: Registration, discovery, and matching demonstrations
```

---

## Troubleshooting

### Common Installation Issues

#### Python Version Error

**Error**: `SyntaxError` or `requires Python 3.11 or higher`

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.11+

# Use specific Python version
python3.11 -m venv venv
source venv/bin/activate
```

#### Cryptography Installation Failed

**Error**: `Failed building wheel for cryptography`

**Solution (macOS)**:
```bash
# Install development tools
xcode-select --install

# Install OpenSSL
brew install openssl

# Set environment variables
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"

# Retry installation
pip install cryptography
```

**Solution (Linux)**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

# CentOS/RHEL
sudo yum install gcc openssl-devel python3-devel

# Retry installation
pip install cryptography
```

#### Permission Denied

**Error**: `Permission denied` when creating ~/.team_agent/

**Solution**:
```bash
# Create directory manually
mkdir -p ~/.team_agent/pki

# Set permissions
chmod 700 ~/.team_agent
chmod 700 ~/.team_agent/pki
```

#### Import Errors

**Error**: `ModuleNotFoundError: No module named 'swarms'`

**Solution**:
```bash
# Ensure you're in the correct directory
cd ta_base/swarm2/team-agent

# Verify virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Platform-Specific Notes

### macOS

- **XCode Command Line Tools** required for cryptography
- Use Homebrew for OpenSSL: `brew install openssl`
- Default shell may require `source venv/bin/activate`

### Linux

- Install build tools: `sudo apt-get install build-essential`
- Some distributions require explicit Python 3.11 installation
- SELinux may require permissions adjustment

### Windows (WSL)

- **Windows Subsystem for Linux (WSL 2)** recommended
- Install Ubuntu 22.04 or newer from Microsoft Store
- Follow Linux installation instructions within WSL
- Native Windows support experimental

---

## Uninstallation

To completely remove Team Agent:

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove installation directory
rm -rf ta_base/

# 3. Remove Team Agent data (optional)
rm -rf ~/.team_agent/

# 4. Remove virtual environment (if created separately)
rm -rf venv/
```

---

## Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Build your first workflow
2. **[Examples](examples.md)** - Explore example use cases
3. **[Development Setup](../development/setup.md)** - Set up for development
4. **[Architecture Overview](../architecture/overview.md)** - Understand the system

---

## Getting Help

If you encounter installation issues:

1. Check this troubleshooting section
2. Review [Common Issues](../development/setup.md#common-issues)
3. Search [GitHub Issues](https://github.com/lalbacore/ta_base/issues)
4. Open a new issue with:
   - Operating system and version
   - Python version (`python --version`)
   - Full error message
   - Installation method used

---

**Installation complete?** Move on to the [Quick Start Guide](quick-start.md)!
