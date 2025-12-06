"""
Specialist Agents - Domain-specific agents that use capabilities.

Specialist agents are registered in agent_cards with type="specialist".
They use one or more capabilities from the capability registry to perform
domain-specific tasks.

Available Specialists:
- LegalSpecialist: Legal document generation and contract analysis
- AWSSpecialist: AWS cloud infrastructure provisioning (Terraform, CloudFormation, boto3)
- AzureSpecialist: Azure cloud infrastructure provisioning (Terraform, ARM, Azure SDK)
- GCPSpecialist: GCP cloud infrastructure provisioning (Terraform, Deployment Manager, gcloud)
- MedicalSpecialist: Medical documentation (future)
- FinancialSpecialist: Financial reports and analysis (future)
"""

from .base import BaseSpecialist
from .legal_specialist import LegalSpecialist
from .aws_specialist import AWSSpecialist
from .azure_specialist import AzureSpecialist
from .gcp_specialist import GCPSpecialist
from .oci_specialist import OCISpecialist

__all__ = [
    "BaseSpecialist",
    "LegalSpecialist",
    "AWSSpecialist",
    "AzureSpecialist",
    "GCPSpecialist",
    "OCISpecialist",
]
