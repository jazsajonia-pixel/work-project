import hashlib
import os
from pathlib import Path

CACHE_DIR = Path('/tmp/gschpt-materialized')
BLOB_TOKEN = os.getenv('BLOB_READ_WRITE_TOKEN') or os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN')
BLOB_STORE_ID = os.getenv('BLOB_STORE_ID')
try:
    from vercel.blob import sync as blob
except Exception:  # Optional locally; local filesystem remains the development default.
    blob = None


def persistent_enabled() -> bool:
    return bool(blob and (BLOB_TOKEN or (BLOB_STORE_ID and os.getenv('VERCEL_OIDC_TOKEN'))))


def storage_mode() -> str:
    if persistent_enabled():
        return 'persistent'
    return 'ephemeral' if os.getenv('VERCEL') else 'local'


def _blob_ref(pathname: str) -> str:
    return f'blob:{pathname}'


def _pathname(reference: str) -> str:
    return reference[5:] if reference.startswith('blob:') else reference


def put(pathname: str, data: bytes, content_type: str) -> str:
    if not persistent_enabled():
        raise RuntimeError('Persistent object storage is not configured.')
    result = blob.put_blob(pathname, data, access='private', content_type=content_type, allow_overwrite=True)
    return _blob_ref(result.pathname)


def read(reference: str) -> bytes:
    if not reference.startswith('blob:'):
        return Path(reference).read_bytes()
    if not persistent_enabled():
        raise FileNotFoundError('Persistent object storage is not configured.')
    return blob.get_blob(_pathname(reference), access='private').body


def remove(reference: str) -> None:
    if reference.startswith('blob:') and persistent_enabled():
        blob.delete_blob(_pathname(reference))
    else:
        Path(reference).unlink(missing_ok=True)


def materialize(reference: str) -> Path:
    if not reference.startswith('blob:'):
        return Path(reference)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(reference.encode()).hexdigest()
    target = CACHE_DIR / digest
    if not target.exists():
        target.write_bytes(read(reference))
    return target
