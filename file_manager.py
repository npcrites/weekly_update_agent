"""File management for weekly update documents."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from confluence_client import ConfluenceClient
import config

class FileManager:
    """Manages creation and finding of weekly update files."""
    
    def __init__(self):
        """Initialize the file manager."""
        self.confluence = ConfluenceClient()
    
    def get_current_week_friday(self) -> datetime:
        """Get the Friday date of the current week."""
        return config.Config.get_week_friday()
    
    def get_page_title_for_date(self, date: datetime) -> str:
        """Get the page title for a given Friday date."""
        return config.Config.format_page_title(date)
    
    def get_quarter_folder_name(self, date: datetime) -> str:
        """Get the quarterly folder name for a date."""
        return config.Config.get_quarter_folder_name(date)
    
    def find_quarter_folder_id(self, date: datetime) -> Optional[str]:
        """Find the ID of the quarterly folder for a given date."""
        quarter_name = self.get_quarter_folder_name(date)
        
        # Use confluence client to find folder
        folder = self.confluence.find_quarter_folder(date)
        return folder
    
    def find_or_create_quarter_folder(self, date: datetime) -> str:
        """Find or create the quarterly folder for a date."""
        folder_id = self.find_quarter_folder_id(date)
        
        if folder_id:
            return folder_id
        
        # Create the folder
        quarter_name = self.get_quarter_folder_name(date)
        folder = self.confluence.create_page(
            title=quarter_name,
            content="",
            parent_id=config.Config.CONFLUENCE_PARENT_PAGE_ID
        )
        
        return folder.get("id")
    
    def find_weekly_page(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Find an existing weekly page for a given Friday date."""
        title = self.get_page_title_for_date(date)
        
        # First try to find in quarter folder
        folder_id = self.find_quarter_folder_id(date)
        if folder_id:
            page = self.confluence.find_weekly_page(title, folder_id)
            if page:
                return page
        
        # Also check parent directly (for pages not in folders)
        page = self.confluence.find_weekly_page(title, config.Config.CONFLUENCE_PARENT_PAGE_ID)
        return page
    
    def create_weekly_page(self, date: datetime) -> Dict[str, Any]:
        """Create a new weekly update page."""
        title = self.get_page_title_for_date(date)
        
        # Get or create quarterly folder
        folder_id = self.find_or_create_quarter_folder(date)
        
        # Initialize with empty sections
        initial_content = """## Highlights

## This Week

## Next Week

## Customer Corner
"""
        
        # Create the page
        page = self.confluence.create_page(
            title=title,
            content=initial_content,
            parent_id=folder_id
        )
        
        return page
    
    def get_current_weekly_page(self) -> Optional[Dict[str, Any]]:
        """Get the current week's page (most recent Friday)."""
        friday = self.get_current_week_friday()
        return self.find_weekly_page(friday)
    
    def get_or_create_current_weekly_page(self) -> Dict[str, Any]:
        """Get or create the current week's page."""
        page = self.get_current_weekly_page()
        
        if page:
            return page
        
        # Create new page
        friday = self.get_current_week_friday()
        return self.create_weekly_page(friday)
    
    def should_create_new_page(self) -> bool:
        """Determine if a new weekly page should be created (Monday check)."""
        today = datetime.now()
        
        # Check if it's Monday
        if today.weekday() != 0:  # Monday is 0
            return False
        
        # Check if page for this week already exists
        friday = self.get_current_week_friday()
        existing_page = self.find_weekly_page(friday)
        
        return existing_page is None
    
    def update_page_content(self, page_id: str, new_content: str, append: bool = True) -> Dict[str, Any]:
        """Update a page's content, optionally appending."""
        if append:
            # Get existing content
            existing_content = self.confluence.get_page_content(page_id)
            
            # Append new content (deduplication handled by content generator)
            updated_content = existing_content + "\n\n" + new_content
        else:
            updated_content = new_content
        
        # Update the page
        return self.confluence.update_page(page_id, updated_content)
