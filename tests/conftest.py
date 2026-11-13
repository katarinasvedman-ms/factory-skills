import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def library(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for name in ("catalog.json", "catalog.schema.json", "evaluations.json"):
        shutil.copyfile(ROOT / name, root / name)
    shutil.copytree(ROOT / "skills", root / "skills")
    return root
