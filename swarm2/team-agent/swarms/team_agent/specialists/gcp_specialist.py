"""
GCP Cloud Specialist Agent - Domain expert for GCP infrastructure.

Uses GCPCapability to generate Infrastructure-as-Code (Terraform, Deployment Manager)
and Google Cloud SDK scripts for provisioning GCP resources.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.cloud import GCPCapability


class GCPSpecialist(BaseSpecialist):
    """
    Specialist agent for GCP cloud infrastructure.

    Primary Capability: GCPCapability
    Domains: gcp, google-cloud, cloud, infrastructure, terraform
    Keywords: gcp, compute engine, cloud storage, cloud sql, cloud run, terraform

    Use Cases:
    - Provision Compute Engine instances and instance groups
    - Create Cloud Storage buckets
    - Deploy Cloud Run services and Cloud Functions
    - Set up Cloud SQL databases
    - Configure VPC networks and firewall rules
    - Generate Terraform or Deployment Manager templates
    - Create Google Cloud SDK scripts for automation
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize GCP Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "GCP Cloud Specialist"
        self.description = (
            "Specialist agent for GCP cloud infrastructure provisioning. "
            "Generates Terraform, Deployment Manager templates, and Google Cloud SDK scripts "
            "for Compute Engine, Cloud Storage, Cloud SQL, Cloud Run, VPC, and other GCP services."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = GCPCapability()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute GCP infrastructure provisioning.

        Args:
            context: dict with:
                - mission: str - Description of GCP infrastructure to create
                - architecture: str - Optional architecture from Architect

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "gcp_cloud_infrastructure"
                - artifacts: list - Generated IaC/SDK scripts
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")

        # Execute primary capability
        result = self.primary_capability.execute({
            "mission": mission,
            "architecture": architecture
        })

        # Return standardized result
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "capability_used": "gcp_cloud_infrastructure",
            "artifacts": result.get("artifacts", []),
            "content": result.get("content", ""),
            "metadata": {
                **result.get("metadata", {}),
                "specialist": self.name,
                "specialist_version": self.version,
                "cloud_provider": "gcp"
            }
        }

    @classmethod
    def get_keywords(cls) -> list:
        """
        Get keywords for specialist discovery.

        Returns:
            List of keywords that trigger this specialist
        """
        return [
            # Provider
            "gcp", "google cloud", "google cloud platform",
            # Compute
            "compute engine", "gce", "gcp vm", "gcp instance",
            "cloud run", "cloud functions",
            "gke", "google kubernetes engine",
            "app engine",
            # Storage
            "cloud storage", "gcs", "gcp bucket",
            "persistent disk",
            "filestore",
            # Database
            "cloud sql", "gcp database",
            "firestore", "datastore",
            "bigtable", "spanner",
            "memorystore", "redis gcp",
            # Networking
            "vpc network", "gcp vpc",
            "cloud load balancing",
            "cloud cdn", "cloud armor",
            "cloud dns",
            # IaC Tools
            "terraform gcp", "deployment manager", "gcloud",
            # General GCP terms
            "gcp infrastructure", "provision gcp", "deploy gcp",
            "gcp project"
        ]
