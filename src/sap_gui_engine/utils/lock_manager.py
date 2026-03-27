import os
import threading
import time
from pathlib import Path
from typing import Optional


class ConnectionLockManager:
    """
    A file-based lock manager to ensure only one worker can call open_connection at a time.
    This is especially important when using Dramatiq with multiple workers.
    """

    def __init__(self, lock_file_path: Optional[str] = None):
        if lock_file_path:
            self.lock_file = Path(lock_file_path)
        else:
            # Default to a lock file in the temp directory
            temp_dir = Path(os.environ.get('TEMP', os.path.expanduser('~')))
            self.lock_file = temp_dir / 'sap_connection.lock'

        # Use threading lock for same-process synchronization
        self._thread_lock = threading.Lock()

    def acquire(self, timeout: int = 30) -> bool:
        """
        Acquire the lock with a timeout.

        Args:
            timeout: Maximum time to wait for the lock in seconds

        Returns:
            bool: True if lock was acquired, False otherwise
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # First try to acquire the thread lock
            if self._thread_lock.acquire(blocking=False):
                try:
                    # Now try to create the file lock
                    try:
                        # Try to create the lock file exclusively
                        fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                        os.close(fd)
                        # Successfully created the lock file
                        return True
                    except FileExistsError:
                        # Lock file already exists, another process holds the lock
                        pass
                finally:
                    # Release the thread lock regardless of file lock status
                    self._thread_lock.release()

            # Wait a bit before retrying
            time.sleep(0.1)

        return False

    def release(self) -> bool:
        """
        Release the lock.

        Returns:
            bool: True if lock was released, False if we didn't hold the lock
        """
        try:
            # Acquire thread lock first
            if self._thread_lock.acquire(blocking=False):
                try:
                    # Remove the lock file if it exists and we own it
                    if self.lock_file.exists():
                        self.lock_file.unlink()
                        return True
                    return False
                finally:
                    self._thread_lock.release()
            return False
        except Exception:
            # If anything goes wrong, try to release the thread lock
            try:
                self._thread_lock.release()
            except RuntimeError:
                # Thread lock wasn't held, ignore
                pass
            return False

    def __enter__(self):
        """Context manager entry."""
        acquired = self.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock within timeout period for {self.lock_file}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


# Global lock manager instance
_global_lock_manager = None


def get_global_lock_manager() -> ConnectionLockManager:
    """Get the global lock manager instance."""
    global _global_lock_manager
    if _global_lock_manager is None:
        _global_lock_manager = ConnectionLockManager()
    return _global_lock_manager
