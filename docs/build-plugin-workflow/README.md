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

The workflow consists of two jobs:

### Build Job

1. **Build Environment**: Uses the `ghcr.io/lumeweb/portal-builder:latest` Docker container which includes Go 1.26, XPortal CLI, and build dependencies
2. **Checkout Repo**: Checks out the repository with submodules
3. **Extract Repo Name**: Determines the plugin name from the repository
4. **Create Plugin Manifest**: Generates a `portal-plugins.yaml` manifest with the current plugin and any additional dependencies
5. **Build Portal**: Runs the `build-portal` script which uses XPortal to compile the portal binary
6. **Upload Artifacts**: Saves the compiled portal binary for the run job

### Run Job

1. **Checkout Repo**: Checks out the repository with submodules
2. **Download Artifacts**: Retrieves the compiled portal binary from the build job
3. **Checkout Workflows for Config**: Checks out the LumeWeb/workflows repository to access core configuration files
4. **Generate Environment Variables**: Merges core and plugin configs, converts to env vars using Python script
5. **Run Mock Renterd Server**: Starts a mock renterd server for testing
6. **Run Portal**: Executes the portal with binding detection and graceful shutdown

### Portal Builder Container

The workflow uses the `ghcr.io/lumeweb/portal-builder:latest` Docker container which provides:
- Go 1.26
- XPortal CLI tool
- Pre-configured build environment
- Go module cache for faster builds
- YAML validation for plugin manifests

### Plugin Manifest

The workflow creates a `portal-plugins.yaml` manifest file with the plugin configuration:

```yaml
portalVersion: develop
plugins:
  - module: go.lumeweb.com/your-plugin-name
    version: latest
```

When `additional_dependencies` is provided, additional plugin entries are added:
```yaml
portalVersion: develop
plugins:
  - module: go.lumeweb.com/your-plugin-name
    version: latest
  - module: go.lumeweb.com/portal-plugin-frontend
    version: latest
  - module: go.lumeweb.com/portal-plugin-app-shell
    version: latest
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
- No additional setup required - the portal-builder container provides all build dependencies

## Troubleshooting

### Build fails with module not found
- Ensure your Go module path matches the repository name pattern: `go.lumeweb.com/your-plugin-name`
- Check that `go.mod` exists and is properly configured

### Dependencies not being included
- Verify the dependency format: `go.lumeweb.com/plugin-name` (comma-separated)
- Ensure dependencies are comma-separated with no spaces or single spaces after commas
- Example: `go.lumeweb.com/plugin-1,go.lumeweb.com/plugin-2` or `go.lumeweb.com/plugin-1, go.lumeweb.com/plugin-2`

### Build fails in container
- Check the build logs for specific error messages
- Verify that the portal-builder image is accessible: `ghcr.io/lumeweb/portal-builder:latest`
- Ensure the `portal-plugins.yaml` manifest is being created correctly

## Portal Testing

The workflow includes a `run` job that executes the built portal for testing.

### Configuration

**Core Config** (in LumeWeb/workflows repo):
- `.github/config/portal-core.yml` - Standard configuration for all plugins

**Plugin Config** (optional, in plugin repo):
- `.github/portal-config.yml` - Plugin-specific configuration overrides

### How It Works

The run job:
1. Downloads the compiled portal binary from the build job
2. Generates environment variables from YAML configuration files
3. Starts a mock renterd server for testing
4. Starts the portal in the background
5. Waits for it to bind to the configured port
6. Once bound, gracefully shuts down the portal
7. Returns the actual exit code

This approach:
- Does not use timeout (which would mask error codes)
- Detects successful binding to determine success
- Preserves actual exit codes for proper error reporting
- Uses the actual compiled binary for realistic testing

### Container Build Benefits

Using the portal-builder container provides:
- Consistent build environment across all plugins
- Faster builds due to pre-populated Go module cache
- No need to install Go or XPortal in each workflow run
- Alpine Linux base for minimal footprint

## Support

For issues or questions:
- Check the workflow logs in GitHub Actions
- Review the [portal-builder documentation](https://github.com/LumeWeb/portal-builder)
- Review the [XPortal documentation](https://github.com/LumeWeb/xportal)
- Open an issue in the [LumeWeb/workflows](https://github.com/LumeWeb/workflows) repository
