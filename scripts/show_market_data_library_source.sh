#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${repo_root}"

# Keep the Poetry environment authoritative when probing the import source.
unset VIRTUAL_ENV
unset POETRY_ACTIVE
unset PYTHONHOME
unset PYTHONPATH

poetry run python - <<'PY'
import importlib.metadata as metadata
import json
import os

import market_data_library

dist = metadata.distribution('market-data-library')
direct_url_text = dist.read_text('direct_url.json')
mode = 'unknown'
configured_source = 'unknown'

if direct_url_text:
    direct_url = json.loads(direct_url_text)
    configured_source = direct_url.get('url', configured_source)
    if direct_url.get('dir_info', {}).get('editable'):
        mode = 'local-sibling-editable'
    elif 'vcs_info' in direct_url:
        mode = 'git-installed-package'

print(f'Dependency mode: {mode}')
print(f'Configured source: {configured_source}')
print(f'Imported module path: {os.path.realpath(os.path.dirname(market_data_library.__file__))}')
PY
