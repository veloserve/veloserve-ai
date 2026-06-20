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
python scripts/run_crew.py panel --preset quota-review
python scripts/run_crew.py panel --preset ownership-audit
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
VELOSERVE_AI_INPUTS_JSON='{"goal":"Review next platform billing work","repo_scope":"platform"}' \
  venv/bin/python -m veloserve_ai_amp.main
```

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
