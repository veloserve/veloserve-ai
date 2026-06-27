from __future__ import annotations

from pathlib import Path

from veloserve_ai_amp.repo_context import build_repo_profile


BASE = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path}"
    return path.read_text(encoding="utf-8", errors="ignore")


def build_shared_context(repo_scope: str = "fullstack") -> str:
    paths = [
        ("Company context", BASE / "knowledge" / "company" / "veloserve_context.md"),
        ("Repository inventory", BASE / "knowledge" / "repos" / "repos_inventory.md"),
        ("Repository map", BASE / "knowledge" / "architecture" / "repo_map.md"),
        ("Crew routing", BASE / "knowledge" / "architecture" / "crew_routing.md"),
        ("Subdomain model", BASE / "knowledge" / "architecture" / "subdomains.md"),
        ("Operating model", BASE / "runbooks" / "crew_operating_model.md"),
    ]
    rendered = [f"{title}:\n\n{_read(path)}" for title, path in paths]
    repo_profile = build_repo_profile(repo_scope)
    if repo_profile:
        rendered.append(f"Repo scope profile:\n\n{repo_profile}")
    return "\n\n".join(rendered)
