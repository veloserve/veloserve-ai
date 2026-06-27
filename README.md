# VeloServe AI Workspace

CrewAI workspace for coordinating work across the VeloServe product family:

- `veloserve` - web server engine
- `velopanel` - hosting control panel
- `platform` - customer SaaS and billing platform
- `licensing` - licensing service
- `community` - community website

## Layout

- `crews/` - crew definitions and shared runner code
- `knowledge/` - shared product, repo, and routing context
- `repos/` - local clones of VeloServe repositories
- `reports/` - generated crew outputs
- `runbooks/` - operating rules for AI execution

## Current Crew Set

- `product_orchestrator_crew`
- `veloserve_server_crew`
- `velopanel_crew`
- `platform_crew`
- `licensing_crew`
- `community_crew`
- `shared_qa_security_crew`
- `veloserve_product_crew` - legacy roadmap crew kept for compatibility

## Running A Crew

From the workspace root:

```bash
source venv/bin/activate
python crews/platform_crew/crew.py
```

Each crew writes a markdown report into `reports/`.

## Local Launcher

Use the local launcher to run any crew with a task-oriented prompt:

```bash
source venv/bin/activate
python scripts/run_crew.py platform \
  --goal "Review the next billing improvements for platform.veloserve.io" \
  --repo-scope "platform" \
  --constraints "No production deploys; keep work PR-sized" \
  --success-definition "Return an implementation plan and risks"
```

The launcher also supports the newer structured AMP-style schema:

```bash
source venv/bin/activate
python scripts/run_crew.py platform \
  --task-type review_segment \
  --repo-scope platform \
  --segment billing \
  --target platform.veloserve.io \
  --constraints "No production deploys; PR-sized only; no schema-breaking changes" \
  --success-definition "Return prioritized findings, a staging verification checklist, and 3 PR-sized improvement candidates with risks" \
  --artifacts-required findings_list,priority_order,staging_checklist,pr_candidates,risk_summary
```

Another example for VeloPanel:

```bash
source venv/bin/activate
python scripts/run_crew.py panel \
  --goal "Add quota enforcement for account-level domain and database creation" \
  --repo-scope "velopanel" \
  --constraints "No destructive account changes; verify ownership and quota checks" \
  --success-definition "Return first PR scope, likely files, and validation steps"
```

## Preset Profiles

Common review profiles are available for `platform` and `panel`.

Examples:

```bash
source venv/bin/activate
python scripts/run_crew.py platform --preset billing-review
python scripts/run_crew.py platform --preset auth-review
python scripts/run_crew.py platform --preset billing-structured
python scripts/run_crew.py platform --preset webhooks-hardening
python scripts/run_crew.py platform --preset observability-issue
python scripts/run_crew.py panel --preset quota-review
python scripts/run_crew.py panel --preset ownership-audit
python scripts/run_crew.py panel --preset ownership-hardening-issue
python scripts/run_crew.py panel --preset packages-flow-plan
python scripts/run_crew.py panel --preset account-limits-enforcement
```

You can still override any preset field:

```bash
source venv/bin/activate
python scripts/run_crew.py panel \
  --preset quota-review \
  --goal "Review quota enforcement specifically for addon domains and database creation"
```

## CrewAI AMP

This repo now includes an AMP-ready CrewAI project under `src/veloserve_ai_amp/`.

### What It Gives You

- A standard `pyproject.toml` expected by CrewAI AMP
- A deployable entrypoint at `src/veloserve_ai_amp/main.py`
- A generic intake/planning/review crew for assigning VeloServe tasks from the AMP dashboard

### Prepare Environment

Copy `.env.example` to `.env` and set the LLM provider variables you actually use.

### Local Test

```bash
source venv/bin/activate
PYTHONPATH=src \
VELOSERVE_AI_INPUTS_JSON='{"task_type":"review_segment","repo_scope":"platform","segment":"billing","target":"platform.veloserve.io","artifacts_required":["findings_list","staging_checklist","pr_candidates"]}' \
  venv/bin/python -m veloserve_ai_amp.main
```

The module entrypoint now prints the final crew output, so this command works as a real local smoke test.

### AMP Input Schema v1

Recommended payload fields for AMP:

- `task_type`: `review_segment | draft_issue | implementation_plan | hardening_review`
- `repo_scope`: `platform | velopanel | veloserve | licensing | community | admin | api | worker | fullstack`
- `segment`: `billing | auth | notifications | webhooks | infra | observability | support_admin | general`
- `target`: app, flow, or product surface under review
- `constraints`: guardrails for this run
- `success_definition`: what the output must contain
- `artifacts_required`: array or comma-separated artifact list
- `context_urls`: optional array of staging/spec/issue links
- `notes`: optional short context

Legacy `goal` payloads still work. The AMP wrapper now synthesizes a routing goal automatically when you send the structured schema above.

### Deploy To AMP

From the repo root:

```bash
source venv/bin/activate
crewai login
crewai deploy validate
crewai deploy create
crewai deploy push
crewai deploy status
crewai deploy logs
```

AMP deployment notes:

- The project must stay in standard CrewAI format with `pyproject.toml`
- `uv.lock` should be committed for reliable deployments
- Put `veloserve-ai` in its own Git repository before the first AMP deployment
- The AMP dashboard will expose run history, traces, metrics, and manual task triggering
