"""
OCI Cloud Specialist Agent - Domain expert for Oracle Cloud Infrastructure.

Uses OCICapability to generate Infrastructure-as-Code (Terraform, OCI CLI)
and OCI SDK scripts for provisioning Oracle Cloud resources.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.cloud import OCICapability


class OCISpecialist(BaseSpecialist):
    """
    Specialist agent for Oracle Cloud Infrastructure (OCI).

    Primary Capability: OCICapability
    Domains: oci, oracle-cloud, cloud, infrastructure, terraform
    Keywords: oci, compute, object storage, autonomous database, vcn, oke

    Use Cases:
    - Provision Compute instances and instance pools
    - Create Object Storage buckets
    - Deploy Autonomous Databases (ATP, ADW)
    - Set up VCNs, subnets, and security lists
    - Configure Load Balancers and Network Security Groups
    - Deploy Container Engine for Kubernetes (OKE)
    - Generate Terraform or OCI CLI scripts
    - Create OCI Python SDK scripts for automation
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize OCI Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "OCI Cloud Specialist"
        self.description = (
            "Specialist agent for Oracle Cloud Infrastructure (OCI) provisioning. "
            "Generates Terraform, OCI CLI scripts, and OCI Python SDK code "
            "for Compute, Object Storage, Autonomous Database, VCN, Load Balancers, and other OCI services."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = OCICapability()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute OCI infrastructure provisioning.

        Args:
            context: dict with:
                - mission: str - Description of OCI infrastructure to create
                - architecture: str - Optional architecture from Architect

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "oci_cloud_infrastructure"
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
            "capability_used": "oci_cloud_infrastructure",
            "artifacts": result.get("artifacts", []),
            "content": result.get("content", ""),
            "metadata": {
                **result.get("metadata", {}),
                "specialist": self.name,
                "specialist_version": self.version,
                "cloud_provider": "oci"
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
            "oci", "oracle cloud", "oracle cloud infrastructure",
            # Compute
            "oci compute", "oci instance", "oci vm",
            "instance pool", "autoscaling",
            # Storage
            "object storage", "oci bucket",
            "block volume", "boot volume",
            "file storage", "fss",
            # Database
            "autonomous database", "adb", "atp", "adw",
            "oci database", "database system",
            "mysql database service",
            # Networking
            "vcn", "virtual cloud network",
            "subnet", "security list",
            "network security group", "nsg",
            "load balancer", "oci lb",
            "fastconnect", "vpn",
            # Container & Kubernetes
            "oke", "oracle kubernetes engine",
            "container engine", "kubernetes oci",
            "container instances", "oci containers",
            # Functions & Serverless
            "oci functions", "serverless oci",
            # Monitoring & Management
            "oci monitoring", "logging analytics",
            "resource manager", "orm",
            # IaC Tools
            "terraform oci", "oci cli", "oci sdk",
            # General OCI terms
            "oci infrastructure", "provision oci", "deploy oci",
            "compartment", "tenancy"
        ]
