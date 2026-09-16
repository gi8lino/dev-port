#!/usr/bin/env python3
"""Exercise SVG to PNG conversion without requiring librsvg."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class SvgToPngTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.helper = Path(__file__).resolve().parent.parent / "scripts" / "svg-to-png"
        self.svg = self.root / "logo.svg"
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 512"/>\n')
        self.output = self.root / "images" / "logo.png"
        self.args_file = self.root / "converter-args"
        self.converter = self.root / "rsvg-convert"
        self.converter.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "printf '%s\\n' \"$@\" > \"$SVG_TO_PNG_TEST_ARGS\"\n"
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
        environment = os.environ.copy()
        environment["SVG_TO_PNG_TEST_ARGS"] = str(self.args_file)
        if env is not None:
            environment.update(env)
        return subprocess.run(
            [sys.executable, str(self.helper), *args],
            text=True,
            capture_output=True,
            check=check,
            env=environment,
        )

    def convert(self, *args, check=True):
        return self.call("--converter", str(self.converter), *args, check=check)

    def converter_args(self):
        return self.args_file.read_text().splitlines()

    def test_width_only_creates_png(self):
        result = self.convert("--width", "1200", str(self.svg), str(self.output))

        self.assertTrue(self.output.is_file())
        self.assertIn(f"create {self.output}", result.stdout)
        self.assertEqual(
            self.converter_args(),
            ["--width", "1200", "--keep-aspect-ratio", "--output", str(self.output), str(self.svg)],
        )

    def test_height_only_is_supported(self):
        self.convert("--height", "512", str(self.svg), str(self.output))

        self.assertEqual(
            self.converter_args(),
            ["--height", "512", "--keep-aspect-ratio", "--output", str(self.output), str(self.svg)],
        )

    def test_width_and_height_are_supported(self):
        self.convert("--width", "1200", "--height", "512", str(self.svg), str(self.output))

        self.assertEqual(
            self.converter_args(),
            [
                "--width", "1200",
                "--height", "512",
                "--keep-aspect-ratio",
                "--output", str(self.output),
                str(self.svg),
            ],
        )

    def test_dimension_is_required(self):
        result = self.convert(str(self.svg), str(self.output), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("set --width, --height, or both", result.stderr)
        self.assertFalse(self.output.exists())

    def test_dimension_must_be_positive(self):
        result = self.convert("--width", "0", str(self.svg), str(self.output), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dimension must be a positive integer", result.stderr)

    def test_missing_svg_fails(self):
        result = self.convert("--width", "1200", str(self.root / "missing.svg"), str(self.output), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing SVG", result.stderr)

    def test_svg_convert_environment_variable_is_supported(self):
        self.call(
            "--width", "1200", str(self.svg), str(self.output),
            env={"SVG_CONVERT": str(self.converter)},
        )

        self.assertTrue(self.output.is_file())

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

        result = self.convert("--width", "1200", str(self.svg), str(self.output), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("could not create PNG", result.stderr)

    def test_version(self):
        result = self.call("--version")

        self.assertEqual(result.stdout.strip(), "svg-to-png __VERSION__")


if __name__ == "__main__":
    unittest.main()
