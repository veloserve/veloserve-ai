# Veloserve Repository Inventory

Generated: Sat Jun 13 11:33:57 CEST 2026

## community

**Remote:** https://github.com/veloserve/community.git

**Default branch:** unknown

**Recent commits:**

**Detected files:**

**Top-level structure:**
.git

## licensing

**Remote:** https://github.com/veloserve/licensing.git

**Default branch:** unknown

**Recent commits:**

**Detected files:**

**Top-level structure:**
.git

## platform

**Remote:** https://github.com/veloserve/platform.git

**Default branch:** main

**Recent commits:**
382f2b7 Merge pull request #28 from veloserve/fix/persist-session-email-conflict
959377f fix(auth): resolve canonical user_id from DB in persist_auth_session
0c8f9a9 Merge pull request #27 from veloserve/fix/magic-link-duplicate-user
2c0c6ea fix(auth): handle returning users in magic link verify (ON CONFLICT DO NOTHING)
a868100 Merge pull request #26 from veloserve/fix/magic-link-redirect

**Detected files:**
./Cargo.toml
./Dockerfile
./README.md

**Top-level structure:**
.dockerignore
.foo
.git
.github
.gitignore
CONTRIBUTING.md
Cargo.lock
Cargo.toml
Dockerfile
README.md
apps
crates
deploy
docs
fly.toml
github-test.txt
scripts

## velopanel

**Remote:** https://github.com/veloserve/velopanel.git

**Default branch:** main

**Recent commits:**
74e8f96 Merge pull request #23 from veloserve/fix/email-service-check
d1deb2b feat(admin): Software Installer, custom services/software, PHP modules, service config
349e183 fix(email): require email service configured before creating account-level email
287ce50 chore: release 1.0.5
e03b408 Merge pull request #22 from veloserve/feat/account-databases-privileges

**Detected files:**
./Cargo.toml
./README.md
./panel-ui/package.json

**Top-level structure:**
.git
.github
.gitignore
CHANGELOG.md
Cargo.lock
Cargo.toml
README.md
deploy-to-lima.sh
install.sh
migrations
panel-ui
src
uninstall.sh
velopanel.example.toml
velopanel.service

## veloserve

**Remote:** https://github.com/veloserve/veloserve.git

**Default branch:** main

**Recent commits:**
37ffd63 Merge pull request #35 from veloserve/fix/pricing-page
7dc3acc feat: rewrite pricing around domains + VeloPanel, add VeloPanel section to homepage
4753fb1 Merge pull request #34 from veloserve/fix/pricing-page
4375de3 fix: use root vercel.json for pricing rewrite, remove duplicate
f30d83f Merge pull request #33 from veloserve/fix/pricing-page

**Detected files:**
./Cargo.toml
./README.md
./cpanel/README.md
./docs-site/requirements.txt
./docs/README.md
./wordpress-plugin/README.md

**Top-level structure:**
.devcontainer
.git
.github
.gitignore
.gitpod.Dockerfile
.gitpod.yml
CHANGELOG.md
CONTRIBUTING.md
Cargo.toml
Makefile
README.md
build.rs
cpanel
docs
docs-site
examples
scripts
src
tests
veloserve.toml
vercel.json
website
wordpress-plugin
wordpress-sapi.toml
wordpress.toml

