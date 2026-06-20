from __future__ import annotations

from pathlib import Path


BASE = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path}"
    return path.read_text(encoding="utf-8", errors="ignore")


def build_shared_context() -> str:
    paths = [
        ("Company context", BASE / "knowledge" / "company" / "veloserve_context.md"),
        ("Repository inventory", BASE / "knowledge" / "repos" / "repos_inventory.md"),
        ("Repository map", BASE / "knowledge" / "architecture" / "repo_map.md"),
        ("Crew routing", BASE / "knowledge" / "architecture" / "crew_routing.md"),
        ("Subdomain model", BASE / "knowledge" / "architecture" / "subdomains.md"),
        ("Operating model", BASE / "runbooks" / "crew_operating_model.md"),
    ]
    return "\n\n".join(f"{title}:\n\n{_read(path)}" for title, path in paths)
