# VeloServe Repo Map

## Core Repositories

### `veloserve`

- Product: web server
- Expected host surface: product/runtime, download artifacts, engine docs
- Main concerns: request handling, PHP execution, caching, config, virtual hosts, performance, CMS compatibility

### `velopanel`

- Product: hosting control panel
- Expected host surface: panel app on managed servers
- Main concerns: account lifecycle, domains, SSL, databases, backups, monitoring, admin UX, account UX

### `platform`

- Product: central SaaS platform
- Expected host surface: `platform.veloserve.io`
- Main concerns: auth, subscriptions, billing, invoices, downloads, tickets, customer dashboard, central identity

### `licensing`

- Product: licensing platform
- Expected host surface: `licensing.veloserve.io`
- Main concerns: license issuance, validation, activation, renewal state, entitlements, heartbeat APIs

### `community`

- Product: community website
- Expected host surface: `community.veloserve.io`
- Main concerns: public community experience, participation, discovery, showcase, documentation entry points

## Boundary Rules

- `platform` owns customer identity, billing, and central account workflows.
- `velopanel` owns operational hosting controls inside the panel.
- `veloserve` owns the server engine and runtime behavior.
- `licensing` should stay reusable across multiple products.
- `community` stays public-facing and separate from product transaction flows.
