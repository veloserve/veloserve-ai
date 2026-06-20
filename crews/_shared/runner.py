from __future__ import annotations

from datetime import datetime
from pathlib import Path
from string import Formatter

import yaml
from crewai import Agent, Crew, Process, Task


BASE = Path.home() / "Projects" / "veloserve-ai"
REPORTS_DIR = BASE / "reports"
KNOWLEDGE_DIR = BASE / "knowledge"


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path}"
    return path.read_text(encoding="utf-8", errors="ignore")


def build_shared_context(extra_files: list[Path] | None = None) -> str:
    sections = [
        ("Company context", KNOWLEDGE_DIR / "company" / "veloserve_context.md"),
        ("Repository inventory", KNOWLEDGE_DIR / "repos" / "repos_inventory.md"),
        ("Repository map", KNOWLEDGE_DIR / "architecture" / "repo_map.md"),
        ("Crew routing", KNOWLEDGE_DIR / "architecture" / "crew_routing.md"),
        ("Subdomain model", KNOWLEDGE_DIR / "architecture" / "subdomains.md"),
        ("Operating model", BASE / "runbooks" / "crew_operating_model.md"),
    ]

    for path in extra_files or []:
        sections.append((f"Additional context: {path.name}", path))

    rendered = []
    for title, path in sections:
        rendered.append(f"{title}:\n\n{read_text(path)}")
    return "\n\n".join(rendered)


class SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _format_string(template: str, inputs: dict[str, object]) -> str:
    formatter = Formatter()
    field_names = [
        field_name
        for _, field_name, _, _ in formatter.parse(template)
        if field_name is not None
    ]
    values = SafeFormatDict({key: "" if value is None else value for key, value in inputs.items()})
    if not field_names:
        return template
    return template.format_map(values)


def apply_inputs(value: object, inputs: dict[str, object]) -> object:
    if isinstance(value, str):
        return _format_string(value, inputs)
    if isinstance(value, list):
        return [apply_inputs(item, inputs) for item in value]
    if isinstance(value, dict):
        return {key: apply_inputs(item, inputs) for key, item in value.items()}
    return value


def build_agents(agents_config: dict, shared_context: str, inputs: dict[str, object]) -> dict[str, Agent]:
    agents: dict[str, Agent] = {}
    for name, cfg in agents_config.items():
        cfg = apply_inputs(cfg, inputs)
        agents[name] = Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"] + "\n\n" + shared_context,
            verbose=True,
            allow_delegation=cfg.get("allow_delegation", False),
        )
    return agents


def build_tasks(tasks_config: dict, agents: dict[str, Agent], inputs: dict[str, object]) -> list[Task]:
    tasks: list[Task] = []
    for cfg in tasks_config.values():
        cfg = apply_inputs(cfg, inputs)
        task_kwargs = {
            "description": cfg["description"],
            "expected_output": cfg["expected_output"],
            "agent": agents[cfg["agent"]],
        }
        if "output_file" in cfg:
            task_kwargs["output_file"] = cfg["output_file"]
        tasks.append(
            Task(**task_kwargs)
        )
    return tasks


def run_from_crew_dir(crew_dir: Path, inputs: dict[str, object] | None = None) -> Path:
    config_dir = crew_dir / "config"
    context = load_yaml(config_dir / "context.yaml")
    agents_config = load_yaml(config_dir / "agents.yaml")
    tasks_config = load_yaml(config_dir / "tasks.yaml")

    extra_context_files = [BASE / relative for relative in context.get("knowledge_files", [])]
    shared_context = build_shared_context(extra_context_files)
    merged_inputs: dict[str, object] = {
        "crew_name": context.get("name", crew_dir.name),
        "shared_context": shared_context,
        "goal": context.get("default_goal", "Review the current product surface and propose the next practical work."),
        "repo_scope": context.get("default_repo_scope", "all relevant repos"),
        "constraints": context.get(
            "default_constraints",
            "Do not deploy, do not change billing or pricing without approval, and keep work small and reviewable.",
        ),
        "success_definition": context.get(
            "default_success_definition",
            "Produce a clear markdown result with practical next steps and explicit risks.",
        ),
    }
    if inputs:
        merged_inputs.update(inputs)

    agents = build_agents(agents_config, shared_context, merged_inputs)
    tasks = build_tasks(tasks_config, agents, merged_inputs)

    process_name = context.get("process", "sequential")
    process = Process.hierarchical if process_name == "hierarchical" else Process.sequential

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=process,
        verbose=True,
    )

    result = crew.kickoff()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    prefix = context.get("report_prefix", crew_dir.name)
    out = REPORTS_DIR / f"{prefix}_{timestamp}.md"
    out.write_text(str(result), encoding="utf-8")
    return out
