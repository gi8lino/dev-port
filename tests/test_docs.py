#!/usr/bin/env python3
"""Verify the checked-in Lore documentation structure and target coverage."""

from pathlib import Path
import unittest


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.content = self.root / "docs" / "content"

    def test_lore_site_layout(self):
        config = (self.root / "docs" / "site.toml").read_text()

        self.assertIn('site_url = "https://gi8lino.github.io/dev-tools/"', config)
        self.assertIn('source_dir = "docs/content"', config)
        self.assertIn('output_dir = "docs/site"', config)
        self.assertTrue((self.content / "index.md").is_file())

    def test_all_repository_make_targets_are_documented(self):
        documentation = (self.content / "make-modules.md").read_text()
        targets = (
            "current",
            "patch",
            "minor",
            "major",
            "push",
            "help",
            "test",
            "site",
            "site-serve",
        )

        for target in targets:
            with self.subTest(target=target):
                self.assertIn(f"`make {target}`", documentation)

    def test_readme_stays_focused_on_modules_and_bootstrap(self):
        readme = (self.root / "README.md").read_text()

        self.assertIn("## Make modules", readme)
        self.assertIn("## Quick start", readme)
        self.assertIn("https://gi8lino.github.io/dev-tools/", readme)
        self.assertNotIn("## Releases", readme)
        self.assertNotIn("## Development", readme)

    def test_lore_is_pinned_and_installed_with_shared_release_helper(self):
        makefile = (self.root / "Makefile").read_text()

        self.assertIn("depName=gi8lino/lore", makefile)
        self.assertRegex(makefile, r"(?m)^LORE_VERSION \?= v\d+\.\d+\.\d+$",)
        self.assertIn("LORE := bin/lore", makefile)
        self.assertIn("lore: $(GITHUB_RELEASE_INSTALL)", makefile)
        self.assertIn("--repo gi8lino/lore", makefile)
        self.assertIn("--tag \"$(LORE_VERSION)\"", makefile)
        self.assertIn("--asset \"$(LORE_ASSET)\"", makefile)
        self.assertIn("--target \"$(LORE)\"", makefile)
        self.assertIn("site: lore", makefile)
        self.assertIn("include make/dev-tools-port.mk", makefile)
        self.assertIn("SITE_PORT ?= $(call dev-port,site)", makefile)
        self.assertIn("site-serve: lore $(DEV_PORT)", makefile)
        self.assertNotIn("SITE_PORT ?= 8081", makefile)
        self.assertNotIn("LORE_VERSIONED", makefile)
        self.assertNotIn("ln -sf", makefile)
        self.assertNotIn("github.com/gi8lino/lore/releases/download", makefile)

    def test_github_release_installer_is_documented_and_released(self):
        tools = (self.content / "tools.md").read_text()
        release = (self.root / ".github" / "workflows" / "release.yml").read_text()
        core = (self.root / "make" / "dev-tools.mk").read_text()

        self.assertIn("## github-release-install", tools)
        self.assertIn("GITHUB_RELEASE_INSTALL :=", core)
        self.assertIn("scripts/github-release-install", release)
        self.assertIn("dist/github-release-install --version", release)

    def test_favicon_generator_is_documented_and_released(self):
        index = (self.content / "index.md").read_text()
        tools = (self.content / "tools.md").read_text()
        releases = (self.content / "releases.md").read_text()
        release = (self.root / ".github" / "workflows" / "release.yml").read_text()

        self.assertIn("`favicon-generate`", index)
        self.assertIn("## favicon-generate", tools)
        self.assertIn("SVG_CONVERT", tools)
        self.assertIn("favicon-generate", releases)
        self.assertIn("scripts/favicon-generate", release)
        self.assertIn("dist/favicon-generate --version", release)

    def test_svg_to_png_is_documented_and_released(self):
        index = (self.content / "index.md").read_text()
        tools = (self.content / "tools.md").read_text()
        releases = (self.content / "releases.md").read_text()
        release = (self.root / ".github" / "workflows" / "release.yml").read_text()

        self.assertIn("`svg-to-png`", index)
        self.assertIn("## svg-to-png", tools)
        self.assertIn("SVG_CONVERT", tools)
        self.assertIn("svg-to-png", releases)
        self.assertIn("scripts/svg-to-png", release)
        self.assertIn("dist/svg-to-png --version", release)

    def test_pages_uses_make_site_for_lore_download(self):
        workflow = (self.root / ".github" / "workflows" / "pages.yml").read_text()

        self.assertIn("run: make site", workflow)
        self.assertNotIn("Install Lore", workflow)


if __name__ == "__main__":
    unittest.main()
