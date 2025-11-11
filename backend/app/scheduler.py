"""
Scheduler for running periodic monitoring tasks.
Enhanced with minute-level uploads for near real-time monitoring.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from app.monitoring import get_monitoring_service

logger = logging.getLogger("uvicorn")


class MonitoringScheduler:
    """Manages scheduled monitoring tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.monitoring_service = get_monitoring_service()
        self.is_running = False
    
    def start(self):
        """Start the scheduler with all monitoring tasks."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        try:
            # Schedule periodic report uploads for near real-time monitoring
            # This ensures we never lose more than 5 minutes of data on crash
            # Files are small and uploaded efficiently every 5 minutes
            self.scheduler.add_job(
                self.monitoring_service.minute_report_task,
                IntervalTrigger(minutes=5),
                id='minute_report',
                name='Generate and upload monitoring report every 5 minutes',
                replace_existing=True
            )
            logger.info("Scheduled periodic report task (every 5 minutes)")
            
            # Keep hourly memory logging for debugging
            self.scheduler.add_job(
                self.monitoring_service.log_memory_usage,
                CronTrigger(minute=0),  # Every hour at :00
                id='hourly_memory_log',
                name='Log memory usage',
                replace_existing=True
            )
            logger.info("Scheduled hourly memory logging")

            # Schedule periodic garbage collection every 10 minutes
            self.scheduler.add_job(
                self.monitoring_service.periodic_gc,
                IntervalTrigger(minutes=10),
                id='periodic_gc',
                name='Periodic garbage collection',
                replace_existing=True
            )
            logger.info("Scheduled periodic garbage collection every 10 minutes")

            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            logger.info("Monitoring scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting monitoring scheduler: {e}", exc_info=True)
    
    async def shutdown(self):
        """Gracefully shutdown the scheduler."""
        if not self.is_running:
            return
        
        try:
            # Generate final report before shutdown
            logger.info("Generating final report before shutdown...")
            await self.monitoring_service.minute_report_task()
            
            # Shutdown scheduler
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Monitoring scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")


# Global scheduler instance
monitoring_scheduler = MonitoringScheduler()


def get_monitoring_scheduler() -> MonitoringScheduler:
    """Get the global monitoring scheduler instance."""
    return monitoring_scheduler
