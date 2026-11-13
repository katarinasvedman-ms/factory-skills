import json
import zipfile

import pytest

from tools.skills import build, validate


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
