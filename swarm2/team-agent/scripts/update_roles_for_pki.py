#!/usr/bin/env python3
"""
Script to update all role files to support PKI certificates.

This script adds:
1. workflow_id parameter to __init__
2. cert_chain parameter to __init__
3. Signer initialization
4. Output signing in run/act methods
"""

import re
from pathlib import Path

ROLES_DIR = Path("swarms/team_agent/roles")

# Crypto import to add
CRYPTO_IMPORT = """
# Import crypto modules (optional)
try:
    from swarms.team_agent.crypto import Signer
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Signer = None
"""

# Signer init code
SIGNER_INIT = """
        # Initialize signer if cert_chain is provided
        self.signer = None
        if cert_chain and CRYPTO_AVAILABLE:
            try:
                self.signer = Signer(
                    private_key_pem=cert_chain['key'],
                    certificate_pem=cert_chain['cert'],
                    signer_id="{role_name}"
                )
            except Exception:
                pass
"""

def update_role_file(filepath: Path, role_name: str):
    """Update a single role file."""
    print(f"Updating {filepath.name}...")

    content = filepath.read_text()

    # Check if already updated
    if "cert_chain" in content:
        print(f"  {filepath.name} already has cert_chain support, skipping")
        return

    # Add crypto import after other imports
    if "from ..tools import" in content and CRYPTO_IMPORT.strip() not in content:
        content = content.replace(
            "from ..tools import",
            CRYPTO_IMPORT + "\nfrom ..tools import"
        )

    # Update __init__ signature
    # Find the __init__ method
    init_pattern = r"def __init__\(\s*self,\s*([^)]+)\):"
    match = re.search(init_pattern, content)

    if match:
        current_params = match.group(1)
        # Add workflow_id and cert_chain if not present
        if "workflow_id" not in current_params:
            new_params = f"workflow_id: str = \"unknown\",\n        {current_params},\n        cert_chain: Optional[Dict[str, bytes]] = None"
            content = re.sub(init_pattern, f"def __init__(\\n        self,\\n        {new_params}):", content)
        elif "cert_chain" not in current_params:
            new_params = f"{current_params},\n        cert_chain: Optional[Dict[str, bytes]] = None"
            content = re.sub(init_pattern, f"def __init__(self, {new_params}):", content)

    # Add workflow_id assignment after __init__
    if "self.workflow_id = workflow_id" not in content:
        # Find first self.name = assignment and add workflow_id before it
        content = re.sub(
            r"(    def __init__[^\n]*\n(?:[^\n]*\n)*?)(        self\.name = )",
            r"\1        self.workflow_id = workflow_id\n\2",
            content
        )

    # Add signer initialization at end of __init__
    if "self.signer" not in content:
        # Find the last line of __init__ (before next def)
        signer_code = SIGNER_INIT.format(role_name=role_name.lower())
        # Add before the closing of __init__
        content = re.sub(
            r"(        self\._register_default_tools\(\))",
            r"\1\n" + signer_code,
            content
        )

    filepath.write_text(content)
    print(f"  ✓ Updated {filepath.name}")

# Update each role
roles_to_update = [
    ("builder.py", "Builder"),
    ("critic.py", "Critic"),
    ("recorder.py", "Recorder"),
]

for filename, role_name in roles_to_update:
    filepath = ROLES_DIR / filename
    if filepath.exists():
        try:
            update_role_file(filepath, role_name)
        except Exception as e:
            print(f"  ✗ Error updating {filename}: {e}")

print("\nDone! Please review the changes manually.")
