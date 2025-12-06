# Team Agent GitHub Workflow & PR Strategy

**Date:** December 6, 2025
**Purpose:** Centralized management of features, bug fixes, and architectural enhancements

---

## Branch Strategy

```
main (production-ready)
  ├── develop (integration branch)
  │   ├── feat/feature-name (new features)
  │   ├── fix/bug-description (bug fixes)
  │   ├── docs/documentation-topic (documentation)
  │   ├── refactor/component-name (code refactoring)
  │   └── chore/maintenance-task (tooling, deps)
  └── hotfix/critical-bug (emergency production fixes)
```

### Branch Naming Conventions

- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring (no behavior change)
- `chore/` - Dependencies, tooling, maintenance
- `test/` - Test additions/improvements
- `perf/` - Performance improvements
- `hotfix/` - Critical production fixes

**Examples:**
- `feat/a2a-protocol-implementation`
- `fix/registry-json-parsing-error`
- `docs/decentralized-marketplace-vision`
- `refactor/orchestrator-specialist-registration`

---

## PR Organization for Current Work

### PR #1: fix/registry-json-parsing-error
**Type:** Bug Fix
**Priority:** High
**Size:** Small

**Description:**
Fixes 500 error on `/api/registry/capabilities` endpoint caused by attempting to JSON parse SQLAlchemy columns that are already deserialized.

**Changes:**
- `backend/app/services/registry_service.py` (lines 56-57)

**Testing:**
- Manual: `curl http://localhost:5002/api/registry/capabilities`
- Frontend: Verify registry view loads without console errors

**Labels:** `bug`, `backend`, `api`, `priority:high`

**Commit Message:**
```
fix(registry): Handle SQLAlchemy JSON column deserialization

SQLAlchemy JSON columns auto-deserialize to Python lists, but code was
attempting json.loads() on already-deserialized data. Added type checking
to handle both cases (list vs JSON string).

Fixes #XX (500 error on capability registry endpoint)
```

---

### PR #2: chore/cleanup-duplicate-agents-script
**Type:** Maintenance
**Priority:** Medium
**Size:** Small

**Description:**
Adds database cleanup utility to remove duplicate agent entries created from multiple backend restarts.

**Changes:**
- `scripts/cleanup_duplicate_agents.py` (new file, 120 lines)

**Testing:**
- Run script: `python scripts/cleanup_duplicate_agents.py`
- Verify agents reduced from 35 → 9
- Verify no unintended deletions

**Labels:** `chore`, `tooling`, `database`, `priority:medium`

**Commit Message:**
```
chore(agents): Add cleanup script for duplicate agent entries

Multiple backend restarts created duplicate specialist agents with
different UUIDs. Script identifies duplicates by (agent_type, agent_name)
and keeps the most recent instance.

Reduces database clutter and ensures clean agent registry state.
```

---

### PR #3: docs/decentralized-marketplace-architecture
**Type:** Documentation
**Priority:** High (Planning)
**Size:** Large

**Description:**
Comprehensive architecture plan for evolving Team Agent into a decentralized agent marketplace on Ethereum Optimism L2.

**Changes:**
- `docs/DECENTRALIZED_MARKETPLACE_VISION.md` (new file, 1,200+ lines)

**Key Sections:**
- Current state (Phase 1: Foundation)
- Agent2Agent (A2A) protocol implementation
- Model Context Protocol (MCP) server completion
- Ethereum Optimism L2 smart contract architecture
- Flexible payment system (multi-token support)
- Research assistant platform
- 36-week implementation roadmap

**Labels:** `documentation`, `architecture`, `planning`, `priority:high`

**Commit Message:**
```
docs: Add decentralized marketplace architecture plan

Comprehensive vision document covering:
- A2A protocol for agent discovery
- MCP server for external invocations
- Ethereum Optimism L2 smart contracts (3 contracts + DAO)
- IPFS artifact storage
- Flexible payment system (ETH, OP, USDC, custom tokens)
- Research assistant platform for academic use cases
- 36-week phased implementation roadmap

Sets strategic direction for Team Agent evolution into decentralized
agent marketplace.
```

---

### PR #4: feat/cloud-specialists-aws-azure-gcp-oci
**Type:** Feature
**Priority:** Medium
**Size:** Large (already implemented, needs PR)

**Description:**
Adds four cloud infrastructure specialist agents with capabilities for provisioning AWS, Azure, GCP, and OCI resources.

**Changes:**
- `swarms/team_agent/capabilities/cloud/__init__.py` (new)
- `swarms/team_agent/capabilities/cloud/aws_capability.py` (new, 586 lines)
- `swarms/team_agent/capabilities/cloud/azure_capability.py` (new, 279 lines)
- `swarms/team_agent/capabilities/cloud/gcp_capability.py` (new, 336 lines)
- `swarms/team_agent/capabilities/cloud/oci_capability.py` (new, 400+ lines)
- `swarms/team_agent/specialists/aws_specialist.py` (new, 115 lines)
- `swarms/team_agent/specialists/azure_specialist.py` (new, 109 lines)
- `swarms/team_agent/specialists/gcp_specialist.py` (new, 109 lines)
- `swarms/team_agent/specialists/oci_specialist.py` (new, 120+ lines)
- `swarms/team_agent/specialists/__init__.py` (updated exports)
- `swarms/team_agent/orchestrator.py` (registration logic)
- `swarms/team_agent/agent_manager.py` (specialist registration methods)

**Testing:**
- Unit tests for each capability
- Integration tests for specialist registration
- Example missions for each cloud provider

**Labels:** `feature`, `specialists`, `cloud`, `aws`, `azure`, `gcp`, `oci`, `size:large`

**Commit Message:**
```
feat(specialists): Add cloud infrastructure specialists for AWS, Azure, GCP, OCI

Implements four cloud specialist agents with capabilities for:
- AWS: Terraform, CloudFormation, boto3 (EC2, S3, Lambda, RDS, etc.)
- Azure: Terraform, ARM templates, Azure SDK (VMs, Storage, Functions, etc.)
- GCP: Terraform, Deployment Manager, gcloud (Compute, Storage, Functions, etc.)
- OCI: Terraform, OCI CLI, OCI SDK (Compute, Storage, Functions, etc.)

Each specialist:
- Registered in agent_cards database
- Mapped to primary capability in capability_registry
- Auto-discovered by DynamicBuilder keyword matching
- Supports complete infrastructure provisioning workflows

Example usage:
  mission = "Deploy a scalable web application on AWS with auto-scaling"
  # → AWS Specialist selected
  # → Generates Terraform + CloudFormation + boto3 code
```

---

## PR Templates

### Bug Fix Template

```markdown
## Description
Brief description of the bug and the fix.

## Root Cause
What caused the bug?

## Changes
- List of files changed
- Summary of modifications

## Testing
- [ ] Manual testing performed
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] No regressions introduced

## Related Issues
Fixes #XX
Relates to #YY

## Screenshots (if applicable)
Before/after screenshots
```

### Feature Template

```markdown
## Description
What does this feature do?

## Motivation
Why is this feature needed?

## Implementation Details
High-level overview of implementation approach

## Changes
- List of files changed
- Summary of modifications

## Testing
- [ ] Unit tests added (coverage: XX%)
- [ ] Integration tests added
- [ ] Example usage documented
- [ ] Manual testing completed

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] Example code provided

## Breaking Changes
List any breaking changes (if applicable)

## Related Issues
Closes #XX
Relates to #YY
```

### Documentation Template

```markdown
## Description
What documentation is being added/updated?

## Changes
- List of documentation files

## Review Checklist
- [ ] Accurate and up-to-date
- [ ] Clear and concise
- [ ] Examples provided
- [ ] Links verified
- [ ] Spelling/grammar checked

## Related Issues
Closes #XX
```

---

## GitHub Labels

### Type Labels
- `bug` - Something isn't working
- `feature` - New feature or enhancement
- `documentation` - Documentation only
- `refactor` - Code refactoring
- `test` - Test additions/improvements
- `chore` - Maintenance, tooling, dependencies
- `performance` - Performance improvements

### Priority Labels
- `priority:critical` - Blocks production, immediate attention
- `priority:high` - Important, should be addressed soon
- `priority:medium` - Normal priority
- `priority:low` - Nice to have

### Component Labels
- `backend` - Backend/API changes
- `frontend` - Frontend/UI changes
- `database` - Database schema or queries
- `specialists` - Specialist agents
- `capabilities` - Capability system
- `orchestrator` - Orchestrator logic
- `pki` - PKI/crypto infrastructure
- `blockchain` - Blockchain integration
- `api` - API endpoints

### Size Labels
- `size:xs` - < 50 lines changed
- `size:small` - 50-200 lines changed
- `size:medium` - 200-500 lines changed
- `size:large` - 500-1000 lines changed
- `size:xl` - > 1000 lines changed

### Status Labels
- `status:in-progress` - Currently being worked on
- `status:blocked` - Blocked by another issue/PR
- `status:needs-review` - Ready for code review
- `status:needs-testing` - Needs QA testing
- `status:approved` - Approved, ready to merge

---

## Milestones

### Milestone: v1.1 - Foundation & Bug Fixes
**Due:** December 20, 2025
**Goal:** Stabilize current functionality, fix known bugs

**Issues/PRs:**
- PR #1: fix/registry-json-parsing-error
- PR #2: chore/cleanup-duplicate-agents-script
- Issue #XX: Fix certificate rotation edge cases
- Issue #XX: Improve error handling in DynamicBuilder

---

### Milestone: v1.2 - Cloud Specialists
**Due:** January 15, 2026
**Goal:** Complete cloud infrastructure capabilities

**Issues/PRs:**
- PR #4: feat/cloud-specialists-aws-azure-gcp-oci
- Issue #XX: Add cloud specialist unit tests
- Issue #XX: Cloud specialist documentation
- Issue #XX: Example missions for each cloud provider

---

### Milestone: v2.0 - Agent Discovery & Interoperability (Phase 2)
**Due:** February 15, 2026
**Goal:** A2A protocol and MCP server implementation

**Epic Issues:**
- Issue #XX: A2A Protocol Implementation
  - [ ] `.well-known/agent.json` endpoint
  - [ ] A2A agent card schema
  - [ ] A2A client library
  - [ ] Agent card signing with PKI

- Issue #XX: MCP Server Completion
  - [ ] HTTP endpoints (list tools, invoke)
  - [ ] WebSocket streaming support
  - [ ] API key authentication
  - [ ] Tool execution routing

- Issue #XX: External Discovery
  - [ ] Agent discovery from remote instances
  - [ ] Capability matching algorithms
  - [ ] Integration tests

---

### Milestone: v3.0 - Ethereum Optimism L2 Integration (Phase 3)
**Due:** June 15, 2026
**Goal:** Blockchain-based workflow execution and marketplace

**Epic Issues:**
- Issue #XX: Smart Contract Development
  - [ ] WorkflowConductor.sol
  - [ ] CapabilityMarketplace.sol
  - [ ] ReputationDAO.sol
  - [ ] PaymentRouter.sol
  - [ ] CustomValueRegistry.sol
  - [ ] Unit tests (Hardhat/Foundry)
  - [ ] Security audit

- Issue #XX: IPFS Integration
  - [ ] IPFS client implementation
  - [ ] Pinata/Web3.Storage integration
  - [ ] Artifact upload/retrieval
  - [ ] Pinning service automation

- Issue #XX: Blockchain Client
  - [ ] Optimism RPC client
  - [ ] Workflow submission
  - [ ] Event listeners
  - [ ] Payment automation

---

### Milestone: v4.0 - Research Assistant Platform (Phase 5)
**Due:** September 15, 2026
**Goal:** Academic and research use cases

**Epic Issues:**
- Issue #XX: Research Specialists
  - [ ] Literature Review Agent
  - [ ] Data Analysis Agent
  - [ ] Experiment Design Agent
  - [ ] Grant Writing Agent
  - [ ] Lab Automation Agent

- Issue #XX: Research Payment Models
  - [ ] Institution credits
  - [ ] Grant-funded workflows
  - [ ] Open science bounties

- Issue #XX: Research Documentation
  - [ ] Use case examples
  - [ ] Academic API integrations
  - [ ] Researcher onboarding guide

---

## GitHub Projects Board

### Kanban Board Structure

**Columns:**
1. **Backlog** - All open issues/PRs not yet prioritized
2. **To Do** - Prioritized and ready for work
3. **In Progress** - Actively being worked on
4. **In Review** - Code review in progress
5. **QA Testing** - Needs testing before merge
6. **Done** - Merged to develop/main

**Automation Rules:**
- New PR → "In Review" column
- PR approved → "QA Testing" column
- PR merged → "Done" column
- Issue assigned → "In Progress" column

---

## Example Project Board Setup

### Project: Decentralized Marketplace
**Description:** Evolution of Team Agent into decentralized agent marketplace on Optimism L2

**Columns:**

#### Backlog
- #XX: PaymentRouter.sol implementation
- #XX: CustomValueRegistry.sol implementation
- #XX: Research payment models
- #XX: Lab Automation Agent

#### To Do
- PR #3: docs/decentralized-marketplace-architecture
- #XX: A2A protocol specification
- #XX: MCP server API design

#### In Progress
- PR #1: fix/registry-json-parsing-error
- PR #4: feat/cloud-specialists-aws-azure-gcp-oci

#### In Review
- (empty)

#### QA Testing
- (empty)

#### Done
- PR #2: chore/cleanup-duplicate-agents-script
- PR #31: Complete PKI signing implementation
- PR #32: Phase 1 Frontend & Backend

---

## PR Workflow

### 1. Create Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feat/a2a-protocol-implementation
```

### 2. Implement Feature
```bash
# Make changes
git add .
git commit -m "feat(a2a): implement agent card endpoint"
```

### 3. Push Branch
```bash
git push origin feat/a2a-protocol-implementation
```

### 4. Create Pull Request
```bash
# Via GitHub UI or gh CLI
gh pr create \
  --title "feat: A2A Protocol Implementation - Agent Discovery" \
  --body-file .github/PULL_REQUEST_TEMPLATE/feature.md \
  --base develop \
  --label "feature,backend,api,priority:high,size:large"
```

### 5. Code Review
- Address reviewer comments
- Push additional commits
- Request re-review

### 6. Merge
```bash
# Squash and merge for clean history
gh pr merge --squash --delete-branch
```

---

## Commit Message Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Scopes:**
- `orchestrator`, `agents`, `specialists`, `capabilities`
- `backend`, `frontend`, `api`
- `blockchain`, `ipfs`, `pki`
- `database`, `tests`, `docs`

**Examples:**
```
feat(a2a): implement agent card discovery endpoint

Adds /.well-known/agent.json endpoint for A2A protocol compliance.
Returns all active specialist agents with capabilities, pricing,
and reputation metadata.

Closes #42
```

```
fix(registry): handle SQLAlchemy JSON column deserialization

SQLAlchemy JSON columns auto-deserialize to lists, but code attempted
json.loads() on already-deserialized data. Added type checking.

Fixes #38
```

---

## Release Process

### 1. Version Bump
```bash
# Update version in setup.py, package.json
git checkout develop
git pull origin develop
git checkout -b release/v2.0.0
# Update versions
git commit -m "chore: bump version to 2.0.0"
```

### 2. Create Release PR
```bash
gh pr create \
  --title "Release v2.0.0 - Agent Discovery & Interoperability" \
  --base main \
  --body "Release notes..."
```

### 3. Merge to Main
```bash
gh pr merge --merge
git checkout main
git pull origin main
git tag v2.0.0
git push origin v2.0.0
```

### 4. GitHub Release
```bash
gh release create v2.0.0 \
  --title "v2.0.0 - Agent Discovery & Interoperability" \
  --notes-file docs/RELEASE_NOTES_v2.0.0.md
```

### 5. Sync Develop
```bash
git checkout develop
git merge main
git push origin develop
```

---

## Recommended GitHub Actions Workflows

### 1. PR Checks (.github/workflows/pr-checks.yml)
```yaml
name: PR Checks

on:
  pull_request:
    branches: [develop, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pylint black isort mypy
      - name: Run linters
        run: |
          black --check swarms/ utils/ backend/
          isort --check swarms/ utils/ backend/
          pylint swarms/ utils/ backend/
          mypy swarms/ utils/ backend/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest utils/tests/ -v --cov=swarms --cov=utils
```

### 2. Auto-Label PRs (.github/workflows/auto-label.yml)
```yaml
name: Auto Label PR

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v4
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Stale Issue Management (.github/workflows/stale.yml)
```yaml
name: Close Stale Issues

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v8
        with:
          stale-issue-message: 'This issue is stale and will be closed in 7 days.'
          days-before-stale: 60
          days-before-close: 7
```

---

## Summary

This workflow provides:

✅ **Clear PR organization** - Logical separation of bug fixes, features, docs
✅ **Comprehensive labeling** - Type, priority, component, size labels
✅ **Milestone planning** - Organized by version/phase
✅ **Project boards** - Kanban workflow for visual tracking
✅ **Standardized templates** - Consistent PR/issue structure
✅ **Commit conventions** - Clean, searchable git history
✅ **Automated workflows** - CI/CD, linting, labeling, stale management

**Next Steps:**
1. Create GitHub labels (via Settings → Labels)
2. Set up milestones for v1.1, v1.2, v2.0, etc.
3. Create project board for "Decentralized Marketplace"
4. Add PR templates to `.github/PULL_REQUEST_TEMPLATE/`
5. Add issue templates to `.github/ISSUE_TEMPLATE/`
6. Configure GitHub Actions workflows
7. Create PRs for current work (PR #1-4 from above)
