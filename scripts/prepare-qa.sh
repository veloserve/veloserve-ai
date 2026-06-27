#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM_REPO="${PLATFORM_REPO:-$BASE_DIR/repos/platform}"
VELOPANEL_REPO="${VELOPANEL_REPO:-$BASE_DIR/repos/velopanel}"
PLATFORM_QA_SCRIPT="${PLATFORM_QA_SCRIPT:-$PLATFORM_REPO/scripts/qa/lima-platform-qa.sh}"
VELOPANEL_VM_SCRIPT="${VELOPANEL_VM_SCRIPT:-$HOME/velopanel-vm.sh}"
VELOPANEL_DEPLOY_SCRIPT="${VELOPANEL_DEPLOY_SCRIPT:-$VELOPANEL_REPO/deploy-to-lima.sh}"

PLATFORM_HEALTH_URL="${PLATFORM_HEALTH_URL:-http://127.0.0.1:8080/healthz}"
PLATFORM_UI_URL="${PLATFORM_UI_URL:-http://127.0.0.1:4173/}"
PANEL_UI_URL="${PANEL_UI_URL:-http://127.0.0.1:7070/}"
PANEL_API_URL="${PANEL_API_URL:-http://127.0.0.1:7070}"
PANEL_HTTP_URL="${PANEL_HTTP_URL:-http://127.0.0.1:8080/}"
PANEL_HTTPS_URL="${PANEL_HTTPS_URL:-https://127.0.0.1:8443/}"

PANEL_ADMIN_USER="${PANEL_ADMIN_USER:-admin}"
PANEL_ADMIN_PASS="${PANEL_ADMIN_PASS:-Admin12345}"
PANEL_SEED_PACKAGE="${PANEL_SEED_PACKAGE:-qa-small}"
PANEL_SEED_ACCOUNT_USER="${PANEL_SEED_ACCOUNT_USER:-qatest1}"
PANEL_SEED_ACCOUNT_DOMAIN="${PANEL_SEED_ACCOUNT_DOMAIN:-qatest1.qa.local}"
PANEL_SEED_ACCOUNT_EMAIL="${PANEL_SEED_ACCOUNT_EMAIL:-qatest1@qa.local}"
PANEL_SEED_ACCOUNT_PASS="${PANEL_SEED_ACCOUNT_PASS:-QaTest12345}"
PANEL_SMOKE_USER_PREFIX="${PANEL_SMOKE_USER_PREFIX:-qasmk}"

DRY_RUN=0
PANEL_FIRST_TIME=0
ACTION=""
PANEL_ADMIN_TOKEN=""
PANEL_HUMAN_ACCOUNT_ID=""
RESPONSE_STATUS=""
RESPONSE_BODY=""

info() { echo -e "\033[0;36m[prepare-qa]\033[0m $*"; }
ok() { echo -e "\033[0;32m[ok]\033[0m $*"; }
warn() { echo -e "\033[0;33m[warn]\033[0m $*"; }
die() { echo -e "\033[0;31m[error]\033[0m $*" >&2; exit 1; }

usage() {
  cat <<EOF
Usage: $(basename "$0") <action> [--dry-run] [--panel-first-time]

Actions:
  status    Show configured paths, URLs, and script availability
  platform  Run the existing platform QA flow
  panel     Start the panel VM and deploy the local panel build
  seed      Seed qa-small package + qatest1 account in VeloPanel
  panel-smoke  Run panel API smoke and limit boundary checks
  all       Run platform + panel + seed + smoke
  smoke     Run lightweight local smoke checks against known QA URLs

Flags:
  --dry-run           Print actions without executing them
  --panel-first-time  When running 'panel' or 'all', pass --first-time to deploy-to-lima.sh
  -h, --help          Show this help
EOF
}

run_cmd() {
  local desc="$1"
  shift
  if [[ "$DRY_RUN" == "1" ]]; then
    info "dry-run: $desc"
    printf '  '
    printf '%q ' "$@"
    printf '\n'
    return 0
  fi
  info "$desc"
  "$@"
}

require_file() {
  local path="$1"
  [[ -f "$path" ]] || die "Missing file: $path"
}

show_status() {
  echo "prepare-qa status"
  echo ""
  echo "Base:"
  echo "  $BASE_DIR"
  echo ""
  echo "Platform:"
  echo "  repo:   $PLATFORM_REPO"
  echo "  script: $PLATFORM_QA_SCRIPT"
  echo "  health: $PLATFORM_HEALTH_URL"
  echo "  ui:     $PLATFORM_UI_URL"
  echo ""
  echo "Panel:"
  echo "  repo:   $VELOPANEL_REPO"
  echo "  vm:     $VELOPANEL_VM_SCRIPT"
  echo "  deploy: $VELOPANEL_DEPLOY_SCRIPT"
  echo "  ui:     $PANEL_UI_URL"
  echo "  api:    $PANEL_API_URL"
  echo "  http:   $PANEL_HTTP_URL"
  echo "  https:  $PANEL_HTTPS_URL"
  echo "  seed package: $PANEL_SEED_PACKAGE"
  echo "  seed account: $PANEL_SEED_ACCOUNT_USER ($PANEL_SEED_ACCOUNT_DOMAIN)"
  echo ""

  [[ -f "$PLATFORM_QA_SCRIPT" ]] && ok "Platform QA script found" || warn "Platform QA script missing"
  [[ -f "$VELOPANEL_VM_SCRIPT" ]] && ok "VeloPanel VM script found" || warn "VeloPanel VM script missing"
  [[ -f "$VELOPANEL_DEPLOY_SCRIPT" ]] && ok "VeloPanel deploy script found" || warn "VeloPanel deploy script missing"
}

run_platform() {
  require_file "$PLATFORM_QA_SCRIPT"
  run_cmd "Platform QA up" bash "$PLATFORM_QA_SCRIPT" up
}

run_panel() {
  require_file "$VELOPANEL_VM_SCRIPT"
  require_file "$VELOPANEL_DEPLOY_SCRIPT"

  if [[ "$DRY_RUN" == "1" ]]; then
    run_cmd "Start VeloPanel QA VM" bash "$VELOPANEL_VM_SCRIPT" start
  else
    local vm_log="/tmp/prepare-qa-velopanel-vm.log"
    info "Start VeloPanel QA VM"
    bash "$VELOPANEL_VM_SCRIPT" start >"$vm_log" 2>&1 &
    local vm_pid=$!
    local waited=0
    local max_wait=90

    while (( waited < max_wait )); do
      if limactl list velopanel 2>/dev/null | awk 'NR>1 {print $2}' | grep -qx "Running"; then
        ok "VeloPanel VM is running"
        break
      fi
      sleep 2
      waited=$((waited + 2))
    done

    if ! limactl list velopanel 2>/dev/null | awk 'NR>1 {print $2}' | grep -qx "Running"; then
      warn "VeloPanel VM did not reach Running state within ${max_wait}s"
      warn "Last VM log lines:"
      tail -n 40 "$vm_log" || true
      die "Failed to confirm VeloPanel VM startup"
    fi

    if kill -0 "$vm_pid" 2>/dev/null; then
      wait "$vm_pid" || true
    fi
  fi

  if [[ "$PANEL_FIRST_TIME" == "1" ]]; then
    run_cmd "Deploy local VeloPanel build to Lima VM (first-time setup)" \
      bash "$VELOPANEL_DEPLOY_SCRIPT" --build --first-time
  else
    run_cmd "Deploy local VeloPanel build to Lima VM" \
      bash "$VELOPANEL_DEPLOY_SCRIPT" --build
  fi
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

panel_url() {
  local path="$1"
  printf "%s%s" "${PANEL_API_URL%/}" "$path"
}

panel_api() {
  local method="$1"
  local path="$2"
  local token="${3:-}"
  local payload="${4:-}"
  local tmp status

  tmp="$(mktemp)"
  if [[ -n "$payload" ]]; then
    status="$(curl -k -sS --max-time 20 -o "$tmp" -w "%{http_code}" \
      -X "$method" "$(panel_url "$path")" \
      -H "Content-Type: application/json" \
      ${token:+-H "Authorization: Bearer $token"} \
      -d "$payload")" || {
      rm -f "$tmp"
      die "Panel API request failed: $method $path"
    }
  else
    status="$(curl -k -sS --max-time 20 -o "$tmp" -w "%{http_code}" \
      -X "$method" "$(panel_url "$path")" \
      ${token:+-H "Authorization: Bearer $token"})" || {
      rm -f "$tmp"
      die "Panel API request failed: $method $path"
    }
  fi

  RESPONSE_STATUS="$status"
  RESPONSE_BODY="$(cat "$tmp")"
  rm -f "$tmp"
}

json_field() {
  local filter="$1"
  jq -r "$filter // empty" <<<"$RESPONSE_BODY"
}

expect_status() {
  local expected="$1"
  local desc="$2"
  [[ "$RESPONSE_STATUS" == "$expected" ]] || {
    warn "$desc failed with HTTP $RESPONSE_STATUS"
    warn "$RESPONSE_BODY"
    die "$desc failed"
  }
}

ensure_panel_admin_token() {
  require_command curl
  require_command jq

  panel_api POST "/api/auth/login" "" \
    "{\"username\":\"$PANEL_ADMIN_USER\",\"password\":\"$PANEL_ADMIN_PASS\"}"

  if [[ "$RESPONSE_STATUS" == "200" ]]; then
    PANEL_ADMIN_TOKEN="$(json_field '.data.token')"
    [[ -n "$PANEL_ADMIN_TOKEN" ]] || die "Admin login returned no token"
    ok "Logged into panel as admin"
    return 0
  fi

  panel_api POST "/api/auth/setup" "" \
    "{\"username\":\"$PANEL_ADMIN_USER\",\"password\":\"$PANEL_ADMIN_PASS\"}"

  if [[ "$RESPONSE_STATUS" == "200" ]]; then
    PANEL_ADMIN_TOKEN="$(json_field '.data.token')"
    [[ -n "$PANEL_ADMIN_TOKEN" ]] || die "Admin setup returned no token"
    ok "Created panel admin account"
    return 0
  fi

  if grep -q "Setup already completed" <<<"$RESPONSE_BODY"; then
    die "Panel admin already exists, but login failed for $PANEL_ADMIN_USER. Set PANEL_ADMIN_USER/PANEL_ADMIN_PASS and retry."
  fi

  warn "$RESPONSE_BODY"
  die "Could not authenticate panel admin"
}

find_package_id() {
  panel_api GET "/api/packages" "$PANEL_ADMIN_TOKEN"
  expect_status 200 "List packages"
  jq -r --arg name "$PANEL_SEED_PACKAGE" '.data[]? | select(.name == $name) | .id' <<<"$RESPONSE_BODY" | head -n 1
}

find_account_id_by_username() {
  local username="$1"
  panel_api GET "/api/accounts" "$PANEL_ADMIN_TOKEN"
  expect_status 200 "List accounts"
  jq -r --arg username "$username" '.data[]? | select(.username == $username) | .id' <<<"$RESPONSE_BODY" | head -n 1
}

delete_account_if_exists() {
  local username="$1"
  local account_id
  account_id="$(find_account_id_by_username "$username")"
  if [[ -n "$account_id" ]]; then
    panel_api DELETE "/api/accounts/$account_id" "$PANEL_ADMIN_TOKEN"
    expect_status 200 "Delete existing account $username"
    ok "Deleted existing account $username"
  fi
}

ensure_seed_package() {
  local package_id
  package_id="$(find_package_id)"

  if [[ -n "$package_id" ]]; then
    panel_api PUT "/api/packages/$package_id" "$PANEL_ADMIN_TOKEN" \
      "{\"name\":\"$PANEL_SEED_PACKAGE\",\"disk_quota_mb\":1024,\"bandwidth_quota_mb\":10240,\"max_domains\":2,\"max_databases\":1,\"max_email_accounts\":1,\"max_ftp_accounts\":1,\"features_json\":\"{}\"}"
    expect_status 200 "Update seed package"
    ok "Updated seed package $PANEL_SEED_PACKAGE"
  else
    panel_api POST "/api/packages" "$PANEL_ADMIN_TOKEN" \
      "{\"name\":\"$PANEL_SEED_PACKAGE\",\"disk_quota_mb\":1024,\"bandwidth_quota_mb\":10240,\"max_domains\":2,\"max_databases\":1,\"max_email_accounts\":1,\"max_ftp_accounts\":1,\"features_json\":\"{}\"}"
    expect_status 200 "Create seed package"
    ok "Created seed package $PANEL_SEED_PACKAGE"
  fi
}

ensure_human_seed_account() {
  delete_account_if_exists "$PANEL_SEED_ACCOUNT_USER"

  panel_api POST "/api/accounts" "$PANEL_ADMIN_TOKEN" \
    "{\"username\":\"$PANEL_SEED_ACCOUNT_USER\",\"domain\":\"$PANEL_SEED_ACCOUNT_DOMAIN\",\"email\":\"$PANEL_SEED_ACCOUNT_EMAIL\",\"password\":\"$PANEL_SEED_ACCOUNT_PASS\",\"plan\":\"$PANEL_SEED_PACKAGE\"}"
  expect_status 200 "Create human seed account"
  PANEL_HUMAN_ACCOUNT_ID="$(json_field '.data.id')"
  [[ -n "$PANEL_HUMAN_ACCOUNT_ID" ]] || die "Human seed account returned no id"
  ok "Created human QA account $PANEL_SEED_ACCOUNT_USER"
}

run_seed() {
  if [[ "$DRY_RUN" == "1" ]]; then
    info "dry-run: authenticate panel admin"
    info "dry-run: ensure package $PANEL_SEED_PACKAGE"
    info "dry-run: recreate account $PANEL_SEED_ACCOUNT_USER"
    return 0
  fi

  ensure_panel_admin_token
  ensure_seed_package
  ensure_human_seed_account

  echo ""
  ok "Panel QA seed ready"
  echo "  Admin:   $PANEL_ADMIN_USER"
  echo "  Account: $PANEL_SEED_ACCOUNT_USER"
  echo "  Domain:  $PANEL_SEED_ACCOUNT_DOMAIN"
  echo "  Package: $PANEL_SEED_PACKAGE"
  echo "  Panel:   $PANEL_UI_URL"
}

panel_account_token() {
  local account_id="$1"
  panel_api POST "/api/accounts/$account_id/login-as" "$PANEL_ADMIN_TOKEN"
  expect_status 200 "Login as account $account_id"
  json_field '.data.token'
}

smoke_assert_limit_message() {
  local body="$1"
  local needle="$2"
  grep -Fq "$needle" <<<"$body" || {
    warn "$body"
    die "Expected limit message containing: $needle"
  }
}

run_panel_smoke() {
  local smoke_user smoke_domain smoke_email smoke_token email_configured

  if [[ "$DRY_RUN" == "1" ]]; then
    info "dry-run: authenticate panel admin"
    info "dry-run: ensure package $PANEL_SEED_PACKAGE and base account $PANEL_SEED_ACCOUNT_USER"
    info "dry-run: create temp smoke account and run domain/db/email/ftp boundary checks"
    return 0
  fi

  ensure_panel_admin_token
  ensure_seed_package
  ensure_human_seed_account

  smoke_user="${PANEL_SMOKE_USER_PREFIX}$(date +%H%M%S)"
  smoke_domain="${smoke_user}.qa.local"
  smoke_email="${smoke_user}@qa.local"

  panel_api POST "/api/accounts" "$PANEL_ADMIN_TOKEN" \
    "{\"username\":\"$smoke_user\",\"domain\":\"$smoke_domain\",\"email\":\"$smoke_email\",\"password\":\"$PANEL_SEED_ACCOUNT_PASS\",\"plan\":\"$PANEL_SEED_PACKAGE\"}"
  expect_status 200 "Create smoke account"
  local smoke_account_id
  smoke_account_id="$(json_field '.data.id')"
  [[ -n "$smoke_account_id" ]] || die "Smoke account returned no id"
  ok "Created smoke account $smoke_user"

  smoke_token="$(panel_account_token "$smoke_account_id")"
  [[ -n "$smoke_token" ]] || die "Smoke account login returned no token"

  panel_api GET "/api/panel/me" "$smoke_token"
  expect_status 200 "Panel /me"
  panel_api GET "/api/panel/prefs" "$smoke_token"
  expect_status 200 "Panel /prefs"
  smoke_assert_limit_message "$RESPONSE_BODY" "\"max_domains\":2"
  smoke_assert_limit_message "$RESPONSE_BODY" "\"max_databases\":1"
  smoke_assert_limit_message "$RESPONSE_BODY" "\"max_email_accounts\":1"
  smoke_assert_limit_message "$RESPONSE_BODY" "\"max_ftp_accounts\":1"

  panel_api GET "/api/panel/domains" "$smoke_token"
  expect_status 200 "List panel domains"
  panel_api GET "/api/panel/databases" "$smoke_token"
  expect_status 200 "List panel databases"
  panel_api GET "/api/panel/email/accounts" "$smoke_token"
  expect_status 200 "List panel email accounts"
  panel_api GET "/api/panel/ftp" "$smoke_token"
  expect_status 200 "List panel ftp accounts"

  panel_api POST "/api/panel/domains" "$smoke_token" \
    "{\"domain_name\":\"one-${smoke_domain}\",\"domain_type\":\"addon\"}"
  expect_status 200 "Create smoke domain 1"
  panel_api POST "/api/panel/domains" "$smoke_token" \
    "{\"domain_name\":\"two-${smoke_domain}\",\"domain_type\":\"addon\"}"
  [[ "$RESPONSE_STATUS" == "400" ]] || die "Expected domain limit denial on second addon domain"
  smoke_assert_limit_message "$RESPONSE_BODY" "Domain limit reached for your package"
  ok "Domain boundary smoke passed"

  panel_api POST "/api/panel/databases" "$smoke_token" \
    "{\"db_name\":\"app\",\"db_password\":\"DbPass12345\",\"engine\":\"mysql\"}"
  expect_status 200 "Create smoke database 1"
  panel_api POST "/api/panel/databases" "$smoke_token" \
    "{\"db_name\":\"overflow\",\"db_password\":\"DbPass12345\",\"engine\":\"mysql\"}"
  [[ "$RESPONSE_STATUS" == "400" ]] || die "Expected database limit denial on second database"
  smoke_assert_limit_message "$RESPONSE_BODY" "Database limit reached for your package"
  ok "Database boundary smoke passed"

  panel_api POST "/api/panel/ftp" "$smoke_token" \
    "{\"username\":\"ftp1\",\"password\":\"FtpPass12345\",\"directory\":\"public_html\",\"quota_mb\":0}"
  expect_status 200 "Create smoke ftp 1"
  panel_api POST "/api/panel/ftp" "$smoke_token" \
    "{\"username\":\"ftp2\",\"password\":\"FtpPass12345\",\"directory\":\"public_html\",\"quota_mb\":0}"
  [[ "$RESPONSE_STATUS" == "400" ]] || die "Expected FTP limit denial on second ftp account"
  smoke_assert_limit_message "$RESPONSE_BODY" "FTP account limit reached for your package"
  ok "FTP boundary smoke passed"

  panel_api GET "/api/panel/email/status" "$smoke_token"
  expect_status 200 "Email service status"
  email_configured="$(json_field '.data.configured')"
  if [[ "$email_configured" == "true" ]]; then
    panel_api POST "/api/panel/email/accounts" "$smoke_token" \
      "{\"email\":\"mail@$smoke_domain\",\"password\":\"MailPass12345\",\"quota_mb\":250}"
    expect_status 200 "Create smoke email 1"
    panel_api POST "/api/panel/email/accounts" "$smoke_token" \
      "{\"email\":\"mail2@$smoke_domain\",\"password\":\"MailPass12345\",\"quota_mb\":250}"
    [[ "$RESPONSE_STATUS" == "400" ]] || die "Expected email limit denial on second email account"
    smoke_assert_limit_message "$RESPONSE_BODY" "Email account limit reached for your package"
    ok "Email boundary smoke passed"
  else
    warn "Email service not configured in QA VM; skipping email create boundary smoke"
  fi

  ok "Panel API smoke passed"
  echo ""
  echo "Manual QA seed:"
  echo "  Admin:   $PANEL_ADMIN_USER"
  echo "  Account: $PANEL_SEED_ACCOUNT_USER"
  echo "  Domain:  $PANEL_SEED_ACCOUNT_DOMAIN"
  echo "  Package: $PANEL_SEED_PACKAGE"
}

smoke_url() {
  local label="$1"
  local url="$2"

  if [[ "$DRY_RUN" == "1" ]]; then
    info "dry-run: smoke $label -> $url"
    return 0
  fi

  if curl -k -fsS --max-time 8 "$url" >/dev/null 2>&1; then
    ok "$label reachable: $url"
  else
    warn "$label not reachable yet: $url"
  fi
}

run_smoke() {
  smoke_url "Panel API health" "$(panel_url "/api/health")"
  smoke_url "Platform health" "$PLATFORM_HEALTH_URL"
  smoke_url "Platform UI" "$PLATFORM_UI_URL"
  smoke_url "Panel UI" "$PANEL_UI_URL"
  smoke_url "Panel hosted HTTP" "$PANEL_HTTP_URL"
  smoke_url "Panel hosted HTTPS" "$PANEL_HTTPS_URL"
}

parse_args() {
  [[ "$#" -gt 0 ]] || {
    usage
    exit 1
  }

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      status|platform|panel|seed|panel-smoke|all|smoke)
        [[ -z "$ACTION" ]] || die "Only one action is allowed"
        ACTION="$1"
        ;;
      --dry-run)
        DRY_RUN=1
        ;;
      --panel-first-time)
        PANEL_FIRST_TIME=1
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument: $1"
        ;;
    esac
    shift
  done

  [[ -n "$ACTION" ]] || die "Missing action"
}

main() {
  parse_args "$@"

  case "$ACTION" in
    status)
      show_status
      ;;
    platform)
      run_platform
      ;;
    panel)
      run_panel
      ;;
    seed)
      run_seed
      ;;
    panel-smoke)
      run_panel_smoke
      ;;
    all)
      run_platform
      run_panel
      run_seed
      run_panel_smoke
      run_smoke
      ;;
    smoke)
      run_smoke
      ;;
    *)
      die "Unhandled action: $ACTION"
      ;;
  esac
}

main "$@"
