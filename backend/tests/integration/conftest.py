"""Every test in this folder is an integration test (docs/testing.md, Two speeds, rule 4).

The marker is added by path, so a new file here is selected by `-m integration` without being
listed anywhere — and excluded from `-m "not integration"`.
"""

from pathlib import Path

import pytest

INTEGRATION_DIR = Path(__file__).resolve().parent


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if INTEGRATION_DIR in item.path.resolve().parents:
            item.add_marker(pytest.mark.integration)
