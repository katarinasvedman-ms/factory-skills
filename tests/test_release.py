import json
import zipfile

import pytest

from tools.skills import build, bump_versions, file_hashes, validate


def test_release_is_reproducible_and_contains_resources(library, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert build(library, a) == build(library, b)
    assert a.with_suffix(".zip").read_bytes() == b.with_suffix(".zip").read_bytes()
    with zipfile.ZipFile(a.with_suffix(".zip")) as archive:
        assert "skills/dotnet-development/references/validation.md" in archive.namelist()


@pytest.mark.parametrize("defect", ["dependency", "cycle", "duplicate", "resource", "evaluation"])
def test_invalid_library_is_rejected(library, defect):
    catalog = json.loads((library / "catalog.json").read_text())
    if defect == "dependency":
        catalog["skills"][0]["dependencies"] = ["missing"]
    elif defect == "cycle":
        catalog["skills"][0]["dependencies"] = [catalog["skills"][0]["id"]]
    elif defect == "duplicate":
        catalog["skills"].append(catalog["skills"][0])
    elif defect == "resource":
        (library / "skills/dotnet-development/references/validation.md").unlink()
    else:
        (library / "evaluations.json").write_text("[]")
    (library / "catalog.json").write_text(json.dumps(catalog))
    with pytest.raises(ValueError):
        validate(library)


def test_changed_resource_changes_release_digest(library, tmp_path):
    a = build(library, tmp_path / "a")
    resource = library / "skills/dotnet-development/references/validation.md"
    resource.write_text(resource.read_text() + "\nExtra validation.\n")
    b = build(library, tmp_path / "b")
    assert (
        a["skills"]["dotnet-development"]["sha256"] != b["skills"]["dotnet-development"]["sha256"]
    )


def published(library):
    return {
        "release": {
            "skills": {
                entry["id"]: {
                    "catalog_version": entry["version"],
                    "files": file_hashes(library / entry["path"]),
                }
                for entry in validate(library)["skills"]
            }
        }
    }


@pytest.mark.parametrize("resource", ["SKILL.md", "references/validation.md"])
def test_ci_bumps_only_changed_skill_and_preserves_metadata(library, resource):
    baseline = published(library)
    before = validate(library)
    evaluations = (library / "evaluations.json").read_bytes()
    path = library / "skills/dotnet-development" / resource
    path.write_text(path.read_text() + "\nAdditional guidance.\n")
    updates = bump_versions(library, baseline)
    entry = next(item for item in before["skills"] if item["id"] == "dotnet-development")
    major, minor, patch = entry["version"].split(".")
    number = f"{major}.{minor}.{int(patch) + 1}"
    assert updates == {"dotnet-development": {"before": entry["version"], "after": number}}
    entry["version"] = number
    assert validate(library) == before
    assert (library / "evaluations.json").read_bytes() == evaluations
    once = (library / "catalog.json").read_bytes()
    assert bump_versions(library, baseline) == {}
    assert (library / "catalog.json").read_bytes() == once


def test_ci_detects_deleted_supporting_resources(library):
    baseline = published(library)
    path = library / "skills/dotnet-development/references/unused.md"
    path.write_text("Old supplemental guidance.")
    baseline["release"]["skills"]["dotnet-development"]["files"] = file_hashes(path.parent.parent)
    path.unlink()
    assert set(bump_versions(library, baseline)) == {"dotnet-development"}


def test_ci_keeps_explicit_higher_version(library):
    baseline = published(library)
    catalog = validate(library)
    entry = catalog["skills"][0]
    major, minor, patch = map(int, entry["version"].split("."))
    entry["version"] = f"{major}.{minor + 1}.{patch}"
    (library / "catalog.json").write_text(json.dumps(catalog))
    path = library / entry["path"] / "SKILL.md"
    path.write_text(path.read_text() + "\nExplicit minor release.\n")
    before = (library / "catalog.json").read_bytes()
    assert bump_versions(library, baseline) == {}
    assert (library / "catalog.json").read_bytes() == before


@pytest.mark.parametrize("first_release", [False, True])
def test_ci_does_not_rewrite_unchanged_or_initial_catalog(library, first_release):
    baseline = None if first_release else published(library)
    before = (library / "catalog.json").read_bytes()
    assert bump_versions(library, baseline) == {}
    assert (library / "catalog.json").read_bytes() == before


@pytest.mark.parametrize("defect", ["downgrade", "invalid-skill"])
def test_ci_rejects_bad_source_without_writing_catalog(library, defect):
    baseline = published(library)
    if defect == "downgrade":
        baseline["release"]["skills"]["dotnet-development"]["catalog_version"] = "999.0.0"
    else:
        (library / "skills/dotnet-development/SKILL.md").write_text("Missing frontmatter.")
    before = (library / "catalog.json").read_bytes()
    with pytest.raises(ValueError):
        bump_versions(library, baseline)
    assert (library / "catalog.json").read_bytes() == before
