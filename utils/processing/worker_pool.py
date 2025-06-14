"""
Worker pool implementation for managing concurrent processing tasks.
Provides controlled parallelism and resource management.
"""

import asyncio
from typing import Dict, List, Any, Awaitable, Optional
import multiprocessing


class VideoWorkerPool:
    """A pool of worker tasks for video processing with controlled concurrency."""

    def __init__(self, max_workers: int = None):
        """
        Initialize the worker pool with the specified maximum number of workers.

        Args:
            max_workers: Maximum number of concurrent video processing tasks.
                         Defaults to CPU count.
        """
        if max_workers is None:
            # Default to CPU count for optimal parallelism
            max_workers = max(1, multiprocessing.cpu_count())

        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        self.tasks: List[asyncio.Task] = []
        self.results: Dict[str, Any] = {}

    async def submit(self, task_id: str, coro: Awaitable) -> None:
        """
        Submit a coroutine to be executed with semaphore control.

        Args:
            task_id: Unique identifier for the task
            coro: Coroutine to execute
        """
        async def _wrapped_task():
            print(f"🔄 Starting task: {task_id}")
            async with self.semaphore:
                try:
                    result = await coro
                    self.results[task_id] = result
                    print(f"✅ Completed task: {task_id}")
                except Exception as e:
                    print(f"❌ Task {task_id} failed: {str(e)}")
                    self.results[task_id] = None
                    # Re-raise to ensure the error is captured by wait_all
                    raise

        task = asyncio.create_task(_wrapped_task())
        self.tasks.append(task)

    async def wait_all(self) -> Dict[str, Any]:
        """
        Wait for all submitted tasks to complete.

        Returns:
            Dict mapping task_ids to their results
        """
        if not self.tasks:
            return self.results

        await asyncio.gather(*self.tasks, return_exceptions=True)
        return self.results


# Global instance for shared use across the application
_shared_pool: Optional[VideoWorkerPool] = None
_pool_lock = asyncio.Lock()


async def get_worker_pool(max_workers: int = None) -> VideoWorkerPool:
    """Get or create a shared worker pool instance."""
    global _shared_pool

    async with _pool_lock:
        if _shared_pool is None:
            _shared_pool = VideoWorkerPool(max_workers)

    return _shared_pool


async def cleanup_worker_pool() -> None:
    """Clean up the shared worker pool."""
    global _shared_pool

    if _shared_pool is not None:
        # Make sure all tasks are completed
        if _shared_pool.tasks:
            try:
                await asyncio.gather(*_shared_pool.tasks, return_exceptions=True)
            except Exception:
                pass

        # Clear the pool
        async with _pool_lock:
            _shared_pool = None
