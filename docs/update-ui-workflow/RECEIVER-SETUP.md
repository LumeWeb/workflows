# UI Update Workflow - Receiver Setup

This document describes how to set up the UI update workflow in receiver repositories and apps.

## Overview

The workflow handles updating Go UI dependencies when triggered by a repository dispatch event from the `lume/web` repository.

## Setup Steps

### 1. Create the Receiver Workflow

Create a file `.github/workflows/update-ui.yml` in your repository:

```yaml
name: Handle UI Update

on:
  repository_dispatch:
    types: [update-ui]

jobs:
  call-workflow:
    uses: LumeWeb/workflows/.github/workflows/update-ui.yml@main
    with:
      commit_hash: ${{ github.event.client_payload.commit_hash }}
      app_name: ${{ github.event.client_payload.app_name }}
      repository: ${{ github.event.client_payload.repository }}
    secrets:
      PAT: ${{ secrets.PAT }}
```

### 2. Required Secrets

Ensure your repository has the following secret:
- `PAT`: A GitHub Personal Access Token with `repo` permissions (required for creating pull requests)

### 3. Required Permissions

The workflow needs `contents: write` permission to create pull requests. Add this to your workflow if needed:

```yaml
permissions:
  contents: write
  pull-requests: write
```

## Workflow Inputs

The workflow accepts the following inputs:

| Input | Description | Required |
|-------|-------------|----------|
| `commit_hash` | The commit hash to update to | Yes |
| `app_name` | The name of the app being updated (e.g., `portal-frontend`) | Yes |
| `repository` | The source repository (for PR description) | Yes |

## What the Workflow Does

1. Checks out the repository code
2. Sets up Go 1.23.0
3. Updates the Go dependency using `go get` with the specified commit hash
4. Runs `go mod tidy` to clean up dependencies
5. Creates a pull request to the `develop` branch with:
   - Commit message: `chore: update UI dependency to ${version}`
   - Title: `chore: update UI dependency to ${version}`
   - Body containing source repository and version info
   - Branch: `deps/update-ui` (auto-deleted after merge)
   - Labels: `dependencies`, `automated pr`

## Example

When the sender triggers an event with:
```json
{
  "commit_hash": "abc123def456",
  "app_name": "portal-frontend",
  "repository": "LumeWeb/web"
}
```

The receiver will:
1. Update `go.lumeweb.com/web/go/portal-frontend` to commit `abc123def456`
2. Create a PR titled "chore: update UI dependency"

## Troubleshooting

### Workflow not triggering
- Ensure the sender repository has your repository added to the dispatch targets
- Check that the event type matches: `update-ui`

### PR not created
- Verify `PAT` secret exists and has `repo` permissions
- Check that the workflow has `contents: write` permission

### Dependency update fails
- Ensure Go 1.23.0 is compatible with your project
- Check that the dependency path matches your project structure
