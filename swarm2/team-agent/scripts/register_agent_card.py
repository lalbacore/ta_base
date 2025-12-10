#!/usr/bin/env python3
"""
Register Agent Card Script

Parses a JSON Agent Card, validates it against the schema, and registers it
into the local Registry database.

Usage:
    python scripts/register_agent_card.py path/to/agent_card.json
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from swarms.team_agent.a2a.registry import CapabilityRegistry, CapabilityType, TrustDomain

def validate_card_manual(data):
    required = ["agent_id", "agent_name", "agent_type", "version", "trust_domain", "module_path", "class_name"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

def register_card(card_path: str):
    card_path = Path(card_path)
    if not card_path.exists():
        print(f"Error: File not found at {card_path}")
        sys.exit(1)

    try:
        with open(card_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}")
        sys.exit(1)

    # Validate Schema Manually
    print("Validating schema...")
    try:
        validate_card_manual(data)
    except ValueError as e:
        print(f"Error: Validation failed: {e}")
        sys.exit(1)

    print(f"Registering Agent: {data['agent_name']} ({data['agent_id']})...")

    # Initialize Registry
    registry = CapabilityRegistry()
    
    # Register Provider (Agent)
    try:
        trust_domain = TrustDomain[data['trust_domain']]
    except KeyError:
        print(f"Error: Invalid Trust Domain {data['trust_domain']}")
        sys.exit(1)

    provider = registry.register_provider(
        provider_id=data['agent_id'],
        provider_type="agent",
        trust_domain=trust_domain,
        metadata={
            "agent_name": data['agent_name'],
            "description": data['description'],
            "module_path": data['module_path'],
            "class_name": data['class_name']
        }
    )
    print(f"  - Provider registered: {provider.provider_id}")

    # Register Capabilities
    capabilities = data.get("capabilities", [])
    if capabilities:
        print(f"Registering {len(capabilities)} capabilities...")
        for cap_data in capabilities:
            try:
                # Map string type to Enum
                cap_type_str = cap_data['capability_type'].upper()
                try:
                    cap_type = CapabilityType[cap_type_str]
                except KeyError:
                    # Fallback or strict error? Let's default to CUSTOM if unknown, or error.
                    # For now, let's try to find a match or fail. 
                    # Actually, the schema allows any string, but our code needs an Enum.
                    # We'll try to match, defaulting to CUSTOM if it fails but printing a warning.
                    print(f"Warning: Unknown capability type '{cap_type_str}', defaulting to CUSTOM.")
                    cap_type = CapabilityType.CUSTOM

                registry.register_capability(
                    provider_id=data['agent_id'],
                    capability_type=cap_type,
                    name=cap_data['name'],
                    description=cap_data['description'],
                    version=cap_data.get('version', '1.0.0'),
                    input_schema=cap_data.get('input_schema'),
                    output_schema=cap_data.get('output_schema'),
                    price=cap_data.get('price_per_invocation', 0.0),
                    tags=cap_data.get('keywords', []),
                    categories=cap_data.get('domains', []),
                    metadata={
                        "original_id": cap_data['capability_id']
                    },
                    capability_id=cap_data.get('capability_id')
                )
                print(f"  - Capability registered: {cap_data['name']}")
            except Exception as e:
                print(f"  - Failed to register capability {cap_data.get('name')}: {e}")

    print("Success! Agent card registered.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register an Agent Card")
    parser.add_argument("card_file", help="Path to the JSON agent card file")
    args = parser.parse_args()
    
    register_card(args.card_file)
