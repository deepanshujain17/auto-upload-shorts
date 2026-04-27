"""Idempotency store: append-only JSONL of upload keys to avoid duplicate uploads on reruns."""

import asyncio
import hashlib
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, Optional

from utils.file_lock import FileLock

_upload_key_locks: Dict[str, asyncio.Lock] = {}
_upload_key_locks_guard = asyncio.Lock()


@asynccontextmanager
async def serialize_same_upload_key(key: str) -> AsyncIterator[None]:
    """
    Serialize was_uploaded → upload → mark_uploaded for one idempotency key.

    Without this, concurrent tasks with the same key can both pass was_uploaded
    before either appends to the store (TOCTOU). Unrelated keys still run in parallel.
    """
    async with _upload_key_locks_guard:
        if key not in _upload_key_locks:
            _upload_key_locks[key] = asyncio.Lock()
        lock = _upload_key_locks[key]
    async with lock:
        yield


def _stable_article_id(article: Dict[str, Any]) -> str:
    """
    Return a stable identity string for an article.

    - Prefer URL: it's the best cross-run/cross-machine identifier.
    - Fall back to title + publishedAt when URL is missing (some feeds omit it).

    This function intentionally returns a *string*, not a hash. Hashing happens later
    after country/language are included, so different locales don't collide.
    """
    url = (article.get("url") or "").strip()
    if url:
        return url
    title = (article.get("title") or "").strip()
    published = (article.get("publishedAt") or "").strip()
    if title or published:
        return f"{title}::{published}"
    # No stable identity: avoid "::" colliding across different malformed rows in one run.
    return f"unknown::{uuid.uuid4().hex}"


def make_upload_key(*, article: Dict[str, Any], country: str, language: str) -> str:
    """
    Build a deterministic idempotency key for "did we already upload this?" checks.

    We include country + language because the same article may be uploaded in
    different locales (different voice, metadata, playlists, etc.).
    """
    raw = f"{country}::{language}::{_stable_article_id(article)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def was_uploaded(*, store_path: str, key: str) -> bool:
    """
    Check if a given key exists in the JSONL store.

    Store format: one JSON object per line (append-only).
    """
    if not os.path.exists(store_path):
        return False

    # Use the existing in-process path lock to avoid concurrent writers/readers
    # interleaving and corrupting reads while a write is in progress.
    await FileLock.acquire(store_path)
    try:
        with open(store_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("key") == key:
                    return True
        return False
    finally:
        await FileLock.release(store_path)


async def mark_uploaded(
    *,
    store_path: str,
    key: str,
    video_id: str,
    article: Dict[str, Any],
    country: str,
    language: str,
    category: str,
    hashtag: Optional[str],
) -> None:
    """
    Append a successful upload record to the JSONL store.

    This is intentionally append-only:
    - fast
    - resilient to partial writes (worst case you lose one trailing line)
    - easy to inspect/debug in CI
    """
    os.makedirs(os.path.dirname(store_path), exist_ok=True)

    record = {
        "key": key,
        "video_id": video_id,
        "article_url": (article.get("url") or "").strip() or None,
        "article_title": (article.get("title") or "").strip() or None,
        "country": country,
        "language": language,
        "category": category,
        "hashtag": hashtag,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    await FileLock.acquire(store_path)
    try:
        with open(store_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    finally:
        await FileLock.release(store_path)
