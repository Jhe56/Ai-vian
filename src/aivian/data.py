from __future__ import annotations
import os
from pathlib import Path


from .config import DATASETS, DEFAULT_DATASET, CSV_NAMES, resolve_cache_dir
 
 
def _running_on_kaggle() -> bool:
    """Kaggle Notebooks set this env var; a reliable way to detect the environment."""
    return "KAGGLE_KERNEL_RUN_TYPE" in os.environ
 
 
def _kaggle_attached_path(slug: str) -> Path | None:
    """Look for the dataset already attached under /kaggle/input."""
    candidate = Path("/kaggle/input") / slug.split("/")[-1]
    return candidate if candidate.exists() else None
 
 
def get_dataset_path(name: str = DEFAULT_DATASET) -> Path:
    """Return a local path to a dataset's root, downloading it only if needed.
 
    Args:
        name: A short name from config.DATASETS (e.g. "A-M", "N-Z").
 
    Raises:
        RuntimeError: if kagglehub is needed but not installed.
    """
    slug = DATASETS[name]
 
    if _running_on_kaggle():
        attached = _kaggle_attached_path(slug)
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
 
    return Path(kagglehub.dataset_download(slug))
 
 
def get_csv_paths() -> dict[str, Path]:
    """Return {dataset name: path to its metadata CSV}, ready for pd.read_csv."""
    paths = {}
    for name in DATASETS:
        root = get_dataset_path(name)
        matches = sorted(root.rglob(CSV_NAMES[name]))
        if not matches:
            raise FileNotFoundError(f"No {CSV_NAMES[name]} found under {root} ({name}).")
        paths[name] = matches[0]
    return paths
 
 
if __name__ == "__main__":
    for name, path in get_csv_paths().items():
        print(f"{name}: {path}")

# from __future__ import annotations

# import os
# from pathlib import Path

# from .config import DATASET_SLUG, resolve_cache_dir


# def _running_on_kaggle() -> bool:
#     """Kaggle Notebooks set this env var; a reliable way to detect the environment."""
#     return "KAGGLE_KERNEL_RUN_TYPE" in os.environ


# def _kaggle_attached_path() -> Path | None:
#     """Look for the dataset already attached under /kaggle/input."""
#     dataset_dirname = DATASET_SLUG.split("/")[-1]
#     candidate = Path("/kaggle/input") / dataset_dirname
#     return candidate if candidate.exists() else None


# def get_dataset_path() -> Path:
#     """Return a local path to the dataset root, downloading it only if needed.

#     Raises:
#         RuntimeError: if kagglehub is needed but not installed.
#     """
#     if _running_on_kaggle():
#         attached = _kaggle_attached_path()
#         if attached is not None:
#             return attached
#         # Fall through to kagglehub if, for some reason, it isn't attached.

#     cache_dir = resolve_cache_dir()
#     if cache_dir is not None:
#         os.environ.setdefault("KAGGLEHUB_CACHE", str(cache_dir))

#     try:
#         import kagglehub
#     except ImportError as exc:  # pragma: no cover
#         raise RuntimeError(
#             "kagglehub is required to download the dataset outside of a "
#             "Kaggle Notebook. Install it with `uv add kagglehub` or "
#             "`pip install kagglehub`."
#         ) from exc

#     return Path(kagglehub.dataset_download(DATASET_SLUG))


# if __name__ == "__main__":
#     path = get_dataset_path()
#     print(f"Dataset available at: {path}")