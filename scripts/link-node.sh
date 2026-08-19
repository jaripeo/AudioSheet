#!/usr/bin/env bash
# Expose the Node toolchain from the nodejs-wheel-binaries package on a stable path.
#
# Node is not available system-wide in every environment this project is developed
# in, so `make bootstrap-ts` installs it as a Python wheel and this script links the
# binaries into .tooling/bin. A system Node, when present, is preferred: pass
# AUDIOSHEET_USE_SYSTEM_NODE=1.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tooling="$root/.tooling"
bin="$tooling/bin"

# The npm-installed pnpm shim starts with `#!/usr/bin/env node`, so node has to be
# resolvable by name before pnpm can run at all.
export PATH="$bin:$PATH"

if [[ "${AUDIOSHEET_USE_SYSTEM_NODE:-0}" == "1" ]]; then
  command -v node >/dev/null || { echo "AUDIOSHEET_USE_SYSTEM_NODE=1 but no node on PATH" >&2; exit 1; }
  echo "using system node: $(node --version)"
  exit 0
fi

wheel="$(find "$tooling/lib" -maxdepth 3 -type d -name nodejs_wheel -print -quit)"
if [[ -z "$wheel" ]]; then
  echo "nodejs_wheel not found under $tooling/lib; run: .tooling/bin/pip install nodejs-wheel-binaries" >&2
  exit 1
fi

ln -sf "$wheel/bin/node" "$bin/node"

# npm and npx ship as scripts that resolve their CLI relative to their own location,
# which a symlink breaks; wrap them instead.
for tool in npm npx; do
  cat > "$bin/$tool" <<WRAP
#!/bin/sh
exec "$wheel/bin/node" "$wheel/lib/node_modules/npm/bin/$tool-cli.js" "\$@"
WRAP
  chmod +x "$bin/$tool"
done

if [[ ! -x "$bin/pnpm" ]]; then
  echo ">> installing pnpm"
  "$bin/npm" install -g --prefix "$tooling" pnpm@9 >/dev/null
fi

echo "node $("$bin/node" --version), npm $("$bin/npm" --version), pnpm $("$bin/pnpm" --version)"
