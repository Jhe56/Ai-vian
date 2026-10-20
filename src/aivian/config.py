"""Central configuration for the Ai-vian project.

Keeping the dataset reference here, as well as defining default dataset and csv names
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Dataset reference -----------------------------------------------------
# Kaggle dataset slug in "<owner>/<dataset>" form. This is the single source
# of truth for which dataset the project uses.
DATASETS = {
    "A-M" : "rohanrao/xeno-canto-bird-recordings-extended-a-m",
    "N-Z" : "rohanrao/xeno-canto-bird-recordings-extended-n-z",
    "CA-NV-USA" : "samhiatt/xenocanto-avian-vocalizations-canv-usa",
    "EU" : "monogenea/birdsongs-from-europe",
} 

DEFAULT_DATASET = "A-M"

CSV_NAMES = {
    "A-M" : "train_extended.csv",
    "N-Z" : "train_extended.csv",
    "CA-NV-USA" : "xeno-canto_ca-nv_index.csv",
    "EU" : "metadata.csv",
}

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