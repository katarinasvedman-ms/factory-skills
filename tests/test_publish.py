import io
import json
import zipfile

import pytest

from tools.publish_foundry import package_skill, publish, publish_roles


def test_publisher_preserves_resources_and_pins_every_reference(library):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if "/skills/" in url:
            with zipfile.ZipFile(io.BytesIO(kwargs["files"]["files"][1])) as package:
                assert "SKILL.md" in package.namelist()
                if "dotnet-development" in url:
                    assert "references/validation.md" in package.namelist()
            return {"version": "2"}
        references = kwargs["json"]["skills"]
        assert all(item["version"] == "2" for item in references)
        assert kwargs["json"]["tools"] == []
        return {"version": "4"}

    binding = publish(
        library, "https://test.services.ai.azure.com/api/projects/test", "factory", request
    )
    assert binding["version"] == "4"
    count = len(json.loads((library / "catalog.json").read_text())["skills"])
    assert len(binding["skills"]) == count
    assert len(calls) == count + 1


ENDPOINT = "https://test.services.ai.azure.com/api/projects/test"
COMMIT = "a" * 40
ROLES = ("architect", "planner", "coder", "reviewer", "tester")
IDENTITIES = {
    role: {
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "client_id": f"22222222-2222-2222-2222-{number:012d}",
        "principal_id": f"33333333-3333-3333-3333-{number:012d}",
    }
    for number, role in enumerate(ROLES)
}


class Foundry:
    def __init__(self):
        self.calls, self.packages, self.toolboxes = [], {}, {}

    def __call__(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        parts = url.split("?")[0].split("/")
        if "/skills/" in url:
            name = parts[parts.index("skills") + 1]
            if method == "POST":
                number = str(1 + sum(skill == name for skill, _ in self.packages))
                self.packages[name, number] = kwargs["files"]["files"][1]
                return {"version": number}
            return self.packages[name, parts[-2]]
        name = parts[parts.index("toolboxes") + 1]
        if method == "POST":
            number = str(1 + sum(toolbox == name for toolbox, _ in self.toolboxes))
            self.toolboxes[name, number] = kwargs["json"]
            return {"version": number}
        return self.toolboxes[name, parts[-1]]


def release(library, service, baseline=None):
    return publish_roles(
        library, ENDPOINT, IDENTITIES, service, source_commit=COMMIT, baseline=baseline
    )


def test_role_release_filters_pins_and_preserves_every_supporting_file(library):
    service = Foundry()
    result = release(library, service)
    assert len(service.packages) == len(
        json.loads((library / "catalog.json").read_text())["skills"]
    )
    assert len(service.toolboxes) == 5
    assert "architecture-analysis" not in result["roles"]["coder"]["skills"]
    assert "test-strategy" in result["roles"]["coder"]["skills"]
    assert "legacy-code-analysis" not in result["roles"]["tester"]["skills"]
    assert {row["skills"]["dotnet-development"] for row in result["roles"].values()} == {"1"}
    assert result["roles"]["coder"]["identity"] == IDENTITIES["coder"]
    assert result["release"]["source_commit"] == COMMIT
    with zipfile.ZipFile(io.BytesIO(service.packages["dotnet-development", "1"])) as archive:
        assert "references/validation.md" in archive.namelist()


def test_unchanged_release_reuses_all_versions_without_remote_writes(library):
    service = Foundry()
    first = release(library, service)
    service.calls.clear()
    second = release(library, service, first)
    assert second["roles"] == first["roles"]
    assert second["release"]["uploaded_skills"] == []
    assert second["release"]["changed_toolboxes"] == []
    assert all(method == "GET" for method, _, _ in service.calls)


def test_changed_shared_resource_updates_one_package_and_all_consuming_roles(library):
    service = Foundry()
    first = release(library, service)
    resource = library / "skills/dotnet-development/references/validation.md"
    resource.write_text(resource.read_text() + "\nAdditional compatibility check.\n")
    catalog = json.loads((library / "catalog.json").read_text())
    entry = next(entry for entry in catalog["skills"] if entry["id"] == "dotnet-development")
    major, minor, patch = entry["version"].split(".")
    entry["version"] = f"{major}.{minor}.{int(patch) + 1}"
    (library / "catalog.json").write_text(json.dumps(catalog))
    result = release(library, service, first)
    assert result["release"]["uploaded_skills"] == ["dotnet-development"]
    assert set(result["release"]["changed_toolboxes"]) == set(ROLES)
    assert {row["skills"]["dotnet-development"] for row in result["roles"].values()} == {"2"}
    assert result["roles"]["tester"]["skills"]["test-strategy"] == "1"


def test_role_metadata_change_rebuilds_only_affected_toolbox(library):
    service = Foundry()
    first = release(library, service)
    catalog = json.loads((library / "catalog.json").read_text())
    next(entry for entry in catalog["skills"] if entry["id"] == "legacy-code-analysis")[
        "roles"
    ].remove("coder")
    (library / "catalog.json").write_text(json.dumps(catalog))
    result = release(library, service, first)
    assert result["release"]["uploaded_skills"] == []
    assert result["release"]["changed_toolboxes"] == ["coder"]
    assert "legacy-code-analysis" not in result["roles"]["coder"]["skills"]


def test_unversioned_change_is_rejected_before_any_remote_request(library):
    service = Foundry()
    first = release(library, service)
    service.calls.clear()
    path = library / "skills/test-strategy/SKILL.md"
    path.write_text(path.read_text() + "\nChanged instructions.\n")
    with pytest.raises(ValueError, match="version increment"):
        release(library, service, first)
    assert service.calls == []


def test_bad_remote_content_cannot_be_promoted_or_create_toolboxes(library):
    service = Foundry()
    first = release(library, service)
    service.calls.clear()
    path = library / "skills/dotnet-development/references/validation.md"
    original = path.read_bytes()
    path.write_text("Tampered remote package.")
    service.packages["dotnet-development", "1"] = package_skill(path.parent.parent)
    path.write_bytes(original)
    with pytest.raises(ValueError, match="integrity mismatch"):
        release(library, service, first)
    assert not any(method == "POST" for method, _, _ in service.calls)


def test_changed_toolbox_references_are_not_trusted_on_reuse(library):
    service = Foundry()
    first = release(library, service)
    service.toolboxes["coder-skills", "1"]["skills"].pop()
    with pytest.raises(ValueError, match="differs from approved pins"):
        release(library, service, first)


@pytest.mark.parametrize("defect", ["identity", "duplicate-identity", "project", "commit"])
def test_invalid_release_configuration_cannot_publish(library, defect):
    service = Foundry()
    first = release(library, service)
    service.calls.clear()
    identities, commit = dict(IDENTITIES), COMMIT
    if defect == "identity":
        identities.pop("coder")
    elif defect == "duplicate-identity":
        identities["coder"] = identities["tester"]
    elif defect == "project":
        first["roles"]["coder"]["project_endpoint"] = ENDPOINT + "-other"
    else:
        commit = "main"
    with pytest.raises(ValueError):
        publish_roles(library, ENDPOINT, identities, service, source_commit=commit, baseline=first)
    assert service.calls == []
