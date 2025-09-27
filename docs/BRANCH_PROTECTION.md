# Branch Protection Configuration

This document outlines the branch protection rules that must be configured for the Wizbi repository to ensure code quality and enforce the PR-based workflow.

## Required Branch Protection Rules

### Main Branch Protection

Configure the following rules for the `main` branch:

#### General Rules
- ✅ **Restrict pushes that create files larger than 100 MB**
- ✅ **Require a pull request before merging**
- ✅ **Require approvals**: Minimum 1 approval required
- ✅ **Dismiss stale reviews when new commits are pushed**
- ✅ **Require review from code owners** (when CODEOWNERS file is present)

#### Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**

**Required status checks:**
- `Backend Tests`
- `Frontend Tests` 
- `Code Quality Checks`
- `Security Scan`
- `Docker Build Test`

#### Additional Restrictions
- ✅ **Restrict pushes that create merge commits**
- ✅ **Require signed commits**
- ✅ **Require linear history**
- ✅ **Include administrators** (enforce rules for repository administrators)
- ✅ **Allow force pushes**: ❌ Disabled
- ✅ **Allow deletions**: ❌ Disabled

### Develop Branch Protection

Configure the following rules for the `develop` branch:

#### General Rules
- ✅ **Require a pull request before merging**
- ✅ **Require approvals**: Minimum 1 approval required
- ✅ **Dismiss stale reviews when new commits are pushed**

#### Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**

**Required status checks:**
- `Backend Tests`
- `Frontend Tests`
- `Code Quality Checks`

#### Additional Restrictions
- ✅ **Allow force pushes**: ❌ Disabled
- ✅ **Allow deletions**: ❌ Disabled

## Setting Up Branch Protection Rules

### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Branches**
3. Click **Add rule** or edit existing rules
4. Configure the branch name pattern (e.g., `main`, `develop`)
5. Enable the required protection settings as outlined above
6. Click **Create** or **Save changes**

### Via GitHub CLI

```bash
# Main branch protection
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Backend Tests","Frontend Tests","Code Quality Checks","Security Scan","Docker Build Test"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null

# Develop branch protection
gh api repos/:owner/:repo/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Backend Tests","Frontend Tests","Code Quality Checks"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

### Via Terraform (Infrastructure as Code)

```hcl
resource "github_branch_protection" "main" {
  repository_id = github_repository.wizbi.node_id
  pattern       = "main"

  required_status_checks {
    strict = true
    contexts = [
      "Backend Tests",
      "Frontend Tests", 
      "Code Quality Checks",
      "Security Scan",
      "Docker Build Test"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
    require_code_owner_reviews     = true
  }

  enforce_admins = true

  allows_deletions    = false
  allows_force_pushes = false
}

resource "github_branch_protection" "develop" {
  repository_id = github_repository.wizbi.node_id
  pattern       = "develop"

  required_status_checks {
    strict = true
    contexts = [
      "Backend Tests",
      "Frontend Tests",
      "Code Quality Checks"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
  }

  allows_deletions    = false
  allows_force_pushes = false
}
```

## Code Owners Configuration

Create a `.github/CODEOWNERS` file to automatically request reviews from designated code owners:

```
# Global code owners
* @team-leads

# Backend specific
/backend/ @backend-team @senior-backend-dev

# Frontend specific  
/frontend/ @frontend-team @senior-frontend-dev

# Infrastructure and CI/CD
/.github/ @devops-team @platform-team
/docker/ @devops-team
/k8s/ @devops-team

# Documentation
*.md @docs-team @tech-writers
/docs/ @docs-team @tech-writers

# Configuration files
*.yml @devops-team
*.yaml @devops-team
*.json @senior-devs
```

## Workflow Integration

The branch protection rules work in conjunction with our GitHub Actions workflows:

### Pull Request Workflow
1. Developer creates feature branch from `develop`
2. Developer pushes changes and creates PR to `develop`
3. GitHub automatically triggers CI workflows
4. All required status checks must pass
5. At least 1 approval required from code owners
6. Branch must be up-to-date with target branch
7. PR can be merged only after all requirements are met

### Release Workflow
1. When ready for release, create PR from `develop` to `main`
2. Additional security scans and comprehensive tests run
3. Requires approval from senior team members
4. All status checks must pass
5. Upon merge to `main`, production deployment triggers

## Troubleshooting Common Issues

### Status Check Failures
- Ensure all required workflows are configured correctly
- Check that workflow names match the required status check names
- Verify that workflows run on PR events for the protected branches

### Permission Issues
- Ensure the GitHub Actions have appropriate permissions
- Check that required secrets are configured
- Verify team and user permissions for the repository

### Force Push Restrictions
- If you need to rewrite history, temporarily disable protection
- Consider using `git revert` instead of force pushing
- For emergency fixes, contact repository administrators

## Monitoring and Maintenance

- Regularly review protection rules and update as needed
- Monitor failed CI/CD runs and investigate root causes
- Update required status checks when new workflows are added
- Review and update code owners as team structure changes

## Emergency Procedures

In case of critical production issues:

1. **Hot Fixes**: Create emergency branches with reduced protection
2. **Temporary Bypass**: Repository administrators can temporarily disable protection
3. **Post-Emergency**: Re-enable all protection rules immediately after the fix
4. **Review Process**: Conduct post-incident review and update procedures

## Compliance and Auditing

- All changes to protected branches are logged
- GitHub audit logs track protection rule changes
- Regular compliance reviews should include branch protection verification
- Failed merge attempts and overrides are tracked for security auditing