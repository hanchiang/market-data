#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git_repo="${MARKET_DATA_LIBRARY_GIT_REPO:-git+ssh://git@github.com/hanchiang/market_data_api.git}"
git_ref="${MARKET_DATA_LIBRARY_GIT_REF:-1.5.0}"

cd "${repo_root}"

# Do not let an already-activated sibling repo virtualenv override this repo's Poetry env.
unset VIRTUAL_ENV
unset POETRY_ACTIVE
unset PYTHONHOME
unset PYTHONPATH

poetry run python -m pip uninstall -y market-data-library >/dev/null 2>&1 || true
poetry run python -m pip install --force-reinstall "market-data-library @ ${git_repo}@${git_ref}"

echo "Using git-installed market-data-library from ${git_repo}@${git_ref}"
