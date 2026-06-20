#!/usr/bin/env python
from __future__ import annotations

from datetime import datetime
import json
import os
import sys
import warnings

from veloserve_ai_amp.crew import VeloserveAiAmpCrew


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _default_inputs() -> dict[str, str]:
    return {
        "goal": "Review the highest-value next work for the VeloServe product family.",
        "repo_scope": "platform, velopanel, veloserve",
        "constraints": "Do not deploy, do not change pricing or billing without approval, keep work PR-sized.",
        "success_definition": "Return a markdown recommendation with repo ownership, plan, and risks.",
        "current_year": str(datetime.now().year),
    }


def _load_inputs() -> dict[str, str]:
    inputs = _default_inputs()
    raw_env = os.getenv("VELOSERVE_AI_INPUTS_JSON", "").strip()
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else ""

    raw = raw_env or raw_arg
    if raw:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("VELOSERVE_AI_INPUTS_JSON must be a JSON object")
        inputs.update({str(key): str(value) for key, value in payload.items()})
    return inputs


def run():
    try:
        return VeloserveAiAmpCrew().crew().kickoff(inputs=_load_inputs())
    except Exception as exc:
        raise Exception(f"An error occurred while running the VeloServe AMP crew: {exc}")


def train():
    try:
        inputs = _load_inputs()
        VeloserveAiAmpCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )
    except Exception as exc:
        raise Exception(f"An error occurred while training the VeloServe AMP crew: {exc}")


def replay():
    try:
        VeloserveAiAmpCrew().crew().replay(task_id=sys.argv[1])
    except Exception as exc:
        raise Exception(f"An error occurred while replaying the VeloServe AMP crew: {exc}")


def test():
    try:
        inputs = _load_inputs()
        VeloserveAiAmpCrew().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )
    except Exception as exc:
        raise Exception(f"An error occurred while testing the VeloServe AMP crew: {exc}")


def run_with_trigger():
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument") from exc

    inputs = _default_inputs()
    inputs["crewai_trigger_payload"] = trigger_payload
    return VeloserveAiAmpCrew().crew().kickoff(inputs=inputs)
