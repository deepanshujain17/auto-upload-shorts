import asyncio
import os
from pathlib import Path
from typing import Dict, Optional

class FileLock:
    _locks: Dict[str, asyncio.Lock] = {}

    @classmethod
    def get_lock(cls, file_path: str) -> asyncio.Lock:
        """Get or create a lock for the given file path."""
        abs_path = str(Path(file_path).resolve())
        if abs_path not in cls._locks:
            cls._locks[abs_path] = asyncio.Lock()
        return cls._locks[abs_path]

    @classmethod
    async def acquire(cls, file_path: str):
        """Acquire a lock for the given file path."""
        lock = cls.get_lock(file_path)
        await lock.acquire()

    @classmethod
    async def release(cls, file_path: str):
        """Release the lock for the given file path."""
        lock = cls.get_lock(file_path)
        lock.release()
