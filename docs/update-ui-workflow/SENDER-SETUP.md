# UI Update Workflow - Sender Setup

This document describes how the sender workflow dispatches UI update events to receiver repositories and apps.

## Overview

The sender workflow (`release-go.yml` in `lume/web`) triggers UI updates across multiple portal plugin repositories when Go modules are released.

## Sender Workflow Flow

### 1. Prepare Job
- Checks out all commits
- Runs `scripts/release-go.py` to determine modified apps
- Creates a matrix of affected repositories
- Outputs: `matrix`, `has_changes`, `commit_hash`

### 2. Dispatch Job
- Runs conditionally if there are changes (`has_changes == 'true'`)
- Uses a matrix strategy to dispatch to multiple repositories in parallel
- Maps app names to repository names:
  - `portal-frontend` → `portal-plugin-frontend`
  - `portal-app-shell` → `portal-plugin-app-shell`
  - etc.

## Dispatch Payload

Each dispatch event sends the following payload:

```json
{
  "commit_hash": "<git commit hash>",
  "app_name": "<app name, e.g., portal-frontend>",
  "repository": "<sender repo, e.g., LumeWeb/web>",
  "ref": "<git ref, e.g., refs/heads/main>"
}
```

## Adding New Receivers

To add a new receiver repository:

1. **Update the mapping** in `release-go.yml`:
   ```yaml
   # In the get_modified_apps job step
   # Add your app mapping:
   jq -n --arg app "$app" --arg repo "$repo" '{app: $app, repo: $repo}'
   ```

2. **Set up the receiver** following the instructions in `RECEIVER-SETUP.md`

3. **Ensure the sender has permissions**:
   - The `PAT` secret must have access to the receiver repository
   - The sender repository must be able to dispatch to the receiver (same organization or explicit permissions)

## Example: Adding `portal-plugin-example`

If you have a new app `portal-example` that needs updates:

1. In the sender's `get_modified_apps` step, ensure the mapping exists:
   ```bash
   base_name=${app#portal-}
   repo="portal-plugin-$base_name"
   ```

2. This will automatically map `portal-example` to `portal-plugin-example`

3. Set up the receiver workflow in `LumeWeb/portal-plugin-example`

## Sender Workflow Requirements

### Secrets
- `PAT`: GitHub Personal Access Token with `repo` scope for all target repositories

### Permissions
```yaml
permissions:
  contents: write
```

## Concurrency

The sender workflow uses concurrency control:
```yaml
concurrency: commits-to-master
```

This ensures only one release process runs at a time, preventing race conditions.

## Triggering the Sender

The sender workflow can be triggered by:
1. `repository_dispatch` event with type `release-go`
2. Manual `workflow_dispatch` (for testing)

### Manual Trigger Example
```bash
gh workflow run release-go.yml -R LumeWeb/web
```

## Troubleshooting

### Dispatch not reaching receivers
- Verify `PAT` has access to all target repositories
- Check that receiver workflows have the correct event type: `update-ui`
- Ensure receiver repositories exist and are accessible

### Matrix not including expected repos
- Check `scripts/release-go.py` output in `/tmp/modified_apps.txt`
- Verify the app name matches the expected pattern `portal-*`

### Concurrency blocking workflow
- Check for in-progress runs in the Actions tab
- Cancel stuck runs if necessary
