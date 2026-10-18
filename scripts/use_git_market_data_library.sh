#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

# Do not let an already-activated sibling repo virtualenv override this repo's Poetry env.
unset VIRTUAL_ENV
unset POETRY_ACTIVE
unset PYTHONHOME
unset PYTHONPATH

# The default comes from pyproject.toml's pin, never a literal here: a hardcoded ref sat at
# 1.5.0 while the pin moved to 1.8.0, so a bare run downgraded the library. Parsed as TOML so
# a moved or reformatted declaration fails loudly instead of yielding a wrong value.
read -r pinned_repo pinned_ref < <(poetry run python -c '
import sys, tomllib
with open(sys.argv[1], "rb") as fh:
    dep = tomllib.load(fh)["tool"]["poetry"]["dependencies"]["market-data-library"]
print(dep["git"], dep["rev"])
' pyproject.toml)

git_repo="${MARKET_DATA_LIBRARY_GIT_REPO:-git+${pinned_repo}}"
git_ref="${MARKET_DATA_LIBRARY_GIT_REF:-${pinned_ref}}"

relock="(unset VIRTUAL_ENV POETRY_ACTIVE; poetry lock && poetry sync)"

poetry run python -m pip uninstall -y market-data-library >/dev/null 2>&1 || true
# `--no-deps`: the lock governs every other package. Without it, `--force-reinstall` resolved
# the library's own ranges afresh and moved 18 packages off the lock (aiohttp 3.13.3 to 3.14.5).
poetry run python -m pip install --no-deps --force-reinstall "market-data-library @ ${git_repo}@${git_ref}"

# `--no-deps` turns a dependency the lock does not carry into an ImportError later, so catch it here.
if ! poetry run python -m pip check; then
  echo "market-data-library ${git_ref} needs packages the lock does not have." >&2
  echo "Run: ${relock}" >&2
  exit 1
fi

echo "Using git-installed market-data-library from ${git_repo}@${git_ref}"
echo "If that version changed its own dependencies, run: ${relock}"
