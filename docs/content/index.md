# dev-tools

`dev-tools` is a small collection of reusable development helpers for macOS and Linux. Executable tools are written with the Python standard library, while the GNU Make integration is split into a small core and optional feature modules.

The goal is to keep project Makefiles readable: commit one bootstrap file, include the capabilities the project needs, and let the pinned release provide the rest.

## Make modules

| Module  | Purpose                                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------------------ |
| Core    | Shared download helpers, versioned cache, readable local-tool execution, `go-install-tool`, and `github-release-install` |
| Tagging | Semantic-version tag targets                                                                                             |
| Ports   | Persistent named development ports                                                                                       |
| Browser | Wait for a local HTTP endpoint and open it in the default browser                                                        |
| Help    | Generate grouped Make help from `##` and `##@` comments                                                                  |

Start with [Getting started](getting-started.md), then see [Make modules and targets](make-modules.md) for the complete Make interface.

## Executable tools

The releases also contain these directly runnable tools:

- `dev-port`
- `open-browser`
- `dev-tag`
- `make-help`
- `go-install-tool`
- `github-release-install`
- `favicon-generate`

See [Executable tools](tools.md) for their command-line behavior and examples.

## Source layout

```text
make/       GNU Make modules
scripts/    executable source tools
tests/      unit tests
docs/       this Lore documentation site
```

Release assets are flat even though the source tree separates Make modules from executables.
