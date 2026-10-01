"""Count LEGACY RATCHET entries in apps/api/pyproject.toml (must not exceed baseline)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "apps" / "api" / "pyproject.toml"
BASELINE = ROOT / "scripts" / "ratchet-baseline.txt"


def count_legacy_entries(text: str) -> int:
    marker = "# LEGACY RATCHET — list only shrinks. See docs/TECH_DEBT.md"
    parts = text.split(marker)
    if len(parts) < 3:
        raise RuntimeError("Expected two LEGACY RATCHET sections in pyproject.toml")

    ruff_section = parts[1]
    mypy_section = parts[2]

    ruff_count = sum(1 for line in ruff_section.splitlines() if line.strip().startswith('"app/'))
    mypy_count = sum(1 for line in mypy_section.splitlines() if line.strip().startswith('"app.'))
    return ruff_count + mypy_count


def main() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    count = count_legacy_entries(text)
    baseline = int(BASELINE.read_text(encoding="utf-8").strip())
    print(f"ratchet_entries={count} baseline={baseline}")
    if count > baseline:
        print(f"RATCHET regression: {count} > {baseline}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
