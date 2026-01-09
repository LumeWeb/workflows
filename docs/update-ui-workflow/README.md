# UI Update Workflow

A centralized GitHub Actions workflow for updating Go UI dependencies across multiple portal plugin repositories and apps.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Sender: web/.github/workflows/release-go.yml          │
│  - Detects modified Go modules                               │
│  - Builds matrix of affected repositories                   │
│  - Dispatches repository_dispatch events                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ repository_dispatch (update-ui)
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Receiver 1   │          │ Receiver N   │
│ portal-      │  ...     │ portal-      │
│ plugin-      │          │ plugin-xyz   │
│ dashboard    │          │ OR app       │
│              │          │              │
└──────┬───────┘          └──────┬───────┘
       │                         │
       │ Calls centralized workflow │
       ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Central: LumeWeb/workflows/.github/workflows/               │
│           update-ui.yml                                      │
│  - Updates Go dependency via go get                          │
│  - Runs go mod tidy                                          │
│  - Creates PR to develop branch                              │
└─────────────────────────────────────────────────────────────┘
```

## Files

- **`update-ui.yml`**: The workflow that receiver repositories call
- **`RECEIVER-SETUP.md`**: Instructions for setting up receiver repositories
- **`SENDER-SETUP.md`**: Instructions for the sender workflow

## Quick Start

### For Receiver Repositories

1. Create `.github/workflows/update-ui.yml`:
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
         version: ${{ github.event.client_payload.version }}
         app_name: ${{ github.event.client_payload.app_name }}
         repository: ${{ github.event.client_payload.repository }}
       secrets:
         PAT: ${{ secrets.PAT }}
   ```

2. Add `PAT` secret to your repository

3. Ensure workflow permissions:
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```

See [RECEIVER-SETUP.md](./RECEIVER-SETUP.md) for detailed instructions.

### For Sender Repository

The sender workflow is already configured in `lume/web`. See [SENDER-SETUP.md](./SENDER-SETUP.md) for details on how it works and how to add new receivers.

## Workflow Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `commit_hash` | Git commit hash to update to | `abc123def456` |
| `app_name` | App name (e.g., `portal-frontend`) | `portal-frontend` |
| `repository` | Source repository | `LumeWeb/web` |

## Workflow Behavior

1. **Checkout**: Clones the receiver repository
2. **Setup Go**: Installs Go 1.23.0
3. **Update Dependency**: Runs `go get` with the specified commit hash
4. **Tidy**: Runs `go mod tidy` to clean up `go.mod`
5. **Create PR**: Opens a pull request to `develop` branch with:
   - Branch: `deps/update-ui`
   - Auto-delete on merge
   - Labels: `dependencies`, `automated pr`

## Important Notes

### Go Module Path

### Go Module Path

The workflow assumes Go modules are at:
```
go.lumeweb.com/web/go/${{ inputs.app_name }}
```

Adjust if your project uses a different module path.

## Security

- Requires `PAT` secret with `repo` permissions
- Secrets must be configured in each receiver repository
- The sender's `PAT` must have access to all target repositories

## Testing

To test the workflow manually:

```bash
# Trigger sender workflow
gh workflow run release-go.yml -R LumeWeb/web

# Or trigger a specific receiver directly
gh repo dispatch LumeWeb/portal-plugin-dashboard \
  --event-type update-ui \
  -f commit_hash=abc123 \
  -f app_name=portal-frontend \
  -f repository=LumeWeb/web
```

## Support

For issues or questions:
- Check the troubleshooting sections in `RECEIVER-SETUP.md` and `SENDER-SETUP.md`
- Review workflow logs in GitHub Actions
- Verify secrets and permissions are correctly configured
