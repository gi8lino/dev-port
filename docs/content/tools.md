# Executable tools

The release ships seven standalone executable helpers. Maintained source scripts live under `scripts/`; release assets use the short executable names shown here.

The Python tools require Python 3.8 or newer and use only the standard library. `favicon-generate` additionally invokes `rsvg-convert` from librsvg.

## dev-port

`dev-port` provides persistent, named TCP ports for local development.

```sh
./scripts/dev-port postgres
./scripts/dev-port app
./scripts/dev-port pdf
```

The first lookup asks the operating system for an available loopback port and saves it by name. Later calls return the saved assignment, including while the corresponding service is running.

Each project's current directory gets its own `.dev-ports.json` by default. Use `--file PATH` to choose another state file.

```sh
./scripts/dev-port postgres              # Get or allocate a port
./scripts/dev-port postgres --port 5433  # Save a fixed port
./scripts/dev-port --reset               # Clear assignments after stopping services
./scripts/dev-port --version
```

Fixed ports are validated but are not checked for availability. Two service names in one state file cannot share a port.

A saved port is never silently changed merely because another process occupies it. Stop the conflicting service or explicitly update the assignment.

Allocated ports are released immediately; `dev-port` does not reserve them between lookup and service startup. Separate projects use independent state files rather than a global reservation pool.

A separate lock file serializes concurrent readers and writers. State is replaced atomically. Invalid JSON or invalid assignments produce an error without silently replacing the state; `--reset` explicitly clears it. Do not delete the lock file while callers are running.

## open-browser

`open-browser` waits for an HTTP or HTTPS endpoint to respond, then opens it in the default browser.

```sh
./scripts/open-browser http://127.0.0.1:8080/
./scripts/open-browser --timeout 30 http://127.0.0.1:8080/
./scripts/open-browser --version
```

Any HTTP response proves the endpoint is reachable, including responses such as `401` or `404`. Connection failures are retried until the timeout expires.

This is useful for development targets that start a server and browser together without racing the browser against application startup.

## dev-tag

`dev-tag` creates lightweight semantic-version Git tags using the latest valid `X.Y.Z` tag in the repository. The default prefix is `v`.

```sh
./scripts/dev-tag current
./scripts/dev-tag patch
./scripts/dev-tag minor
./scripts/dev-tag major
./scripts/dev-tag --prefix "" patch
```

With no matching tags, `current` prints `0.0.0` and the first patch tag is `v0.0.1`.

Unrelated tags and non-semantic-version tags are ignored. `dev-tag` creates tags locally; pushing them remains an explicit operation.

The [tagging Make module](make-modules.md) wraps these commands as `make current`, `make patch`, `make minor`, `make major`, and `make push`.

## make-help

`make-help` generates Makefile help from targets documented with `##` and section headings documented with `##@`.

```makefile
.DEFAULT_GOAL := help

##@ Development

.PHONY: test
test: ## Run all tests.
	python3 -m unittest discover -s tests -v

.PHONY: help
help: ## Display this help.
	@make-help $(MAKEFILE_LIST)
```

Running `make` or `make help` can then produce grouped output such as:

```text
Usage:
  make <target>

Development
  test                 Run all tests.

General
  help                 Display this help.
```

Multiple Makefiles may be passed explicitly. The shared help module automatically passes `$(MAKEFILE_LIST)`, so documented targets from included feature modules are visible as well.

## go-install-tool

`go-install-tool` installs a pinned Go tool into a local bin directory, keeps a versioned binary, and links a stable binary name to it.

```sh
./scripts/go-install-tool \
  --target ./bin/golangci-lint \
  --package github.com/golangci/golangci-lint/v2/cmd/golangci-lint \
  --tool-version v2.13.2
```

The example creates `bin/golangci-lint-v2.13.2` and links `bin/golangci-lint` to it. An existing versioned binary is reused instead of being downloaded again.

See [Installing Go tools](make-modules.md) for the corresponding Make pattern.

## github-release-install

`github-release-install` installs a platform-specific executable from a GitHub release while keeping a stable target name. It detects macOS/Linux and amd64/arm64, expands the release asset template, stores the binary under a versioned name, and points the requested target at that version with a relative symlink.

For an archive such as Lore:

```sh
./scripts/github-release-install \
  --repo gi8lino/lore \
  --tag v0.13.0 \
  --asset 'lore_{version}_{os}_{arch}.tar.gz' \
  --binary lore \
  --target ./bin/lore
```

This produces:

```text
bin/
├── lore -> lore-v0.13.0
└── lore-v0.13.0
```

If `lore-v0.13.0` already exists, it is reused. Installing `v0.14.0` creates `lore-v0.14.0` and repoints `bin/lore`; the old version remains available for a later rollback.

The asset template supports these placeholders:

| Placeholder | Example             |
| ----------- | ------------------- |
| `{tag}`     | `v0.13.0`           |
| `{version}` | `0.13.0`            |
| `{os}`      | `darwin` or `linux` |
| `{arch}`    | `amd64` or `arm64`  |

`--binary` selects the executable inside a tar archive. Omit it when the release asset is already the executable itself.

The helper intentionally owns the versioned filename and symlink. Consuming Makefiles only declare the stable target, release tag, and asset pattern.

## favicon-generate

`favicon-generate` renders PNG favicons from an SVG source with `rsvg-convert`. The caller chooses the favicon sizes and output directory; `--apple-touch` additionally creates the conventional 180x180 `apple-touch-icon.png`.

```sh
./scripts/favicon-generate \
  --apple-touch \
  web/src/assets/favicon.svg \
  web/static \
  16x16 32x32
```

This produces `favicon-16x16.png`, `favicon-32x32.png`, and `apple-touch-icon.png` in the output directory. Sizes must use `WIDTHxHEIGHT` with positive integers.

By default the tool runs `rsvg-convert`. Override it with `SVG_CONVERT` or `--converter` when librsvg is installed elsewhere:

```sh
SVG_CONVERT=/opt/homebrew/bin/rsvg-convert \
  ./scripts/favicon-generate favicon.svg public/icons 16x16 32x32
```

Projects can download it through the existing core helper without adding another Make module:

```makefile
FAVICON_GENERATE := $(DEV_TOOLS_BIN)/favicon-generate

$(FAVICON_GENERATE): | $(DEV_TOOLS_BIN)
	$(call download-dev-tool,favicon-generate,$@)

.PHONY: favicons
favicons: $(FAVICON_GENERATE)
	$(call run-tool,$(FAVICON_GENERATE),\
		--apple-touch \
		web/src/assets/favicon.svg \
		web/static \
		16x16 32x32)
```
