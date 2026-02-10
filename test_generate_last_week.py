"""Test script to generate weekly update for last week using actual MCP tools."""
import sys
from datetime import datetime, timedelta
from file_manager import FileManager
from content_generator import ContentGenerator
from jira_aggregator import JiraAggregator
from glean_aggregator import GleanAggregator
from pendo_aggregator import PendoAggregator
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_last_week_friday() -> datetime:
    """Get the Friday date of last week."""
    today = datetime.now()
    # Go back to last week
    last_week = today - timedelta(days=7)
    return config.Config.get_week_friday(last_week)

def generate_test_update():
    """Generate a test weekly update for last week."""
    logger.info("Generating test weekly update for last week...")
    
    # Get last week's Friday date
    last_friday = get_last_week_friday()
    logger.info(f"Target date: {last_friday.strftime('%B %d, %Y')}")
    
    # Initialize components
    file_manager = FileManager()
    content_generator = ContentGenerator()
    
    # Generate page title
    page_title = file_manager.get_page_title_for_date(last_friday)
    logger.info(f"Page title: {page_title}")
    
    # Generate content
    logger.info("Generating content sections...")
    
    try:
        # Test data fetching
        logger.info("Fetching Jira data...")
        jira = JiraAggregator()
        issues = jira.get_issues_updated_this_week()
        logger.info(f"Found {len(issues)} Jira issues")
        
        logger.info("Fetching Glean data...")
        glean = GleanAggregator()
        project_updates = glean.search_project_updates()
        logger.info(f"Found {len(project_updates)} Glean project updates")
        
        customer_calls = glean.get_customer_calls()
        logger.info(f"Found {len(customer_calls)} customer calls")
        
        logger.info("Fetching Pendo data...")
        pendo = PendoAggregator()
        metrics = pendo.get_activity_metrics()
        logger.info(f"Found {len(metrics)} Pendo metrics")
        
    except Exception as e:
        logger.warning(f"Error fetching data: {e}")
        logger.info("Continuing with content generation...")
    
    # Generate all sections
    logger.info("Generating Highlights...")
    highlights = content_generator.generate_highlights()
    
    logger.info("Generating This Week...")
    this_week = content_generator.generate_this_week()
    
    logger.info("Generating Next Week...")
    next_week = content_generator.generate_next_week()
    
    logger.info("Generating Customer Corner...")
    customer_corner = content_generator.generate_customer_corner()
    
    # Combine into full content
    sections = []
    if highlights:
        sections.append("## Highlights\n\n" + highlights)
    if this_week:
        sections.append("\n## This Week\n\n" + this_week)
    if next_week:
        sections.append("\n## Next Week\n\n" + next_week)
    if customer_corner:
        sections.append("\n## Customer Corner\n\n" + customer_corner)
    
    full_content = "\n".join(sections)
    
    # Output results
    print("\n" + "="*80)
    print(f"WEEKLY UPDATE: {page_title}")
    print("="*80)
    print(full_content)
    print("="*80)
    
    # Save to file
    output_file = f"/Users/nickcrites/weekly_updates_agent/test_output_{last_friday.strftime('%Y%m%d')}.md"
    with open(output_file, 'w') as f:
        f.write(f"# {page_title}\n\n")
        f.write(full_content)
    
    logger.info(f"Content saved to: {output_file}")
    
    return {
        "title": page_title,
        "content": full_content,
        "file": output_file
    }

if __name__ == "__main__":
    try:
        result = generate_test_update()
        print(f"\n✅ Successfully generated test update!")
        print(f"📄 File: {result['file']}")
    except Exception as e:
        logger.error(f"Error generating test update: {e}", exc_info=True)
        sys.exit(1)
