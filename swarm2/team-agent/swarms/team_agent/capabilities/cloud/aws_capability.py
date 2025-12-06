"""
AWS Cloud Infrastructure Capability.

Generates Infrastructure-as-Code and SDK scripts for AWS services including:
- Compute (EC2, Lambda, ECS, EKS)
- Storage (S3, EBS, EFS)
- Databases (RDS, DynamoDB, ElastiCache)
- Networking (VPC, CloudFront, Route53)
- Security (IAM, KMS, Secrets Manager)
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class AWSCapability(BaseCapability):
    """
    AWS cloud infrastructure capability.

    Generates Terraform/CloudFormation templates and boto3 SDK scripts
    for provisioning and managing AWS resources.
    """

    def get_metadata(self) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "name": "aws_cloud_infrastructure",
            "display_name": "AWS Cloud Infrastructure",
            "type": "cloud_infrastructure",
            "domains": ["aws", "cloud", "infrastructure", "devops", "terraform"],
            "description": (
                "Generate Infrastructure-as-Code (Terraform, CloudFormation) and "
                "boto3 SDK scripts for AWS services. Supports EC2, Lambda, S3, RDS, "
                "VPC, IAM, and more."
            ),
            "version": "1.0.0",
            "module_path": "swarms.team_agent.capabilities.cloud.aws_capability"
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AWS infrastructure code.

        Args:
            context: dict with:
                - mission: str - Description of AWS infrastructure to create
                - architecture: str - Optional architecture design

        Returns:
            dict with:
                - content: str - Generated infrastructure code
                - artifacts: list - Code files (Terraform, CloudFormation, boto3)
                - metadata: dict - Capability metadata
        """
        mission = context.get("mission", "")
        architecture = context.get("architecture", "")

        # Determine infrastructure type from mission
        mission_lower = mission.lower()

        # Select appropriate IaC tool and generate code
        if any(kw in mission_lower for kw in ["terraform", "tf", "hcl"]):
            code = self._generate_terraform(mission, architecture)
            filename = "main.tf"
        elif any(kw in mission_lower for kw in ["cloudformation", "cfn", "cloud formation"]):
            code = self._generate_cloudformation(mission, architecture)
            filename = "template.yaml"
        else:
            # Default to boto3 SDK script
            code = self._generate_boto3_script(mission, architecture)
            filename = "aws_setup.py"

        return {
            "content": code,
            "artifacts": [{
                "type": "infrastructure",
                "name": "aws_infrastructure",
                "filename": filename,
                "content": code
            }],
            "metadata": self.metadata
        }

    def _generate_terraform(self, mission: str, architecture: str) -> str:
        """Generate Terraform configuration for AWS."""
        mission_lower = mission.lower()

        # Detect required resources
        resources = []

        if any(kw in mission_lower for kw in ["ec2", "instance", "server", "vm"]):
            resources.append(self._tf_ec2_instance())

        if any(kw in mission_lower for kw in ["s3", "bucket", "storage"]):
            resources.append(self._tf_s3_bucket())

        if any(kw in mission_lower for kw in ["lambda", "function", "serverless"]):
            resources.append(self._tf_lambda_function())

        if any(kw in mission_lower for kw in ["rds", "database", "mysql", "postgres"]):
            resources.append(self._tf_rds_instance())

        if any(kw in mission_lower for kw in ["vpc", "network", "subnet"]):
            resources.append(self._tf_vpc())

        # Default to basic infrastructure if no keywords matched
        if not resources:
            resources = [
                self._tf_vpc(),
                self._tf_s3_bucket(),
                self._tf_ec2_instance()
            ]

        terraform_code = f"""# AWS Infrastructure - Terraform Configuration
# Mission: {mission}

terraform {{
  required_version = ">= 1.0"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region

  default_tags {{
    tags = {{
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }}
  }}
}}

# Variables
variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "dev"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "team-agent-infra"
}}

{chr(10).join(resources)}

# Outputs
output "infrastructure_summary" {{
  description = "Summary of created infrastructure"
  value = {{
    region      = var.aws_region
    environment = var.environment
    project     = var.project_name
  }}
}}
"""
        return terraform_code

    def _tf_vpc(self) -> str:
        """Terraform VPC configuration."""
        return """
# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
    Type = "public"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
"""

    def _tf_s3_bucket(self) -> str:
        """Terraform S3 bucket configuration."""
        return """
# S3 Bucket for storage
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-${var.environment}-data"

  tags = {
    Name = "${var.project_name}-data-bucket"
  }
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
"""

    def _tf_ec2_instance(self) -> str:
        """Terraform EC2 instance configuration."""
        return """
# EC2 Instance
resource "aws_security_group" "instance" {
  name        = "${var.project_name}-instance-sg"
  description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "${var.project_name}-instance-sg"
  }
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "main" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public[0].id

  vpc_security_group_ids = [aws_security_group.instance.id]

  tags = {
    Name = "${var.project_name}-instance"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              EOF
}

output "instance_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.main.public_ip
}
"""

    def _tf_lambda_function(self) -> str:
        """Terraform Lambda function configuration."""
        return """
# Lambda Function
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "main" {
  filename      = "lambda_function.zip"
  function_name = "${var.project_name}-function"
  role          = aws_iam_role.lambda.arn
  handler       = "index.handler"
  runtime       = "python3.11"

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-lambda"
  }
}

output "lambda_function_arn" {
  description = "ARN of Lambda function"
  value       = aws_lambda_function.main.arn
}
"""

    def _tf_rds_instance(self) -> str:
        """Terraform RDS instance configuration."""
        return """
# RDS Database
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.public[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS instance"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "PostgreSQL access from VPC"
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "aws_db_instance" "main" {
  identifier           = "${var.project_name}-db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true

  db_name  = "appdb"
  username = "admin"
  password = var.db_password  # Set via terraform.tfvars or environment variable

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  skip_final_snapshot = true

  tags = {
    Name = "${var.project_name}-postgres"
  }
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}
"""

    def _generate_cloudformation(self, mission: str, architecture: str) -> str:
        """Generate CloudFormation template."""
        return f"""# AWS Infrastructure - CloudFormation Template
# Mission: {mission}

AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation stack for {mission}'

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Environment name

  ProjectName:
    Type: String
    Default: team-agent-infra
    Description: Project name for resource naming

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-vpc'
        - Key: Environment
          Value: !Ref Environment

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-public-subnet'

  # Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${{ProjectName}}-public-rt'

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  # S3 Bucket
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${{ProjectName}}-${{Environment}}-data'
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${{AWS::StackName}}-VPC'

  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${{AWS::StackName}}-PublicSubnet'

  DataBucketName:
    Description: S3 Data Bucket Name
    Value: !Ref DataBucket
    Export:
      Name: !Sub '${{AWS::StackName}}-DataBucket'
"""

    def _generate_boto3_script(self, mission: str, architecture: str) -> str:
        """Generate boto3 SDK script."""
        return f'''"""
AWS Infrastructure Setup Script
Mission: {mission}

Prerequisites:
- pip install boto3
- AWS credentials configured (aws configure or environment variables)
"""

import boto3
import json
from typing import Dict, Any


class AWSInfrastructure:
    """AWS infrastructure provisioning using boto3."""

    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize AWS clients.

        Args:
            region: AWS region
        """
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.iam = boto3.client('iam')
        self.lambda_client = boto3.client('lambda', region_name=region)

    def create_vpc(self, vpc_name: str = 'team-agent-vpc') -> Dict[str, Any]:
        """Create VPC with public subnet."""
        print(f"Creating VPC: {{vpc_name}}")

        # Create VPC
        vpc_response = self.ec2.create_vpc(
            CidrBlock='10.0.0.0/16',
            TagSpecifications=[{{
                'ResourceType': 'vpc',
                'Tags': [{{'Key': 'Name', 'Value': vpc_name}}]
            }}]
        )
        vpc_id = vpc_response['Vpc']['VpcId']
        print(f"  ✓ Created VPC: {{vpc_id}}")

        # Enable DNS hostnames
        self.ec2.modify_vpc_attribute(
            VpcId=vpc_id,
            EnableDnsHostnames={{'Value': True}}
        )

        # Create Internet Gateway
        igw_response = self.ec2.create_internet_gateway(
            TagSpecifications=[{{
                'ResourceType': 'internet-gateway',
                'Tags': [{{'Key': 'Name', 'Value': f'{{vpc_name}}-igw'}}]
            }}]
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        print(f"  ✓ Created Internet Gateway: {{igw_id}}")

        # Attach IGW to VPC
        self.ec2.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )

        # Create public subnet
        subnet_response = self.ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock='10.0.1.0/24',
            TagSpecifications=[{{
                'ResourceType': 'subnet',
                'Tags': [{{'Key': 'Name', 'Value': f'{{vpc_name}}-public'}}]
            }}]
        )
        subnet_id = subnet_response['Subnet']['SubnetId']
        print(f"  ✓ Created Subnet: {{subnet_id}}")

        # Create route table
        rt_response = self.ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[{{
                'ResourceType': 'route-table',
                'Tags': [{{'Key': 'Name', 'Value': f'{{vpc_name}}-public-rt'}}]
            }}]
        )
        rt_id = rt_response['RouteTable']['RouteTableId']

        # Add route to internet
        self.ec2.create_route(
            RouteTableId=rt_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )

        # Associate route table with subnet
        self.ec2.associate_route_table(
            RouteTableId=rt_id,
            SubnetId=subnet_id
        )
        print(f"  ✓ Configured routing")

        return {{
            'vpc_id': vpc_id,
            'subnet_id': subnet_id,
            'internet_gateway_id': igw_id,
            'route_table_id': rt_id
        }}

    def create_s3_bucket(self, bucket_name: str) -> str:
        """Create S3 bucket with encryption and versioning."""
        print(f"Creating S3 bucket: {{bucket_name}}")

        try:
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={{'LocationConstraint': self.region}}
                )

            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={{'Status': 'Enabled'}}
            )

            # Enable encryption
            self.s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={{
                    'Rules': [{{
                        'ApplyServerSideEncryptionByDefault': {{
                            'SSEAlgorithm': 'AES256'
                        }}
                    }}]
                }}
            )

            # Block public access
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={{
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }}
            )

            print(f"  ✓ Created S3 bucket with encryption and versioning")
            return bucket_name

        except Exception as e:
            print(f"  ✗ Error creating bucket: {{e}}")
            raise

    def launch_ec2_instance(
        self,
        subnet_id: str,
        instance_name: str = 'team-agent-instance',
        instance_type: str = 't3.micro'
    ) -> str:
        """Launch EC2 instance."""
        print(f"Launching EC2 instance: {{instance_name}}")

        # Get latest Amazon Linux 2 AMI
        images = self.ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {{'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']}},
                {{'Name': 'state', 'Values': ['available']}}
            ],
            MaxResults=1
        )
        ami_id = images['Images'][0]['ImageId']

        # Launch instance
        response = self.ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            SubnetId=subnet_id,
            TagSpecifications=[{{
                'ResourceType': 'instance',
                'Tags': [{{'Key': 'Name', 'Value': instance_name}}]
            }}]
        )

        instance_id = response['Instances'][0]['InstanceId']
        print(f"  ✓ Launched instance: {{instance_id}}")

        return instance_id


def main():
    """Main execution."""
    print("=" * 60)
    print("AWS Infrastructure Setup")
    print("=" * 60)
    print()

    # Initialize
    aws = AWSInfrastructure(region='us-east-1')

    # Create VPC
    vpc_info = aws.create_vpc('team-agent-vpc')
    print()

    # Create S3 bucket
    bucket_name = f"team-agent-data-{{aws.region}}"
    aws.create_s3_bucket(bucket_name)
    print()

    # Launch EC2 instance
    instance_id = aws.launch_ec2_instance(
        subnet_id=vpc_info['subnet_id'],
        instance_name='team-agent-server'
    )
    print()

    print("=" * 60)
    print("✓ Infrastructure Setup Complete!")
    print("=" * 60)
    print()
    print("Resources Created:")
    print(f"  - VPC: {{vpc_info['vpc_id']}}")
    print(f"  - Subnet: {{vpc_info['subnet_id']}}")
    print(f"  - S3 Bucket: {{bucket_name}}")
    print(f"  - EC2 Instance: {{instance_id}}")


if __name__ == '__main__':
    main()
'''


# Module exports
__all__ = ["AWSCapability"]
