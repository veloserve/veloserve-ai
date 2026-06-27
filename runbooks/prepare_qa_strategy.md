# Prepare QA Strategy

## Goal

Create a repeatable QA flow for the VeloServe ecosystem that combines:

- `Fly.io` for `platform` / billing / auth / dashboard preview
- an ephemeral VM for `velopanel` + `veloserve` server-like validation
- lightweight smoke automation before human click-through QA

The outcome should be a single operator-facing flow such as `prepare-qa` that returns:

- a `platform` staging URL
- a `velopanel` QA URL
- seeded test credentials
- smoke-check results
- a short manual QA checklist

## Why Hybrid

`Fly.io` is a strong fit for:

- preview deploys of `platform`
- auth and billing verification
- smoke testing API and dashboard availability
- generating a stable URL for quick human review

An ephemeral VM is a better fit for:

- `velopanel` account lifecycle
- `veloserve` vhost generation and sync
- system user creation
- local MySQL/PostgreSQL behavior
- disk quota hooks
- email / FTP / SSL / ACME style server-side integrations

Do not force full server QA into `Fly.io`. Use Fly for control-plane QA, and a disposable VM for server-plane QA.

## Target Operator Experience

Human workflow should look like:

1. Run `prepare-qa`.
2. Wait for automation to finish.
3. Open the returned `platform` and `panel` URLs.
4. Use the seeded test account/package.
5. Perform a short click-through QA pass.
6. Review smoke summary and report any gaps.

## Scope Split

### Fly.io Scope

Owns:

- `platform` staging deploy
- auth flows
- billing/dashboard smoke checks
- seeded platform-side test admin/customer
- health and basic API validation

Suggested outputs:

- staging URL
- seeded login email
- smoke results for `/healthz`, login page, dashboard load, billing page load

### VM Scope

Owns:

- `velopanel`
- `veloserve`
- local DB setup
- package/account seeding
- resource-limit verification environment
- host-like services required for realistic panel behavior

Suggested outputs:

- panel URL
- panel admin credentials
- seeded hosting account credentials
- smoke results for account/package/resource flows

## `prepare-qa` Responsibilities

The future launcher should orchestrate these steps:

1. Sync target repos/refs for QA.
2. Deploy or refresh `platform` staging on `Fly.io`.
3. Provision a disposable VM for panel/server QA.
4. Install and configure `veloserve` and `velopanel`.
5. Seed a low-limit package for deterministic testing.
6. Seed one fresh hosting account bound to that package.
7. Run smoke checks against both environments.
8. Print URLs, credentials, and manual QA steps.

## Seed Data

Use deterministic low-limit data so boundary behavior is obvious.

### Panel Seed Package

Recommended seed package:

- name: `qa-small`
- `max_domains = 2`
- `max_databases = 1`
- `max_email_accounts = 1`
- `max_ftp_accounts = 1`
- low but usable disk/bandwidth quotas

### Panel Seed Account

Recommended account:

- username: `qatest1`
- domain: disposable QA subdomain
- package: `qa-small`

### Platform Seed Data

Recommended seed objects:

- one admin user
- one customer user
- one test billing/subscription fixture

## Automatic Smoke Checks

### Platform Smoke

- `GET /healthz` returns OK
- login page loads
- dashboard shell loads after login
- billing screen loads
- key API endpoints respond with expected auth behavior

### Panel Smoke

- panel login works
- packages page loads
- seeded package exists
- create account page loads and shows seeded package
- seeded account exists
- account pages for domains/databases/email/FTP load
- usage/limit values are visible in UI-backed API data

### Boundary Smoke

Run API-level checks for:

- domain create succeeds until limit
- domain create fails at `limit + 1`
- database create succeeds until limit
- database create fails at `limit + 1`
- email create succeeds until limit
- email create fails at `limit + 1`
- FTP create succeeds until limit
- FTP create fails at `limit + 1`

This is important even when UI disables buttons, because backend denial must remain authoritative.

## Human QA Slice

After smoke passes, human QA should stay short and focused:

1. Log into `platform` staging and confirm auth/dashboard/billing screens render normally.
2. Log into `velopanel` and confirm the seeded package and account are visible.
3. Open the seeded account and verify usage/limit cards on domains/databases/email/FTP.
4. Create one allowed resource of each type.
5. Confirm the limit state updates in the UI.
6. Confirm the next create action is blocked or clearly rejected.

Target duration: `5-10` minutes.

## Recommended Implementation Order

### Phase 1

Implement the operator-facing runbook and one launcher entrypoint:

- `prepare-qa platform`
- `prepare-qa panel`
- `prepare-qa all`

### Phase 2

Automate platform staging:

- branch/ref selection
- Fly deploy
- auth/billing smoke checks

### Phase 3

Automate panel/server VM:

- VM create/start
- app install/config
- seed package/account
- panel smoke checks

### Phase 4

Add result summary output:

- URLs
- credentials
- green/red checks
- short manual QA list

## Suggested First Deliverables

The first practical implementation slice should produce:

- a shell or task runner entrypoint for `prepare-qa`
- a `platform` staging subflow
- a `panel` VM subflow
- a seed-data subflow
- a smoke summary output

Do not start by over-designing a large framework. Start with one predictable scriptable flow and evolve it.
