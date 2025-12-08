"""
Memory trimming utility to return freed memory to the OS.

Python's garbage collector frees memory but glibc may hold onto freed arenas.
This module periodically calls malloc_trim to return memory to the OS.
"""
import ctypes
import logging
import threading
import time

logger = logging.getLogger(__name__)


def _trim_loop(period_sec=600):
    """Background thread that periodically trims malloc arenas."""
    try:
        libc = ctypes.CDLL("libc.so.6")
    except Exception as e:
        logger.warning(f"Could not load libc.so.6 for malloc_trim: {e}")
        return
    
    logger.info(f"malloc_trim thread started (period: {period_sec}s)")
    
    while True:
        try:
            libc.malloc_trim(0)
        except Exception as e:
            logger.warning(f"malloc_trim failed: {e}")
        time.sleep(period_sec)


def start_malloc_trimmer(period_sec=600):
    """
    Start a background daemon thread that periodically calls malloc_trim.
    
    Args:
        period_sec: Interval in seconds between malloc_trim calls (default: 600 = 10 minutes)
    """
    t = threading.Thread(target=_trim_loop, args=(period_sec,), daemon=True)
    t.start()
    logger.info(f"Started malloc_trimmer with {period_sec}s period")
