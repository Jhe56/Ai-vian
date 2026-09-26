"""Portable access to the project's dataset.

`get_dataset_path()` is the one function the rest of the codebase should
call. It resolves to the right location no matter where the code runs:

1. Inside an actual Kaggle Notebook, the dataset is already attached and
   mounted read-only at /kaggle/input/<dataset-name> -- no download needed.
2. Elsewhere (local machine, a remote VM, Colab, etc.), it downloads via
   kagglehub, honoring KAGGLEHUB_CACHE (see config.py) so you control where
   the ~17GB actually lands.
"""

from __future__ import annotations

import os
from pathlib import Path

from .config import DATASET_SLUG, resolve_cache_dir


def _running_on_kaggle() -> bool:
    """Kaggle Notebooks set this env var; a reliable way to detect the environment."""
    return "KAGGLE_KERNEL_RUN_TYPE" in os.environ


def _kaggle_attached_path() -> Path | None:
    """Look for the dataset already attached under /kaggle/input."""
    dataset_dirname = DATASET_SLUG.split("/")[-1]
    candidate = Path("/kaggle/input") / dataset_dirname
    return candidate if candidate.exists() else None


def get_dataset_path() -> Path:
    """Return a local path to the dataset root, downloading it only if needed.

    Raises:
        RuntimeError: if kagglehub is needed but not installed.
    """
    if _running_on_kaggle():
        attached = _kaggle_attached_path()
        if attached is not None:
            return attached
        # Fall through to kagglehub if, for some reason, it isn't attached.

    cache_dir = resolve_cache_dir()
    if cache_dir is not None:
        os.environ.setdefault("KAGGLEHUB_CACHE", str(cache_dir))

    try:
        import kagglehub
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "kagglehub is required to download the dataset outside of a "
            "Kaggle Notebook. Install it with `uv add kagglehub` or "
            "`pip install kagglehub`."
        ) from exc

    return Path(kagglehub.dataset_download(DATASET_SLUG))


if __name__ == "__main__":
    path = get_dataset_path()
    print(f"Dataset available at: {path}")