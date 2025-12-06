"""
Tests for Legal Document Generator Capability.
"""

import pytest
from swarms.team_agent.capabilities.legal import LegalDocumentGenerator
from swarms.team_agent.capabilities.registry import CapabilityRegistry


class TestLegalDocumentGenerator:
    """Test suite for LegalDocumentGenerator capability."""

    def test_metadata(self):
        """Test that legal capability returns correct metadata."""
        cap = LegalDocumentGenerator()
        metadata = cap.get_metadata()

        assert metadata["name"] == "legal_document_generator"
        assert metadata["type"] == "document_generation"
        assert metadata["domain"] == "legal"
        assert "legal" in metadata["domains"]
        assert "contracts" in metadata["domains"]
        assert "compliance" in metadata["domains"]
        assert metadata["version"] == "1.0.0"
        assert metadata["specialty"] == "legal_documentation"
        assert "markdown" in metadata["formats"]

    def test_nda_generation(self):
        """Test NDA document generation."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Generate a non-disclosure agreement for software development project"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "nda"
        assert artifact["filename"] == "non_disclosure_agreement.md"
        assert "Non-Disclosure Agreement" in artifact["content"]
        assert "CONFIDENTIAL INFORMATION" in artifact["content"]
        assert "Disclosing Party" in artifact["content"]
        assert "Receiving Party" in artifact["content"]

    def test_contract_generation(self):
        """Test service contract generation."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Create a service agreement contract for consulting services"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "service_contract"
        assert artifact["filename"] == "service_agreement.md"
        assert "Service Agreement" in artifact["content"]
        assert "COMPENSATION" in artifact["content"]
        assert "DELIVERABLES" in artifact["content"]

    def test_terms_of_service_generation(self):
        """Test Terms of Service generation."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Generate terms of service for web application"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "terms_of_service"
        assert artifact["filename"] == "terms_of_service.md"
        assert "Terms of Service" in artifact["content"]
        assert "ACCEPTANCE OF TERMS" in artifact["content"]
        assert "USER CONDUCT" in artifact["content"]

    def test_privacy_policy_generation(self):
        """Test Privacy Policy generation."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Create a privacy policy for mobile app"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "privacy_policy"
        assert artifact["filename"] == "privacy_policy.md"
        assert "Privacy Policy" in artifact["content"]
        assert "INFORMATION WE COLLECT" in artifact["content"]
        assert "GDPR" in artifact["content"]
        assert "CCPA" in artifact["content"]

    def test_compliance_generation(self):
        """Test compliance document generation."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Generate GDPR compliance documentation"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "compliance_documentation"
        assert artifact["filename"] == "compliance_documentation.md"
        assert "Compliance Documentation" in artifact["content"]
        assert "GDPR" in artifact["content"]
        assert "COMPLIANCE OVERVIEW" in artifact["content"]

    def test_generic_legal_document(self):
        """Test generic legal document generation when type is unclear."""
        cap = LegalDocumentGenerator()
        context = {
            "mission": "Generate a legal document for business purposes"
        }
        result = cap.execute(context)

        assert "content" in result
        assert "artifacts" in result
        assert len(result["artifacts"]) == 1

        artifact = result["artifacts"][0]
        assert artifact["type"] == "markdown"
        assert artifact["name"] == "legal_document"
        assert artifact["filename"] == "legal_document.md"
        assert "Legal Document" in artifact["content"]

    def test_document_type_detection_nda(self):
        """Test that NDA keywords are properly detected."""
        cap = LegalDocumentGenerator()

        # Test various NDA keywords
        nda_missions = [
            "Create an NDA for partnership",
            "Generate non-disclosure agreement",
            "Draft confidentiality agreement"
        ]

        for mission in nda_missions:
            doc_type = cap._determine_document_type(mission.lower())
            assert doc_type == "nda", f"Failed to detect NDA for mission: {mission}"

    def test_document_type_detection_contract(self):
        """Test that contract keywords are properly detected."""
        cap = LegalDocumentGenerator()

        contract_missions = [
            "Generate a service agreement contract",
            "Create contractor agreement",
            "Draft service contract"
        ]

        for mission in contract_missions:
            doc_type = cap._determine_document_type(mission.lower())
            assert doc_type == "contract", f"Failed to detect contract for mission: {mission}"

    def test_document_type_detection_terms(self):
        """Test that terms of service keywords are properly detected."""
        cap = LegalDocumentGenerator()

        terms_missions = [
            "Generate terms of service",
            "Create TOS document",
            "Draft terms and conditions"
        ]

        for mission in terms_missions:
            doc_type = cap._determine_document_type(mission.lower())
            assert doc_type == "terms", f"Failed to detect terms for mission: {mission}"

    def test_document_type_detection_privacy(self):
        """Test that privacy policy keywords are properly detected."""
        cap = LegalDocumentGenerator()

        privacy_missions = [
            "Generate privacy policy",
            "Create data protection policy",
            "Draft privacy notice"
        ]

        for mission in privacy_missions:
            doc_type = cap._determine_document_type(mission.lower())
            assert doc_type == "privacy", f"Failed to detect privacy for mission: {mission}"

    def test_document_type_detection_compliance(self):
        """Test that compliance keywords are properly detected."""
        cap = LegalDocumentGenerator()

        compliance_missions = [
            "Generate GDPR compliance document",
            "Create regulatory compliance report",
            "Draft HIPAA compliance documentation"
        ]

        for mission in compliance_missions:
            doc_type = cap._determine_document_type(mission.lower())
            assert doc_type == "compliance", f"Failed to detect compliance for mission: {mission}"

    def test_registry_registration(self):
        """Test that legal capability can be registered in registry."""
        registry = CapabilityRegistry()
        cap = LegalDocumentGenerator()
        registry.register(cap)

        # Test finding by keyword
        found = registry.find("legal")
        assert found is not None
        assert found.metadata["name"] == "legal_document_generator"

    def test_registry_find_by_domain(self):
        """Test finding legal capability by domain."""
        registry = CapabilityRegistry()
        cap = LegalDocumentGenerator()
        registry.register(cap)

        legal_caps = registry.get_by_domain("legal")
        assert len(legal_caps) > 0
        assert any(c.metadata["name"] == "legal_document_generator" for c in legal_caps)

    def test_registry_find_by_type(self):
        """Test finding legal capability by type."""
        registry = CapabilityRegistry()
        cap = LegalDocumentGenerator()
        registry.register(cap)

        doc_caps = registry.get_by_type("document_generation")
        assert len(doc_caps) > 0
        assert any(c.metadata["name"] == "legal_document_generator" for c in doc_caps)

    def test_multiple_artifacts_structure(self):
        """Test that all artifacts have correct structure."""
        cap = LegalDocumentGenerator()
        missions = [
            "Generate NDA",
            "Create service contract",
            "Generate terms of service",
            "Create privacy policy",
            "Generate compliance document"
        ]

        for mission in missions:
            result = cap.execute({"mission": mission})
            assert "artifacts" in result
            assert len(result["artifacts"]) > 0

            for artifact in result["artifacts"]:
                assert "type" in artifact
                assert "name" in artifact
                assert "filename" in artifact
                assert "content" in artifact
                assert "summary" in artifact
                assert len(artifact["content"]) > 0
                assert mission in artifact["summary"] or mission.lower() in artifact["summary"].lower()

    def test_empty_mission(self):
        """Test handling of empty mission context."""
        cap = LegalDocumentGenerator()
        result = cap.execute({})

        assert "content" in result
        assert "artifacts" in result
        # Should still generate a document (generic)
        assert len(result["artifacts"]) == 1

    def test_metadata_consistency(self):
        """Test that capability metadata is consistent across instances."""
        cap1 = LegalDocumentGenerator()
        cap2 = LegalDocumentGenerator()

        assert cap1.get_metadata() == cap2.get_metadata()
        assert cap1.name == cap2.name
        assert cap1.domains == cap2.domains

    def test_artifact_filename_format(self):
        """Test that all generated artifacts have proper filename extensions."""
        cap = LegalDocumentGenerator()
        missions = [
            ("Generate NDA", "non_disclosure_agreement.md"),
            ("Create service contract", "service_agreement.md"),
            ("Generate terms of service", "terms_of_service.md"),
            ("Create privacy policy", "privacy_policy.md"),
            ("Generate compliance document", "compliance_documentation.md"),
            ("Generate legal document", "legal_document.md")
        ]

        for mission, expected_filename in missions:
            result = cap.execute({"mission": mission})
            artifact = result["artifacts"][0]
            assert artifact["filename"] == expected_filename

    def test_disclaimer_present(self):
        """Test that all generated documents include legal disclaimer."""
        cap = LegalDocumentGenerator()
        missions = [
            "Generate NDA",
            "Create contract",
            "Generate terms of service",
            "Create privacy policy",
            "Generate compliance document"
        ]

        for mission in missions:
            result = cap.execute({"mission": mission})
            content = result["artifacts"][0]["content"]
            assert "DISCLAIMER" in content or "disclaimer" in content.lower()
            assert "attorney" in content.lower() or "legal" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
