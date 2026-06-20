#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import yaml


BASE = Path.home() / "Projects" / "veloserve-ai"
sys.path.append(str(BASE / "crews"))
sys.path.append(str(BASE / "src"))

from _shared.runner import run_from_crew_dir
from veloserve_ai_amp.inputs import normalize_inputs


CREW_MAP = {
    "orchestrator": "product_orchestrator_crew",
    "product": "veloserve_product_crew",
    "server": "veloserve_server_crew",
    "panel": "velopanel_crew",
    "platform": "platform_crew",
    "licensing": "licensing_crew",
    "community": "community_crew",
    "qa": "shared_qa_security_crew",
}


def load_preset(crew: str, preset_name: str) -> dict[str, object]:
    crew_dir = BASE / "crews" / CREW_MAP[crew]
    preset_file = crew_dir / "config" / "presets.yaml"
    if not preset_file.exists():
        raise SystemExit(f"No presets defined for crew '{crew}'. Expected: {preset_file}")

    presets = yaml.safe_load(preset_file.read_text(encoding="utf-8")) or {}
    if preset_name not in presets:
        available = ", ".join(sorted(presets.keys())) or "none"
        raise SystemExit(
            f"Unknown preset '{preset_name}' for crew '{crew}'. Available presets: {available}"
        )
    return presets[preset_name]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a VeloServe CrewAI crew locally.")
    parser.add_argument("crew", choices=sorted(CREW_MAP.keys()), help="Crew alias to run")
    parser.add_argument("--preset", default="", help="Named preset profile for this crew")
    parser.add_argument("--goal", default="", help="Primary task or request for the crew")
    parser.add_argument("--task-type", default="", help="Structured task mode such as review_segment or draft_issue")
    parser.add_argument("--repo-scope", default="", help="Target repository or product surface")
    parser.add_argument("--segment", default="", help="Structured segment such as billing, auth, or webhooks")
    parser.add_argument("--target", default="", help="Specific app, flow, or surface under review")
    parser.add_argument("--constraints", default="", help="Constraints or rules for this run")
    parser.add_argument("--success-definition", default="", help="What a successful output should include")
    parser.add_argument(
        "--artifacts-required",
        default="",
        help="Comma-separated artifact list such as issue_draft,staging_checklist,pr_candidates",
    )
    parser.add_argument(
        "--context-url",
        action="append",
        default=[],
        help="Optional context URL. Repeat the flag to add multiple URLs.",
    )
    parser.add_argument("--notes", default="", help="Short extra context")
    parser.add_argument("--inputs-json", default="", help="Extra inputs as raw JSON object")
    args = parser.parse_args()

    extra_inputs: dict[str, object] = {}
    if args.inputs_json:
        extra_inputs = json.loads(args.inputs_json)

    preset_inputs: dict[str, object] = {}
    if args.preset:
        preset_inputs = load_preset(args.crew, args.preset)

    cli_inputs = {
        "goal": args.goal,
        "task_type": args.task_type,
        "repo_scope": args.repo_scope,
        "segment": args.segment,
        "target": args.target,
        "constraints": args.constraints,
        "success_definition": args.success_definition,
        "artifacts_required": args.artifacts_required,
        "context_urls": args.context_url,
        "notes": args.notes,
    }
    cli_inputs = {key: value for key, value in cli_inputs.items() if value not in ("", None)}

    inputs = {}
    inputs.update(preset_inputs)
    inputs.update(cli_inputs)
    inputs.update(extra_inputs)
    inputs = {key: value for key, value in inputs.items() if value not in ("", None)}
    inputs = normalize_inputs(inputs)

    crew_dir = BASE / "crews" / CREW_MAP[args.crew]
    out = run_from_crew_dir(crew_dir, inputs=inputs)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
