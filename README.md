# Lume Workflows

Shared GitHub Actions workflows for LumeWeb projects. This repository provides reusable, centralized workflows that can be called from other repositories to standardize CI/CD processes across the Lume ecosystem.

## Overview

This repository contains:
- **Reusable workflows**: GitHub Actions workflows that other repositories can call via `workflow_call`
- **Documentation**: Setup guides and templates for implementing workflows
- **Templates**: Ready-to-use workflow files for quick integration

## Available Workflows

### Build Plugin Workflow

A centralized workflow for building and testing LumeWeb portal plugins. This workflow provides a standardized build process with support for additional plugin dependencies.

**Workflow File**: `.github/workflows/build-plugin.yml`

**Documentation**: See [docs/build-plugin-workflow/](./docs/build-plugin-workflow/)
- [Overview & Quick Start](./docs/build-plugin-workflow/README.md)
- [Receiver Template](./docs/build-plugin-workflow/receiver-template.yml)

#### Features
- Standardized build process for all portal plugins
- Automatic module replacement for local development
- Support for additional plugin dependencies (comma-separated)
- Triggers on push and pull requests

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Plugin Repository                                          │
│  .github/workflows/build.yml                                │
│  - Triggers on push/PR                                      │
│  - Calls centralized build workflow                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ workflow_call
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Central: LumeWeb/workflows/.github/workflows/               │
│           build-plugin.yml                                   │
│  - Sets up Go 1.22.1                                         │
│  - Installs XPortal                                         │
│  - Extracts repo name                                       │
│  - Builds plugin with module replacements                   │
│  - Supports additional dependencies via --with flags        │
└─────────────────────────────────────────────────────────────┘
```

### UI Update Workflow

A centralized workflow for updating Go UI dependencies across multiple portal plugin repositories and apps.

**Workflow File**: `.github/workflows/update-ui.yml`

**Documentation**: See [docs/update-ui-workflow/](./docs/update-ui-workflow/)
- [Overview & Quick Start](./docs/update-ui-workflow/README.md)
- [Receiver Setup Guide](./docs/update-ui-workflow/RECEIVER-SETUP.md)
- [Sender Setup Guide](./docs/update-ui-workflow/SENDER-SETUP.md)
- [Receiver Template](./docs/update-ui-workflow/receiver-template.yml)

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Sender: lume/web/.github/workflows/release-go.yml          │
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

## Quick Start

### Setting Up a Plugin Repository

1. **Copy the build template** to your repository:
   ```bash
   curl -o .github/workflows/build.yml \
     https://raw.githubusercontent.com/LumeWeb/workflows/main/docs/build-plugin-workflow/receiver-template.yml
   ```

2. **Add dependencies** (if your plugin requires them):
   Uncomment the `with:` section in the workflow and add your dependencies.

See the [Build Plugin Workflow Documentation](./docs/build-plugin-workflow/README.md) for detailed instructions.

### Setting Up a Receiver Repository (UI Updates)

1. **Copy the receiver template** to your repository:
   ```bash
   curl -o .github/workflows/update-ui.yml \
     https://raw.githubusercontent.com/LumeWeb/workflows/main/docs/update-ui-workflow/receiver-template.yml
   ```

2. **Add the required secret**:
   - Add `PAT` to your repository secrets (a GitHub Personal Access Token with `repo` permissions)

3. **Configure permissions** (if needed):
   ```yaml
   permissions:
     contents: write
     pull-requests: write
   ```

See the [Receiver Setup Guide](./docs/update-ui-workflow/RECEIVER-SETUP.md) for detailed instructions.

### Adding a New Workflow

When adding a new workflow to this repository:

1. Create the workflow file in `.github/workflows/`
2. Create a documentation directory in `docs/<workflow-name>/`
3. Include at minimum:
   - `README.md` - Overview and quick start guide
   - Setup instructions (e.g., `RECEIVER-SETUP.md`, `SENDER-SETUP.md`)
   - Template files for easy integration
4. Update this README with the new workflow information

## Requirements

- GitHub Actions
- Appropriate secrets configured in receiver repositories
- Workflow permissions (contents: write, pull-requests: write)

## Security

- All workflows use `PAT` secrets with appropriate permissions
- Secrets must be configured in each receiver repository
- Workflows follow least-privilege principles

## Contributing

Contributions are welcome! To add a new workflow:

1. Fork the repository
2. Create a feature branch
3. Add your workflow and documentation
4. Submit a pull request

## License

See [LICENSE](./LICENSE) for details.

## Support

For issues or questions:
- Check the documentation in the respective workflow directory
- Review GitHub Actions logs
- Open an issue in this repository
