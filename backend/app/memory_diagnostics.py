"""
Advanced memory diagnostics module for identifying memory leaks.
Combines tracemalloc, psutil, and gc introspection for comprehensive tracking.
"""

import os
import sys
import gc
import logging
import tracemalloc
import psutil
import threading
import time
import ctypes
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from pathlib import Path
import json

logger = logging.getLogger("uvicorn")

# Configuration
BYTES_TO_MB = 1024 * 1024
ENABLE_MEMORY_MONITORING = os.getenv("ENABLE_MEMORY_MONITORING", "true").lower() == "true"
TRACEMALLOC_FRAMES = int(os.getenv("TRACEMALLOC_FRAMES", "25"))
SNAPSHOT_INTERVAL_SECONDS = int(os.getenv("SNAPSHOT_INTERVAL_SECONDS", "300"))  # 5 minutes


class MemoryDiagnostics:
    """
    Comprehensive memory diagnostics with tracemalloc snapshots,
    object counting, and malloc trimming.
    """
    
    def __init__(self):
        self.process = psutil.Process()
        self.snapshots: List[Tuple[datetime, Any]] = []
        self.max_snapshots = 12  # Keep last 12 snapshots (~1 hour if every 5 min)
        self._snapshot_lock = threading.Lock()
        self._baseline_snapshot = None
        self._malloc_trim_enabled = False
        self._monitoring_enabled = ENABLE_MEMORY_MONITORING
        
        if not self._monitoring_enabled:
            logger.info("Memory monitoring disabled via ENABLE_MEMORY_MONITORING=false")
            return
        
        # Try to load libc for malloc_trim
        try:
            self.libc = ctypes.CDLL("libc.so.6")
            self._malloc_trim_enabled = True
            logger.info("malloc_trim enabled")
        except Exception as e:
            logger.warning(f"malloc_trim not available: {e}")
            self.libc = None
        
        # Start tracemalloc if enabled
        if self._monitoring_enabled:
            if not tracemalloc.is_tracing():
                tracemalloc.start(TRACEMALLOC_FRAMES)
                logger.info(f"tracemalloc started (capturing {TRACEMALLOC_FRAMES} frames)")
                
                # Take baseline snapshot
                time.sleep(0.1)  # Let things settle
                self._baseline_snapshot = tracemalloc.take_snapshot()
                logger.info("Baseline memory snapshot captured")
        else:
            logger.info("tracemalloc disabled via config")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics.
        This is the main method to call for the dashboard.
        """
        if not self._monitoring_enabled:
            return {}
        
        try:
            # Process memory info
            mem_info = self.process.memory_info()
            mem_percent = self.process.memory_percent()
            
            # System memory
            sys_mem = psutil.virtual_memory()
            
            # GC statistics
            gc_stats = gc.get_stats()
            gc_counts = gc.get_count()
            
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                
                # Process memory
                "process": {
                    "rss_mb": mem_info.rss / BYTES_TO_MB,
                    "vms_mb": mem_info.vms / BYTES_TO_MB,
                    "percent": mem_percent,
                    "num_threads": self.process.num_threads(),
                },
                
                # System memory
                "system": {
                    "total_mb": sys_mem.total / BYTES_TO_MB,
                    "available_mb": sys_mem.available / BYTES_TO_MB,
                    "used_mb": sys_mem.used / BYTES_TO_MB,
                    "percent": sys_mem.percent,
                },
                
                # Python GC
                "gc": {
                    "counts": {
                        "generation_0": gc_counts[0],
                        "generation_1": gc_counts[1],
                        "generation_2": gc_counts[2],
                    },
                    "thresholds": gc.get_threshold(),
                    # Note: gc.get_objects() removed - it creates massive memory spikes (400MB+)
                    # on systems with 600K+ objects. Use tracemalloc stats instead.
                },
            }
            
            # Add tracemalloc stats if enabled
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                stats["tracemalloc"] = {
                    "current_mb": current / BYTES_TO_MB,
                    "peak_mb": peak / BYTES_TO_MB,
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error collecting memory stats: {e}", exc_info=True)
            return {}
    
    def get_top_allocations_by_type(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top memory allocations grouped by file/line.
        REPLACEMENT for get_top_objects() - uses tracemalloc instead of gc.get_objects().
        
        This is much more memory-efficient and still shows WHERE memory is allocated.
        """
        if not self._monitoring_enabled or not tracemalloc.is_tracing():
            return []
        
        try:
            snapshot = tracemalloc.take_snapshot()
            
            # Group by traceback (file + line)
            top_stats = snapshot.statistics('traceback')
            
            allocations = []
            for stat in top_stats[:limit]:
                # Get the most relevant frame (skip tracemalloc internals)
                frames = stat.traceback.format()
                location = frames[0] if frames else "unknown"
                
                allocations.append({
                    "location": location,
                    "size_mb": stat.size / BYTES_TO_MB,
                    "count": stat.count,
                    "avg_size_bytes": stat.size / stat.count if stat.count > 0 else 0,
                })
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error getting top allocations: {e}", exc_info=True)
            return []
    
    def get_tracemalloc_top_allocations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top memory allocations by line number.
        Shows WHERE in your code memory is being allocated.
        """
        if not self._monitoring_enabled or not tracemalloc.is_tracing():
            return []
        
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            allocations = []
            for stat in top_stats[:limit]:
                allocations.append({
                    "filename": stat.traceback.format()[0] if stat.traceback else "unknown",
                    "size_mb": stat.size / BYTES_TO_MB,
                    "count": stat.count,
                    "average_bytes": stat.size / stat.count if stat.count > 0 else 0,
                })
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error getting tracemalloc allocations: {e}", exc_info=True)
            return []
    
    def compare_to_baseline(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Compare current memory to baseline snapshot.
        THIS IS THE MOST IMPORTANT METHOD - shows memory growth over time.
        """
        if not self._monitoring_enabled or not tracemalloc.is_tracing():
            return []
        
        if not self._baseline_snapshot:
            logger.warning("No baseline snapshot available")
            return []
        
        try:
            current_snapshot = tracemalloc.take_snapshot()
            top_stats = current_snapshot.compare_to(self._baseline_snapshot, 'lineno')
            
            differences = []
            for stat in top_stats[:limit]:
                differences.append({
                    "filename": stat.traceback.format()[0] if stat.traceback else "unknown",
                    "size_diff_mb": stat.size_diff / BYTES_TO_MB,
                    "count_diff": stat.count_diff,
                    "new_size_mb": stat.size / BYTES_TO_MB,
                    "new_count": stat.count,
                })
            
            return differences
            
        except Exception as e:
            logger.error(f"Error comparing to baseline: {e}", exc_info=True)
            return []
    
    def take_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Take a comprehensive memory snapshot for later analysis.
        Called periodically by scheduler.
        """
        if not self._monitoring_enabled or not tracemalloc.is_tracing():
            return None
        
        try:
            with self._snapshot_lock:
                snapshot = tracemalloc.take_snapshot()
                timestamp = datetime.utcnow()
                
                # Store snapshot
                self.snapshots.append((timestamp, snapshot))
                
                # Keep only recent snapshots
                if len(self.snapshots) > self.max_snapshots:
                    self.snapshots.pop(0)
                
                # Get basic stats
                stats = self.get_memory_stats()
                stats["snapshot_time"] = timestamp.isoformat()
                stats["total_snapshots"] = len(self.snapshots)
                
                logger.info(
                    f"Memory snapshot taken: "
                    f"RSS={stats['process']['rss_mb']:.1f} MB, "
                    f"Objects={stats['gc']['total_objects']:,}"
                )
                
                return stats
                
        except Exception as e:
            logger.error(f"Error taking snapshot: {e}", exc_info=True)
            return None
    
    def compare_recent_snapshots(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Compare the two most recent snapshots to see what grew.
        Great for identifying recent memory increases.
        """
        if not self._monitoring_enabled or len(self.snapshots) < 2:
            return None
        
        try:
            with self._snapshot_lock:
                # Get two most recent snapshots
                older_time, older_snap = self.snapshots[-2]
                newer_time, newer_snap = self.snapshots[-1]
                
                # Compare
                top_stats = newer_snap.compare_to(older_snap, 'lineno')
                
                differences = []
                for stat in top_stats[:limit]:
                    differences.append({
                        "filename": stat.traceback.format()[0] if stat.traceback else "unknown",
                        "size_diff_mb": stat.size_diff / BYTES_TO_MB,
                        "count_diff": stat.count_diff,
                        "time_diff_seconds": (newer_time - older_time).total_seconds(),
                    })
                
                return differences
                
        except Exception as e:
            logger.error(f"Error comparing recent snapshots: {e}", exc_info=True)
            return None
    
    def malloc_trim(self) -> bool:
        """
        Return freed memory to the OS.
        CRITICAL: Python's GC doesn't do this automatically.
        """
        if not self._monitoring_enabled or not self._malloc_trim_enabled or not self.libc:
            return False
        
        try:
            # Get memory before
            mem_before = self.process.memory_info().rss / BYTES_TO_MB
            
            # Call malloc_trim
            self.libc.malloc_trim(0)
            
            # Get memory after
            time.sleep(0.1)  # Brief delay to let OS update
            mem_after = self.process.memory_info().rss / BYTES_TO_MB
            
            freed = mem_before - mem_after
            
            if freed > 0:
                logger.info(f"malloc_trim freed {freed:.1f} MB")
            else:
                logger.debug("malloc_trim called (no significant memory freed)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in malloc_trim: {e}")
            return False
    
    def full_diagnostic_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive diagnostic report.
        USE THIS for the dashboard main view.
        """
        if not self._monitoring_enabled:
            return {"monitoring_enabled": False}
        
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "monitoring_enabled": True,
                "basic_stats": self.get_memory_stats(),
                "top_allocations_by_type": self.get_top_allocations_by_type(limit=20),
                "top_allocations_by_line": self.get_tracemalloc_top_allocations(limit=10),
                "baseline_comparison": self.compare_to_baseline(limit=10),
                "recent_growth": self.compare_recent_snapshots(limit=10),
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating diagnostic report: {e}", exc_info=True)
            return {}
    
    def save_diagnostic_report(self, filepath: str) -> bool:
        """Save diagnostic report to JSON file."""
        if not self._monitoring_enabled:
            return False
        
        try:
            report = self.full_diagnostic_report()
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Diagnostic report saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving diagnostic report: {e}")
            return False


# Global instance
memory_diagnostics = None


def get_memory_diagnostics() -> Optional[MemoryDiagnostics]:
    """Get the global memory diagnostics instance."""
    global memory_diagnostics
    
    if memory_diagnostics is None:
        memory_diagnostics = MemoryDiagnostics()
    
    return memory_diagnostics


def start_malloc_trimmer(period_sec: int = 300):
    """
    Start background thread that periodically calls malloc_trim.
    This returns memory to the OS that Python's GC doesn't release.
    """
    if not ENABLE_MEMORY_MONITORING:
        logger.info("malloc_trim thread not started (memory monitoring disabled)")
        return
    
    diagnostics = get_memory_diagnostics()
    
    if not diagnostics:
        return
    
    def _trim_loop():
        while True:
            try:
                # Force GC first
                gc.collect()
                time.sleep(1)
                
                # Then trim
                diagnostics.malloc_trim()
                
            except Exception as e:
                logger.error(f"Error in malloc trim loop: {e}")
            
            time.sleep(period_sec)
    
    thread = threading.Thread(target=_trim_loop, daemon=True)
    thread.start()
    logger.info(f"malloc_trim background thread started (period: {period_sec}s)")
