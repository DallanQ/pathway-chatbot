"""
Scheduler for running periodic monitoring tasks.
Enhanced with configurable intervals and robust error handling.
"""

import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from datetime import datetime
from typing import Optional

from app.monitoring import get_monitoring_service

logger = logging.getLogger("uvicorn")


def safe_int_env(key: str, default: int) -> int:
    """Safely parse integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        logger.warning(f"Invalid {key} env var, using default: {default}")
        return default


class MonitoringScheduler:
    """Manages scheduled monitoring tasks with robust error handling."""
    
    # Configurable intervals (in minutes)
    REPORT_INTERVAL_MINUTES = safe_int_env("MONITORING_REPORT_INTERVAL_MINUTES", 5)
    GC_INTERVAL_MINUTES = safe_int_env("MONITORING_GC_INTERVAL_MINUTES", 10)
    MEMORY_LOG_INTERVAL_MINUTES = safe_int_env("MONITORING_MEMORY_LOG_INTERVAL_MINUTES", 60)
    
    def __init__(self):
        # Configure scheduler with timezone and job defaults
        self.scheduler = AsyncIOScheduler(
            timezone='UTC',  # Explicit timezone to avoid container issues
            job_defaults={
                'coalesce': True,  # Combine missed runs into one
                'max_instances': 1,  # Prevent concurrent runs of same job
                'misfire_grace_time': 300  # 5 minutes grace for misfires
            }
        )
        self.monitoring_service = get_monitoring_service()
        self.is_running = False
        self._job_execution_count = {}
        
        # Add event listeners for job monitoring
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._job_error_listener,
            EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(
            self._job_missed_listener,
            EVENT_JOB_MISSED
        )
    
    def _job_executed_listener(self, event):
        """Log successful job executions."""
        job_id = event.job_id
        self._job_execution_count[job_id] = self._job_execution_count.get(job_id, 0) + 1
        logger.debug(
            f"Job '{job_id}' executed successfully "
            f"(run #{self._job_execution_count[job_id]})"
        )
    
    def _job_error_listener(self, event):
        """Log job errors."""
        logger.error(
            f"Job '{event.job_id}' raised an exception: {event.exception}",
            exc_info=True
        )
    
    def _job_missed_listener(self, event):
        """Log missed job executions."""
        logger.warning(
            f"Job '{event.job_id}' missed its scheduled run time "
            f"(scheduled: {event.scheduled_run_time})"
        )
    
    def start(self):
        """Start the scheduler with all monitoring tasks."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            # Schedule periodic report uploads for near real-time monitoring
            # This ensures we never lose more than N minutes of data on crash
            report_job = self.scheduler.add_job(
                self._safe_periodic_report,
                IntervalTrigger(minutes=self.REPORT_INTERVAL_MINUTES),
                id='periodic_report',
                name=f'Generate and upload monitoring report every {self.REPORT_INTERVAL_MINUTES} minutes',
                replace_existing=True
            )
            if report_job:
                logger.info(
                    f"✓ Scheduled periodic report task (every {self.REPORT_INTERVAL_MINUTES} minutes)"
                )
            else:
                logger.error("Failed to schedule periodic report task")
            
            # Schedule memory logging for production monitoring
            memory_log_job = self.scheduler.add_job(
                self._safe_memory_log,
                IntervalTrigger(minutes=self.MEMORY_LOG_INTERVAL_MINUTES),
                id='memory_log',
                name=f'Log memory usage every {self.MEMORY_LOG_INTERVAL_MINUTES} minutes',
                replace_existing=True
            )
            if memory_log_job:
                logger.info(
                    f"✓ Scheduled memory logging (every {self.MEMORY_LOG_INTERVAL_MINUTES} minutes)"
                )
            else:
                logger.error("Failed to schedule memory logging")

            # Schedule periodic garbage collection
            gc_job = self.scheduler.add_job(
                self._safe_gc,
                IntervalTrigger(minutes=self.GC_INTERVAL_MINUTES),
                id='periodic_gc',
                name=f'Periodic garbage collection every {self.GC_INTERVAL_MINUTES} minutes',
                replace_existing=True
            )
            if gc_job:
                logger.info(
                    f"✓ Scheduled periodic garbage collection (every {self.GC_INTERVAL_MINUTES} minutes)"
                )
            else:
                logger.error("Failed to schedule garbage collection")

            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            # Verify scheduler is running
            if self.scheduler.running:
                logger.info("✓ Monitoring scheduler started successfully")
                self._log_scheduled_jobs()
            else:
                logger.error("Scheduler failed to start properly")
                self.is_running = False
            
        except Exception as e:
            logger.error(f"Error starting monitoring scheduler: {e}", exc_info=True)
            self.is_running = False
    
    def _log_scheduled_jobs(self):
        """Log all scheduled jobs for verification."""
        jobs = self.scheduler.get_jobs()
        if jobs:
            logger.info(f"Active scheduled jobs ({len(jobs)}):")
            for job in jobs:
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S UTC') if job.next_run_time else 'N/A'
                logger.info(f"  - {job.id}: {job.name} (next run: {next_run})")
        else:
            logger.warning("No jobs scheduled!")
    
    async def _safe_periodic_report(self):
        """Wrapper for periodic report with error handling."""
        try:
            await self.monitoring_service.periodic_report_task()
        except Exception as e:
            logger.error(f"Error in periodic report task: {e}", exc_info=True)
    
    async def _safe_memory_log(self):
        """Wrapper for memory logging with error handling."""
        try:
            self.monitoring_service.log_memory_usage()
        except Exception as e:
            logger.error(f"Error in memory logging: {e}", exc_info=True)
    
    async def _safe_gc(self):
        """Wrapper for garbage collection with error handling."""
        try:
            self.monitoring_service.periodic_gc()
        except Exception as e:
            logger.error(f"Error in garbage collection: {e}", exc_info=True)
    
    async def shutdown(self, timeout: int = 30):
        """
        Gracefully shutdown the scheduler.
        
        Args:
            timeout: Maximum seconds to wait for running jobs to complete
        """
        if not self.is_running:
            logger.info("Scheduler not running, nothing to shutdown")
            return
        
        try:
            logger.info("Initiating scheduler shutdown...")
            
            # Check if there are running jobs
            running_jobs = [job for job in self.scheduler.get_jobs() if job.next_run_time]
            if running_jobs:
                logger.info(f"Waiting for {len(running_jobs)} scheduled jobs to complete...")
            
            # Generate final report before shutdown
            logger.info("Generating final report before shutdown...")
            try:
                await self.monitoring_service.periodic_report_task()
                logger.info("Final report generated successfully")
            except Exception as e:
                logger.error(f"Error generating final report: {e}", exc_info=True)
            
            # Shutdown scheduler with timeout
            logger.info(f"Shutting down scheduler (timeout: {timeout}s)...")
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            
            # Log execution statistics
            if self._job_execution_count:
                logger.info("Job execution statistics:")
                for job_id, count in self._job_execution_count.items():
                    logger.info(f"  - {job_id}: {count} executions")
            
            logger.info("✓ Monitoring scheduler stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}", exc_info=True)
            # Force shutdown if graceful shutdown fails
            try:
                self.scheduler.shutdown(wait=False)
                self.is_running = False
                logger.warning("Forced scheduler shutdown due to error")
            except Exception as force_error:
                logger.error(f"Error in forced shutdown: {force_error}")
    
    def get_status(self) -> dict:
        """Get scheduler status and job information."""
        if not self.is_running:
            return {
                "status": "stopped",
                "jobs": [],
                "execution_counts": {}
            }
        
        jobs = self.scheduler.get_jobs()
        job_info = []
        
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "executions": self._job_execution_count.get(job.id, 0)
            })
        
        return {
            "status": "running",
            "running": self.scheduler.running,
            "jobs": job_info,
            "execution_counts": self._job_execution_count,
            "total_executions": sum(self._job_execution_count.values())
        }
    
    def pause(self):
        """Pause all scheduled jobs."""
        if self.is_running and self.scheduler.running:
            self.scheduler.pause()
            logger.info("Scheduler paused")
    
    def resume(self):
        """Resume all scheduled jobs."""
        if self.is_running and not self.scheduler.running:
            self.scheduler.resume()
            logger.info("Scheduler resumed")


# Global scheduler instance
monitoring_scheduler = MonitoringScheduler()


def get_monitoring_scheduler() -> MonitoringScheduler:
    """Get the global monitoring scheduler instance."""
    return monitoring_scheduler