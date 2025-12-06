"""
Cloud infrastructure capabilities for AWS, Azure, GCP, and OCI.
"""

from swarms.team_agent.capabilities.cloud.aws_capability import AWSCapability
from swarms.team_agent.capabilities.cloud.azure_capability import AzureCapability
from swarms.team_agent.capabilities.cloud.gcp_capability import GCPCapability
from swarms.team_agent.capabilities.cloud.oci_capability import OCICapability

__all__ = ["AWSCapability", "AzureCapability", "GCPCapability", "OCICapability"]
