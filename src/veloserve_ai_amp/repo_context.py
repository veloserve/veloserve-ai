from __future__ import annotations

import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]
REPOS_DIR = BASE / "repos"

DEFAULT_SCOPE_REPOS = {
    "platform": ["platform"],
    "velopanel": ["velopanel"],
    "veloserve": ["veloserve"],
    "licensing": ["licensing"],
    "community": ["community"],
    "admin": ["platform"],
    "api": ["platform", "licensing"],
    "worker": ["platform"],
    "fullstack": ["platform", "velopanel", "veloserve", "licensing", "community"],
}

REPO_HINTS = {
    "velopanel": [
        "src/api/account_panel.rs",
        "src/db/mod.rs",
        "panel-ui/package.json",
        "panel-ui/src/pages/Packages.svelte",
        "panel-ui/src/pages/CreateAccount.svelte",
    ],
    "platform": [
        "Cargo.toml",
        "apps",
        "crates",
        "docs",
    ],
    "veloserve": [
        "Cargo.toml",
        "src",
        "tests",
        "website",
    ],
    "licensing": [
        "Cargo.toml",
        "src",
    ],
    "community": [
        "README.md",
    ],
}


def resolve_repo_scopes(repo_scope: str) -> list[str]:
    normalized = str(repo_scope or "fullstack").strip().lower().replace("-", "_")
    return DEFAULT_SCOPE_REPOS.get(normalized, [normalized])


def build_repo_profile(repo_scope: str) -> str:
    repo_names = resolve_repo_scopes(repo_scope)
    sections = []
    for repo_name in repo_names:
        sections.append(_build_repo_section(repo_name))
    return "\n\n".join(section for section in sections if section).strip()


def _build_repo_section(repo_name: str) -> str:
    repo_dir = REPOS_DIR / repo_name
    if not repo_dir.exists():
        return f"Repo profile for `{repo_name}`: missing local mirror at {repo_dir}"

    lines = [f"Repo profile for `{repo_name}`:"]
    readme_title = _read_readme_title(repo_dir / "README.md")
    if readme_title:
        lines.append(f"- Summary: {readme_title}")

    stack_summary = _detect_stack(repo_dir)
    if stack_summary:
        lines.append(f"- Stack: {stack_summary}")

    top_level = _list_top_level(repo_dir)
    if top_level:
        lines.append(f"- Top-level paths: {', '.join(top_level)}")

    hinted_paths = _collect_hinted_paths(repo_dir, repo_name)
    if hinted_paths:
        lines.append(f"- Important paths: {', '.join(hinted_paths)}")

    return "\n".join(lines)


def _read_readme_title(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _detect_stack(repo_dir: Path) -> str:
    parts: list[str] = []

    if (repo_dir / "Cargo.toml").exists():
        parts.append("Rust")
    if (repo_dir / "pyproject.toml").exists():
        parts.append("Python")

    package_paths = list(repo_dir.glob("package.json"))
    package_paths.extend(repo_dir.glob("*/package.json"))
    framework_bits: list[str] = []
    for package_path in sorted(package_paths):
        framework = _detect_package_framework(package_path)
        if framework:
            rel = package_path.relative_to(repo_dir)
            framework_bits.append(f"{framework} at {rel}")

    if framework_bits:
        parts.extend(framework_bits[:3])

    return ", ".join(parts)


def _detect_package_framework(package_path: Path) -> str:
    try:
        payload = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    deps = {}
    deps.update(payload.get("dependencies") or {})
    deps.update(payload.get("devDependencies") or {})
    dep_names = {str(name).lower() for name in deps}

    if "svelte" in dep_names or "@sveltejs/vite-plugin-svelte" in dep_names:
        return "Svelte SPA"
    if "next" in dep_names:
        return "Next.js"
    if "react" in dep_names or "react-dom" in dep_names:
        return "React"
    if "vue" in dep_names:
        return "Vue"
    return "Node UI"


def _list_top_level(repo_dir: Path) -> list[str]:
    names = []
    for path in sorted(repo_dir.iterdir()):
        if path.name.startswith("."):
            continue
        names.append(path.name + ("/" if path.is_dir() else ""))
    return names[:8]


def _collect_hinted_paths(repo_dir: Path, repo_name: str) -> list[str]:
    hinted_paths = []
    for relative in REPO_HINTS.get(repo_name, []):
        if (repo_dir / relative).exists():
            hinted_paths.append(relative)
    return hinted_paths
