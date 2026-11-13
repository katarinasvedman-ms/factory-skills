from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import jsonschema
import yaml


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def file_hashes(directory: Path) -> dict[str, str]:
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = digest(path.read_bytes())
    return result


def validate(root: Path) -> dict:
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    schema = json.loads((root / "catalog.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(catalog, schema)
    entries = catalog["skills"]
    by_id = {entry["id"]: entry for entry in entries}
    if len(by_id) != len(entries):
        raise ValueError("Duplicate skill identifier")
    folders = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    if folders != set(by_id):
        raise ValueError("Catalog and skill directories must match")
    for entry in entries:
        name = entry["id"]
        if entry["path"] != f"skills/{name}":
            raise ValueError(f"Noncanonical skill path: {name}")
        directory = root / entry["path"]
        file_hashes(directory)
        text = (directory / "SKILL.md").read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError(f"Missing frontmatter: {name}")
        front = yaml.safe_load(parts[1])
        if front.get("name") != name or not isinstance(front.get("description"), str):
            raise ValueError(f"Invalid frontmatter: {name}")
        if not 1 <= len(front["description"]) <= 1024 or not parts[2].strip():
            raise ValueError(f"Missing description or instructions: {name}")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", parts[2]):
            if "://" in link or link.startswith("#"):
                continue
            linked = (directory / link).resolve()
            if not linked.is_relative_to(directory.resolve()) or not linked.is_file():
                raise ValueError(f"Missing or unsafe resource: {name}: {link}")
    visited, active = set(), set()

    def visit(name: str) -> None:
        if name not in by_id:
            raise ValueError(f"Missing dependency: {name}")
        if name in active:
            raise ValueError(f"Cyclic dependency: {name}")
        if name in visited:
            return
        active.add(name)
        for dependency in by_id[name]["dependencies"]:
            visit(dependency)
        active.remove(name)
        visited.add(name)

    for name in by_id:
        visit(name)
    evaluations = json.loads((root / "evaluations.json").read_text(encoding="utf-8"))
    if {case["skill"] for case in evaluations} != set(by_id):
        raise ValueError("Each skill needs a behavioral evaluation fixture")
    for case in evaluations:
        if not all(case.get(key) for key in ("task", "expected", "negative_task")):
            raise ValueError(f"Incomplete evaluation: {case['skill']}")
    return catalog


def build(root: Path, output: Path) -> dict:
    catalog = validate(root)
    output = output.resolve()
    if output.exists():
        raise ValueError("Release output already exists; choose a fresh directory")
    if root.resolve().is_relative_to(output):
        raise ValueError("Release output cannot contain the source repository")
    output.mkdir(parents=True)
    shutil.copyfile(root / "catalog.json", output / "catalog.json")
    records = {}
    for entry in catalog["skills"]:
        source = root / entry["path"]
        target = output / entry["path"]
        shutil.copytree(source, target)
        files = file_hashes(target)
        records[entry["id"]] = {
            "version": entry["version"],
            "sha256": digest(canonical(files)),
            "files": files,
        }
    release = {
        "schema_version": 1,
        "catalog_sha256": digest((output / "catalog.json").read_bytes()),
        "skills": records,
    }
    (output / "release.json").write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
    archive = output.with_suffix(".zip")
    if archive.exists():
        raise ValueError("Release archive already exists")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(output).as_posix(), (2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, path.read_bytes())
    return release


def bump_versions(root: Path, binding: dict | None) -> dict:
    catalog = validate(root)
    previous = binding["release"]["skills"] if binding else {}
    updates = {}
    for entry in catalog["skills"]:
        name = entry["id"]
        old = previous.get(name)
        if old is None:
            continue
        before = tuple(map(int, old["catalog_version"].split(".")))
        current = tuple(map(int, entry["version"].split(".")))
        if current < before:
            raise ValueError(f"Catalog version is older than the published version: {name}")
        if file_hashes(root / entry["path"]) != old["files"] and current == before:
            number = f"{before[0]}.{before[1]}.{before[2] + 1}"
            updates[name] = {"before": entry["version"], "after": number}
            entry["version"] = number
    if updates:
        (root / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return updates


def verify_changes(root: Path, baseline: str) -> None:
    if not re.fullmatch(r"[a-f0-9]{40}", baseline):
        raise ValueError("Baseline must be a full commit SHA")
    previous = subprocess.run(
        ["git", "-C", str(root), "show", f"{baseline}:catalog.json"],
        capture_output=True,
        check=False,
    )
    if previous.returncode:
        # The initial commit has no skill catalog to compare with.
        return
    old = {entry["id"]: entry for entry in json.loads(previous.stdout)["skills"]}
    new = {entry["id"]: entry for entry in validate(root)["skills"]}
    changed = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", baseline, "--", "skills"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    names = {path.split("/")[1] for path in changed if len(path.split("/")) >= 3}
    for name in names & old.keys() & new.keys():
        before = tuple(map(int, old[name]["version"].split(".")))
        after = tuple(map(int, new[name]["version"].split(".")))
        if after <= before:
            raise ValueError(f"Changed skill must increment its version: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "build", "version"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("dist/release"))
    parser.add_argument("--baseline", help="Reject changed skills without a version increment")
    parser.add_argument(
        "--release-binding", type=Path, help="Last promoted Foundry binding for automatic versions"
    )
    args = parser.parse_args()
    if args.command == "build":
        build(args.root, args.output)
    elif args.command == "version":
        binding = (
            json.loads(args.release_binding.read_text(encoding="utf-8"))
            if args.release_binding
            else None
        )
        print(json.dumps(bump_versions(args.root, binding), indent=2))
    else:
        validate(args.root)
        if args.baseline:
            verify_changes(args.root, args.baseline)
    print(f"{args.command}: OK")


if __name__ == "__main__":
    main()
