# Build Plugin Workflow

A centralized GitHub Actions workflow for building and testing LumeWeb portal plugins. This workflow provides a standardized, reusable build process across all portal plugin repositories.

## Overview

This workflow handles building portal plugins using XPortal, supporting both standalone plugins and plugins with additional dependencies. It automatically extracts the repository name and builds the plugin with proper module replacements.

## Available Workflows

This repository provides two reusable workflows:

1. **`build-plugin.yml`** - For building and testing portal plugins with the plugin included
2. **`build-portal.yml`** - For building and testing the portal itself (no plugins)
3. **`run-portal.yml`** - Internal reusable workflow for running portal tests (used by both workflows above)

## Quick Start

### Setting Up Your Repository

1. **Create the workflow file** `.github/workflows/build.yml`:
   ```yaml
   name: Build

   on:
     push:
       branches: [ develop ]
     pull_request:
       branches: [ develop ]

   jobs:
     build:
       uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@develop
   ```

2. **For plugins with dependencies**:
   ```yaml
   name: Build

   on:
     push:
       branches: [ develop ]
     pull_request:
       branches: [ develop ]

   jobs:
     build:
       uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@develop
       with:
         additional_dependencies: go.lumeweb.com/portal-plugin-frontend,go.lumeweb.com/portal-plugin-app-shell
   ```

## Workflow Inputs

### build-plugin.yml

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `additional_dependencies` | Additional plugin dependencies to include (comma-separated, format: `go.lumeweb.com/plugin-name,go.lumeweb.com/another-plugin`) | No | `''` |
| `replacements` | Go module replacements (comma-separated, format: `old_module@version=new_module@version`) | No | `''` |
| `setup_script` | Bash script to run inside the container before generate/build/test. Use for installing extra deps (e.g. Kubo, jq). | No | `''` |
| `build_tags` | Go build tags to apply when compiling the portal binary (comma-separated, format: `foo,bar`). | No | `''` |
| `excludes` | Go module exclusion directives (comma-separated, format: `module@version`). | No | `''` |

### build-portal.yml

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `build_tags` | Go build tags to apply when compiling the portal binary (comma-separated, format: `foo,bar`). | No | `''` |
| `excludes` | Go module exclusion directives (comma-separated, format: `module@version`). | No | `''` |

### run-portal.yml

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `db_type` | Database type to use (`sqlite` or `mysql`) | Yes | N/A |

## How It Works

The workflow consists of two jobs:

### Build Job

1. **Build Environment**: Uses the `ghcr.io/lumeweb/portal-builder:ubuntu` Docker container which includes Go 1.26, XPortal CLI, and build dependencies
2. **Checkout Repo**: Checks out the repository with submodules
3. **Extract Repo Name**: Determines the plugin name from the repository
4. **Create Plugin Manifest**: Generates a `portal-plugins.yaml` manifest with the current plugin and any additional dependencies
5. **Setup + Generate + Build + Test**: Runs all steps in a single container session:
   - Runs the `setup_script` (if provided) to install extra dependencies
   - Runs `go generate ./...` to generate code
   - Runs `build-portal` to compile the portal binary
   - Runs `go test` to run the test suite
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

When `replacements` is provided, a `replacements` array is added (equivalent to `go.mod` replace directives):
```yaml
portalVersion: develop
plugins:
  - module: go.lumeweb.com/your-plugin-name
    version: latest
replacements:
  - old: github.com/original/module@v1.0.0
    new: github.com/fork/module@v1.0.1
```

When `build_tags` is provided, a `buildTags` array is added (passed to `go build -tags`; the default `nobadger` tag is always applied on top):
```yaml
portalVersion: develop
plugins:
  - module: go.lumeweb.com/your-plugin-name
    version: latest
buildTags:
  - foo
  - bar
```

When `excludes` is provided, an `excludes` array is added (each entry adds a `go mod edit -exclude` directive preventing that module version from being selected):
```yaml
portalVersion: develop
plugins:
  - module: go.lumeweb.com/your-plugin-name
    version: latest
excludes:
  - module: github.com/foo/bar
    version: v1.2.0
```

When `setup` is provided, the inline bash script runs inside the container before `go generate`, build, and test. This is useful for plugins that need extra system dependencies:
```yaml
portalVersion: develop
setup: |
  apt-get update && apt-get install -y jq
  wget -q https://github.com/ipfs/kubo/releases/download/v0.34.0/kubo_v0.34.0_linux-amd64.tar.gz
  tar -xzf kubo_v0.34.0_linux-amd64.tar.gz
  cp kubo/ipfs /usr/local/bin/
  ipfs init
plugins:
  - module: go.lumeweb.com/portal-plugin-ipfs
    version: latest
```

> **Note:** The `setup_script` workflow input takes precedence over the manifest `setup` field. When using the shared workflow, prefer `setup_script` input over manifest `setup`.

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

### Plugin with Module Replacements

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
      replacements: github.com/original/module@v1.0.0=github.com/fork/module@v1.0.1,github.com/another/dep=github.com/replace/dep@v2.0.0
```

### Plugin with Go Build Tags

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
      build_tags: foo,bar
```

### Plugin with Module Excludes

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
      excludes: github.com/foo/bar@v1.2.0,github.com/baz/qux@v2.0.0
```

### Plugin with Custom Environment Setup

When your plugin requires extra system dependencies (e.g. Kubo for IPFS, jq for test fixtures), use the `setup_script` input. The script runs inside the build container before `go generate`, `build-portal`, and `go test`.

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [ develop ]
  pull_request:
    branches: [ develop ]

jobs:
  build:
    uses: LumeWeb/workflows/.github/workflows/build-plugin.yml@develop
    with:
      setup_script: |
        apt-get update && apt-get install -y jq
        KUBO_VERSION=$(wget -qO- https://github.com/ipfs/kubo/releases/latest | grep -oP 'tag/\K[^"]+' | head -1)
        wget -q https://github.com/ipfs/kubo/releases/download/${KUBO_VERSION}/kubo_${KUBO_VERSION}_linux-amd64.tar.gz
        tar -xzf kubo_${KUBO_VERSION}_linux-amd64.tar.gz
        cp kubo/ipfs /usr/local/bin/
        ipfs init
```

The `setup_script` can also be specified in the plugin manifest's `setup` field (see [Plugin Manifest](#plugin-manifest) below). The workflow input takes precedence.

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

## Portal-Only Testing

For testing the portal itself without any plugins (useful for core portal development), use the `build-portal.yml` workflow:

```yaml
# .github/workflows/build-portal.yml
name: Build Portal

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    uses: LumeWeb/workflows/.github/workflows/build-portal.yml@main
```

This workflow:
- Builds the portal without any plugins included
- Runs the same comprehensive test suite (SQLite and MySQL)
- Uses the same mock renterd server for testing
- Follows the same environment configuration process

## Workflow Architecture

The workflows are designed with a DRY (Don't Repeat Yourself) principle:

1. **`build-plugin.yml`** - Builds portal with plugins and runs tests
2. **`build-portal.yml`** - Builds portal without plugins and runs tests
3. **`run-portal.yml`** - Reusable workflow that handles running portal tests

Both `build-plugin.yml` and `build-portal.yml` delegate the test execution to `run-portal.yml`, eliminating code duplication.

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
