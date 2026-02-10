"""Main entry point for weekly update automation."""
import sys
import argparse
from scheduler import WeeklyUpdateScheduler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Weekly Update Automation Agent")
    parser.add_argument(
        "--job",
        choices=["monday", "daily", "friday", "run"],
        default="run",
        help="Type of job to run (monday, daily, friday) or run scheduler (run)"
    )
    
    args = parser.parse_args()
    
    scheduler = WeeklyUpdateScheduler()
    
    if args.job == "monday":
        logger.info("Running Monday job manually")
        scheduler.monday_job()
    elif args.job == "daily":
        logger.info("Running daily job manually")
        scheduler.daily_job()
    elif args.job == "friday":
        logger.info("Running Friday job manually")
        scheduler.friday_job()
    else:
        logger.info("Starting scheduler")
        scheduler.run()

if __name__ == "__main__":
    main()
