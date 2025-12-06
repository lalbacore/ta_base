#!/bin/bash
# Helper script to create PRs for current work
# Prerequisites: gh CLI installed and authenticated

set -e

echo "========================================="
echo "Team Agent - PR Creation Helper"
echo "========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated."
    echo "Run: gh auth login"
    exit 1
fi

echo "GitHub CLI is ready!"
echo ""

# Function to create PR
create_pr() {
    local branch=$1
    local title=$2
    local body=$3
    local labels=$4
    local template=$5

    echo "Creating PR: $title"
    echo "Branch: $branch"
    echo "Labels: $labels"
    echo ""

    # Check if branch exists
    if ! git rev-parse --verify "$branch" &> /dev/null; then
        echo "Warning: Branch $branch does not exist locally. Skipping..."
        echo ""
        return
    fi

    # Create PR
    gh pr create \
        --head "$branch" \
        --base develop \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        --template "$template" \
        || echo "Failed to create PR for $branch (may already exist)"

    echo ""
}

# PR #1: Fix registry JSON parsing error
create_pr \
    "fix/registry-json-parsing-error" \
    "fix(registry): Handle SQLAlchemy JSON column deserialization" \
    "Fixes 500 error on /api/registry/capabilities endpoint.

SQLAlchemy JSON columns auto-deserialize to Python lists, but code was attempting json.loads() on already-deserialized data. Added type checking to handle both cases (list vs JSON string).

**Changes:**
- backend/app/services/registry_service.py (lines 56-57)

**Testing:**
- Manual: curl http://localhost:5002/api/registry/capabilities
- Frontend: Verify registry view loads without console errors

**Fixes:** 500 error on capability registry endpoint" \
    "bug,backend,api,priority:high" \
    "bug_fix.md"

# PR #2: Cleanup duplicate agents script
create_pr \
    "chore/cleanup-duplicate-agents" \
    "chore(agents): Add cleanup script for duplicate agent entries" \
    "Adds database cleanup utility to remove duplicate agent entries created from multiple backend restarts.

**Changes:**
- scripts/cleanup_duplicate_agents.py (new file, 120 lines)

**Testing:**
- Run script: python scripts/cleanup_duplicate_agents.py
- Verify agents reduced from 35 → 9
- Verify no unintended deletions

**Result:**
- 4 role agents: Architect, Critic, Recorder, Governance
- 5 specialist agents: Legal, AWS, Azure, GCP, OCI" \
    "chore,tooling,database,priority:medium" \
    "feature.md"

# PR #3: Decentralized marketplace architecture documentation
create_pr \
    "docs/decentralized-marketplace-vision" \
    "docs: Add decentralized marketplace architecture plan" \
    "Comprehensive architecture plan for evolving Team Agent into a decentralized agent marketplace on Ethereum Optimism L2.

**Changes:**
- docs/DECENTRALIZED_MARKETPLACE_VISION.md (new file, 1,200+ lines)
- docs/GITHUB_WORKFLOW.md (new file, 600+ lines)

**Key Sections:**
- Current state (Phase 1: Foundation)
- Agent2Agent (A2A) protocol implementation
- Model Context Protocol (MCP) server completion
- Ethereum Optimism L2 smart contract architecture (3 contracts + DAO)
- IPFS artifact storage integration
- Flexible payment system (ETH, OP, USDC, TEAM tokens, custom value stores)
- Research assistant platform for academic use cases
- 36-week phased implementation roadmap

**Strategic Direction:**
Sets the roadmap for Team Agent's evolution into a decentralized marketplace where autonomous agents can discover each other, collaborate, build reputation, and transact value through flexible payment systems." \
    "documentation,architecture,planning,priority:high" \
    "feature.md"

# PR #4: Cloud specialists (AWS, Azure, GCP, OCI)
create_pr \
    "feat/cloud-specialists-aws-azure-gcp-oci" \
    "feat(specialists): Add cloud infrastructure specialists for AWS, Azure, GCP, OCI" \
    "Implements four cloud specialist agents with capabilities for provisioning infrastructure on AWS, Azure, GCP, and OCI.

**Specialists:**
- AWS: Terraform, CloudFormation, boto3 (EC2, S3, Lambda, RDS, etc.)
- Azure: Terraform, ARM templates, Azure SDK (VMs, Storage, Functions, etc.)
- GCP: Terraform, Deployment Manager, gcloud (Compute, Storage, Functions, etc.)
- OCI: Terraform, OCI CLI, OCI SDK (Compute, Storage, Functions, etc.)

**Changes:**
- swarms/team_agent/capabilities/cloud/ (4 capability files, 1,600+ lines)
- swarms/team_agent/specialists/ (4 specialist files, 450+ lines)
- swarms/team_agent/orchestrator.py (registration logic)
- swarms/team_agent/agent_manager.py (specialist registration methods)

**Features:**
- Auto-discovered by DynamicBuilder keyword matching
- Registered in agent_cards database
- Mapped to capabilities in capability_registry
- Supports complete infrastructure provisioning workflows

**Example Usage:**
\`\`\`python
mission = \"Deploy a scalable web application on AWS with auto-scaling\"
# → AWS Specialist selected
# → Generates Terraform + CloudFormation + boto3 code
\`\`\`" \
    "feature,specialists,cloud,aws,azure,gcp,oci,size:large" \
    "feature.md"

echo ""
echo "========================================="
echo "PR creation process complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review PRs on GitHub"
echo "2. Address any reviewer comments"
echo "3. Merge approved PRs"
echo ""
