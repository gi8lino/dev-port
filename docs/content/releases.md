# Releases and caching

A pushed `v*` tag creates a GitHub release containing the standalone executables, the Make integration, and a checksum file.

## Release assets

```text
dev-port
open-browser
dev-tag
make-help
go-install-tool
github-release-install
favicon-generate
dev-tools.mk
dev-tools-tag.mk
dev-tools-port.mk
dev-tools-browser.mk
dev-tools-help.mk
checksums.txt
```

The source tree keeps executables and Make modules separate:

```text
scripts/    executable source tools
make/       GNU Make module sources
```

The release intentionally flattens both directories because consuming projects download assets by their short release name.

## Embedded version

Each executable and Make module contains a `__VERSION__` placeholder in source. The release workflow replaces it with the pushed tag version, verifies the executable `--version` output and Make-module version markers, then creates SHA-256 checksums before publishing the assets.

## Consumer cache

The committed `bin/dev-tools.mk` bootstrap derives a cache directory from `DEV_TOOLS_VERSION`:

```text
bin/.dev-tools/<version>/
```

Feature modules and dev-tools executables are downloaded there. Version-specific paths make upgrades deterministic: selecting another release selects another cache instead of comparing modification times.

For example:

```text
bin/.dev-tools/
├── v0.6.0/
│   ├── dev-tools-tag.mk
│   └── dev-tag
└── v0.6.0/
    ├── dev-tools-tag.mk
    └── dev-tag
```

Keeping an older cache is harmless and allows a project to switch back without downloading those assets again.

## Creating a release

The repository uses the tagging module itself:

```sh
make current
make patch
make minor
make major
```

Tags are local until explicitly pushed:

```sh
make push
```

The GitHub release workflow runs when a `v*` tag is pushed.
