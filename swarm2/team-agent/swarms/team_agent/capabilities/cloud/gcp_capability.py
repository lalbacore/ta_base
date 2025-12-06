"""
GCP Cloud Infrastructure Capability.

Generates Infrastructure-as-Code and SDK scripts for GCP services including:
- Compute (Compute Engine, Cloud Run, GKE, Cloud Functions)
- Storage (Cloud Storage, Persistent Disks, Filestore)
- Databases (Cloud SQL, Firestore, Bigtable)
- Networking (VPC, Cloud Load Balancing, Cloud CDN)
- Security (IAM, Secret Manager, KMS)
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class GCPCapability(BaseCapability):
    """
    GCP cloud infrastructure capability.

    Generates Terraform/Deployment Manager templates and Google Cloud SDK scripts
    for provisioning and managing GCP resources.
    """

    def get_metadata(self) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "name": "gcp_cloud_infrastructure",
            "display_name": "GCP Cloud Infrastructure",
            "type": "cloud_infrastructure",
            "domains": ["gcp", "google-cloud", "cloud", "infrastructure", "devops", "terraform"],
            "description": (
                "Generate Infrastructure-as-Code (Terraform, Deployment Manager) and "
                "Google Cloud SDK scripts for GCP services. Supports Compute Engine, "
                "Cloud Storage, Cloud SQL, VPC, IAM, and more."
            ),
            "version": "1.0.0",
            "module_path": "swarms.team_agent.capabilities.cloud.gcp_capability"
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate GCP infrastructure code.

        Args:
            context: dict with:
                - mission: str - Description of GCP infrastructure to create
                - architecture: str - Optional architecture design

        Returns:
            dict with:
                - content: str - Generated infrastructure code
                - artifacts: list - Code files (Terraform, Deployment Manager, SDK)
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        mission_lower = mission.lower()

        # Select appropriate IaC tool
        if any(kw in mission_lower for kw in ["terraform", "tf", "hcl"]):
            code = self._generate_terraform(mission)
            filename = "main.tf"
        elif any(kw in mission_lower for kw in ["deployment manager", "gcp template"]):
            code = self._generate_deployment_manager(mission)
            filename = "config.yaml"
        else:
            # Default to Google Cloud SDK Python script
            code = self._generate_gcloud_sdk_script(mission)
            filename = "gcp_setup.py"

        return {
            "content": code,
            "artifacts": [{
                "type": "infrastructure",
                "name": "gcp_infrastructure",
                "filename": filename,
                "content": code
            }],
            "metadata": self.metadata
        }

    def _generate_terraform(self, mission: str) -> str:
        """Generate Terraform configuration for GCP."""
        return f"""# GCP Infrastructure - Terraform Configuration
# Mission: {mission}

terraform {{
  required_version = ">= 1.0"

  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

# Variables
variable "project_id" {{
  description = "GCP Project ID"
  type        = string
}}

variable "region" {{
  description = "GCP region"
  type        = string
  default     = "us-central1"
}}

variable "zone" {{
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "dev"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "teamagent"
}}

provider "google" {{
  project = var.project_id
  region  = var.region
  zone    = var.zone
}}

# VPC Network
resource "google_compute_network" "main" {{
  name                    = "${{var.project_name}}-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}}

resource "google_compute_subnetwork" "main" {{
  name          = "${{var.project_name}}-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id
}}

# Firewall Rules
resource "google_compute_firewall" "allow_ssh" {{
  name    = "${{var.project_name}}-allow-ssh"
  network = google_compute_network.main.name
  project = var.project_id

  allow {{
    protocol = "tcp"
    ports    = ["22"]
  }}

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["allow-ssh"]
}}

resource "google_compute_firewall" "allow_http" {{
  name    = "${{var.project_name}}-allow-http"
  network = google_compute_network.main.name
  project = var.project_id

  allow {{
    protocol = "tcp"
    ports    = ["80", "443"]
  }}

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["allow-http"]
}}

# Cloud Storage Bucket
resource "google_storage_bucket" "data" {{
  name          = "${{var.project_id}}-${{var.project_name}}-data"
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {{
    enabled = true
  }}

  encryption {{
    default_kms_key_name = null
  }}

  labels = {{
    environment = var.environment
    managed_by  = "terraform"
  }}
}}

# Compute Engine Instance
resource "google_compute_instance" "main" {{
  name         = "${{var.project_name}}-instance"
  machine_type = "e2-micro"
  zone         = var.zone
  project      = var.project_id

  tags = ["allow-ssh", "allow-http"]

  boot_disk {{
    initialize_params {{
      image = "debian-cloud/debian-11"
      size  = 20
    }}
  }}

  network_interface {{
    network    = google_compute_network.main.name
    subnetwork = google_compute_subnetwork.main.name

    access_config {{
      // Ephemeral public IP
    }}
  }}

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
  EOF

  labels = {{
    environment = var.environment
  }}
}}

# Cloud SQL Instance (PostgreSQL)
resource "google_sql_database_instance" "main" {{
  name             = "${{var.project_name}}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  settings {{
    tier = "db-f1-micro"

    ip_configuration {{
      ipv4_enabled    = true
      private_network = null

      authorized_networks {{
        name  = "allow-all"
        value = "0.0.0.0/0"
      }}
    }}

    backup_configuration {{
      enabled = true
    }}
  }}

  deletion_protection = false
}}

resource "google_sql_database" "app" {{
  name     = "appdb"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}}

# Cloud Run Service
resource "google_cloud_run_service" "main" {{
  name     = "${{var.project_name}}-service"
  location = var.region
  project  = var.project_id

  template {{
    spec {{
      containers {{
        image = "gcr.io/cloudrun/hello"

        env {{
          name  = "ENVIRONMENT"
          value = var.environment
        }}
      }}
    }}
  }}

  traffic {{
    percent         = 100
    latest_revision = true
  }}
}}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "public" {{
  service  = google_cloud_run_service.main.name
  location = google_cloud_run_service.main.location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}}

# Outputs
output "instance_public_ip" {{
  description = "Public IP of Compute Engine instance"
  value       = google_compute_instance.main.network_interface[0].access_config[0].nat_ip
}}

output "storage_bucket" {{
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.data.name
}}

output "cloud_sql_connection" {{
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}}

output "cloud_run_url" {{
  description = "Cloud Run service URL"
  value       = google_cloud_run_service.main.status[0].url
}}
"""

    def _generate_deployment_manager(self, mission: str) -> str:
        """Generate GCP Deployment Manager template."""
        return f"""# GCP Infrastructure - Deployment Manager Configuration
# Mission: {mission}

imports:
- path: vm_instance.jinja

resources:
# VPC Network
- name: teamagent-vpc
  type: compute.v1.network
  properties:
    autoCreateSubnetworks: false

# Subnet
- name: teamagent-subnet
  type: compute.v1.subnetwork
  properties:
    network: $(ref.teamagent-vpc.selfLink)
    ipCidrRange: 10.0.1.0/24
    region: us-central1

# Firewall - Allow SSH
- name: teamagent-allow-ssh
  type: compute.v1.firewall
  properties:
    network: $(ref.teamagent-vpc.selfLink)
    sourceRanges: ["0.0.0.0/0"]
    allowed:
    - IPProtocol: tcp
      ports: ["22"]

# Firewall - Allow HTTP/HTTPS
- name: teamagent-allow-http
  type: compute.v1.firewall
  properties:
    network: $(ref.teamagent-vpc.selfLink)
    sourceRanges: ["0.0.0.0/0"]
    allowed:
    - IPProtocol: tcp
      ports: ["80", "443"]

# Storage Bucket
- name: teamagent-data-bucket
  type: storage.v1.bucket
  properties:
    location: US
    storageClass: STANDARD
    versioning:
      enabled: true

# Compute Instance
- name: teamagent-instance
  type: compute.v1.instance
  properties:
    zone: us-central1-a
    machineType: zones/us-central1-a/machineTypes/e2-micro
    disks:
    - deviceName: boot
      type: PERSISTENT
      boot: true
      autoDelete: true
      initializeParams:
        sourceImage: projects/debian-cloud/global/images/family/debian-11
        diskSizeGb: 20
    networkInterfaces:
    - network: $(ref.teamagent-vpc.selfLink)
      subnetwork: $(ref.teamagent-subnet.selfLink)
      accessConfigs:
      - name: External NAT
        type: ONE_TO_ONE_NAT

outputs:
- name: instanceIP
  value: $(ref.teamagent-instance.networkInterfaces[0].accessConfigs[0].natIP)
- name: bucketName
  value: $(ref.teamagent-data-bucket.name)
"""

    def _generate_gcloud_sdk_script(self, mission: str) -> str:
        """Generate Google Cloud SDK Python script."""
        return f'''"""
GCP Infrastructure Setup Script
Mission: {mission}

Prerequisites:
- pip install google-cloud-compute google-cloud-storage google-cloud-sql
- GCP credentials configured (gcloud auth application-default login)
"""

from google.cloud import compute_v1, storage
from typing import Dict, Any
import time


class GCPInfrastructure:
    """GCP infrastructure provisioning using Google Cloud SDK."""

    def __init__(self, project_id: str, region: str = 'us-central1', zone: str = 'us-central1-a'):
        """
        Initialize GCP clients.

        Args:
            project_id: GCP project ID
            region: GCP region
            zone: GCP zone
        """
        self.project_id = project_id
        self.region = region
        self.zone = zone

        # Initialize clients
        self.compute_client = compute_v1.InstancesClient()
        self.networks_client = compute_v1.NetworksClient()
        self.firewalls_client = compute_v1.FirewallsClient()
        self.storage_client = storage.Client(project=project_id)

    def create_vpc_network(self, network_name: str) -> str:
        """Create VPC network."""
        print(f"Creating VPC network: {{network_name}}")

        network = compute_v1.Network()
        network.name = network_name
        network.auto_create_subnetworks = False

        operation = self.networks_client.insert(
            project=self.project_id,
            network_resource=network
        )

        # Wait for operation to complete
        self._wait_for_operation(operation)
        print(f"  ✓ Created VPC network: {{network_name}}")
        return network_name

    def create_firewall_rules(self, network_name: str) -> None:
        """Create firewall rules."""
        print("Creating firewall rules...")

        # Allow SSH
        ssh_firewall = compute_v1.Firewall()
        ssh_firewall.name = f"{{network_name}}-allow-ssh"
        ssh_firewall.network = f"global/networks/{{network_name}}"
        ssh_firewall.source_ranges = ["0.0.0.0/0"]
        ssh_firewall.allowed = [
            compute_v1.Allowed(I_p_protocol="tcp", ports=["22"])
        ]

        operation = self.firewalls_client.insert(
            project=self.project_id,
            firewall_resource=ssh_firewall
        )
        self._wait_for_operation(operation)
        print(f"  ✓ Created SSH firewall rule")

        # Allow HTTP/HTTPS
        http_firewall = compute_v1.Firewall()
        http_firewall.name = f"{{network_name}}-allow-http"
        http_firewall.network = f"global/networks/{{network_name}}"
        http_firewall.source_ranges = ["0.0.0.0/0"]
        http_firewall.allowed = [
            compute_v1.Allowed(I_p_protocol="tcp", ports=["80", "443"])
        ]

        operation = self.firewalls_client.insert(
            project=self.project_id,
            firewall_resource=http_firewall
        )
        self._wait_for_operation(operation)
        print(f"  ✓ Created HTTP/HTTPS firewall rule")

    def create_storage_bucket(self, bucket_name: str) -> str:
        """Create Cloud Storage bucket."""
        print(f"Creating storage bucket: {{bucket_name}}")

        bucket = self.storage_client.create_bucket(
            bucket_name,
            location=self.region
        )

        # Enable versioning
        bucket.versioning_enabled = True
        bucket.patch()

        print(f"  ✓ Created bucket: {{bucket.name}}")
        return bucket.name

    def create_compute_instance(
        self,
        instance_name: str,
        network_name: str,
        machine_type: str = 'e2-micro'
    ) -> str:
        """Create Compute Engine instance."""
        print(f"Creating Compute Engine instance: {{instance_name}}")

        instance = compute_v1.Instance()
        instance.name = instance_name
        instance.machine_type = f"zones/{{self.zone}}/machineTypes/{{machine_type}}"

        # Boot disk
        disk = compute_v1.AttachedDisk()
        disk.boot = True
        disk.auto_delete = True
        initialize_params = compute_v1.AttachedDiskInitializeParams()
        initialize_params.source_image = "projects/debian-cloud/global/images/family/debian-11"
        initialize_params.disk_size_gb = 20
        disk.initialize_params = initialize_params
        instance.disks = [disk]

        # Network interface
        network_interface = compute_v1.NetworkInterface()
        network_interface.network = f"global/networks/{{network_name}}"
        access_config = compute_v1.AccessConfig()
        access_config.name = "External NAT"
        access_config.type_ = "ONE_TO_ONE_NAT"
        network_interface.access_configs = [access_config]
        instance.network_interfaces = [network_interface]

        operation = self.compute_client.insert(
            project=self.project_id,
            zone=self.zone,
            instance_resource=instance
        )

        self._wait_for_operation(operation)

        # Get instance details
        instance_details = self.compute_client.get(
            project=self.project_id,
            zone=self.zone,
            instance=instance_name
        )

        external_ip = instance_details.network_interfaces[0].access_configs[0].nat_i_p
        print(f"  ✓ Created instance: {{instance_name}} (IP: {{external_ip}})")
        return external_ip

    def _wait_for_operation(self, operation) -> None:
        """Wait for operation to complete."""
        # Simple polling - production code should use proper operation tracking
        time.sleep(5)


def main():
    """Main execution."""
    import os

    print("=" * 60)
    print("GCP Infrastructure Setup")
    print("=" * 60)
    print()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set")
        return

    # Initialize
    gcp = GCPInfrastructure(project_id, region='us-central1')

    # Create network
    network_name = "teamagent-vpc"
    gcp.create_vpc_network(network_name)
    print()

    # Create firewall rules
    gcp.create_firewall_rules(network_name)
    print()

    # Create storage bucket
    bucket_name = f"{{project_id}}-teamagent-data"
    bucket = gcp.create_storage_bucket(bucket_name)
    print()

    # Create compute instance
    instance_ip = gcp.create_compute_instance(
        "teamagent-instance",
        network_name
    )
    print()

    print("=" * 60)
    print("✓ Infrastructure Setup Complete!")
    print("=" * 60)
    print()
    print("Resources Created:")
    print(f"  - VPC Network: {{network_name}}")
    print(f"  - Storage Bucket: {{bucket}}")
    print(f"  - Compute Instance IP: {{instance_ip}}")


if __name__ == '__main__':
    main()
'''


__all__ = ["GCPCapability"]
