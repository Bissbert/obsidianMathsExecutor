#!/usr/bin/env python3
"""Reproduce every number quoted in this repository's documentation.

Measures source size, then runs the type check, the linter and the production
build, reporting each exit code and the size of the bundle they produce.

    python3 tools/measure.py

Requires `npm install` to have been run first. Standard library only; the
toolchain itself comes from devDependencies.
"""

import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

SOURCES = [
    "main.ts",
    "styles.css",
    "manifest.json",
    "package.json",
    "tsconfig.json",
    "esbuild.config.mjs",
    "version-bump.mjs",
    "versions.json",
]

STEPS = [
    ("type check", ["npx", "tsc", "-noEmit", "-skipLibCheck"]),
    ("lint", ["npx", "eslint", "main.ts"]),
    ("production build", ["npm", "run", "build"]),
]

DEPS = [
    "obsidian",
    "typescript",
    "esbuild",
    "eslint",
    "@typescript-eslint/parser",
    "tslib",
    "builtin-modules",
    "@types/node",
]


def run(cmd):
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, time.monotonic() - start, proc


def section(title):
    print(f"\n## {title}\n")


def main():
    if not (ROOT / "node_modules").is_dir():
        print("node_modules is missing -- run `npm install` first.", file=sys.stderr)
        return 1

    section("Source size")
    print(f"| {'File':<20} | {'Bytes':>6} | {'Lines':>5} |")
    print(f"|{'-' * 22}|{'-' * 8}:|{'-' * 7}:|")
    for name in SOURCES:
        path = ROOT / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        print(f"| `{name}`{'':<{max(0, 18 - len(name))}} | {len(data):>6} | "
              f"{data.count(10):>5} |")

    section("Resolved toolchain")
    print(f"| {'Package':<26} | Version |")
    print(f"|{'-' * 28}|{'-' * 9}|")
    for dep in DEPS:
        meta = ROOT / "node_modules" / dep / "package.json"
        version = json.loads(meta.read_text())["version"] if meta.is_file() else "n/a"
        print(f"| `{dep}`{'':<{max(0, 24 - len(dep))}} | {version} |")

    section("Toolchain runs")
    bundle = ROOT / "main.js"
    bundle.unlink(missing_ok=True)

    print(f"| {'Step':<18} | Exit | Seconds | Output |")
    print(f"|{'-' * 20}|{'-' * 6}:|{'-' * 9}:|{'-' * 8}|")
    failures = 0
    for label, cmd in STEPS:
        code, secs, proc = run(cmd)
        failures += code != 0
        noise = (proc.stdout + proc.stderr).strip()
        # npm echoes the script banner on success; that is not a diagnostic.
        lines = [l for l in noise.splitlines()
                 if l.strip() and not l.startswith(">")]
        summary = "clean" if code == 0 and not lines else f"{len(lines)} line(s)"
        print(f"| {label:<18} | {code:>4} | {secs:>7.1f} | {summary} |")
        if lines:
            for line in lines:
                print(f"      {line}")

    section("Build artefact")
    if bundle.is_file():
        size = bundle.stat().st_size
        print(f"`main.js`: {size} bytes ({size / 1024:.1f} KiB)")
    else:
        print("`main.js` was not produced.")

    print()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
