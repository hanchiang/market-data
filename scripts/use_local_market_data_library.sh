#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
library_root="${repo_root}/../market-data-library"

if [[ ! -f "${library_root}/pyproject.toml" ]]; then
  echo "Expected sibling market-data-library repo at ${library_root}" >&2
  exit 1
fi

cd "${repo_root}"

# Do not let an already-activated sibling repo virtualenv override this repo's Poetry env.
unset VIRTUAL_ENV
unset POETRY_ACTIVE
unset PYTHONHOME
unset PYTHONPATH

poetry run python -m pip uninstall -y market-data-library >/dev/null 2>&1 || true
poetry run python -m pip install --no-deps --editable "${library_root}" >/dev/null

echo "Using local editable market-data-library from ${library_root}"
echo "Re-run this script after poetry install if Poetry reinstalls the git dependency."
