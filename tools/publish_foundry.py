from __future__ import annotations

import argparse
import io
import json
import re
import zipfile
from pathlib import Path

from tools.skills import digest, file_hashes, validate


def destination(endpoint: str, toolbox: str) -> str:
    endpoint = endpoint.rstrip("/")
    if not re.fullmatch(
        r"https://[a-zA-Z0-9-]+\.services\.ai\.azure\.com/api/projects/[a-zA-Z0-9_-]+",
        endpoint,
    ) or not re.fullmatch(r"[a-zA-Z0-9_-]+", toolbox):
        raise ValueError("Invalid public-cloud Foundry project endpoint or toolbox")
    return endpoint


def package_skill(directory: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as package:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                package.writestr(path.relative_to(directory).as_posix(), path.read_bytes())
    return buffer.getvalue()


def version(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value):
        raise ValueError("Foundry versions must be explicit numeric strings")
    return value


def verify_package(content: bytes, name: str, expected: dict) -> None:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        files = [item for item in archive.infolist() if not item.is_dir()]
        if len(files) > 2048 or sum(item.file_size for item in files) > 20 * 1024 * 1024:
            raise ValueError("Foundry skill package exceeds verification limits")
        names = [item.filename for item in files]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate files in Foundry skill package")
        prefix = "" if "SKILL.md" in names else name + "/"
        if not all(path.startswith(prefix) for path in names):
            raise ValueError("Unsupported Foundry skill package layout")
        actual = {item.filename[len(prefix) :]: digest(archive.read(item)) for item in files}
    if actual != expected:
        raise ValueError(f"Foundry package integrity mismatch: {name}")


def publish(root: Path, endpoint: str, toolbox: str, request) -> dict:
    endpoint = destination(endpoint, toolbox)
    catalog = validate(root)
    versions = {}
    for entry in catalog["skills"]:
        directory = root / entry["path"]
        response = request(
            "POST",
            f"{endpoint}/skills/{entry['id']}/versions?api-version=v1",
            files={"files": (entry["id"] + ".zip", package_skill(directory), "application/zip")},
        )
        versions[entry["id"]] = response["version"]
    response = request(
        "POST",
        f"{endpoint}/toolboxes/{toolbox}/versions?api-version=v1",
        json={
            "description": "Approved factory skills; all references are pinned.",
            "tools": [],
            "skills": [
                {"type": "skill_reference", "name": name, "version": version}
                for name, version in versions.items()
            ],
        },
    )
    return {
        "project_endpoint": endpoint,
        "toolbox": toolbox,
        "version": response["version"],
        "skills": versions,
    }


def publish_roles(
    root: Path,
    endpoint: str,
    identities: dict,
    request,
    *,
    source_commit: str,
    baseline: dict | None = None,
) -> dict:
    endpoint = destination(endpoint, "factory-skills")
    catalog = validate(root)
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("Publication requires a full source commit SHA")
    roles = sorted({role for entry in catalog["skills"] for role in entry["roles"]})
    for role in roles:
        identity = identities.get(role, {})
        if any(
            not isinstance(identity.get(key), str)
            or not re.fullmatch(
                r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", identity[key]
            )
            for key in ("tenant_id", "client_id", "principal_id")
        ):
            raise ValueError(f"Explicit Entra identity is required for role: {role}")
    if len({identities[role]["principal_id"].lower() for role in roles}) != len(roles):
        raise ValueError("Each role requires a distinct Entra principal")
    baseline = baseline or {"roles": {}, "release": {"skills": {}}}
    for role, binding in baseline["roles"].items():
        if binding["project_endpoint"] != endpoint or binding["toolbox"] != f"{role}-skills":
            raise ValueError("Baseline must belong to this project's role toolboxes")
    previous = baseline["release"]["skills"]
    records, uploads, pins = {}, [], {}
    # Check every version before making any remote mutation.
    for entry in catalog["skills"]:
        name = entry["id"]
        hashes = file_hashes(root / entry["path"])
        old = previous.get(name)
        if old:
            current_number = tuple(map(int, entry["version"].split(".")))
            old_number = tuple(map(int, old["catalog_version"].split(".")))
            if current_number < old_number or (
                hashes != old["files"] and current_number <= old_number
            ):
                raise ValueError(f"Changed skill requires a version increment: {name}")
        records[name] = {"catalog_version": entry["version"], "files": hashes}
        if old and hashes == old["files"]:
            pins[name] = version(old["foundry_version"])
        else:
            uploads.append(entry)
    for entry in uploads:
        name = entry["id"]
        print(f"Uploading changed skill: {name}", flush=True)
        response = request(
            "POST",
            f"{endpoint}/skills/{name}/versions?api-version=v1",
            files={
                "files": (name + ".zip", package_skill(root / entry["path"]), "application/zip")
            },
        )
        pins[name] = version(response["version"])
    for name in sorted(pins):
        content = request(
            "GET",
            f"{endpoint}/skills/{name}/versions/{pins[name]}/content?api-version=v1",
        )
        verify_package(content, name, records[name]["files"])
        records[name]["foundry_version"] = pins[name]
        print(f"Verified skill package: {name}@{pins[name]}", flush=True)
    bindings, changed = {}, []
    for role in roles:
        name = f"{role}-skills"
        selected = {
            entry["id"]: pins[entry["id"]] for entry in catalog["skills"] if role in entry["roles"]
        }
        old = baseline["roles"].get(role)
        if old and old["skills"] == selected:
            number = version(old["version"])
        else:
            response = request(
                "POST",
                f"{endpoint}/toolboxes/{name}/versions?api-version=v1",
                json={
                    "description": f"Factory {role}; source {source_commit}.",
                    "tools": [],
                    "skills": [
                        {"type": "skill_reference", "name": skill, "version": pin}
                        for skill, pin in sorted(selected.items())
                    ],
                },
            )
            number = version(response["version"])
            changed.append(role)
        actual = request("GET", f"{endpoint}/toolboxes/{name}/versions/{number}?api-version=v1")
        references = actual["skills"]
        if (
            actual.get("tools")
            or len(references) != len(selected)
            or any(item["type"] != "skill_reference" for item in references)
            or {item["name"]: item["version"] for item in references} != selected
        ):
            raise ValueError(f"Published role toolbox differs from approved pins: {role}")
        bindings[role] = {
            "project_endpoint": endpoint,
            "toolbox": name,
            "version": number,
            "skills": selected,
            "identity": identities[role],
        }
        print(f"Verified role toolbox: {name}@{number}", flush=True)
    return {
        "roles": bindings,
        "release": {
            "source_commit": source_commit,
            "skills": records,
            "uploaded_skills": [entry["id"] for entry in uploads],
            "changed_toolboxes": changed,
            "verification": "Downloaded package hashes and exact role toolbox references matched",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish immutable Foundry skills and toolbox version"
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--endpoint", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--toolbox")
    mode.add_argument("--role-identities", type=Path, help="Publish role-filtered toolboxes")
    parser.add_argument("--baseline", type=Path, help="Previous approved role bindings")
    parser.add_argument("--source-commit", help="Full approved source commit for a role release")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--publish",
        action="store_true",
        required=True,
        help="Explicit consent to creating remote versions",
    )
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output binding already exists; choose a fresh path")
    if args.role_identities and not args.source_commit:
        parser.error("--source-commit is required for role releases")
    if args.baseline and not args.role_identities:
        parser.error("--baseline requires --role-identities")
    import httpx
    from azure.identity import DefaultAzureCredential

    with DefaultAzureCredential(exclude_interactive_browser_credential=True) as credential:
        with httpx.Client(timeout=60, follow_redirects=False) as client:

            def request(method, url, **kwargs):
                token = credential.get_token("https://ai.azure.com/.default").token
                response = client.request(
                    method,
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Foundry-Features": "Skills=V1Preview",
                    },
                    **kwargs,
                )
                if not response.is_success:
                    raise ValueError(f"Foundry publication failed: HTTP {response.status_code}")
                return response.content if "/content?" in url else response.json()

            if args.role_identities:
                binding = publish_roles(
                    args.root,
                    args.endpoint,
                    json.loads(args.role_identities.read_text(encoding="utf-8")),
                    request,
                    source_commit=args.source_commit,
                    baseline=(
                        json.loads(args.baseline.read_text(encoding="utf-8"))
                        if args.baseline
                        else None
                    ),
                )
            else:
                binding = publish(args.root, args.endpoint, args.toolbox, request)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    print("Published immutable versions; binding written. Existing toolbox defaults unchanged.")


if __name__ == "__main__":
    main()
