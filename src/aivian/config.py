"""Central configuration for the Ai-vian project.

Keeping the dataset reference here (instead of inline in notebooks/scripts)
means there is exactly one place to look when the dataset moves, gets a new
version, or the storage location changes between machines.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Dataset reference -----------------------------------------------------
# Kaggle dataset slug in "<owner>/<dataset>" form. This is the single source
# of truth for which dataset the project uses.
DATASET_SLUG = "rohanrao/xeno-canto-bird-recordings-extended-a-m"

# --- Storage location --------------------------------------------------
# kagglehub caches downloads under ~/.cache/kagglehub by default, which is
# fine on a remote/cloud box but not something you want eating 17GB+ of a
# laptop's disk. Setting the KAGGLEHUB_CACHE env var lets you redirect that
# cache to:
#   - /kaggle/input  (implicitly, when running inside an actual Kaggle
#     Notebook -- the dataset is already attached there, see data.py)
#   - an external drive or a mounted cloud volume when running locally
#   - a project-local "data/" folder if you don't mind the bloat, e.g. on a
#     disposable cloud VM
#
# Example (bash):
#   export KAGGLEHUB_CACHE=/mnt/external-drive/kagglehub-cache
#
# If unset, kagglehub's own default is used.
CACHE_DIR_ENV_VAR = "KAGGLEHUB_CACHE"


def resolve_cache_dir() -> Path | None:
    """Return the configured cache directory, or None to use kagglehub's default."""
    value = os.environ.get(CACHE_DIR_ENV_VAR)
    return Path(value).expanduser() if value else None