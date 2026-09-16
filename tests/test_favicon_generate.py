#!/usr/bin/env python3
"""Exercise favicon generation without requiring librsvg."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class FaviconGenerateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.helper = Path(__file__).resolve().parent.parent / "scripts" / "favicon-generate"
        self.svg = self.root / "icon.svg"
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"/>\n')
        self.output = self.root / "icons"
        self.converter = self.root / "rsvg-convert"
        self.converter.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "output=\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  case \"$1\" in\n"
            "    --width|--height) shift 2 ;;\n"
            "    --keep-aspect-ratio) shift ;;\n"
            "    --output) output=$2; shift 2 ;;\n"
            "    *) shift ;;\n"
            "  esac\n"
            "done\n"
            "printf 'png\\n' > \"$output\"\n"
        )
        self.converter.chmod(0o755)

    def call(self, *args, check=True, env=None):
        return subprocess.run(
            [sys.executable, str(self.helper), *args],
            text=True,
            capture_output=True,
            check=check,
            env=env,
        )

    def generate(self, *args, check=True):
        return self.call(
            "--converter", str(self.converter),
            *args,
            check=check,
        )

    def test_creates_requested_favicons(self):
        result = self.generate(str(self.svg), str(self.output), "16x16", "32x32")

        self.assertTrue((self.output / "favicon-16x16.png").is_file())
        self.assertTrue((self.output / "favicon-32x32.png").is_file())
        self.assertFalse((self.output / "apple-touch-icon.png").exists())
        self.assertIn(f"create {self.output / 'favicon-16x16.png'}", result.stdout)

    def test_apple_touch_icon_is_explicit(self):
        self.generate("--apple-touch", str(self.svg), str(self.output), "32x32")

        self.assertTrue((self.output / "favicon-32x32.png").is_file())
        self.assertTrue((self.output / "apple-touch-icon.png").is_file())

    def test_rejects_invalid_size(self):
        result = self.generate(str(self.svg), str(self.output), "32", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("size must use WIDTHxHEIGHT", result.stderr)
        self.assertFalse(self.output.exists())

    def test_missing_svg_fails(self):
        result = self.generate(str(self.root / "missing.svg"), str(self.output), "32x32", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing icon SVG", result.stderr)

    def test_svg_convert_environment_variable_is_supported(self):
        env = os.environ.copy()
        env["SVG_CONVERT"] = str(self.converter)
        self.call(str(self.svg), str(self.output), "32x32", env=env)

        self.assertTrue((self.output / "favicon-32x32.png").is_file())

    def test_empty_converter_output_fails(self):
        self.converter.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "output=\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  case \"$1\" in\n"
            "    --output) output=$2; shift 2 ;;\n"
            "    --width|--height) shift 2 ;;\n"
            "    --keep-aspect-ratio) shift ;;\n"
            "    *) shift ;;\n"
            "  esac\n"
            "done\n"
            ": > \"$output\"\n"
        )
        self.converter.chmod(0o755)

        result = self.generate(str(self.svg), str(self.output), "32x32", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not create icon", result.stderr)

    def test_version(self):
        result = self.call("--version")

        self.assertEqual(result.stdout.strip(), "favicon-generate __VERSION__")


if __name__ == "__main__":
    unittest.main()
