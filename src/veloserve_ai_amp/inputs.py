from __future__ import annotations

from datetime import datetime
from typing import Any


DEFAULT_CONSTRAINTS = (
    "No production deploys; no billing or pricing changes without approval; "
    "keep work PR-sized and reviewable."
)
DEFAULT_SUCCESS_DEFINITION = (
    "Return markdown artifacts with recommended owner, implementation approach, "
    "validation steps, and explicit risks."
)

ALLOWED_TASK_TYPES = {
    "review_segment",
    "draft_issue",
    "implementation_plan",
    "hardening_review",
}

ALLOWED_REPO_SCOPES = {
    "platform",
    "velopanel",
    "veloserve",
    "licensing",
    "community",
    "admin",
    "api",
    "worker",
    "fullstack",
}

ALLOWED_SEGMENTS = {
    "billing",
    "auth",
    "notifications",
    "webhooks",
    "infra",
    "observability",
    "support_admin",
    "general",
}

RAW_DEFAULT_INPUTS: dict[str, object] = {
    "task_type": "review_segment",
    "repo_scope": "fullstack",
    "segment": "general",
    "target": "the VeloServe product family",
    "constraints": DEFAULT_CONSTRAINTS,
    "success_definition": DEFAULT_SUCCESS_DEFINITION,
    "artifacts_required": [
        "routing_brief",
        "implementation_plan",
        "risk_summary",
    ],
    "notes": "",
    "context_urls": [],
}


def default_inputs() -> dict[str, object]:
    return dict(RAW_DEFAULT_INPUTS, current_year=str(datetime.now().year))


def normalize_inputs(payload: dict[str, Any] | None) -> dict[str, object]:
    merged: dict[str, object] = default_inputs()
    if payload:
        merged.update(payload)

    task_type = _coerce_enum(merged.get("task_type"), ALLOWED_TASK_TYPES, "review_segment")
    repo_scope = _coerce_enum(merged.get("repo_scope"), ALLOWED_REPO_SCOPES, "fullstack")
    segment = _coerce_enum(merged.get("segment"), ALLOWED_SEGMENTS, "general")
    target = _string_or_default(merged.get("target"), "the VeloServe product family")
    constraints = _string_or_default(merged.get("constraints"), DEFAULT_CONSTRAINTS)
    success_definition = _string_or_default(
        merged.get("success_definition"), DEFAULT_SUCCESS_DEFINITION
    )
    notes = _string_or_default(merged.get("notes"), "")
    current_year = _string_or_default(merged.get("current_year"), str(datetime.now().year))

    artifacts_required = _coerce_list(merged.get("artifacts_required"))
    context_urls = _coerce_list(merged.get("context_urls"))

    goal = _string_or_default(merged.get("goal"), "")
    if not goal:
        goal = build_goal(task_type=task_type, segment=segment, target=target)

    normalized: dict[str, object] = dict(merged)
    normalized.update(
        {
            "task_type": task_type,
            "repo_scope": repo_scope,
            "segment": segment,
            "target": target,
            "goal": goal,
            "constraints": constraints,
            "success_definition": success_definition,
            "artifacts_required": artifacts_required,
            "artifacts_required_text": ", ".join(artifacts_required) if artifacts_required else "None specified",
            "context_urls": context_urls,
            "context_urls_text": _format_bullets(context_urls, empty_value="None provided"),
            "notes": notes,
            "notes_text": notes or "None provided",
            "structured_request": build_structured_request(
                task_type=task_type,
                repo_scope=repo_scope,
                segment=segment,
                target=target,
                constraints=constraints,
                success_definition=success_definition,
                artifacts_required=artifacts_required,
                context_urls=context_urls,
                notes=notes,
            ),
            "artifact_output_contract": build_artifact_output_contract(
                task_type=task_type,
                artifacts_required=artifacts_required,
            ),
            "scope_lock_rules": build_scope_lock_rules(
                task_type=task_type,
                repo_scope=repo_scope,
                segment=segment,
                target=target,
                goal=goal,
                artifacts_required=artifacts_required,
            ),
            "current_year": current_year,
        }
    )
    return normalized


def build_goal(*, task_type: str, segment: str, target: str) -> str:
    readable_segment = segment.replace("_", " ")
    if task_type == "draft_issue":
        return f"Draft a GitHub-ready issue for {readable_segment} in {target}."
    if task_type == "implementation_plan":
        return f"Create a PR-sized implementation plan for {readable_segment} in {target}."
    if task_type == "hardening_review":
        return f"Review {readable_segment} in {target} for security, reliability, and approval-sensitive risk."
    return f"Review {readable_segment} in {target} and identify the next highest-value PR-sized work."


def build_structured_request(
    *,
    task_type: str,
    repo_scope: str,
    segment: str,
    target: str,
    constraints: str,
    success_definition: str,
    artifacts_required: list[str],
    context_urls: list[str],
    notes: str,
) -> str:
    return "\n".join(
        [
            f"- Task type: {task_type}",
            f"- Repo scope: {repo_scope}",
            f"- Segment: {segment}",
            f"- Target: {target}",
            f"- Constraints: {constraints}",
            f"- Success definition: {success_definition}",
            f"- Artifacts required: {', '.join(artifacts_required) if artifacts_required else 'None specified'}",
            f"- Context URLs: {_inline_or_none(context_urls)}",
            f"- Notes: {notes or 'None provided'}",
        ]
    )


def build_artifact_output_contract(*, task_type: str, artifacts_required: list[str]) -> str:
    artifact_names = artifacts_required or ["result"]
    lines = [
        "Use markdown headings that exactly match the artifact names below.",
        "Keep each artifact distinct. Do not duplicate the same bullets across multiple artifacts.",
        "Do not prepend narrative before the first artifact heading.",
        "If you must change scope, add a final heading named `scope_adjustments` with a short reason.",
    ]

    if task_type == "draft_issue":
        lines.extend(
            [
                "For `issue_title`, return a single bullet with the final title text only.",
                "For `github_issue_body`, place the exact GitHub-ready body inside a fenced `md` code block.",
                "Keep `github_issue_body` concise and implementation-ready. Target 180-220 words unless the request explicitly asks for more.",
                "For `approval_gates`, keep only approval-sensitive steps and required sign-offs. Do not repeat `acceptance_criteria` or `risk_summary` there.",
            ]
        )

    for artifact_name in artifact_names:
        lines.append(f"- Heading required: `## {artifact_name}`")
    return "\n".join(lines)


def build_scope_lock_rules(
    *,
    task_type: str,
    repo_scope: str,
    segment: str,
    target: str,
    goal: str,
    artifacts_required: list[str],
) -> str:
    lines = [
        f"Preserve the original repo scope `{repo_scope}`, segment `{segment}`, and target `{target}`.",
        f"Preserve the intent of this goal: {goal}",
        (
            "Do not silently narrow or replace the requested scope. If you recommend a smaller first PR, "
            "keep the broader requested scope visible and explain the split explicitly."
        ),
    ]
    if artifacts_required:
        lines.append(
            "Preserve these requested artifacts unless the request explicitly changes them: "
            + ", ".join(artifacts_required)
        )
    if task_type == "draft_issue":
        lines.append(
            "For draft_issue tasks, do not drop replay protection, idempotency, DB, or rollout concerns if they are part of the requested brief."
        )
    return "\n".join(lines)


def _coerce_enum(value: Any, allowed: set[str], fallback: str) -> str:
    candidate = _string_or_default(value, fallback).strip().lower().replace("-", "_")
    return candidate if candidate in allowed else fallback


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _string_or_default(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _format_bullets(items: list[str], *, empty_value: str) -> str:
    if not items:
        return empty_value
    return "\n".join(f"- {item}" for item in items)


def _inline_or_none(items: list[str]) -> str:
    if not items:
        return "None provided"
    return ", ".join(items)
