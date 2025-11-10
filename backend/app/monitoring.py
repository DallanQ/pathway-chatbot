"""
Comprehensive monitoring system for the Pathway Chatbot backend.
Tracks memory usage, performance metrics, request patterns, and system health.
Generates hourly Parquet reports and uploads to S3.

ENHANCEMENTS:
- Hourly uploads (reduced from daily for better data safety)
- 90% memory emergency trigger (prevents OOM crashes)
- Startup recovery (uploads unsaved reports from previous session)
- All thresholds configurable via environment variables
"""

import os
import logging
import time
import gc
import psutil
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict, deque
import asyncio
from threading import Lock
import json

logger = logging.getLogger("uvicorn")

# Configuration constants with environment variable overrides
BYTES_TO_MB = 1024 * 1024  # Conversion factor


class MetricsCollector:
    """Collects and stores metrics in memory with thread-safe operations."""
    
    # Configurable thresholds with defaults
    MAX_METRICS_BUFFER = int(os.getenv("MAX_METRICS_BUFFER", "500"))
    EMERGENCY_THRESHOLD_PERCENT = float(os.getenv("EMERGENCY_MEMORY_THRESHOLD_PERCENT", "90"))
    EMERGENCY_ALERT_COOLDOWN_SECONDS = int(os.getenv("EMERGENCY_ALERT_COOLDOWN_SECONDS", "300"))  # 5 minutes
    
    def __init__(self):
        # Use deque with maxlen for automatic eviction of old metrics
        # This prevents unbounded memory growth
        self._metrics: deque = deque(maxlen=self.MAX_METRICS_BUFFER)
        self._lock = Lock()
        self._process = psutil.Process()
        self._start_time = time.time()
        self._flush_callback = None
        self._emergency_callback = None
        
        # Calculate emergency threshold dynamically based on system memory
        # This allows the threshold to adapt if memory limits change
        system_memory = psutil.virtual_memory()
        system_memory_mb = system_memory.total / BYTES_TO_MB
        self._emergency_memory_threshold_mb = (self.EMERGENCY_THRESHOLD_PERCENT / 100) * system_memory_mb
        
        logger.info(
            f"Monitoring configuration:\n"
            f"  Max buffer size: {self.MAX_METRICS_BUFFER:,} metrics\n"
            f"  Emergency threshold: {self._emergency_memory_threshold_mb:.2f} MB "
            f"({self.EMERGENCY_THRESHOLD_PERCENT}% of {system_memory_mb:.2f} MB)\n"
            f"  Alert cooldown: {self.EMERGENCY_ALERT_COOLDOWN_SECONDS} seconds"
        )
        
        # Aggregated counters
        self._request_count = 0
        self._error_count = 0
        self._security_blocks = 0
        self._total_response_time = 0.0
        
        # Track last emergency alert to avoid spam
        self._last_emergency_alert = 0
        
        # Initialize CPU monitoring with background sampling
        # This primes the CPU cache so subsequent interval=None calls work
        self._process.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None)
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # Memory metrics
            mem_info = self._process.memory_info()
            mem_percent = self._process.memory_percent()
            
            # CPU metrics - use non-blocking call only
            cpu_percent = self._process.cpu_percent(interval=None)
            system_cpu_percent = psutil.cpu_percent(interval=None)
            
            # System-wide metrics
            system_memory = psutil.virtual_memory()
            
            # Thread and connection info
            num_threads = self._process.num_threads()
            try:
                num_connections = len(self._process.connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                num_connections = 0
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "memory_rss_mb": mem_info.rss / BYTES_TO_MB,
                "memory_vms_mb": mem_info.vms / BYTES_TO_MB,
                "memory_percent": mem_percent,
                "cpu_percent": cpu_percent,
                "system_cpu_percent": system_cpu_percent,
                "num_threads": num_threads,
                "num_connections": num_connections,
                "system_memory_percent": system_memory.percent,
                "system_memory_available_mb": system_memory.available / BYTES_TO_MB,
                "uptime_seconds": time.time() - self._start_time,
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def check_memory_threshold(self, memory_rss_mb: float) -> bool:
        """
        Check if memory has exceeded emergency threshold.
        Returns True if emergency action needed.
        """
        if memory_rss_mb >= self._emergency_memory_threshold_mb:
            # Avoid spamming alerts - only trigger once per cooldown period
            current_time = time.time()
            if current_time - self._last_emergency_alert > self.EMERGENCY_ALERT_COOLDOWN_SECONDS:
                self._last_emergency_alert = current_time
                return True
        return False
    
    def record_request_start(self, request_id: str, endpoint: str, method: str) -> float:
        """Record the start of a request and return start time."""
        return time.time()
    
    def record_request_end(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        start_time: float,
        status_code: int,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record the completion of a request with all metrics."""
        try:
            end_time = time.time()
            duration = end_time - start_time
            
            # Collect system metrics at request end
            system_metrics = self.collect_system_metrics()
            
            metric = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_seconds": duration,
                "error": error,
                **system_metrics,
            }
            
            # Add metadata if provided (security info, user language, etc.)
            if metadata:
                metric.update(metadata)
            
            with self._lock:
                self._metrics.append(metric)
                self._request_count += 1
                self._total_response_time += duration
                
                # Track errors (4xx and 5xx status codes)
                if status_code >= 400:
                    self._error_count += 1
                
                if metadata and metadata.get("security_blocked"):
                    self._security_blocks += 1
                
                # Check for emergency memory threshold
                memory_rss_mb = system_metrics.get("memory_rss_mb", 0)
                if self.check_memory_threshold(memory_rss_mb):
                    system_memory = psutil.virtual_memory()
                    system_memory_mb = system_memory.total / BYTES_TO_MB
                    logger.critical(
                        f"🚨 EMERGENCY: Memory usage at {memory_rss_mb:.2f} MB "
                        f"({memory_rss_mb/system_memory_mb*100:.1f}% of {system_memory_mb:.0f} MB limit). "
                        f"Triggering emergency upload!"
                    )
                    if self._emergency_callback:
                        # Schedule emergency upload without blocking
                        asyncio.create_task(self._emergency_callback(memory_rss_mb))
                
                # Auto-flush if buffer limit reached
                if len(self._metrics) >= self.MAX_METRICS_BUFFER:
                    logger.warning(
                        f"Metrics buffer reached {self.MAX_METRICS_BUFFER:,} items. "
                        f"Auto-flushing to prevent OOM."
                    )
                    if self._flush_callback:
                        # Schedule async flush without blocking
                        asyncio.create_task(self._flush_callback())
                    
        except Exception as e:
            logger.error(f"Error recording request end: {e}")
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get all collected metrics (thread-safe)."""
        with self._lock:
            return list(self._metrics)
    
    def clear_metrics(self):
        """Clear all collected metrics (thread-safe)."""
        with self._lock:
            self._metrics.clear()
    
    def set_flush_callback(self, callback):
        """Set callback function to call when buffer limit is reached."""
        self._flush_callback = callback
    
    def set_emergency_callback(self, callback):
        """Set callback function to call when memory threshold is exceeded."""
        self._emergency_callback = callback
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the current period."""
        with self._lock:
            if self._request_count == 0:
                avg_response_time = 0
            else:
                avg_response_time = self._total_response_time / self._request_count
            
            system_metrics = self.collect_system_metrics()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_requests": self._request_count,
                "total_errors": self._error_count,
                "security_blocks": self._security_blocks,
                "error_rate": self._error_count / max(self._request_count, 1),
                "avg_response_time_seconds": avg_response_time,
                "uptime_hours": (time.time() - self._start_time) / 3600,
                **system_metrics,
            }


class MonitoringService:
    """Service for managing monitoring, hourly reports, and S3 uploads."""
    
    # Configurable retention period
    CLEANUP_RETENTION_DAYS = int(os.getenv("CLEANUP_RETENTION_DAYS", "7"))
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.reports_dir = Path("monitoring_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Set auto-flush callback to prevent OOM
        self.metrics_collector.set_flush_callback(self._auto_flush_metrics)
        
        # Set emergency callback for memory threshold
        self.metrics_collector.set_emergency_callback(self._emergency_upload)
        
        # AWS S3 configuration
        self.s3_bucket = os.getenv("MONITORING_S3_BUCKET")
        self.s3_prefix = os.getenv("MONITORING_S3_PREFIX", "metrics")
        self.enable_s3_upload = os.getenv("ENABLE_MONITORING_S3_UPLOAD", "false").lower() == "true"
        
        # Initialize S3 client if enabled
        if self.enable_s3_upload and self.s3_bucket:
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                logger.info(f"S3 monitoring enabled: bucket={self.s3_bucket}, prefix={self.s3_prefix}")
                
                # Run startup recovery to upload any unsaved reports
                asyncio.create_task(self.startup_recovery())
                
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.enable_s3_upload = False
        else:
            self.s3_client = None
            logger.info("S3 monitoring disabled")
    
    async def startup_recovery(self):
        """
        On startup, check for unsaved reports from previous session and upload them.
        Also creates a BOOT report to indicate restart/crash recovery.
        This prevents data loss from unexpected crashes.
        """
        try:
            logger.info("Running startup recovery check...")
            
            # Find all local parquet and json files
            parquet_files = list(self.reports_dir.glob("*.parquet"))
            json_files = list(self.reports_dir.glob("*.json"))
            
            # Determine if this was a crash or graceful restart
            had_unsaved_files = len(parquet_files) > 0 or len(json_files) > 0
            restart_type = "crash_recovery" if had_unsaved_files else "clean_start"
            
            # Create BOOT report to mark restart event
            system_metrics = self.metrics_collector.collect_system_metrics()
            boot_data = {
                "event_type": "boot",
                "restart_type": restart_type,
                "timestamp": datetime.utcnow().isoformat(),
                "unsaved_files_found": len(parquet_files) + len(json_files),
                "parquet_files": len(parquet_files),
                "json_files": len(json_files),
                "system_memory_mb": system_metrics.get("memory_rss_mb", 0),
                "system_memory_percent": system_metrics.get("memory_percent", 0),
                "message": f"Backend restarted - {restart_type.replace('_', ' ').title()}",
                "severity": "warning" if had_unsaved_files else "info",
            }
            
            # Save BOOT report
            boot_filename = f"BOOT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            boot_filepath = self.reports_dir / boot_filename
            
            with open(boot_filepath, 'w') as f:
                json.dump(boot_data, f, indent=2)
            
            logger.info(f"Boot report created: {boot_filename} ({restart_type})")
            
            # Upload BOOT report immediately
            if self.enable_s3_upload:
                await self.upload_to_s3(str(boot_filepath))
            
            if not had_unsaved_files:
                logger.info("No unsaved reports found - clean start")
                return
            
            logger.info(f"Found {len(parquet_files)} parquet and {len(json_files)} json files from previous session")
            
            # Upload all found files
            uploaded_count = 0
            for filepath in parquet_files + json_files:
                success = await self.upload_to_s3(str(filepath))
                if success:
                    uploaded_count += 1
                    # Delete after successful upload
                    filepath.unlink()
                    logger.info(f"Recovered and uploaded: {filepath.name}")
            
            logger.info(f"Startup recovery complete: {uploaded_count} files uploaded + 1 BOOT report")
            
        except Exception as e:
            logger.error(f"Error in startup recovery: {e}", exc_info=True)

    async def _emergency_upload(self, memory_mb: float):
        """
        Emergency upload triggered when memory exceeds threshold.
        Creates a special ALERT file and uploads immediately.
        """
        try:
            logger.critical(f"🚨 EMERGENCY UPLOAD: Memory at {memory_mb:.2f} MB")
            
            # Generate emergency report
            filepath = self.generate_daily_report(prefix="EMERGENCY")
            
            if filepath:
                # Upload to S3 immediately
                if self.enable_s3_upload:
                    await self.upload_to_s3(filepath)
                
                # Create emergency alert JSON
                system_memory = psutil.virtual_memory()
                system_memory_mb = system_memory.total / BYTES_TO_MB
                
                alert_data = {
                    "alert_type": "high_memory",
                    "timestamp": datetime.utcnow().isoformat(),
                    "memory_mb": memory_mb,
                    "memory_percent": (memory_mb / system_memory_mb) * 100,
                    "threshold_mb": self.metrics_collector._emergency_memory_threshold_mb,
                    "threshold_percent": self.metrics_collector.EMERGENCY_THRESHOLD_PERCENT,
                    "system_memory_mb": system_memory_mb,
                    "severity": "critical",
                    "message": f"Backend memory usage reached {memory_mb:.2f} MB ({memory_mb/system_memory_mb*100:.1f}% of {system_memory_mb:.0f} MB limit)",
                    "action_required": "Investigate memory leak and restart if needed",
                    "metrics_count": len(self.metrics_collector._metrics),
                }
                
                # Save alert JSON
                alert_filename = f"ALERT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                alert_filepath = self.reports_dir / alert_filename
                
                with open(alert_filepath, 'w') as f:
                    json.dump(alert_data, f, indent=2)
                
                # Upload alert
                if self.enable_s3_upload:
                    await self.upload_to_s3(str(alert_filepath))
                
                logger.critical(f"Emergency alert saved: {alert_filename}")
                
                # Clear metrics after emergency upload
                self.metrics_collector.clear_metrics()
                logger.info("Cleared metrics after emergency upload")
            
        except Exception as e:
            logger.error(f"Error in emergency upload: {e}", exc_info=True)
    
    def generate_daily_report(self, prefix: str = "metrics") -> Optional[str]:
        """
        Generate a Parquet report from collected metrics.
        
        Args:
            prefix: Filename prefix (default: "metrics", can be "EMERGENCY" for alerts)
        """
        try:
            metrics = self.metrics_collector.get_metrics()
            
            if not metrics:
                logger.warning("No metrics to report")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(metrics)
            
            # Add date column for partitioning
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            
            # Generate filename with timestamp
            now = datetime.utcnow()
            filename = f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
            filepath = self.reports_dir / filename
            
            # Save as Parquet (compressed)
            df.to_parquet(
                filepath,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            
            logger.info(f"Generated monitoring report: {filepath} ({len(df)} records)")
            
            # Also save a summary JSON
            summary = self.metrics_collector.get_summary_stats()
            summary_filename = f"summary_{now.strftime('%Y%m%d_%H%M%S')}.json"
            summary_filepath = self.reports_dir / summary_filename
            
            with open(summary_filepath, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Generated summary report: {summary_filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}", exc_info=True)
            return None
    
    async def _auto_flush_metrics(self):
        """Internal method called when metrics buffer is full."""
        try:
            logger.warning("Auto-flushing metrics due to buffer limit")
            
            # Generate an intermediate report
            filepath = self.generate_daily_report(prefix="auto_flush")
            
            if filepath:
                # Upload to S3 if enabled
                if self.enable_s3_upload:
                    await self.upload_to_s3(filepath)
                
                # Also upload summary
                summary_filepath = filepath.replace('.parquet', '.json').replace('auto_flush_', 'summary_')
                if Path(summary_filepath).exists():
                    await self.upload_to_s3(summary_filepath)
                
                # Clear metrics after flush
                self.metrics_collector.clear_metrics()
                logger.info("Auto-flush completed successfully")
            
        except Exception as e:
            logger.error(f"Error in auto-flush: {e}", exc_info=True)
    
    async def upload_to_s3(self, filepath: str) -> bool:
        """Upload report to S3 asynchronously using asyncio.to_thread."""
        if not self.enable_s3_upload or not self.s3_client:
            return False
        
        try:
            filename = Path(filepath).name
            s3_key = f"{self.s3_prefix}/{filename}"
            
            # Upload to S3 in a thread pool to avoid blocking event loop
            await asyncio.to_thread(
                self.s3_client.upload_file,
                filepath,
                self.s3_bucket,
                s3_key
            )
            
            logger.info(f"Uploaded {filename} to s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}", exc_info=True)
            return False
    
    async def hourly_report_task(self):
        """
        Task that runs hourly to generate and upload reports.
        Changed from daily to hourly for better data safety (max 1 hour loss vs 24 hours).
        Memory overhead: ~0.003 MB per hour (negligible).
        """
        try:
            logger.info("Starting hourly report task...")
            
            # Generate the report
            filepath = self.generate_daily_report()
            
            if filepath:
                # Upload to S3 if enabled
                if self.enable_s3_upload:
                    await self.upload_to_s3(filepath)
                
                # Also upload the summary JSON
                summary_filepath = filepath.replace('.parquet', '.json').replace('metrics_', 'summary_')
                if Path(summary_filepath).exists():
                    await self.upload_to_s3(summary_filepath)
                
                # Clear metrics after successful report
                self.metrics_collector.clear_metrics()
                logger.info("Cleared metrics after hourly report")
                
                # Clean up old local files
                self.cleanup_old_reports()
            
        except Exception as e:
            logger.error(f"Error in hourly report task: {e}", exc_info=True)
    
    # Keep daily_report_task as alias for backward compatibility
    async def daily_report_task(self):
        """Alias for hourly_report_task (backward compatibility)."""
        await self.hourly_report_task()
    

    async def minute_report_task(self):
        """
        Task that runs every minute to generate and upload reports.
        Smart batching: Creates small minute-level files that are later merged.
        
        Benefits:
        - Near real-time monitoring (1-minute granularity)
        - Maximum 1 minute of data loss on crash (vs 1 hour before)
        - Emergency upload already handles 90% memory threshold
        - Auto-flush already handles buffer overflow (500 records)
        """
        try:
            logger.info("Starting minute-level report task...")
            
            # Only generate report if we have metrics to report
            metrics_count = len(self.metrics_collector._metrics)
            if metrics_count == 0:
                logger.debug("No metrics to report this minute - skipping")
                return
            
            # Generate the report with minute prefix
            filepath = self.generate_daily_report(prefix="minute")
            
            if filepath:
                # Upload to S3 if enabled
                if self.enable_s3_upload:
                    await self.upload_to_s3(filepath)
                
                # Also upload the summary JSON
                summary_filepath = filepath.replace('.parquet', '.json').replace('minute_', 'summary_')
                if Path(summary_filepath).exists():
                    await self.upload_to_s3(summary_filepath)
                
                # Clear metrics after successful report
                self.metrics_collector.clear_metrics()
                logger.info(f"Minute report completed ({metrics_count} metrics uploaded)")
                
                # Clean up old local files periodically (every 10th minute)
                from datetime import datetime
                if datetime.utcnow().minute % 10 == 0:
                    self.cleanup_old_reports()
            
        except Exception as e:
            logger.error(f"Error in minute report task: {e}", exc_info=True)

    def cleanup_old_reports(self):
        """Delete local report files older than configured retention period."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=self.CLEANUP_RETENTION_DAYS)
            
            deleted_count = 0
            for filepath in self.reports_dir.glob("*.parquet"):
                if filepath.stat().st_mtime < cutoff.timestamp():
                    filepath.unlink()
                    deleted_count += 1
            
            for filepath in self.reports_dir.glob("*.json"):
                if filepath.stat().st_mtime < cutoff.timestamp():
                    filepath.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old reports (retention: {self.CLEANUP_RETENTION_DAYS} days)")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
    
    def log_memory_usage(self):
        """Log current memory usage and system health (useful for debugging crashes)."""
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            summary = self.metrics_collector.get_summary_stats()

            logger.info(
                f"System Health Check:\n"
                f"  Memory: {metrics['memory_rss_mb']:.2f} MB "
                f"({metrics['memory_percent']:.2f}% of system)\n"
                f"  CPU: Process={metrics['cpu_percent']:.2f}%, "
                f"System={metrics['system_cpu_percent']:.2f}%\n"
                f"  Threads: {metrics['num_threads']}, "
                f"Connections: {metrics['num_connections']}\n"
                f"  Requests: {summary['total_requests']} total, "
                f"{summary['total_errors']} errors ({summary['error_rate']*100:.1f}%)\n"
                f"  Avg Response Time: {summary['avg_response_time_seconds']:.3f}s\n"
                f"  Uptime: {summary['uptime_hours']:.2f} hours\n"
                f"  Metrics Buffer: {len(self.metrics_collector._metrics):,}/{self.metrics_collector.MAX_METRICS_BUFFER:,}"
            )
        except Exception as e:
            logger.error(f"Error logging memory usage: {e}")

    def periodic_gc(self):
        """Periodic garbage collection to free memory (runs every 10 minutes)."""
        try:
            # Collect memory metrics before GC
            metrics_before = self.metrics_collector.collect_system_metrics()
            memory_before = metrics_before.get('memory_rss_mb', 0)

            # Force garbage collection
            collected = gc.collect()

            # Collect memory metrics after GC
            metrics_after = self.metrics_collector.collect_system_metrics()
            memory_after = metrics_after.get('memory_rss_mb', 0)

            # Calculate memory freed
            memory_freed = memory_before - memory_after

            logger.info(
                f"Periodic GC completed: "
                f"collected {collected} objects, "
                f"memory: {memory_before:.2f} MB -> {memory_after:.2f} MB "
                f"(freed {memory_freed:.2f} MB)"
            )

        except Exception as e:
            logger.error(f"Error in periodic GC: {e}")


# Global monitoring service instance
monitoring_service = MonitoringService()


def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    return monitoring_service
