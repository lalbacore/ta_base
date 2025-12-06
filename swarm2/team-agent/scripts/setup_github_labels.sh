#!/bin/bash
# Setup GitHub labels for Team Agent repository
# Run this script once to create all standardized labels

set -e

cd "$(dirname "$0")/.."

echo "========================================="
echo "Team Agent - GitHub Labels Setup"
echo "========================================="
echo ""

# Check if in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Type labels
echo "Creating type labels..."
gh label create "bug" --color "d73a4a" --description "Something isn't working" --force
gh label create "feature" --color "0075ca" --description "New feature or enhancement" --force
gh label create "documentation" --color "0075ca" --description "Documentation only changes" --force
gh label create "refactor" --color "fbca04" --description "Code refactoring" --force
gh label create "test" --color "0e8a16" --description "Test additions/improvements" --force
gh label create "chore" --color "fef2c0" --description "Maintenance, tooling, dependencies" --force
gh label create "performance" --color "c5def5" --description "Performance improvements" --force

# Priority labels
echo "Creating priority labels..."
gh label create "priority:critical" --color "b60205" --description "Blocks production, immediate attention" --force
gh label create "priority:high" --color "d93f0b" --description "Important, should be addressed soon" --force
gh label create "priority:medium" --color "fbca04" --description "Normal priority" --force
gh label create "priority:low" --color "0e8a16" --description "Nice to have" --force

# Component labels
echo "Creating component labels..."
gh label create "backend" --color "c5def5" --description "Backend/API changes" --force
gh label create "frontend" --color "c5def5" --description "Frontend/UI changes" --force
gh label create "database" --color "c5def5" --description "Database schema or queries" --force
gh label create "specialists" --color "c5def5" --description "Specialist agents" --force
gh label create "capabilities" --color "c5def5" --description "Capability system" --force
gh label create "orchestrator" --color "c5def5" --description "Orchestrator logic" --force
gh label create "pki" --color "c5def5" --description "PKI/crypto infrastructure" --force
gh label create "blockchain" --color "c5def5" --description "Blockchain integration" --force
gh label create "api" --color "c5def5" --description "API endpoints" --force

# Cloud provider labels
echo "Creating cloud provider labels..."
gh label create "aws" --color "ff9900" --description "AWS-related" --force
gh label create "azure" --color "0078d4" --description "Azure-related" --force
gh label create "gcp" --color "4285f4" --description "GCP-related" --force
gh label create "oci" --color "f80000" --description "OCI-related" --force
gh label create "cloud" --color "d4c5f9" --description "Cloud infrastructure" --force

# Size labels
echo "Creating size labels..."
gh label create "size:xs" --color "ededed" --description "< 50 lines changed" --force
gh label create "size:small" --color "ededed" --description "50-200 lines changed" --force
gh label create "size:medium" --color "ededed" --description "200-500 lines changed" --force
gh label create "size:large" --color "ededed" --description "500-1000 lines changed" --force
gh label create "size:xl" --color "ededed" --description "> 1000 lines changed" --force

# Status labels
echo "Creating status labels..."
gh label create "status:in-progress" --color "1d76db" --description "Currently being worked on" --force
gh label create "status:blocked" --color "b60205" --description "Blocked by another issue/PR" --force
gh label create "status:needs-review" --color "0e8a16" --description "Ready for code review" --force
gh label create "status:needs-testing" --color "fbca04" --description "Needs QA testing" --force
gh label create "status:approved" --color "0e8a16" --description "Approved, ready to merge" --force

# Special labels
echo "Creating special labels..."
gh label create "needs-triage" --color "d876e3" --description "Needs initial triage and prioritization" --force
gh label create "good-first-issue" --color "7057ff" --description "Good for newcomers" --force
gh label create "help-wanted" --color "008672" --description "Extra attention is needed" --force
gh label create "breaking-change" --color "b60205" --description "Breaking change" --force
gh label create "security" --color "ee0701" --description "Security-related" --force

# Architecture/planning labels
echo "Creating architecture labels..."
gh label create "architecture" --color "5319e7" --description "Architectural decisions and planning" --force
gh label create "planning" --color "5319e7" --description "Planning and roadmap" --force

echo ""
echo "========================================="
echo "✓ All labels created successfully!"
echo "========================================="
echo ""
echo "Labels created:"
echo "- Type labels (7): bug, feature, documentation, refactor, test, chore, performance"
echo "- Priority labels (4): critical, high, medium, low"
echo "- Component labels (9): backend, frontend, database, specialists, capabilities, etc."
echo "- Cloud labels (5): aws, azure, gcp, oci, cloud"
echo "- Size labels (5): xs, small, medium, large, xl"
echo "- Status labels (5): in-progress, blocked, needs-review, needs-testing, approved"
echo "- Special labels (5): needs-triage, good-first-issue, help-wanted, breaking-change, security"
echo "- Architecture labels (2): architecture, planning"
echo ""
echo "Total: 42 labels"
echo ""
