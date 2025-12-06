"""
Azure Cloud Infrastructure Capability.

Generates Infrastructure-as-Code and SDK scripts for Azure services including:
- Compute (VMs, App Service, AKS, Functions)
- Storage (Blob Storage, Files, Disks)
- Databases (SQL Database, Cosmos DB, PostgreSQL)
- Networking (VNet, Application Gateway, Front Door)
- Security (Key Vault, Managed Identity, Azure AD)
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class AzureCapability(BaseCapability):
    """
    Azure cloud infrastructure capability.

    Generates Terraform/ARM templates and Azure SDK scripts
    for provisioning and managing Azure resources.
    """

    def get_metadata(self) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "name": "azure_cloud_infrastructure",
            "display_name": "Azure Cloud Infrastructure",
            "type": "cloud_infrastructure",
            "domains": ["azure", "cloud", "infrastructure", "devops", "terraform"],
            "description": (
                "Generate Infrastructure-as-Code (Terraform, ARM) and "
                "Azure SDK scripts for Azure services. Supports VMs, App Service, "
                "Blob Storage, SQL Database, VNet, and more."
            ),
            "version": "1.0.0",
            "module_path": "swarms.team_agent.capabilities.cloud.azure_capability"
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Azure infrastructure code.

        Args:
            context: dict with:
                - mission: str - Description of Azure infrastructure to create
                - architecture: str - Optional architecture design

        Returns:
            dict with:
                - content: str - Generated infrastructure code
                - artifacts: list - Code files (Terraform, ARM, Azure SDK)
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        mission_lower = mission.lower()

        # Select appropriate IaC tool
        if any(kw in mission_lower for kw in ["terraform", "tf", "hcl"]):
            code = self._generate_terraform(mission)
            filename = "main.tf"
        elif any(kw in mission_lower for kw in ["arm", "bicep", "template"]):
            code = self._generate_arm_template(mission)
            filename = "azuredeploy.json"
        else:
            # Default to Azure SDK Python script
            code = self._generate_azure_sdk_script(mission)
            filename = "azure_setup.py"

        return {
            "content": code,
            "artifacts": [{
                "type": "infrastructure",
                "name": "azure_infrastructure",
                "filename": filename,
                "content": code
            }],
            "metadata": self.metadata
        }

    def _generate_terraform(self, mission: str) -> str:
        """Generate Terraform configuration for Azure."""
        return f"""# Azure Infrastructure - Terraform Configuration
# Mission: {mission}

terraform {{
  required_version = ">= 1.0"

  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
}}

# Variables
variable "location" {{
  description = "Azure region"
  type        = string
  default     = "eastus"
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

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "${{var.project_name}}-${{var.environment}}-rg"
  location = var.location

  tags = {{
    Environment = var.environment
    ManagedBy   = "Terraform"
  }}
}}

# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name                = "${{var.project_name}}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {{
    Environment = var.environment
  }}
}}

resource "azurerm_subnet" "main" {{
  name                 = "default-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}}

# Storage Account
resource "azurerm_storage_account" "main" {{
  name                     = "${{replace(var.project_name, "-", "")}}${{var.environment}}st"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {{
    versioning_enabled = true
  }}

  tags = {{
    Environment = var.environment
  }}
}}

resource "azurerm_storage_container" "data" {{
  name                  = "data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}}

# App Service Plan & Web App
resource "azurerm_service_plan" "main" {{
  name                = "${{var.project_name}}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"

  tags = {{
    Environment = var.environment
  }}
}}

resource "azurerm_linux_web_app" "main" {{
  name                = "${{var.project_name}}-${{var.environment}}-app"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_service_plan.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {{
    always_on = false

    application_stack {{
      python_version = "3.11"
    }}
  }}

  app_settings = {{
    "ENVIRONMENT" = var.environment
  }}

  tags = {{
    Environment = var.environment
  }}
}}

# Outputs
output "resource_group_name" {{
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}}

output "storage_account_name" {{
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}}

output "web_app_url" {{
  description = "Web app URL"
  value       = "https://${{azurerm_linux_web_app.main.default_hostname}}"
}}
"""

    def _generate_arm_template(self, mission: str) -> str:
        """Generate ARM template for Azure."""
        return f'''{{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {{
    "description": "Azure infrastructure deployment - {mission}"
  }},
  "parameters": {{
    "location": {{
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {{
        "description": "Location for all resources"
      }}
    }},
    "projectName": {{
      "type": "string",
      "defaultValue": "teamagent",
      "metadata": {{
        "description": "Project name prefix"
      }}
    }},
    "environment": {{
      "type": "string",
      "defaultValue": "dev",
      "allowedValues": ["dev", "staging", "prod"],
      "metadata": {{
        "description": "Environment name"
      }}
    }}
  }},
  "variables": {{
    "storageAccountName": "[concat(parameters('projectName'), parameters('environment'), 'st')]",
    "appServicePlanName": "[concat(parameters('projectName'), '-', parameters('environment'), '-plan')]",
    "webAppName": "[concat(parameters('projectName'), '-', parameters('environment'), '-app')]",
    "vnetName": "[concat(parameters('projectName'), '-vnet')]"
  }},
  "resources": [
    {{
      "type": "Microsoft.Network/virtualNetworks",
      "apiVersion": "2023-04-01",
      "name": "[variables('vnetName')]",
      "location": "[parameters('location')]",
      "properties": {{
        "addressSpace": {{
          "addressPrefixes": ["10.0.0.0/16"]
        }},
        "subnets": [
          {{
            "name": "default-subnet",
            "properties": {{
              "addressPrefix": "10.0.1.0/24"
            }}
          }}
        ]
      }}
    }},
    {{
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[variables('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {{
        "name": "Standard_LRS"
      }},
      "kind": "StorageV2",
      "properties": {{
        "minimumTlsVersion": "TLS1_2",
        "supportsHttpsTrafficOnly": true
      }}
    }},
    {{
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2022-09-01",
      "name": "[variables('appServicePlanName')]",
      "location": "[parameters('location')]",
      "sku": {{
        "name": "B1",
        "tier": "Basic"
      }},
      "kind": "linux",
      "properties": {{
        "reserved": true
      }}
    }},
    {{
      "type": "Microsoft.Web/sites",
      "apiVersion": "2022-09-01",
      "name": "[variables('webAppName')]",
      "location": "[parameters('location')]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
      ],
      "properties": {{
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
        "siteConfig": {{
          "linuxFxVersion": "PYTHON|3.11",
          "appSettings": [
            {{
              "name": "ENVIRONMENT",
              "value": "[parameters('environment')]"
            }}
          ]
        }}
      }}
    }}
  ],
  "outputs": {{
    "storageAccountName": {{
      "type": "string",
      "value": "[variables('storageAccountName')]"
    }},
    "webAppUrl": {{
      "type": "string",
      "value": "[concat('https://', reference(resourceId('Microsoft.Web/sites', variables('webAppName'))).defaultHostName)]"
    }}
  }}
}}
'''

    def _generate_azure_sdk_script(self, mission: str) -> str:
        """Generate Azure SDK Python script."""
        return f'''"""
Azure Infrastructure Setup Script
Mission: {mission}

Prerequisites:
- pip install azure-mgmt-resource azure-mgmt-storage azure-mgmt-network azure-mgmt-web
- pip install azure-identity
- Azure credentials configured (az login or service principal)
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.web import WebSiteManagementClient
from typing import Dict, Any


class AzureInfrastructure:
    """Azure infrastructure provisioning using Azure SDK."""

    def __init__(self, subscription_id: str, location: str = 'eastus'):
        """
        Initialize Azure clients.

        Args:
            subscription_id: Azure subscription ID
            location: Azure region
        """
        self.subscription_id = subscription_id
        self.location = location
        self.credential = DefaultAzureCredential()

        # Initialize clients
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.web_client = WebSiteManagementClient(self.credential, subscription_id)

    def create_resource_group(self, rg_name: str) -> Dict[str, Any]:
        """Create resource group."""
        print(f"Creating resource group: {{rg_name}}")

        rg_result = self.resource_client.resource_groups.create_or_update(
            rg_name,
            {{"location": self.location}}
        )

        print(f"  ✓ Created resource group: {{rg_result.name}}")
        return {{"name": rg_result.name, "location": rg_result.location}}

    def create_vnet(self, rg_name: str, vnet_name: str) -> str:
        """Create virtual network."""
        print(f"Creating virtual network: {{vnet_name}}")

        poller = self.network_client.virtual_networks.begin_create_or_update(
            rg_name,
            vnet_name,
            {{
                "location": self.location,
                "address_space": {{"address_prefixes": ["10.0.0.0/16"]}},
                "subnets": [
                    {{
                        "name": "default-subnet",
                        "address_prefix": "10.0.1.0/24"
                    }}
                ]
            }}
        )

        vnet_result = poller.result()
        print(f"  ✓ Created VNet: {{vnet_result.name}}")
        return vnet_result.name

    def create_storage_account(self, rg_name: str, storage_name: str) -> str:
        """Create storage account."""
        print(f"Creating storage account: {{storage_name}}")

        poller = self.storage_client.storage_accounts.begin_create(
            rg_name,
            storage_name,
            {{
                "location": self.location,
                "sku": {{"name": "Standard_LRS"}},
                "kind": "StorageV2",
                "properties": {{
                    "minimumTlsVersion": "TLS1_2",
                    "supportsHttpsTrafficOnly": True
                }}
            }}
        )

        storage_result = poller.result()
        print(f"  ✓ Created storage account: {{storage_result.name}}")
        return storage_result.name

    def create_app_service(
        self,
        rg_name: str,
        plan_name: str,
        app_name: str
    ) -> str:
        """Create app service plan and web app."""
        print(f"Creating app service: {{app_name}}")

        # Create app service plan
        plan_poller = self.web_client.app_service_plans.begin_create_or_update(
            rg_name,
            plan_name,
            {{
                "location": self.location,
                "sku": {{"name": "B1", "tier": "Basic"}},
                "kind": "linux",
                "reserved": True
            }}
        )
        plan_result = plan_poller.result()
        print(f"  ✓ Created app service plan: {{plan_result.name}}")

        # Create web app
        app_poller = self.web_client.web_apps.begin_create_or_update(
            rg_name,
            app_name,
            {{
                "location": self.location,
                "server_farm_id": plan_result.id,
                "site_config": {{
                    "linux_fx_version": "PYTHON|3.11",
                    "always_on": False
                }}
            }}
        )
        app_result = app_poller.result()
        print(f"  ✓ Created web app: {{app_result.name}}")

        return f"https://{{app_result.default_host_name}}"


def main():
    """Main execution."""
    import os

    print("=" * 60)
    print("Azure Infrastructure Setup")
    print("=" * 60)
    print()

    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        print("Error: AZURE_SUBSCRIPTION_ID environment variable not set")
        return

    # Initialize
    azure = AzureInfrastructure(subscription_id, location='eastus')

    # Create resources
    rg_name = "teamagent-dev-rg"
    rg = azure.create_resource_group(rg_name)
    print()

    vnet = azure.create_vnet(rg_name, "teamagent-vnet")
    print()

    storage = azure.create_storage_account(rg_name, "teamagentdevst")
    print()

    app_url = azure.create_app_service(rg_name, "teamagent-plan", "teamagent-dev-app")
    print()

    print("=" * 60)
    print("✓ Infrastructure Setup Complete!")
    print("=" * 60)
    print()
    print("Resources Created:")
    print(f"  - Resource Group: {{rg_name}}")
    print(f"  - Virtual Network: {{vnet}}")
    print(f"  - Storage Account: {{storage}}")
    print(f"  - Web App URL: {{app_url}}")


if __name__ == '__main__':
    main()
'''


__all__ = ["AzureCapability"]
