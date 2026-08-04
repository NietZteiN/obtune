#!/usr/bin/env bash
# Install the pre-commit hook. There is no hosted CI on this host, so the integrity
# checks (SHA manifests + H1-marker content scan + quarantine lint) run here.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/.git/hooks/pre-commit"
cat > "$HOOK" <<'HOOKEOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
echo "[pre-commit] obtune integrity check"
make check
HOOKEOF
chmod +x "$HOOK"
echo "installed $HOOK"
