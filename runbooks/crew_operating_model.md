# Crew Operating Model

## Purpose

This workspace uses CrewAI for planning, analysis, issue shaping, and implementation preparation across the VeloServe ecosystem.

## Product Boundaries

- `veloserve`: web server runtime and performance layer
- `velopanel`: server-side hosting control panel
- `platform`: central SaaS portal, auth, billing, customer lifecycle
- `licensing`: license issuance, validation, entitlement, heartbeat services
- `community`: public community experience and engagement surface

## Default Behavior

- Prefer analysis, issue generation, implementation plans, and PR shaping.
- Keep production safety checks explicit.
- Use small, reviewable work items.
- Escalate anything involving money, production deployment, pricing, or customer communication.

## Review Gates

Human approval is required before:

- deploying to production
- changing pricing or billing behavior
- merging sensitive auth or billing changes
- deleting customer or production data
- changing infrastructure outside a local or staging context

## Routing Rules

- Route product strategy and cross-repo prioritization to `product_orchestrator_crew`.
- Route server runtime and performance work to `veloserve_server_crew`.
- Route hosting panel workflows to `velopanel_crew`.
- Route SaaS account, billing, and dashboard work to `platform_crew`.
- Route entitlement and activation logic to `licensing_crew`.
- Route public community site work to `community_crew`.
- Route auth, permissions, secrets, and regression review to `shared_qa_security_crew`.
