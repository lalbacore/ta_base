"""
Azure Cloud Specialist Agent - Domain expert for Azure infrastructure.

Uses AzureCapability to generate Infrastructure-as-Code (Terraform, ARM)
and Azure SDK scripts for provisioning Azure resources.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.cloud import AzureCapability


class AzureSpecialist(BaseSpecialist):
    """
    Specialist agent for Azure cloud infrastructure.

    Primary Capability: AzureCapability
    Domains: azure, cloud, infrastructure, terraform, microsoft
    Keywords: azure, vm, app service, storage account, sql database, terraform, arm

    Use Cases:
    - Provision Azure VMs and scale sets
    - Create Storage Accounts and Blob containers
    - Deploy App Services and Functions
    - Set up SQL Databases and Cosmos DB
    - Configure VNets, NSGs, and Application Gateways
    - Generate Terraform or ARM templates
    - Create Azure SDK scripts for automation
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize Azure Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "Azure Cloud Specialist"
        self.description = (
            "Specialist agent for Azure cloud infrastructure provisioning. "
            "Generates Terraform, ARM templates, and Azure SDK scripts "
            "for VMs, App Services, Storage, SQL Database, VNet, and other Azure services."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = AzureCapability()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Azure infrastructure provisioning.

        Args:
            context: dict with:
                - mission: str - Description of Azure infrastructure to create
                - architecture: str - Optional architecture from Architect

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "azure_cloud_infrastructure"
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
            "capability_used": "azure_cloud_infrastructure",
            "artifacts": result.get("artifacts", []),
            "content": result.get("content", ""),
            "metadata": {
                **result.get("metadata", {}),
                "specialist": self.name,
                "specialist_version": self.version,
                "cloud_provider": "azure"
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
            "azure", "microsoft azure",
            # Compute
            "azure vm", "virtual machine", "azure instance",
            "app service", "web app",
            "azure functions", "function app",
            "aks", "azure kubernetes",
            "container instances",
            # Storage
            "storage account", "blob storage", "azure storage",
            "azure files",
            "managed disk",
            # Database
            "sql database", "azure sql",
            "cosmos db", "cosmosdb",
            "postgresql flexible server", "mysql flexible server",
            # Networking
            "vnet", "virtual network",
            "application gateway",
            "front door", "azure cdn",
            "network security group", "nsg",
            # IaC Tools
            "terraform azure", "arm template", "bicep",
            # General Azure terms
            "azure infrastructure", "provision azure", "deploy azure",
            "resource group"
        ]
