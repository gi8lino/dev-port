# Make modules and targets

The Make integration is modular. `dev-tools.mk` is the core; all other `dev-tools-*.mk` files are optional feature modules.

## Core

Include the committed bootstrap directly:

```makefile
include bin/dev-tools.mk
```

The core determines its own location, creates a version-specific cache when `DEV_TOOLS_VERSION` is set, and provides these variables and helpers:

```makefile
$(DEV_TOOLS_ROOT)
$(DEV_TOOLS_CACHE)
$(DEV_TOOLS_BIN)
$(GO_INSTALL_TOOL)
$(GITHUB_RELEASE_INSTALL)
$(call dev-tools-module,<name>)
$(call download-dev-file,<asset>,<target>)
$(call download-dev-tool,<asset>,<target>)
$(call run-tool,<executable>,<arguments>)
```

`DEV_TOOLS_ROOT` is the directory containing the committed `dev-tools.mk`. With a version pin, `DEV_TOOLS_BIN` points to `.dev-tools/<version>` below it.

`run-tool` executes the real local binary while printing only its executable name and arguments. A recipe such as:

```makefile
lint: $(GOLANGCI_LINT)
	$(call run-tool,$(GOLANGCI_LINT),run)
```

prints:

```text
golangci-lint run
```

rather than an absolute local path.

### Installing Go tools

`go-install-tool` belongs to the core because projects can use it to install arbitrary pinned Go tools:

```makefile
GOLANGCI_LINT := bin/golangci-lint

# renovate: datasource=github-releases depName=golangci/golangci-lint
GOLANGCI_LINT_VERSION ?= v2.13.2

$(GOLANGCI_LINT): $(GO_INSTALL_TOOL)
	$(call run-tool,$(GO_INSTALL_TOOL),\
		--target "$(GOLANGCI_LINT)" \
		--package github.com/golangci/golangci-lint/v2/cmd/golangci-lint \
		--tool-version "$(GOLANGCI_LINT_VERSION)")

.PHONY: lint
lint: $(GOLANGCI_LINT)
	$(call run-tool,$(GOLANGCI_LINT),run)
```

### Installing GitHub release binaries

`github-release-install` belongs to the core as well. It hides platform detection, release URL construction, versioned filenames, and symlink management from project Makefiles.

For Lore, a project can keep only the stable path and release metadata:

```makefile
LORE := bin/lore

# renovate: datasource=github-releases depName=gi8lino/lore
LORE_VERSION ?= v0.13.0
LORE_ASSET ?= lore_{version}_{os}_{arch}.tar.gz

.PHONY: lore
lore: $(GITHUB_RELEASE_INSTALL)
	@$(GITHUB_RELEASE_INSTALL) \
		--repo gi8lino/lore \
		--tag "$(LORE_VERSION)" \
		--asset "$(LORE_ASSET)" \
		--binary lore \
		--target "$(LORE)"
```

The installer creates a concrete binary such as `bin/lore-v0.13.0` and maintains `bin/lore` as a relative symlink. The Makefile does not need a `LORE_VERSIONED` variable or its own `ln -sf` recipe.

The `lore` wrapper target is phony on purpose: it lets the installer inspect the requested version on every invocation. If the versioned binary already exists and the symlink is correct, the helper returns without downloading anything. If `LORE_VERSION` changes, it installs the new version and repoints the stable symlink.

## Tagging module

Include:

```makefile
include $(call dev-tools-module,tag)
```

The module provides all tagging targets and defaults `VERSION_PREFIX` to `v`.

| Target         | Behavior                                                             |
| -------------- | -------------------------------------------------------------------- |
| `make current` | Print the latest semantic-version tag matching the configured prefix |
| `make patch`   | Create the next patch tag                                            |
| `make minor`   | Create the next minor tag and reset patch to zero                    |
| `make major`   | Create the next major tag and reset minor and patch to zero          |
| `make push`    | Push local tags to the configured Git remote                         |

Override the tag prefix in the Makefile:

```makefile
VERSION_PREFIX ?= v
```

or create unprefixed tags for one invocation:

```sh
make patch VERSION_PREFIX=
```

## Port module

Include:

```makefile
include $(call dev-tools-module,port)
```

The module exposes `DEV_PORT` and the `dev-port` Make function:

```makefile
APP_PORT = $(call dev-port,app)
DB_PORT = $(call dev-port,postgres)
```

Targets that expand these values should depend on `$(DEV_PORT)` so the executable exists before the recipe is expanded:

```makefile
.PHONY: ports
ports: $(DEV_PORT) ## Show development ports.
	@printf 'App: http://127.0.0.1:%s/\n' '$(APP_PORT)'
	@printf 'Postgres: 127.0.0.1:%s\n' '$(DB_PORT)'
```

The port module intentionally does not inject project-specific targets; projects decide which services and names they need.

## Browser module

Include:

```makefile
include $(call dev-tools-module,browser)
```

The module exposes `OPEN_BROWSER`. Make a target depend on it and invoke it with `run-tool`:

```makefile
.PHONY: open
open: $(DEV_PORT) $(OPEN_BROWSER) ## Open the application.
	$(call run-tool,$(OPEN_BROWSER),"http://127.0.0.1:$(APP_PORT)/")
```

Like the port module, browser integration provides the primitive rather than a fixed `open` target because the URL belongs to the consuming project.

## Help module

Include:

```makefile
include $(call dev-tools-module,help)
```

It provides:

| Target      | Behavior                                                            |
| ----------- | ------------------------------------------------------------------- |
| `make help` | Display all documented targets from the root and included Makefiles |

Put this before the includes if help should be the default target:

```makefile
.DEFAULT_GOAL := help
```

Document targets with `##` and group them with `##@`:

```makefile
##@ Development

.PHONY: test
test: ## Run all tests.
	go test ./...
```

## Targets in the dev-tools repository

The dev-tools repository itself uses the same modules and adds its own development/documentation targets:

| Target            | Behavior                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| `make current`    | Show the current dev-tools semantic version                                                             |
| `make patch`      | Create the next patch release tag                                                                       |
| `make minor`      | Create the next minor release tag                                                                       |
| `make major`      | Create the next major release tag                                                                       |
| `make push`       | Push local tags                                                                                         |
| `make help`       | Show generated Make help                                                                                |
| `make test`       | Run the complete Python unit test suite                                                                 |
| `make site`       | Build this documentation with Lore                                                                      |
| `make site-serve` | Build the documentation for localhost and serve it on the persistent `dev-port` assignment named `site` |
