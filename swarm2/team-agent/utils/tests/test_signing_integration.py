"""
Comprehensive tests for PKI signing integration across all roles and artifacts.
"""
import pytest
import tempfile
from pathlib import Path

from swarms.team_agent.crypto import (
    PKIManager,
    TrustDomain,
    Signer,
    Verifier,
    ManifestGenerator,
    ArtifactSigner,
    create_artifact_manifest,
)
from swarms.team_agent.roles import Builder, Recorder


class TestBuilderSigning:
    """Test Builder role signing implementation."""

    @pytest.fixture
    def pki_setup(self):
        """Setup PKI infrastructure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pki = PKIManager(base_dir=Path(tmpdir))
            pki.initialize_pki()

            # Get certificate chain for execution domain
            cert_chain = pki.get_certificate_chain(TrustDomain.EXECUTION)

            yield {
                "pki": pki,
                "cert_chain": cert_chain
            }

    def test_builder_signs_act_output(self, pki_setup):
        """Test that Builder signs outputs from act() method."""
        builder = Builder(
            workflow_id="test_workflow",
            cert_chain=pki_setup["cert_chain"]
        )

        # Create a valid design
        design = {
            "status": "designed",
            "design_id": "design_001",
            "components": [
                {
                    "name": "Calculator",
                    "responsibilities": ["add", "subtract", "multiply", "divide"]
                }
            ]
        }

        result = builder.act(design)

        # Verify result is signed
        assert result["status"] == "built"
        assert "_signature" in result
        assert "signer" in result["_signature"]
        assert result["_signature"]["signer"] == "builder"
        assert "timestamp" in result["_signature"]

    def test_builder_signs_run_fallback(self, pki_setup):
        """Test that Builder signs outputs from run() fallback."""
        builder = Builder(
            workflow_id="test_workflow",
            cert_chain=pki_setup["cert_chain"]
        )

        context = {"mission": "Build a calculator"}

        result = builder.run(context)

        # Verify result is signed
        assert result["status"] == "built"
        assert "_signature" in result
        assert "signer" in result["_signature"]
        assert result["_signature"]["signer"] == "builder"

    def test_builder_without_cert_chain(self):
        """Test that Builder works without cert_chain (no signing)."""
        builder = Builder(workflow_id="test_workflow")

        design = {
            "status": "designed",
            "design_id": "design_001",
            "components": [{"name": "Module"}]
        }

        result = builder.act(design)

        # Should work but without signature
        assert result["status"] == "built"
        assert "_signature" not in result


class TestManifestGenerator:
    """Test ManifestGenerator functionality."""

    @pytest.fixture
    def pki_setup(self):
        """Setup PKI for signing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pki = PKIManager(base_dir=Path(tmpdir))
            pki.initialize_pki()

            cert_chain = pki.get_certificate_chain(TrustDomain.EXECUTION)

            signer = Signer(
                private_key_pem=cert_chain["key"],
                certificate_pem=cert_chain["cert"],
                signer_id="test_signer"
            )

            yield {"pki": pki, "signer": signer}

    def test_generate_manifest_basic(self):
        """Test basic manifest generation."""
        generator = ManifestGenerator()

        role_outputs = {
            "architect": {"status": "designed", "design_id": "001"},
            "builder": {"status": "built", "build_id": "002"},
        }

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Build a system",
            role_outputs=role_outputs
        )

        assert manifest["workflow_id"] == "wf_001"
        assert manifest["mission"] == "Build a system"
        assert "architect" in manifest["roles"]
        assert "builder" in manifest["roles"]
        assert "manifest_checksum" in manifest

    def test_generate_manifest_with_signatures(self, pki_setup):
        """Test manifest generation with signed role outputs."""
        generator = ManifestGenerator()
        signer = pki_setup["signer"]

        # Create signed outputs
        architect_output = signer.sign_dict({"status": "designed"})
        builder_output = signer.sign_dict({"status": "built"})

        role_outputs = {
            "architect": architect_output,
            "builder": builder_output,
        }

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Test mission",
            role_outputs=role_outputs
        )

        # Verify signatures were captured
        assert "signatures" in manifest
        assert "architect" in manifest["signatures"]
        assert "builder" in manifest["signatures"]
        assert manifest["verification"]["total_signatures"] == 2
        assert manifest["verification"]["valid_signatures"] == 2

    def test_generate_manifest_with_artifacts(self):
        """Test manifest generation with artifacts."""
        generator = ManifestGenerator()

        role_outputs = {"builder": {"status": "built"}}

        artifacts = [
            {"type": "implementation", "name": "module.py", "status": "built"},
            {"type": "test", "name": "test_module.py", "status": "built"},
        ]

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Test",
            role_outputs=role_outputs,
            artifacts=artifacts
        )

        assert len(manifest["artifacts"]) == 2
        assert manifest["artifact_count"] == 2

    def test_verify_manifest(self):
        """Test manifest verification."""
        generator = ManifestGenerator()

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Test",
            role_outputs={"builder": {"status": "built"}}
        )

        results = generator.verify_manifest(manifest)

        assert results["valid"] is True
        assert len(results["errors"]) == 0

    def test_export_manifest_json(self):
        """Test JSON export format."""
        generator = ManifestGenerator()

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Test",
            role_outputs={"builder": {"status": "built"}}
        )

        json_output = generator.export_manifest(manifest, format="json")

        assert isinstance(json_output, str)
        assert "wf_001" in json_output
        assert "Test" in json_output

    def test_export_manifest_text(self):
        """Test text export format."""
        generator = ManifestGenerator()

        manifest = generator.generate_manifest(
            workflow_id="wf_001",
            mission="Test mission",
            role_outputs={"builder": {"status": "built"}}
        )

        text_output = generator.export_manifest(manifest, format="text")

        assert "WORKFLOW MANIFEST" in text_output
        assert "wf_001" in text_output
        assert "Test mission" in text_output
        assert "ROLES:" in text_output
        assert "CHECKSUMS:" in text_output


class TestArtifactSigner:
    """Test ArtifactSigner functionality."""

    @pytest.fixture
    def pki_setup(self):
        """Setup PKI for signing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pki = PKIManager(base_dir=Path(tmpdir))
            pki.initialize_pki()

            cert_chain = pki.get_certificate_chain(TrustDomain.EXECUTION)

            signer = Signer(
                private_key_pem=cert_chain["key"],
                certificate_pem=cert_chain["cert"],
                signer_id="test_signer"
            )

            yield {"pki": pki, "signer": signer, "tmpdir": tmpdir}

    def test_sign_file(self, pki_setup):
        """Test file signing."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        # Create a test file
        test_file = Path(pki_setup["tmpdir"]) / "test.txt"
        test_file.write_text("Hello, World!")

        signed = artifact_signer.sign_file(test_file)

        assert signed["type"] == "file"
        assert signed["name"] == "test.txt"
        assert signed["size"] == 13
        assert "checksum" in signed
        assert "_signature" in signed

    def test_sign_log_entry(self, pki_setup):
        """Test log entry signing."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        log_data = {
            "level": "INFO",
            "message": "Workflow completed",
            "workflow_id": "wf_001"
        }

        signed = artifact_signer.sign_log_entry(log_data, log_type="workflow")

        assert signed["type"] == "log"
        assert signed["log_type"] == "workflow"
        assert signed["data"] == log_data
        assert "checksum" in signed
        assert "_signature" in signed

    def test_sign_policy(self, pki_setup):
        """Test policy signing."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        policy_data = {
            "allowed_operations": ["read", "write"],
            "restrictions": []
        }

        signed = artifact_signer.sign_policy(
            policy_data,
            policy_name="DataAccess",
            version="1.0"
        )

        assert signed["type"] == "policy"
        assert signed["name"] == "DataAccess"
        assert signed["version"] == "1.0"
        assert signed["policy"] == policy_data
        assert "checksum" in signed
        assert "_signature" in signed

    def test_sign_generic_artifact(self, pki_setup):
        """Test generic artifact signing."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        artifact_data = {"key": "value", "data": [1, 2, 3]}

        signed = artifact_signer.sign_artifact(
            artifact_data,
            artifact_type="custom",
            artifact_name="test_artifact"
        )

        assert signed["type"] == "custom"
        assert signed["name"] == "test_artifact"
        assert "checksum" in signed
        assert "_signature" in signed
        assert signed["data"] == artifact_data

    def test_batch_sign_artifacts(self, pki_setup):
        """Test batch artifact signing."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        artifacts = [
            {"data": {"id": 1}, "type": "record", "name": "record_1"},
            {"data": {"id": 2}, "type": "record", "name": "record_2"},
            {"data": {"id": 3}, "type": "record", "name": "record_3"},
        ]

        signed_artifacts = artifact_signer.batch_sign_artifacts(artifacts)

        assert len(signed_artifacts) == 3
        for signed in signed_artifacts:
            assert "checksum" in signed
            assert "_signature" in signed

    def test_verify_artifact(self, pki_setup):
        """Test artifact verification."""
        artifact_signer = ArtifactSigner(signer=pki_setup["signer"])

        signed = artifact_signer.sign_artifact(
            {"test": "data"},
            artifact_type="test",
            artifact_name="test"
        )

        results = artifact_signer.verify_artifact(signed)

        assert results["valid"] is True
        assert len(results["errors"]) == 0

    def test_create_artifact_manifest(self, pki_setup):
        """Test creating artifact manifest."""
        signer = pki_setup["signer"]
        artifact_signer = ArtifactSigner(signer=signer)

        # Create some signed artifacts
        artifacts = artifact_signer.batch_sign_artifacts([
            {"data": "artifact1", "type": "code", "name": "module.py"},
            {"data": "artifact2", "type": "test", "name": "test.py"},
        ])

        manifest = create_artifact_manifest(
            artifacts=artifacts,
            workflow_id="wf_001",
            signer=signer
        )

        assert manifest["type"] == "artifact_manifest"
        assert manifest["workflow_id"] == "wf_001"
        assert manifest["artifact_count"] == 2
        assert "_signature" in manifest
        assert "manifest_checksum" in manifest


class TestRecorderManifestGeneration:
    """Test Recorder's manifest generation."""

    @pytest.fixture
    def pki_setup(self):
        """Setup PKI for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pki = PKIManager(base_dir=Path(tmpdir))
            pki.initialize_pki()

            # Create certificates for all roles
            cert_chain = pki.get_certificate_chain(TrustDomain.EXECUTION)

            yield {
                "pki": pki,
                "cert_chain": cert_chain
            }

    def test_recorder_generates_manifest(self, pki_setup):
        """Test that Recorder generates manifests."""
        recorder = Recorder(
            workflow_id="wf_test",
            cert_chain=pki_setup["cert_chain"]
        )

        payload = {
            "request": {"mission": "Test mission"},
            "design": {"status": "designed", "design_id": "d001"},
            "build": {
                "status": "built",
                "build_id": "b001",
                "artifacts": [
                    {"type": "implementation", "component": "Module", "status": "built"}
                ]
            },
            "review": {"status": "approved", "score": 0.9},
            "governance": {"status": "approved", "allowed": True, "composite_score": 0.85},
        }

        result = recorder.act(payload)

        # Verify manifest was generated
        assert "manifest" in result
        assert "manifest_text" in result

        manifest = result["manifest"]
        assert manifest["workflow_id"] == "wf_test"
        assert manifest["mission"] == "Test mission"
        assert "architect" in manifest["roles"]
        assert "builder" in manifest["roles"]
        assert "critic" in manifest["roles"]
        assert "governance" in manifest["roles"]
        assert len(manifest["artifacts"]) == 1

    def test_recorder_manifest_includes_checksums(self, pki_setup):
        """Test that manifest includes checksums for all role outputs."""
        recorder = Recorder(
            workflow_id="wf_test",
            cert_chain=pki_setup["cert_chain"]
        )

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"},
            "review": {"status": "approved"},
            "governance": {"status": "approved"},
        }

        result = recorder.act(payload)

        manifest = result["manifest"]
        assert "checksums" in manifest
        assert "architect" in manifest["checksums"]
        assert "builder" in manifest["checksums"]

    def test_recorder_signed_output_includes_manifest(self, pki_setup):
        """Test that signed recorder output includes the manifest."""
        recorder = Recorder(
            workflow_id="wf_test",
            cert_chain=pki_setup["cert_chain"]
        )

        payload = {
            "design": {"status": "designed"},
            "build": {"status": "built"},
            "review": {"status": "approved"},
            "governance": {"status": "approved"},
        }

        result = recorder.act(payload)

        # Result should be signed
        assert "_signature" in result
        assert "signer" in result["_signature"]

        # And should contain manifest
        assert "manifest" in result
        assert "manifest_text" in result


class TestEndToEndSigningWorkflow:
    """Test complete signing workflow across all roles."""

    @pytest.fixture
    def pki_setup(self):
        """Setup PKI for all roles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pki = PKIManager(base_dir=Path(tmpdir))
            pki.initialize_pki()

            # Create certificates for builder and recorder
            # Get certificate chain for execution domain (shared by all execution agents)
            cert_chain = pki.get_certificate_chain(TrustDomain.EXECUTION)

            yield {
                "pki": pki,
                "builder_cert": cert_chain,
                "recorder_cert": cert_chain
            }

    def test_complete_workflow_with_signing(self, pki_setup):
        """Test complete workflow with all roles signing."""
        # Create builder
        builder = Builder(
            workflow_id="wf_e2e",
            cert_chain=pki_setup["builder_cert"]
        )

        # Execute build
        design = {
            "status": "designed",
            "design_id": "d_e2e",
            "components": [{"name": "TestModule", "responsibilities": ["test"]}]
        }

        build_result = builder.act(design)

        # Verify build is signed
        assert "_signature" in build_result
        assert build_result["_signature"]["signer"] == "builder"

        # Create recorder
        recorder = Recorder(
            workflow_id="wf_e2e",
            cert_chain=pki_setup["recorder_cert"]
        )

        # Record workflow
        payload = {
            "request": {"mission": "E2E test"},
            "design": design,
            "build": build_result,
            "review": {"status": "approved", "score": 0.9},
            "governance": {"status": "approved", "allowed": True, "composite_score": 0.85},
        }

        record_result = recorder.act(payload)

        # Verify recorder output is signed
        assert "_signature" in record_result
        assert record_result["_signature"]["signer"] == "recorder"

        # Verify manifest was generated
        assert "manifest" in record_result
        manifest = record_result["manifest"]

        # Verify manifest captured builder's signature
        assert "signatures" in manifest
        assert "builder" in manifest["signatures"]
        assert manifest["signatures"]["builder"]["signer_id"] == "builder"

        # Verify manifest has checksums
        assert "checksums" in manifest
        assert "builder" in manifest["checksums"]

        # Verify manifest itself has checksum
        assert "manifest_checksum" in manifest
