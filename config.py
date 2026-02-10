"""Configuration management for Weekly Update Automation Agent."""
import os
from datetime import datetime, timedelta
from typing import Optional

class Config:
    """Configuration settings for the weekly updates agent."""
    
    # Confluence settings
    CONFLUENCE_SPACE_ID = "3149365261"  # Product space
    CONFLUENCE_PARENT_PAGE_ID = "3900833797"  # Nick's Weekly Updates
    
    # Jira settings
    JIRA_CLOUD_ID = "03eb62f4-22ac-4a6d-8e53-73bca97fbbad"
    
    # Glean settings
    GLEAN_INSTANCE = "singleops-be.glean.com"
    
    # Pendo settings
    PENDO_INTEGRATION_KEY = os.getenv("PENDO_INTEGRATION_KEY", "ab621090-eba5-4919-8cc0-1a749ef964f6.us")
    
    # Scheduling settings
    TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
    DAILY_UPDATE_HOUR = 20  # 8pm
    MONDAY_CREATE_HOUR = 0  # Midnight
    
    # File naming
    DATE_FORMAT = "%b %dth %Y"  # e.g., "Feb 13th 2026"
    PAGE_TITLE_PREFIX = "Nick - "
    
    # Content settings
    MAX_HIGHLIGHTS = 5
    PAST_DOCUMENTS_TO_ANALYZE = 5

    # Slack (for slash command: /weekly-update)
    # SLACK_SIGNING_SECRET: from Slack app → Basic Information → Signing Secret (required for verification)
    # SLACK_BOT_TOKEN: optional, only if posting follow-up via chat.postMessage instead of response_url
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    
    @staticmethod
    def get_quarter_folder_name(date: datetime) -> str:
        """Get the quarterly folder name for a given date."""
        quarter = (date.month - 1) // 3 + 1
        year = date.year
        return f"Nick Q{quarter} {year}"
    
    @staticmethod
    def get_week_friday(date: Optional[datetime] = None) -> datetime:
        """Get the Friday date of the current week (or specified date's week)."""
        if date is None:
            date = datetime.now()
        
        # Get Monday of the week
        days_since_monday = date.weekday()
        monday = date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        
        # Friday is 4 days after Monday
        friday = monday + timedelta(days=4)
        return friday
    
    @staticmethod
    def format_page_title(date: datetime) -> str:
        """Format the page title for a given Friday date."""
        formatted_date = date.strftime(Config.DATE_FORMAT)
        return f"{Config.PAGE_TITLE_PREFIX}{formatted_date}"
