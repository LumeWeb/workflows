# Build Plugin Workflow

A centralized GitHub Actions workflow for building and testing LumeWeb portal plugins. This workflow provides a standardized, reusable build process across all portal plugin repositories.

## Overview

This workflow handles building portal plugins using XPortal, supporting both standalone plugins and plugins with additional dependencies. It automatically extracts the repository name and builds the plugin with proper module replacements.

## Quick Start

### Setting Up Your Repository

1. **Create the workflow file** `.github/workflows/build.yml`:
   ```yaml
   name: Build

   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main, develop ]

   jobs:
     build:
       uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@main
   ```

2. **For plugins with dependencies**:
   ```yaml
   name: Build

   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main, develop ]

   jobs:
     build:
       uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@main
       with:
         additional_dependencies: go.lumeweb.com/portal-plugin-frontend,go.lumeweb.com/portal-plugin-app-shell
   ```

## Workflow Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `additional_dependencies` | Additional plugin dependencies to include (comma-separated, format: `go.lumeweb.com/plugin-name,go.lumeweb.com/another-plugin`) | No | `''` |

## How It Works

1. **Setup Go**: Installs Go 1.22.1 using the shared setup action
2. **Install XPortal**: Installs the XPortal CLI tool
3. **Checkout Repo**: Checks out the repository with submodules
4. **Extract Repo Name**: Determines the plugin name from the repository
5. **Build**: Builds the plugin using XPortal with proper module replacements

### Module Replacement

The workflow automatically creates a module replacement for the current plugin:
```
--replace go.lumeweb.com/your-plugin-name=/path/to/plugin
```

This allows XPortal to use the local version of the plugin during the build process.

### Additional Dependencies

When `additional_dependencies` is provided, the workflow adds `--with` flags for each dependency:
```bash
xportal build \
  --with go.lumeweb.com/your-plugin-name \
  --with go.lumeweb.com/portal-plugin-frontend \
  --with go.lumeweb.com/portal-plugin-app-shell \
  --replace go.lumeweb.com/your-plugin-name=/path/to/plugin
```

## Example Usage

### Basic Plugin Build

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@main
```

### Plugin with Dependencies

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@main
    with:
      additional_dependencies: go.lumeweb.com/portal-plugin-frontend,go.lumeweb.com/portal-plugin-app-shell,go.lumeweb.com/portal-plugin-dashboard
```

### Manual Trigger with Dependencies

```yaml
# .github/workflows/build.yml
name: Build

on:
  workflow_dispatch:
    inputs:
      dependencies:
        description: 'Additional dependencies (comma-separated)'
        required: false
        type: string
        default: ''

jobs:
  build:
    uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@main
    with:
      additional_dependencies: ${{ inputs.dependencies }}
```

## Requirements

- GitHub Actions enabled in your repository
- Go module properly configured
- Plugin follows LumeWeb plugin structure

## Troubleshooting

### Build fails with module not found
- Ensure your Go module path matches the repository name pattern: `go.lumeweb.com/your-plugin-name`
- Check that `go.mod` exists and is properly configured

### Dependencies not being included
- Verify the dependency format: `go.lumeweb.com/plugin-name` (comma-separated)
- Ensure dependencies are comma-separated with no spaces or single spaces after commas
- Example: `go.lumeweb.com/plugin-1,go.lumeweb.com/plugin-2` or `go.lumeweb.com/plugin-1, go.lumeweb.com/plugin-2`

### XPortal installation fails
- Check that the XPortal package is available at `go.lumeweb.com/xportal/cmd/xportal`
- Verify Go version compatibility (1.22.1)

## Support

For issues or questions:
- Check the workflow logs in GitHub Actions
- Review the [XPortal documentation](https://github.com/LumeWeb/xportal)
- Open an issue in the [LumeWeb/workflows](https://github.com/LumeWeb/workflows) repository
