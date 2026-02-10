"""Scheduler for weekly update automation."""
import schedule
import time
from datetime import datetime
from file_manager import FileManager
from content_generator import ContentGenerator
import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeeklyUpdateScheduler:
    """Schedules and runs weekly update automation jobs."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.file_manager = FileManager()
        self.content_generator = ContentGenerator()
    
    def monday_job(self):
        """Job to run on Mondays - creates new weekly file."""
        logger.info("Running Monday job - creating new weekly file")
        
        try:
            # Check if we should create a new page
            if self.file_manager.should_create_new_page():
                # Create new weekly page
                page = self.file_manager.create_weekly_page(
                    self.file_manager.get_current_week_friday()
                )
                
                logger.info(f"Created new weekly page: {page.get('id')}")
                
                # Generate initial content from previous week's data
                content = self.content_generator.generate_full_content()
                
                # Update the page with initial content
                self.file_manager.update_page_content(
                    page.get("id"),
                    content,
                    append=False
                )
                
                logger.info("Initial content generated and added to new page")
            else:
                logger.info("Weekly page already exists or not Monday - skipping creation")
        
        except Exception as e:
            logger.error(f"Error in Monday job: {e}", exc_info=True)
    
    def daily_job(self):
        """Job to run daily at 8pm - updates current weekly file."""
        logger.info("Running daily job - updating current weekly file")
        
        try:
            # Get or create current weekly page
            page = self.file_manager.get_or_create_current_weekly_page()
            page_id = page.get("id")
            
            if not page_id:
                logger.error("Could not get page ID")
                return
            
            # Get existing content
            existing_content = self.file_manager.confluence.get_page_content(page_id)
            
            # Generate new content sections
            highlights = self.content_generator.generate_highlights(existing_content)
            this_week = self.content_generator.generate_this_week(existing_content)
            next_week = self.content_generator.generate_next_week(existing_content)
            customer_corner = self.content_generator.generate_customer_corner(existing_content)
            
            # Build update content
            updates = []
            if highlights:
                updates.append("## Highlights\n\n" + highlights)
            if this_week:
                updates.append("## This Week\n\n" + this_week)
            if next_week:
                updates.append("## Next Week\n\n" + next_week)
            if customer_corner:
                updates.append("## Customer Corner\n\n" + customer_corner)
            
            if updates:
                update_content = "\n\n".join(updates)
                
                # Append to page
                self.file_manager.update_page_content(
                    page_id,
                    update_content,
                    append=True
                )
                
                logger.info(f"Updated weekly page {page_id} with new content")
            else:
                logger.info("No new content to add")
        
        except Exception as e:
            logger.error(f"Error in daily job: {e}", exc_info=True)

    def friday_job(self):
        """Job to run Fridays at 8:30pm - compiles week's content into one doc without dupes."""
        logger.info("Running Friday job - compiling weekly content")
        try:
            page = self.file_manager.get_or_create_current_weekly_page()
            page_id = page.get("id")
            if not page_id:
                logger.error("Could not get page ID")
                return
            existing_content = self.file_manager.confluence.get_page_content(page_id)
            compiled = ContentGenerator.compile_and_dedupe_sections(existing_content)
            if not compiled.strip():
                logger.warning("Compiled content empty; skipping update")
                return
            self.file_manager.update_page_content(page_id, compiled, append=False)
            logger.info(f"Friday compile complete: updated page {page_id} with deduplicated content")
        except Exception as e:
            logger.error(f"Error in Friday job: {e}", exc_info=True)

    def setup_schedule(self):
        """Set up the scheduling."""
        # Monday job at midnight
        schedule.every().monday.at("00:00").do(self.monday_job)
        
        # Daily job at 8pm
        schedule.every().day.at("20:00").do(self.daily_job)
        # Friday job at 8:30pm (after daily) - compile week into one doc, no dupes
        schedule.every().friday.at("20:30").do(self.friday_job)

        logger.info("Schedule set up:")
        logger.info("  - Monday job: 00:00 (create new weekly file)")
        logger.info("  - Daily job: 20:00 (update current weekly file)")
        logger.info("  - Friday job: 20:30 (compile week into cohesive doc, no dupes)")
    
    def run(self):
        """Run the scheduler."""
        self.setup_schedule()
        
        logger.info("Scheduler started. Waiting for scheduled jobs...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_now(self, job_type: str = "daily"):
        """Run a job immediately (for testing)."""
        if job_type == "monday":
            self.monday_job()
        elif job_type == "friday":
            self.friday_job()
        else:
            self.daily_job()

if __name__ == "__main__":
    scheduler = WeeklyUpdateScheduler()
    scheduler.run()
