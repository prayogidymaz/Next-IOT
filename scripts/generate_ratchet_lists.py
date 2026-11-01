"""Generate legacy module lists for RATCHET (dev-only helper)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "api" / "app"

CORE_FILE_NAMES = frozenset({"config.py", "main.py", "database.py", "deps.py"})
CORE_PREFIXES = ("auth/", "commands/", "devices/", "tenants/", "users/", "types/")


def is_core(rel: str) -> bool:
    if rel in CORE_FILE_NAMES:
        return True
    if rel.startswith("telemetry/video_feed/"):
        return False
    if rel.startswith("telemetry/"):
        return True
    return any(rel.startswith(prefix) for prefix in CORE_PREFIXES)


def main() -> None:
    legacy_modules: list[str] = []
    legacy_ruff_globs: list[str] = []
    seen_globs: set[str] = set()

    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if is_core(rel):
            continue
        module = "app." + rel[:-3].replace("/", ".")
        legacy_modules.append(module)
        parent = str(Path("app") / Path(rel).parent).replace("\\", "/")
        glob_key = f"{parent}/*.py"
        if glob_key not in seen_globs:
            seen_globs.add(glob_key)
            legacy_ruff_globs.append(glob_key)

    print(f"legacy_modules={len(legacy_modules)}")
    print(f"legacy_ruff_globs={len(legacy_ruff_globs)}")
    for line in legacy_modules:
        print(line)


if __name__ == "__main__":
    main()
