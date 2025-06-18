#!/usr/bin/env python3
"""GitHub Action helper to bump the patch version in `pyproject.toml`.

The script performs a minimal semantic-version bump (MAJOR.MINOR.PATCH -> MAJOR.MINOR.(PATCH+1)).
It rewrites the file in-place and prints the new version.

Usage (in a GitHub Actions step):

    - name: Bump patch version
      run: python .github/scripts/bump_patch.py

If the version string cannot be found the script exits with a non-zero status
so that the workflow fails visibly.
"""

from __future__ import annotations

import pathlib
import re
import sys

PYPROJECT_PATH = pathlib.Path(__file__).resolve().parents[2] / "pyproject.toml"

VERSION_REGEX = re.compile(r"^version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"", re.MULTILINE)


def main() -> None:  # noqa: D401
    """Increment the patch component of the version in *pyproject.toml*."""

    try:
        content = PYPROJECT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("pyproject.toml not found", file=sys.stderr)
        sys.exit(1)

    match = VERSION_REGEX.search(content)
    if match is None:
        print("Unable to locate version string in pyproject.toml", file=sys.stderr)
        sys.exit(1)

    major, minor, patch = map(int, match.groups())
    new_version = f"{major}.{minor}.{patch + 1}"

    new_content = VERSION_REGEX.sub(rf'version = "{new_version}"', content)
    PYPROJECT_PATH.write_text(new_content, encoding="utf-8")

    print(f"Bumped version to {new_version}")


if __name__ == "__main__":
    main()
