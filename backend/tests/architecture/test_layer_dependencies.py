"""Forbidden dependencies from docs/architecture.md, asserted with `ast` (no extra package).

Rules (docs/architecture.md, Forbidden dependencies):
1. app.api imports from app only app.services, app.schemas, app.core (never repositories/models).
2. app.services never imports app.api or fastapi.
3. app.repositories never imports app.services or app.api.
4. app.models imports from app only app.core.
5. app.core imports no other app layer.
app.main is the composition root and is not a layer.
"""

import ast
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[2] / "app"

# Layers whose imports from `app` are limited to an allow-list (itself always allowed).
ALLOWED_APP_IMPORTS: dict[str, set[str]] = {
    "api": {"services", "schemas", "core"},
    "models": {"core"},
    "core": set(),
}
# Layers with an explicit deny-list (top-level module names; "app.x" means layer x).
FORBIDDEN_IMPORTS: dict[str, set[str]] = {
    "services": {"app.api", "fastapi"},
    "repositories": {"app.services", "app.api"},
}


def _layer_of(module: str) -> str | None:
    parts = module.split(".")
    return parts[1] if len(parts) > 1 and parts[0] == "app" else None


def _imported_modules(module: str, source: str, is_package: bool) -> list[str]:
    """Absolute names of every module imported by `source` (relative imports resolved)."""
    package_parts = module.split(".") if is_package else module.split(".")[:-1]
    names: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package_parts[: len(package_parts) - (node.level - 1)]
                prefix = ".".join(base + ([node.module] if node.module else []))
                if node.module:
                    names.append(prefix)
                else:  # from . import x  → each x is a module of the base package
                    names.extend(f"{prefix}.{alias.name}" for alias in node.names)
            elif node.module:
                names.append(node.module)
    return names


def find_violations(module: str, source: str, is_package: bool = False) -> list[str]:
    """Return one message per import in `source` that breaks a rule for `module`'s layer."""
    layer = _layer_of(module)
    if layer is None:
        return []
    violations: list[str] = []
    for imported in _imported_modules(module, source, is_package):
        target_layer = _layer_of(imported)
        if layer in ALLOWED_APP_IMPORTS and imported.split(".")[0] == "app":
            allowed = ALLOWED_APP_IMPORTS[layer] | {layer}
            if target_layer not in allowed:
                violations.append(f"{module} imports {imported} (app.{layer} may not)")
        for forbidden in FORBIDDEN_IMPORTS.get(layer, set()):
            if imported == forbidden or imported.startswith(forbidden + "."):
                violations.append(f"{module} imports {imported} (app.{layer} may not)")
    return violations


def _app_modules() -> list[tuple[str, Path, bool]]:
    modules = []
    for path in sorted(APP_DIR.rglob("*.py")):
        rel = path.relative_to(APP_DIR.parent).with_suffix("")
        is_package = rel.name == "__init__"
        parts = rel.parts[:-1] if is_package else rel.parts
        modules.append((".".join(parts), path, is_package))
    return modules


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("app.api.leave", "from app.repositories.leave import LeaveRepository"),
        ("app.api.leave", "import app.models.leave"),
        ("app.api.leave", "from ..models import leave"),
        ("app.services.leave", "from fastapi import HTTPException"),
        ("app.services.leave", "from app.api.health import router"),
        ("app.repositories.leave", "from app.services.leave import LeaveService"),
        ("app.repositories.leave", "import app.api"),
        ("app.models.leave", "from app.schemas.leave import LeaveCreate"),
        ("app.core.errors", "from app.services import leave"),
    ],
)
def test_detects_forbidden_import(module: str, source: str) -> None:
    assert find_violations(module, source) != []


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("app.api.leave", "from app.services.leave import LeaveService\nfrom app.core import x"),
        ("app.services.leave", "from app.repositories.leave import LeaveRepository"),
        ("app.repositories.leave", "from app.models.leave import Leave"),
        ("app.models.leave", "from app.core.db import Base"),
        ("app.core.errors", "from app.core.security_headers import SECURITY_HEADERS"),
    ],
)
def test_allows_permitted_import(module: str, source: str) -> None:
    assert find_violations(module, source) == []


def test_current_code_has_no_forbidden_imports() -> None:
    modules = _app_modules()
    assert modules, "no modules found under backend/app"
    violations = [
        v
        for module, path, is_package in modules
        for v in find_violations(module, path.read_text(encoding="utf-8"), is_package)
    ]
    assert violations == []
