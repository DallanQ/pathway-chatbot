"""
Comprehensive monitoring system for the Pathway Chatbot backend.
Tracks memory usage, performance metrics, request patterns, and system health.
Generates daily Parquet reports and uploads to S3.
"""

import os
import logging
import time
import psutil
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict
import asyncio
from threading import Lock
import json

logger = logging.getLogger("uvicorn")


class MetricsCollector:
    """Collects and stores metrics in memory with thread-safe operations."""
    
    def __init__(self):
        self._metrics: List[Dict[str, Any]] = []
        self._lock = Lock()
        self._process = psutil.Process()
        self._start_time = time.time()
        
        # Aggregated counters
        self._request_count = 0
        self._error_count = 0
        self._security_blocks = 0
        self._total_response_time = 0.0
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # Memory metrics
            mem_info = self._process.memory_info()
            mem_percent = self._process.memory_percent()
            
            # CPU metrics - get non-blocking value first
            cpu_percent = self._process.cpu_percent(interval=None)
            # If it's the first call or 0, try with a small interval
            if cpu_percent == 0.0:
                cpu_percent = self._process.cpu_percent(interval=0.05)
            
            # System-wide CPU (more reliable)
            system_cpu_percent = psutil.cpu_percent(interval=0.05)
            
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
                "memory_rss_mb": mem_info.rss / 1024 / 1024,
                "memory_vms_mb": mem_info.vms / 1024 / 1024,
                "memory_percent": mem_percent,
                "cpu_percent": cpu_percent,
                "system_cpu_percent": system_cpu_percent,
                "num_threads": num_threads,
                "num_connections": num_connections,
                "system_memory_percent": system_memory.percent,
                "system_memory_available_mb": system_memory.available / 1024 / 1024,
                "uptime_seconds": time.time() - self._start_time,
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
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
                
                if status_code >= 400:
                    self._error_count += 1
                
                if metadata and metadata.get("security_blocked"):
                    self._security_blocks += 1
                    
        except Exception as e:
            logger.error(f"Error recording request end: {e}")
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get all collected metrics (thread-safe)."""
        with self._lock:
            return self._metrics.copy()
    
    def clear_metrics(self):
        """Clear all collected metrics (thread-safe)."""
        with self._lock:
            self._metrics.clear()
    
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
    """Service for managing monitoring, daily reports, and S3 uploads."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.reports_dir = Path("monitoring_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
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
                logger.info(f"S3 monitoring enabled: bucket={self.s3_bucket}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.enable_s3_upload = False
        else:
            self.s3_client = None
            logger.info("S3 monitoring disabled")
    
    def generate_daily_report(self) -> Optional[str]:
        """Generate a Parquet report from collected metrics."""
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
            filename = f"metrics_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
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
    
    async def upload_to_s3(self, filepath: str) -> bool:
        """Upload report to S3 asynchronously."""
        if not self.enable_s3_upload or not self.s3_client:
            return False
        
        try:
            filename = Path(filepath).name
            s3_key = f"{self.s3_prefix}/{filename}"
            
            # Upload to S3
            self.s3_client.upload_file(
                filepath,
                self.s3_bucket,
                s3_key
            )
            
            logger.info(f"Uploaded {filename} to s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}", exc_info=True)
            return False
    
    async def daily_report_task(self):
        """Task that runs daily to generate and upload reports."""
        try:
            logger.info("Starting daily report task...")
            
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
                logger.info("Cleared metrics after daily report")
                
                # Clean up old local files (keep last 7 days)
                self.cleanup_old_reports(days=7)
            
        except Exception as e:
            logger.error(f"Error in daily report task: {e}", exc_info=True)
    
    def cleanup_old_reports(self, days: int = 7):
        """Delete local report files older than specified days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            for filepath in self.reports_dir.glob("*.parquet"):
                if filepath.stat().st_mtime < cutoff.timestamp():
                    filepath.unlink()
                    logger.info(f"Deleted old report: {filepath}")
            
            for filepath in self.reports_dir.glob("*.json"):
                if filepath.stat().st_mtime < cutoff.timestamp():
                    filepath.unlink()
                    logger.info(f"Deleted old summary: {filepath}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
    
    def log_memory_usage(self):
        """Log current memory usage (useful for debugging)."""
        try:
            metrics = self.metrics_collector.collect_system_metrics()
            logger.info(
                f"Memory: {metrics['memory_rss_mb']:.2f} MB "
                f"({metrics['memory_percent']:.2f}%), "
                f"CPU: {metrics['cpu_percent']:.2f}%, "
                f"Threads: {metrics['num_threads']}"
            )
        except Exception as e:
            logger.error(f"Error logging memory usage: {e}")


# Global monitoring service instance
monitoring_service = MonitoringService()


def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    return monitoring_service
