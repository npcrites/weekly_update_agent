"""Test script to verify Granola MCP integration."""
from datetime import datetime, timedelta
from granola_aggregator import GranolaAggregator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_granola():
    """Test Granola MCP integration."""
    logger.info("Testing Granola MCP integration...")
    
    granola = GranolaAggregator()
    
    # Get last week's dates
    last_week_start = granola.get_previous_week_start()
    last_week_end = granola.get_previous_week_end()
    
    logger.info(f"Testing for week: {last_week_start.strftime('%Y-%m-%d')} to {last_week_end.strftime('%Y-%m-%d')}")
    
    # Test 1: List meetings
    logger.info("\n1. Testing list_meetings...")
    try:
        meetings = granola.get_meetings_for_week(last_week_start, last_week_end)
        logger.info(f"Found {len(meetings)} meetings")
        for meeting in meetings[:5]:
            logger.info(f"  - {meeting.get('title', 'Untitled')} ({meeting.get('meeting_date', 'No date')})")
    except Exception as e:
        logger.error(f"Error listing meetings: {e}")
    
    # Test 2: Get customer calls
    logger.info("\n2. Testing get_customer_calls...")
    try:
        customer_calls = granola.get_customer_calls(last_week_start, last_week_end)
        logger.info(f"Found {len(customer_calls)} customer calls")
        for call in customer_calls:
            formatted = granola.format_customer_call(call)
            logger.info(f"  - {formatted.get('customer_name')}: {formatted.get('title')}")
    except Exception as e:
        logger.error(f"Error getting customer calls: {e}")
    
    # Test 3: Search meeting content
    logger.info("\n3. Testing search_meeting_content...")
    try:
        results = granola.search_meeting_content("customer", last_week_start, last_week_end)
        logger.info(f"Found {len(results)} meetings matching 'customer'")
    except Exception as e:
        logger.error(f"Error searching meetings: {e}")
    
    logger.info("\n✅ Granola MCP integration test complete!")

if __name__ == "__main__":
    test_granola()
