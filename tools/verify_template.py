#!/usr/bin/env python3
"""Check this repository against the Obsidian sample-plugin template.

Every tracked file in this repository is compared, by SHA-256, against the
same file in obsidianmd/obsidian-sample-plugin at commit 7112f01 -- the
template revision current when this repository was created on 2023-08-28.

A full MATCH set means no plugin code has been written yet: the repository is
still the unmodified template. Run it after writing code to see the set shrink.

    python3 tools/verify_template.py

Exit status is 0 when the comparison completes, regardless of the result.
Standard library only.
"""

import hashlib
import pathlib
import sys

# obsidianmd/obsidian-sample-plugin @ 7112f01bc6e20f4d6884c71aa2ecf8f6f1f8e3c7
# authored 2023-07-25, the newest template commit preceding this repo's
# "Initial commit" of 2023-08-28 18:46:20 +0200.
UPSTREAM_COMMIT = "7112f01bc6e20f4d6884c71aa2ecf8f6f1f8e3c7"
UPSTREAM_REPO = "obsidianmd/obsidian-sample-plugin"

TEMPLATE_SHA256 = {
    ".editorconfig":      "d5ff47f51fb78124dcc2f99c7b22e6144350936035b290176c7965dd39e82173",
    ".eslintignore":      "03ec2e0933d91ddd57ccec1f3088988f829ca5a4da63ba562167e38ad9eebe3b",
    ".eslintrc":          "879acb8f952ae6ad10658ce2a43ad749c7a36ec9a431b0cdfbb055488c08b083",
    ".gitignore":         "c59322ab1457f9f2f571dd006e59fc58a1956228ba385a29f4601d7ec26a9d6a",
    ".npmrc":             "1e8648fe5564177375a935f6b444a6f9661fa61da625477745929f146162b4dd",
    "README.md":          "7e939a2bb7dca9a28225c5d7b2ce5ac7f91b8064026df3ffaf6d23904d90326e",
    "esbuild.config.mjs": "ba6e5c2d1de1a9636fcebaafd300ccf709147002dce0f349b83f83960a162298",
    "main.ts":            "b42c02dc92d4c14fe246e30617da1af7152ac022a0bd675c136865217aa688e8",
    "manifest.json":      "299d88187a4b3285a99e4940c3406b945daf3d9291b52dc8aeafdab327d185cc",
    "package.json":       "069a320b3cf480c6406d5177974344bfcf1aec2ddb91678e16ebac5a26e0c4fc",
    "styles.css":         "8764243cae0351ebdbb76e770c4feffcb1956ff42420d4ec159212dc7a8535ed",
    "tsconfig.json":      "d473ab32eebcbdf29c8966d0348a58208deaef6cb0e89bc7c9ee65feaa57716e",
    "version-bump.mjs":   "01bbe9f80b1b50986c45d826c7a41141e624ab59daa2535f11a57ce018705ced",
    "versions.json":      "054131a088e6916447d323250004f0c7192069ac534d9e864214f82410c6a1f2",
}

ROOT = pathlib.Path(__file__).resolve().parent.parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    print(f"Comparing against {UPSTREAM_REPO} @ {UPSTREAM_COMMIT[:7]}\n")
    print(f"{'file':<22} {'result':<10} sha256")
    print("-" * 78)

    identical = missing = changed = 0
    for name, expected in sorted(TEMPLATE_SHA256.items()):
        path = ROOT / name
        if not path.is_file():
            print(f"{name:<22} {'ABSENT':<10} -")
            missing += 1
            continue
        actual = sha256(path)
        if actual == expected:
            print(f"{name:<22} {'MATCH':<10} {actual[:16]}...")
            identical += 1
        else:
            print(f"{name:<22} {'MODIFIED':<10} {actual[:16]}...")
            changed += 1

    total = len(TEMPLATE_SHA256)
    print("-" * 78)
    print(f"{identical}/{total} identical, {changed} modified, {missing} absent")

    new_files = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.iterdir()
        if p.is_file() and p.name not in TEMPLATE_SHA256
    )
    if new_files:
        print(f"\nnot part of the template: {', '.join(new_files)}")

    print()
    if identical == total:
        print("VERDICT: unmodified template. No plugin code has been written.")
    else:
        print(f"VERDICT: {changed + missing} of {total} template files have diverged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
