# Release Workflow

A centralized GitHub Actions workflow for creating releases using Knope across LumeWeb repositories. This workflow provides a standardized, reusable release process that handles version management, changelog generation, and GitHub release creation.

## Overview

This workflow automates the release process using [Knope](https://github.com/knope-dev/knope), a tool for conventional changelog management and release automation. It handles:

- Version bumping based on conventional commits
- Automatic changelog generation
- Git tag creation
- GitHub release creation
- Git repository setup and configuration

## Quick Start

### Setting Up Your Repository

1. **Create the workflow file** `.github/workflows/release.yml`:
   ```yaml
   name: Release

   on:
     workflow_dispatch:

   jobs:
     release:
       uses: LumeWeb/workflows/.github/workflows/release.yml@main
       secrets:
         PAT: ${{ secrets.PAT }}
   ```

2. **Add the required secret**:
   - Add `PAT` to your repository secrets (a GitHub Personal Access Token with `repo` permissions)

3. **Create a Knope configuration file** `knope.toml` in your repository root. Example:
   ```toml
   [package]
   versioned_files = ["go.mod"]
   changelog = "CHANGELOG.md"

   [github]
   owner = "LumeWeb"
   repo = "your-repo-name"
   ```

## Workflow Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `knope_version` | Version of Knope to install | No | `0.21.7` |

## Workflow Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `PAT` | GitHub Personal Access Token with `repo` permissions | Yes |

## Workflow Behavior

The workflow executes the following steps:

1. **Checkout Repository**: Checks out the repository with full history (`fetch-depth: 0`) using the provided PAT
2. **Install Knope**: Installs the specified version of Knope
3. **Setup Git**: Configures Git with the shared setup action
4. **Create Release**: Runs `knope release --verbose` using the PAT for authentication

### How It Works

The workflow uses Knope to parse your conventional commits, determine the appropriate version bump, and create a release. Knope follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - Adds a new feature (minor version bump)
- `fix:` - Fixes a bug (patch version bump)
- `BREAKING CHANGE:` - Breaking change (major version bump)

## Requirements

- **GitHub Actions** enabled in your repository
- **Knope configuration** (`knope.toml`) in your repository root
- **PAT secret** with `repo` permissions
- **Conventional commits** in your repository
- **Workflow permissions** (`contents: write`)

## Examples

### Basic Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:

jobs:
  release:
    uses: LumeWeb/workflows/.github/workflows/release.yml@main
    secrets:
      PAT: ${{ secrets.PAT }}
```

### Custom Knope Version

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:

jobs:
  release:
    uses: LumeWeb/workflows/.github/workflows/release.yml@main
    with:
      knope_version: "0.22.0"
    secrets:
      PAT: ${{ secrets.PAT }}
```

### Release on Tag Push

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    uses: LumeWeb/workflows/.github/workflows/release.yml@main
    secrets:
      PAT: ${{ secrets.PAT }}
```

## Manual Trigger

To manually trigger a release:

```bash
# Using GitHub CLI
gh workflow run release.yml

# Or via GitHub Actions UI
# Go to Actions tab → Release workflow → Run workflow
```

## Troubleshooting

### Workflow fails with authentication error

- Verify the `PAT` secret exists and has `repo` permissions
- Ensure the workflow has `contents: write` permission

### Knope fails to determine version

- Check that your commits follow the Conventional Commits specification
- Ensure your `knope.toml` configuration is valid
- Review Knope logs in the workflow output for specific errors

### Release not created on GitHub

- Verify the `PAT` has appropriate permissions
- Check that the workflow completed successfully
- Review the workflow logs for any errors

## Additional Resources

- [Knope Documentation](https://knope.dev/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For issues or questions:
- Check the workflow logs in GitHub Actions
- Review the [Knope documentation](https://knope.dev/)
- Open an issue in the [LumeWeb/workflows](https://github.com/LumeWeb/workflows) repository
