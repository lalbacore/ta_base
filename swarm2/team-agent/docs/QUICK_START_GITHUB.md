# Quick Start: GitHub Workflow for Team Agent

This guide helps you get started with the Team Agent GitHub workflow.

---

## Setup (One-Time)

### 1. Install GitHub CLI
```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Or download from: https://cli.github.com/
```

### 2. Authenticate
```bash
gh auth login
# Follow prompts to authenticate
```

### 3. Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Creating a New Feature

### 1. Create Feature Branch
```bash
cd team-agent
git checkout develop
git pull origin develop
git checkout -b feat/your-feature-name
```

### 2. Make Changes
```bash
# Edit files
# ...

# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat(component): add new feature

Detailed description of what this feature does and why it's needed.

Closes #42"
```

### 3. Push Branch
```bash
git push origin feat/your-feature-name
```

### 4. Create Pull Request
```bash
gh pr create \
  --base develop \
  --title "feat(component): Add new feature" \
  --label "feature,backend,priority:medium" \
  --template "feature.md"
```

Or create PR via GitHub web UI.

---

## Creating a Bug Fix

### 1. Create Fix Branch
```bash
git checkout develop
git pull origin develop
git checkout -b fix/bug-description
```

### 2. Fix the Bug
```bash
# Make fixes
# Add tests
# ...

git add .
git commit -m "fix(component): fix specific bug

Root cause was...
Now it does...

Fixes #123"
```

### 3. Create PR
```bash
git push origin fix/bug-description

gh pr create \
  --base develop \
  --title "fix(component): Fix specific bug" \
  --label "bug,backend,priority:high" \
  --template "bug_fix.md"
```

---

## Current Work: Ready-Made PRs

We have 4 PRs ready to create for recent work:

### Option 1: Use Helper Script (Easiest)
```bash
cd team-agent
./scripts/create_prs.sh
```

This automatically creates all 4 PRs:
- PR #1: fix/registry-json-parsing-error
- PR #2: chore/cleanup-duplicate-agents
- PR #3: docs/decentralized-marketplace-vision
- PR #4: feat/cloud-specialists-aws-azure-gcp-oci

### Option 2: Create Manually

#### PR #1: Registry JSON Parsing Fix
```bash
git checkout -b fix/registry-json-parsing-error
# Cherry-pick the fix commit or apply manually
git add backend/app/services/registry_service.py
git commit -m "fix(registry): Handle SQLAlchemy JSON column deserialization

Fixes #XX"
git push origin fix/registry-json-parsing-error

gh pr create \
  --base develop \
  --title "fix(registry): Handle SQLAlchemy JSON column deserialization" \
  --label "bug,backend,api,priority:high" \
  --template "bug_fix.md"
```

#### PR #2: Cleanup Script
```bash
git checkout develop
git checkout -b chore/cleanup-duplicate-agents
git add scripts/cleanup_duplicate_agents.py
git commit -m "chore(agents): Add cleanup script for duplicate agent entries"
git push origin chore/cleanup-duplicate-agents

gh pr create \
  --base develop \
  --title "chore(agents): Add cleanup script for duplicate agent entries" \
  --label "chore,tooling,database,priority:medium" \
  --template "feature.md"
```

#### PR #3: Architecture Documentation
```bash
git checkout develop
git checkout -b docs/decentralized-marketplace-vision
git add docs/DECENTRALIZED_MARKETPLACE_VISION.md docs/GITHUB_WORKFLOW.md docs/QUICK_START_GITHUB.md
git commit -m "docs: Add decentralized marketplace architecture plan"
git push origin docs/decentralized-marketplace-vision

gh pr create \
  --base develop \
  --title "docs: Add decentralized marketplace architecture plan" \
  --label "documentation,architecture,planning,priority:high" \
  --template "feature.md"
```

#### PR #4: Cloud Specialists
```bash
# This branch should already exist from previous work
git checkout feat/cloud-specialists-aws-azure-gcp-oci
git push origin feat/cloud-specialists-aws-azure-gcp-oci

gh pr create \
  --base develop \
  --title "feat(specialists): Add cloud infrastructure specialists" \
  --label "feature,specialists,cloud,size:large" \
  --template "feature.md"
```

---

## Working with Milestones

### Create Milestone
```bash
gh milestone create \
  --title "v2.0 - Agent Discovery & Interoperability" \
  --description "A2A protocol and MCP server implementation" \
  --due-date "2026-02-15"
```

### Assign Issue to Milestone
```bash
gh issue edit 42 --milestone "v2.0"
```

---

## Labels Reference

Create labels in GitHub UI (Settings → Labels) or via CLI:

```bash
# Type labels
gh label create "bug" --color "d73a4a" --description "Something isn't working"
gh label create "feature" --color "0075ca" --description "New feature"
gh label create "documentation" --color "0075ca" --description "Documentation only"

# Priority labels
gh label create "priority:critical" --color "b60205" --description "Critical priority"
gh label create "priority:high" --color "d93f0b" --description "High priority"
gh label create "priority:medium" --color "fbca04" --description "Medium priority"
gh label create "priority:low" --color "0e8a16" --description "Low priority"

# Component labels
gh label create "backend" --color "c5def5" --description "Backend/API"
gh label create "frontend" --color "c5def5" --description "Frontend/UI"
gh label create "specialists" --color "c5def5" --description "Specialist agents"

# Size labels
gh label create "size:small" --color "ededed" --description "50-200 lines"
gh label create "size:medium" --color "ededed" --description "200-500 lines"
gh label create "size:large" --color "ededed" --description "500-1000 lines"
```

---

## Reviewing PRs

### List Open PRs
```bash
gh pr list
```

### Checkout PR Locally
```bash
gh pr checkout 42
```

### Review PR
```bash
# Approve
gh pr review 42 --approve

# Request changes
gh pr review 42 --request-changes --body "Please fix..."

# Comment only
gh pr review 42 --comment --body "Looks good but..."
```

### Merge PR
```bash
# Squash and merge (recommended for clean history)
gh pr merge 42 --squash --delete-branch

# Regular merge
gh pr merge 42 --merge

# Rebase merge
gh pr merge 42 --rebase
```

---

## Common Workflows

### Scenario: Found a bug while working on feature

```bash
# Stash current work
git stash

# Create fix branch
git checkout develop
git pull origin develop
git checkout -b fix/critical-bug

# Fix bug
# ... make changes ...
git add .
git commit -m "fix: critical bug"
git push origin fix/critical-bug

# Create PR
gh pr create --base develop --title "fix: Critical bug" --label "bug,priority:critical"

# Return to feature work
git checkout feat/your-feature
git stash pop
```

### Scenario: Feature depends on another PR

```bash
# Create feature branch from other branch (not develop)
git checkout feat/dependency-branch
git pull origin feat/dependency-branch
git checkout -b feat/your-feature

# Work and commit
# ...

# Create PR with different base
gh pr create \
  --base feat/dependency-branch \
  --title "feat: Your feature" \
  --body "Depends on #42"
```

### Scenario: Need to update PR after review

```bash
# Checkout PR branch
git checkout feat/your-feature

# Make requested changes
# ...

# Commit and push
git add .
git commit -m "fix: address review comments"
git push origin feat/your-feature

# PR automatically updates
```

---

## Tips & Best Practices

### Commit Messages
✅ **Good:**
```
feat(specialists): Add AWS specialist for cloud provisioning

Implements AWS specialist with support for:
- Terraform infrastructure as code
- CloudFormation templates
- boto3 Python SDK

Closes #42
```

❌ **Bad:**
```
fixed stuff
```

### PR Size
- Keep PRs focused (< 500 lines changed when possible)
- Large features: break into multiple PRs
- Use draft PRs for work-in-progress

### Branch Naming
✅ **Good:**
- `feat/a2a-protocol-implementation`
- `fix/registry-json-parsing-error`
- `docs/architecture-update`

❌ **Bad:**
- `my-changes`
- `update`
- `patch-1`

### Labels
Always add at least:
- Type label: `bug`, `feature`, `docs`, etc.
- Priority label: `priority:high`, `priority:medium`, etc.
- Component label: `backend`, `frontend`, etc.

---

## Getting Help

- **Documentation**: See `docs/GITHUB_WORKFLOW.md` for detailed workflow
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Team Discussions**: Use GitHub Discussions for questions
- **Issues**: Report problems via issue templates

---

## Quick Reference

```bash
# Common gh commands
gh pr list                          # List PRs
gh pr view 42                       # View PR #42
gh pr checkout 42                   # Checkout PR #42
gh pr create                        # Create new PR
gh pr merge 42 --squash             # Merge PR #42
gh pr review 42 --approve           # Approve PR #42

gh issue list                       # List issues
gh issue view 42                    # View issue #42
gh issue create                     # Create new issue
gh issue close 42                   # Close issue #42

gh repo view                        # View repository info
gh run list                         # List workflow runs
gh run view 12345                   # View workflow run

# Git shortcuts
git checkout develop && git pull    # Update develop branch
git checkout -b feat/new-feature    # Create feature branch
git add . && git commit             # Stage and commit
git push origin feat/new-feature    # Push branch
```

---

**Ready to create your first PR?**

```bash
# Start here:
cd team-agent
git checkout develop
git pull origin develop
git checkout -b feat/your-amazing-feature
# ... make changes ...
git add .
git commit -m "feat: add amazing feature"
git push origin feat/your-amazing-feature
gh pr create --template feature.md
```
