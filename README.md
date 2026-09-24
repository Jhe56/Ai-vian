# Ai-vian (a temp readme by claude)

## Dataset

Single reference, defined in `src/aivian/config.py`:

```python
DATASET_SLUG = "rohanrao/xeno-canto-bird-recordings-extended-a-m"
```

Nowhere else in the codebase should the slug or a raw filesystem path to the
dataset appear -- call `aivian.data.get_dataset_path()` instead.

## Running this project without bloating your local machine

The dataset is ~17GB. `get_dataset_path()` picks the right source automatically:

| Where you run it | What happens |
|---|---|
| An actual **Kaggle Notebook** | Dataset is already attached at `/kaggle/input/...` -- nothing is downloaded, zero local disk cost. This is the recommended way to do any heavy processing. |
| **Locally**, no config | Downloads once via `kagglehub` to its default cache (`~/.cache/kagglehub`). |
| **Locally or on a remote VM**, with `KAGGLEHUB_CACHE` set | Downloads once via `kagglehub`, cached wherever you point it (external drive, mounted cloud volume, scratch disk on a disposable VM). |

To redirect the cache:

```bash
cp .env.example .env   # then edit the path
export KAGGLEHUB_CACHE=/mnt/external-drive/kagglehub-cache
```

### Recommended workflow

For anything beyond quick local testing, push the work to a **Kaggle
Notebook** (Settings -> Accelerator as needed) and import this repo's
`src/` there. That keeps the dataset, the compute, and the 17GB download
entirely off your laptop -- only code and small artifacts (figures, trained
model weights, metrics) need to come back to this repo.

## Setup

```bash
uv sync
PYTHONPATH=src uv run python -m aivian.data   # sanity-check dataset access
```