"""Append LEGACY RATCHET sections to apps/api/pyproject.toml (dev helper)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "apps" / "api" / "pyproject.toml"
MODULES_FILE = ROOT / "scripts" / ".legacy-modules.txt"
GLOBS_FILE = ROOT / "scripts" / ".legacy-ruff-globs.txt"

LEGACY_RUFF_EXTRA = [
    ("app/seed.py", ["ANN"]),
    ("app/seed_hardware.py", ["ANN"]),
    ("app/seed_telemetry.py", ["ANN"]),
    ("app/__init__.py", ["ANN"]),
]

MYPY_RELAX = """
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = false
warn_return_any = false
"""


def main() -> None:
    modules = [line.strip() for line in MODULES_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    globs = [line.strip() for line in GLOBS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    ruff_lines = [
        "",
        "# LEGACY RATCHET — list only shrinks. See docs/TECH_DEBT.md",
    ]
    for glob in globs:
        ruff_lines.append(f'"{glob}" = ["ANN"]')
    for path, rules in LEGACY_RUFF_EXTRA:
        ruff_lines.append(f'"{path}" = {rules!r}')

    mypy_lines = [
        "",
        "# LEGACY RATCHET — list only shrinks. See docs/TECH_DEBT.md",
        "[[tool.mypy.overrides]]",
        "module = [",
    ]
    for mod in modules:
        mypy_lines.append(f'    "{mod}",')
    mypy_lines.append("]")
    mypy_lines.extend(MYPY_RELAX.strip().splitlines())

    base = PYPROJECT.read_text(encoding="utf-8")
    if "# LEGACY RATCHET" in base:
        print("pyproject already has LEGACY RATCHET; skip")
        return

    # Insert ruff legacy after existing per-file-ignores block (before [tool.mypy])
    marker = "[tool.mypy]"
    idx = base.index(marker)
    new_ruff = "\n".join(ruff_lines) + "\n\n"
    base = base[:idx] + new_ruff + base[idx:]

    # Append mypy legacy before pytest section
    marker2 = "[tool.pytest.ini_options]"
    idx2 = base.index(marker2)
    new_mypy = "\n".join(mypy_lines) + "\n\n"
    base = base[:idx2] + new_mypy + base[idx2:]

    PYPROJECT.write_text(base, encoding="utf-8")
    entry_count = len(modules) + len(globs) + len(LEGACY_RUFF_EXTRA)
    baseline = ROOT / "scripts" / "ratchet-baseline.txt"
    baseline.write_text(f"{entry_count}\n", encoding="utf-8")
    print(f"ratchet entries={entry_count} modules={len(modules)} globs={len(globs)}")


if __name__ == "__main__":
    main()
