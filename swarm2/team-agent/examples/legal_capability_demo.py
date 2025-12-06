#!/usr/bin/env python3
"""
Demo script for the Legal Document Generator capability.

This shows how to use the legal capability to generate various legal documents.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.capabilities.legal import LegalDocumentGenerator
from swarms.team_agent.capabilities.registry import CapabilityRegistry
from utils.capabilities.dynamic_builder import DynamicBuilder


def demo_direct_usage():
    """Demo: Using legal capability directly."""
    print("\n" + "=" * 70)
    print("Demo 1: Direct Legal Capability Usage")
    print("=" * 70)

    cap = LegalDocumentGenerator()

    # Generate different types of legal documents
    documents = [
        ("Generate a non-disclosure agreement for a software project", "NDA"),
        ("Create a service agreement contract", "Contract"),
        ("Generate terms of service for a web app", "Terms of Service"),
        ("Create a privacy policy for mobile application", "Privacy Policy"),
        ("Generate GDPR compliance documentation", "Compliance Doc"),
    ]

    for mission, doc_type in documents:
        print(f"\n{doc_type}:")
        print(f"  Mission: {mission}")

        result = cap.execute({"mission": mission})
        artifact = result["artifacts"][0]

        print(f"  ✓ Generated: {artifact['filename']}")
        print(f"  ✓ Type: {artifact['type']}")
        print(f"  ✓ Size: {len(artifact['content'])} characters")
        print(f"  ✓ Summary: {artifact['summary'][:60]}...")


def demo_with_registry():
    """Demo: Using capability through registry."""
    print("\n" + "=" * 70)
    print("Demo 2: Legal Capability via Registry")
    print("=" * 70)

    # Create registry and register capability
    registry = CapabilityRegistry()
    cap = LegalDocumentGenerator()
    registry.register(cap)

    # Find capability by keyword
    print("\nFinding capabilities by keyword:")
    for keyword in ["legal", "contract", "privacy", "compliance"]:
        found = registry.find(keyword)
        if found:
            print(f"  ✓ '{keyword}' -> {found.metadata['name']}")

    # Find by domain
    print("\nFinding capabilities by domain:")
    legal_caps = registry.get_by_domain("legal")
    print(f"  ✓ Found {len(legal_caps)} legal domain capabilities")

    # Find by type
    print("\nFinding capabilities by type:")
    doc_caps = registry.get_by_type("document_generation")
    print(f"  ✓ Found {len(doc_caps)} document generation capabilities")


def demo_with_dynamic_builder():
    """Demo: Using capability through DynamicBuilder."""
    print("\n" + "=" * 70)
    print("Demo 3: Legal Capability via DynamicBuilder")
    print("=" * 70)

    # Create registry and builder
    registry = CapabilityRegistry()
    registry.register(LegalDocumentGenerator())
    builder = DynamicBuilder(registry=registry)

    # Test mission keyword detection
    test_missions = [
        "Generate an NDA for our partnership",
        "Create a service contract for consulting",
        "Generate privacy policy for our app",
        "Create GDPR compliance documentation",
        "Generate terms of service for SaaS platform",
    ]

    print("\nAutomatic capability selection based on mission keywords:")
    for mission in test_missions:
        selected = builder.select_capability(mission)
        if selected:
            print(f"  ✓ Mission: '{mission[:50]}...'")
            print(f"    Selected: {selected.metadata['name']}")

    # Full execution via builder
    print("\nFull execution via DynamicBuilder:")
    result = builder.run(
        mission="Generate a confidentiality agreement for software development",
        architecture=""
    )

    print(f"  ✓ Capability used: {result['capability_used']}")
    print(f"  ✓ Artifacts: {len(result.get('artifacts', []))}")
    if result.get('artifacts'):
        artifact = result['artifacts'][0]
        print(f"  ✓ File: {artifact['filename']}")
        print(f"  ✓ Content preview: {artifact['content'][:100]}...")


def demo_metadata_and_features():
    """Demo: Capability metadata and features."""
    print("\n" + "=" * 70)
    print("Demo 4: Legal Capability Metadata and Features")
    print("=" * 70)

    cap = LegalDocumentGenerator()
    metadata = cap.get_metadata()

    print("\nCapability Metadata:")
    print(f"  Name: {metadata['name']}")
    print(f"  Type: {metadata['type']}")
    print(f"  Domain: {metadata['domain']}")
    print(f"  Domains: {', '.join(metadata['domains'])}")
    print(f"  Specialty: {metadata['specialty']}")
    print(f"  Version: {metadata['version']}")
    print(f"  Formats: {', '.join(metadata['formats'])}")

    print("\nSupported Document Types:")
    doc_types = [
        ("NDA", "Non-disclosure agreements for confidentiality"),
        ("Contract", "Service agreements and business contracts"),
        ("Terms of Service", "User terms and conditions"),
        ("Privacy Policy", "GDPR/CCPA compliant privacy policies"),
        ("Compliance", "Regulatory compliance documentation"),
    ]
    for doc_type, description in doc_types:
        print(f"  ✓ {doc_type}: {description}")

    print("\nKeyword Detection Examples:")
    keywords = {
        "NDA": ["nda", "non-disclosure", "confidentiality"],
        "Contract": ["contract", "agreement", "service agreement"],
        "Terms": ["terms of service", "tos", "terms and conditions"],
        "Privacy": ["privacy policy", "privacy", "data protection"],
        "Compliance": ["compliance", "regulatory", "gdpr", "hipaa"],
    }
    for doc_type, kws in keywords.items():
        print(f"  {doc_type}: {', '.join(kws)}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("Legal Document Generator Capability - Demonstration")
    print("=" * 70)

    demo_direct_usage()
    demo_with_registry()
    demo_with_dynamic_builder()
    demo_metadata_and_features()

    print("\n" + "=" * 70)
    print("All demonstrations completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Use the legal capability in your workflows")
    print("  2. Customize generated documents for your needs")
    print("  3. Add more domain-specific capabilities")
    print("  4. Integrate with orchestrator for full workflow execution")
    print()


if __name__ == "__main__":
    main()
