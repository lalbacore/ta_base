"""
AWS Cloud Specialist Agent - Domain expert for AWS infrastructure.

Uses AWSCapability to generate Infrastructure-as-Code (Terraform, CloudFormation)
and boto3 SDK scripts for provisioning AWS resources.
"""

from typing import Dict, Any
from swarms.team_agent.specialists.base import BaseSpecialist
from swarms.team_agent.capabilities.cloud import AWSCapability


class AWSSpecialist(BaseSpecialist):
    """
    Specialist agent for AWS cloud infrastructure.

    Primary Capability: AWSCapability
    Domains: aws, cloud, infrastructure, terraform, ec2, s3, lambda
    Keywords: aws, ec2, s3, lambda, rds, vpc, cloudformation, terraform, boto3

    Use Cases:
    - Provision EC2 instances and auto-scaling groups
    - Create S3 buckets with encryption and versioning
    - Deploy Lambda functions and API Gateway
    - Set up RDS databases (PostgreSQL, MySQL)
    - Configure VPCs, subnets, and security groups
    - Generate Terraform or CloudFormation templates
    - Create boto3 SDK scripts for AWS automation
    """

    def __init__(self, agent_id: str = None, workflow_id: str = None, cert_chain=None):
        """
        Initialize AWS Specialist agent.

        Args:
            agent_id: Unique agent ID (auto-generated if not provided)
            workflow_id: Current workflow ID
            cert_chain: PKI certificate chain for signing
        """
        super().__init__(agent_id, workflow_id, cert_chain)

        # Agent metadata
        self.name = "AWS Cloud Specialist"
        self.description = (
            "Specialist agent for AWS cloud infrastructure provisioning. "
            "Generates Terraform, CloudFormation templates, and boto3 SDK scripts "
            "for EC2, S3, Lambda, RDS, VPC, and other AWS services."
        )
        self.version = "1.0.0"

        # Load primary capability
        self.primary_capability = AWSCapability()

    def get_primary_capability(self):
        """Get the primary capability this specialist uses."""
        return self.primary_capability

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AWS infrastructure provisioning.

        Args:
            context: dict with:
                - mission: str - Description of AWS infrastructure to create
                - architecture: str - Optional architecture from Architect

        Returns:
            dict with:
                - agent_id: str
                - agent_name: str
                - capability_used: str - "aws_cloud_infrastructure"
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
            "capability_used": "aws_cloud_infrastructure",
            "artifacts": result.get("artifacts", []),
            "content": result.get("content", ""),
            "metadata": {
                **result.get("metadata", {}),
                "specialist": self.name,
                "specialist_version": self.version,
                "cloud_provider": "aws"
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
            "aws", "amazon web services",
            # Compute
            "ec2", "elastic compute", "instance", "virtual machine",
            "lambda", "serverless function",
            "ecs", "fargate", "container",
            "eks", "kubernetes",
            # Storage
            "s3", "simple storage", "bucket",
            "ebs", "elastic block store",
            "efs", "elastic file system",
            # Database
            "rds", "relational database",
            "dynamodb", "nosql",
            "aurora", "elasticache", "redis", "memcached",
            # Networking
            "vpc", "virtual private cloud",
            "cloudfront", "cdn",
            "route53", "dns",
            "load balancer", "alb", "elb",
            # IaC Tools
            "terraform", "cloudformation", "boto3",
            # General AWS terms
            "aws infrastructure", "provision aws", "deploy aws"
        ]
