"""
OCI Cloud Capability - Infrastructure-as-Code generation for Oracle Cloud Infrastructure.

Generates Terraform configurations, OCI CLI scripts, and OCI Python SDK code
for provisioning Oracle Cloud resources.
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class OCICapability(BaseCapability):
    """
    Capability for generating Oracle Cloud Infrastructure (OCI) code.

    Supports multiple output formats:
    - Terraform (HCL) with oci provider
    - OCI CLI scripts (bash with oci commands)
    - OCI Python SDK scripts (using oci library)

    Covered services:
    - Compute (VM instances, instance pools)
    - Object Storage (buckets)
    - Autonomous Database (ATP, ADW)
    - VCN (Virtual Cloud Networks, subnets, security lists)
    - Load Balancer
    - Container Engine for Kubernetes (OKE)
    - Block Volume
    - File Storage
    """

    def get_metadata(self) -> Dict[str, Any]:
        """Return capability metadata."""
        return {
            "name": "oci_cloud_infrastructure",
            "type": "code_generation",
            "domains": ["oci", "oracle-cloud", "cloud", "infrastructure", "terraform"],
            "description": (
                "Generates Infrastructure-as-Code (Terraform) and SDK scripts "
                "for Oracle Cloud Infrastructure (OCI). Supports Compute, Object Storage, "
                "Autonomous Database, VCN, Load Balancer, OKE, and other OCI services."
            ),
            "version": "1.0.0",
            "output_formats": ["terraform", "oci_cli", "oci_sdk"],
            "cloud_provider": "oci"
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate OCI infrastructure code.

        Args:
            context: dict with:
                - mission: str - Description of OCI infrastructure to create
                - architecture: str - Optional architecture details

        Returns:
            dict with:
                - content: str - Generated code
                - artifacts: list - Code artifacts
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")

        # Determine output format based on keywords
        mission_lower = mission.lower()

        if any(kw in mission_lower for kw in ["terraform", "tf", "hcl"]):
            code = self._generate_terraform(mission, architecture)
            filename = "main.tf"
            artifact_type = "terraform"
        elif any(kw in mission_lower for kw in ["oci cli", "cli script", "bash"]):
            code = self._generate_oci_cli_script(mission, architecture)
            filename = "oci_setup.sh"
            artifact_type = "bash"
        else:
            # Default to OCI Python SDK
            code = self._generate_oci_sdk_script(mission, architecture)
            filename = "oci_setup.py"
            artifact_type = "python"

        return {
            "content": code,
            "artifacts": [{
                "type": artifact_type,
                "name": "oci_infrastructure",
                "filename": filename,
                "content": code
            }],
            "metadata": {
                **self.metadata,
                "mission": mission,
                "architecture": architecture,
                "output_format": artifact_type
            }
        }

    def _generate_terraform(self, mission: str, architecture: str) -> str:
        """Generate Terraform configuration for OCI."""
        return f'''# Oracle Cloud Infrastructure (OCI) Terraform Configuration
# Mission: {mission}
# Architecture: {architecture or "Standard multi-tier OCI deployment"}

terraform {{
  required_providers {{
    oci = {{
      source  = "oracle/oci"
      version = "~> 5.0"
    }}
  }}
  required_version = ">= 1.0"
}}

# Provider configuration
provider "oci" {{
  # Authentication via API Key or Instance Principal
  # Set OCI_TENANCY_OCID, OCI_USER_OCID, OCI_FINGERPRINT, OCI_KEY_FILE env vars
  region = var.region
}}

# Variables
variable "tenancy_ocid" {{
  description = "OCI Tenancy OCID"
  type        = string
}}

variable "compartment_ocid" {{
  description = "OCI Compartment OCID"
  type        = string
}}

variable "region" {{
  description = "OCI Region (e.g., us-phoenix-1, us-ashburn-1)"
  type        = string
  default     = "us-phoenix-1"
}}

variable "project_name" {{
  description = "Project name for resource naming"
  type        = string
  default     = "myproject"
}}

variable "environment" {{
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}}

variable "ssh_public_key" {{
  description = "SSH public key for compute instances"
  type        = string
}}

# Data sources
data "oci_identity_availability_domains" "ads" {{
  compartment_id = var.tenancy_ocid
}}

data "oci_core_images" "oracle_linux" {{
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = "VM.Standard.E4.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}}

{self._tf_vcn()}

{self._tf_compute()}

{self._tf_object_storage()}

{self._tf_autonomous_database()}

{self._tf_load_balancer()}

# Outputs
output "vcn_id" {{
  description = "VCN OCID"
  value       = oci_core_vcn.main.id
}}

output "compute_instance_public_ip" {{
  description = "Public IP of compute instance"
  value       = oci_core_instance.app.public_ip
}}

output "object_storage_bucket" {{
  description = "Object Storage bucket name"
  value       = oci_objectstorage_bucket.main.name
}}

output "autonomous_database_connection" {{
  description = "Autonomous Database connection string"
  value       = oci_database_autonomous_database.main.connection_strings[0].high
  sensitive   = true
}}

output "load_balancer_ip" {{
  description = "Load Balancer public IP"
  value       = oci_load_balancer_load_balancer.main.ip_address_details[0].ip_address
}}
'''

    def _tf_vcn(self) -> str:
        """Terraform VCN (Virtual Cloud Network) configuration."""
        return '''# Virtual Cloud Network (VCN)
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "${var.project_name}-${var.environment}-vcn"
  dns_label      = "${var.project_name}vcn"
}

# Internet Gateway
resource "oci_core_internet_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-igw"
  enabled        = true
}

# Route Table
resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.main.id
  }
}

# Security List
resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-public-sl"

  # Allow outbound traffic
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  # Allow SSH
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Allow HTTP
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  # Allow HTTPS
  ingress_security_rules {
    protocol = "6"  # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

# Public Subnet
resource "oci_core_subnet" "public" {
  compartment_id      = var.compartment_ocid
  vcn_id              = oci_core_vcn.main.id
  cidr_block          = "10.0.1.0/24"
  display_name        = "${var.project_name}-public-subnet"
  dns_label           = "public"
  route_table_id      = oci_core_route_table.public.id
  security_list_ids   = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic = false
}
'''

    def _tf_compute(self) -> str:
        """Terraform Compute instance configuration."""
        return '''# Compute Instance
resource "oci_core_instance" "app" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "${var.project_name}-${var.environment}-instance"
  shape               = "VM.Standard.E4.Flex"

  shape_config {
    ocpus         = 2
    memory_in_gbs = 16
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.oracle_linux.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    display_name     = "${var.project_name}-vnic"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(<<-EOF
      #!/bin/bash
      yum update -y
      yum install -y docker
      systemctl start docker
      systemctl enable docker
      EOF
    )
  }

  freeform_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
'''

    def _tf_object_storage(self) -> str:
        """Terraform Object Storage bucket configuration."""
        return '''# Object Storage Bucket
resource "oci_objectstorage_bucket" "main" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "${var.project_name}-${var.environment}-bucket"
  access_type    = "NoPublicAccess"

  versioning = "Enabled"

  freeform_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.compartment_ocid
}
'''

    def _tf_autonomous_database(self) -> str:
        """Terraform Autonomous Database configuration."""
        return '''# Autonomous Database
resource "oci_database_autonomous_database" "main" {
  compartment_id           = var.compartment_ocid
  db_name                  = "${var.project_name}db"
  display_name             = "${var.project_name}-${var.environment}-adb"
  admin_password           = random_password.db_password.result
  cpu_core_count           = 1
  data_storage_size_in_tbs = 1
  db_workload              = "OLTP"  # Or "DW" for data warehouse
  is_auto_scaling_enabled  = true
  is_free_tier             = false
  license_model            = "LICENSE_INCLUDED"

  freeform_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}
'''

    def _tf_load_balancer(self) -> str:
        """Terraform Load Balancer configuration."""
        return '''# Load Balancer
resource "oci_load_balancer_load_balancer" "main" {
  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}-${var.environment}-lb"
  shape          = "flexible"

  shape_details {
    minimum_bandwidth_in_mbps = 10
    maximum_bandwidth_in_mbps = 100
  }

  subnet_ids = [oci_core_subnet.public.id]

  is_private = false

  freeform_tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Backend Set
resource "oci_load_balancer_backend_set" "app" {
  load_balancer_id = oci_load_balancer_load_balancer.main.id
  name             = "app-backend-set"
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol          = "HTTP"
    port              = 80
    url_path          = "/"
    interval_ms       = 10000
    timeout_in_millis = 3000
    retries           = 3
  }
}

# Backend
resource "oci_load_balancer_backend" "app" {
  load_balancer_id = oci_load_balancer_load_balancer.main.id
  backendset_name  = oci_load_balancer_backend_set.app.name
  ip_address       = oci_core_instance.app.private_ip
  port             = 80
  backup           = false
  drain            = false
  offline          = false
  weight           = 1
}

# Listener
resource "oci_load_balancer_listener" "http" {
  load_balancer_id         = oci_load_balancer_load_balancer.main.id
  name                     = "http-listener"
  default_backend_set_name = oci_load_balancer_backend_set.app.name
  port                     = 80
  protocol                 = "HTTP"
}
'''

    def _generate_oci_cli_script(self, mission: str, architecture: str) -> str:
        """Generate OCI CLI bash script."""
        return f'''#!/bin/bash
# Oracle Cloud Infrastructure (OCI) CLI Setup Script
# Mission: {mission}
# Architecture: {architecture or "Standard OCI deployment"}
#
# Prerequisites:
# - OCI CLI installed (pip install oci-cli)
# - OCI config file configured (~/.oci/config)
# - Environment variables set: COMPARTMENT_OCID, REGION

set -e  # Exit on error

# Configuration
COMPARTMENT_OCID="${{COMPARTMENT_OCID:-}}"
REGION="${{REGION:-us-phoenix-1}}"
PROJECT_NAME="${{PROJECT_NAME:-myproject}}"
ENVIRONMENT="${{ENVIRONMENT:-dev}}"
SSH_PUBLIC_KEY_FILE="${{SSH_PUBLIC_KEY_FILE:-~/.ssh/id_rsa.pub}}"

echo "=== OCI Infrastructure Setup ==="
echo "Region: $REGION"
echo "Project: $PROJECT_NAME"
echo "Environment: $ENVIRONMENT"

# Create VCN
echo "Creating VCN..."
VCN_OCID=$(oci network vcn create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --cidr-blocks '["10.0.0.0/16"]' \\
  --display-name "$PROJECT_NAME-$ENVIRONMENT-vcn" \\
  --dns-label "${{PROJECT_NAME}}vcn" \\
  --query 'data.id' \\
  --raw-output)
echo "VCN created: $VCN_OCID"

# Create Internet Gateway
echo "Creating Internet Gateway..."
IGW_OCID=$(oci network internet-gateway create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --vcn-id "$VCN_OCID" \\
  --is-enabled true \\
  --display-name "$PROJECT_NAME-igw" \\
  --query 'data.id' \\
  --raw-output)
echo "Internet Gateway created: $IGW_OCID"

# Create Route Table
echo "Creating Route Table..."
ROUTE_TABLE_OCID=$(oci network route-table create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --vcn-id "$VCN_OCID" \\
  --display-name "$PROJECT_NAME-public-rt" \\
  --route-rules "[{{\\"cidrBlock\\":\\"0.0.0.0/0\\",\\"networkEntityId\\":\\"$IGW_OCID\\"}}]" \\
  --query 'data.id' \\
  --raw-output)
echo "Route Table created: $ROUTE_TABLE_OCID"

# Create Security List
echo "Creating Security List..."
SECURITY_LIST_OCID=$(oci network security-list create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --vcn-id "$VCN_OCID" \\
  --display-name "$PROJECT_NAME-public-sl" \\
  --egress-security-rules '[{{"destination":"0.0.0.0/0","protocol":"all"}}]' \\
  --ingress-security-rules '[{{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{{"destinationPortRange":{{"min":22,"max":22}}}}}},{{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{{"destinationPortRange":{{"min":80,"max":80}}}}}},{{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{{"destinationPortRange":{{"min":443,"max":443}}}}}}]' \\
  --query 'data.id' \\
  --raw-output)
echo "Security List created: $SECURITY_LIST_OCID"

# Create Subnet
echo "Creating Subnet..."
SUBNET_OCID=$(oci network subnet create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --vcn-id "$VCN_OCID" \\
  --cidr-block "10.0.1.0/24" \\
  --display-name "$PROJECT_NAME-public-subnet" \\
  --dns-label "public" \\
  --route-table-id "$ROUTE_TABLE_OCID" \\
  --security-list-ids "[\\"$SECURITY_LIST_OCID\\"]" \\
  --query 'data.id' \\
  --raw-output)
echo "Subnet created: $SUBNET_OCID"

# Get latest Oracle Linux image
echo "Finding Oracle Linux image..."
IMAGE_OCID=$(oci compute image list \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --operating-system "Oracle Linux" \\
  --operating-system-version "8" \\
  --shape "VM.Standard.E4.Flex" \\
  --sort-by TIMECREATED \\
  --sort-order DESC \\
  --limit 1 \\
  --query 'data[0].id' \\
  --raw-output)
echo "Image OCID: $IMAGE_OCID"

# Get availability domain
AD_NAME=$(oci iam availability-domain list \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --query 'data[0].name' \\
  --raw-output)
echo "Availability Domain: $AD_NAME"

# Launch compute instance
echo "Launching compute instance..."
INSTANCE_OCID=$(oci compute instance launch \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --availability-domain "$AD_NAME" \\
  --display-name "$PROJECT_NAME-$ENVIRONMENT-instance" \\
  --shape "VM.Standard.E4.Flex" \\
  --shape-config '{{"ocpus":2,"memoryInGBs":16}}' \\
  --image-id "$IMAGE_OCID" \\
  --subnet-id "$SUBNET_OCID" \\
  --assign-public-ip true \\
  --ssh-authorized-keys-file "$SSH_PUBLIC_KEY_FILE" \\
  --query 'data.id' \\
  --raw-output)
echo "Instance launched: $INSTANCE_OCID"

# Create Object Storage bucket
echo "Creating Object Storage bucket..."
NAMESPACE=$(oci os ns get --query 'data' --raw-output)
oci os bucket create \\
  --compartment-id "$COMPARTMENT_OCID" \\
  --name "$PROJECT_NAME-$ENVIRONMENT-bucket" \\
  --public-access-type NoPublicAccess \\
  --versioning Enabled
echo "Bucket created: $PROJECT_NAME-$ENVIRONMENT-bucket"

echo "=== Setup Complete ==="
echo "VCN OCID: $VCN_OCID"
echo "Instance OCID: $INSTANCE_OCID"
echo "Bucket: $PROJECT_NAME-$ENVIRONMENT-bucket"
echo ""
echo "Get instance public IP:"
echo "  oci compute instance list-vnics --instance-id $INSTANCE_OCID --query 'data[0].\\"public-ip\\"' --raw-output"
'''

    def _generate_oci_sdk_script(self, mission: str, architecture: str) -> str:
        """Generate OCI Python SDK script."""
        return f'''#!/usr/bin/env python3
"""
Oracle Cloud Infrastructure (OCI) Python SDK Setup Script
Mission: {mission}
Architecture: {architecture or "Standard OCI deployment"}

Prerequisites:
- pip install oci
- OCI config file configured (~/.oci/config)
- Environment variables: COMPARTMENT_OCID
"""

import os
import sys
import oci
from oci.core import VirtualNetworkClient, ComputeClient
from oci.object_storage import ObjectStorageClient
from oci.database import DatabaseClient

# Configuration
COMPARTMENT_OCID = os.environ.get("COMPARTMENT_OCID")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "myproject")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
SSH_PUBLIC_KEY_FILE = os.environ.get("SSH_PUBLIC_KEY_FILE", os.path.expanduser("~/.ssh/id_rsa.pub"))

if not COMPARTMENT_OCID:
    print("Error: COMPARTMENT_OCID environment variable not set")
    sys.exit(1)

# Initialize OCI config and clients
config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
network_client = VirtualNetworkClient(config)
compute_client = ComputeClient(config)
object_storage_client = ObjectStorageClient(config)
database_client = DatabaseClient(config)

print("=== OCI Infrastructure Setup ===")
print(f"Region: {{config['region']}}")
print(f"Project: {{PROJECT_NAME}}")
print(f"Environment: {{ENVIRONMENT}}")

# Create VCN
print("\\nCreating VCN...")
vcn_response = network_client.create_vcn(
    oci.core.models.CreateVcnDetails(
        compartment_id=COMPARTMENT_OCID,
        cidr_blocks=["10.0.0.0/16"],
        display_name=f"{{PROJECT_NAME}}-{{ENVIRONMENT}}-vcn",
        dns_label=f"{{PROJECT_NAME}}vcn"
    )
)
vcn_id = vcn_response.data.id
print(f"VCN created: {{vcn_id}}")

# Create Internet Gateway
print("Creating Internet Gateway...")
igw_response = network_client.create_internet_gateway(
    oci.core.models.CreateInternetGatewayDetails(
        compartment_id=COMPARTMENT_OCID,
        vcn_id=vcn_id,
        is_enabled=True,
        display_name=f"{{PROJECT_NAME}}-igw"
    )
)
igw_id = igw_response.data.id
print(f"Internet Gateway created: {{igw_id}}")

# Create Route Table
print("Creating Route Table...")
route_table_response = network_client.create_route_table(
    oci.core.models.CreateRouteTableDetails(
        compartment_id=COMPARTMENT_OCID,
        vcn_id=vcn_id,
        display_name=f"{{PROJECT_NAME}}-public-rt",
        route_rules=[
            oci.core.models.RouteRule(
                cidr_block="0.0.0.0/0",
                network_entity_id=igw_id
            )
        ]
    )
)
route_table_id = route_table_response.data.id
print(f"Route Table created: {{route_table_id}}")

# Create Security List
print("Creating Security List...")
security_list_response = network_client.create_security_list(
    oci.core.models.CreateSecurityListDetails(
        compartment_id=COMPARTMENT_OCID,
        vcn_id=vcn_id,
        display_name=f"{{PROJECT_NAME}}-public-sl",
        egress_security_rules=[
            oci.core.models.EgressSecurityRule(
                destination="0.0.0.0/0",
                protocol="all"
            )
        ],
        ingress_security_rules=[
            oci.core.models.IngressSecurityRule(
                source="0.0.0.0/0",
                protocol="6",  # TCP
                tcp_options=oci.core.models.TcpOptions(
                    destination_port_range=oci.core.models.PortRange(min=22, max=22)
                )
            ),
            oci.core.models.IngressSecurityRule(
                source="0.0.0.0/0",
                protocol="6",  # TCP
                tcp_options=oci.core.models.TcpOptions(
                    destination_port_range=oci.core.models.PortRange(min=80, max=80)
                )
            ),
            oci.core.models.IngressSecurityRule(
                source="0.0.0.0/0",
                protocol="6",  # TCP
                tcp_options=oci.core.models.TcpOptions(
                    destination_port_range=oci.core.models.PortRange(min=443, max=443)
                )
            )
        ]
    )
)
security_list_id = security_list_response.data.id
print(f"Security List created: {{security_list_id}}")

# Create Subnet
print("Creating Subnet...")
subnet_response = network_client.create_subnet(
    oci.core.models.CreateSubnetDetails(
        compartment_id=COMPARTMENT_OCID,
        vcn_id=vcn_id,
        cidr_block="10.0.1.0/24",
        display_name=f"{{PROJECT_NAME}}-public-subnet",
        dns_label="public",
        route_table_id=route_table_id,
        security_list_ids=[security_list_id],
        prohibit_public_ip_on_vnic=False
    )
)
subnet_id = subnet_response.data.id
print(f"Subnet created: {{subnet_id}}")

# Get availability domain
print("Getting availability domain...")
availability_domains = identity_client.list_availability_domains(
    COMPARTMENT_OCID
).data
ad_name = availability_domains[0].name
print(f"Using availability domain: {{ad_name}}")

# Get latest Oracle Linux image
print("Finding Oracle Linux image...")
images = compute_client.list_images(
    COMPARTMENT_OCID,
    operating_system="Oracle Linux",
    operating_system_version="8",
    shape="VM.Standard.E4.Flex",
    sort_by="TIMECREATED",
    sort_order="DESC",
    limit=1
).data
image_id = images[0].id
print(f"Using image: {{image_id}}")

# Read SSH public key
with open(SSH_PUBLIC_KEY_FILE, 'r') as f:
    ssh_public_key = f.read().strip()

# Launch compute instance
print("Launching compute instance...")
instance_response = compute_client.launch_instance(
    oci.core.models.LaunchInstanceDetails(
        compartment_id=COMPARTMENT_OCID,
        availability_domain=ad_name,
        display_name=f"{{PROJECT_NAME}}-{{ENVIRONMENT}}-instance",
        shape="VM.Standard.E4.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=2,
            memory_in_gbs=16
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=image_id
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=subnet_id,
            assign_public_ip=True,
            display_name=f"{{PROJECT_NAME}}-vnic"
        ),
        metadata={{
            "ssh_authorized_keys": ssh_public_key
        }},
        freeform_tags={{
            "Project": PROJECT_NAME,
            "Environment": ENVIRONMENT
        }}
    )
)
instance_id = instance_response.data.id
print(f"Instance launched: {{instance_id}}")

# Create Object Storage bucket
print("Creating Object Storage bucket...")
namespace = object_storage_client.get_namespace().data
object_storage_client.create_bucket(
    namespace,
    oci.object_storage.models.CreateBucketDetails(
        compartment_id=COMPARTMENT_OCID,
        name=f"{{PROJECT_NAME}}-{{ENVIRONMENT}}-bucket",
        public_access_type="NoPublicAccess",
        versioning="Enabled",
        freeform_tags={{
            "Project": PROJECT_NAME,
            "Environment": ENVIRONMENT
        }}
    )
)
print(f"Bucket created: {{PROJECT_NAME}}-{{ENVIRONMENT}}-bucket")

print("\\n=== Setup Complete ===")
print(f"VCN OCID: {{vcn_id}}")
print(f"Instance OCID: {{instance_id}}")
print(f"Bucket: {{PROJECT_NAME}}-{{ENVIRONMENT}}-bucket")
print("\\nTo get instance public IP:")
print(f"  vnic_attachments = compute_client.list_vnic_attachments(COMPARTMENT_OCID, instance_id='{{instance_id}}').data")
print(f"  vnic = network_client.get_vnic(vnic_attachments[0].vnic_id).data")
print(f"  print(vnic.public_ip)")
'''
