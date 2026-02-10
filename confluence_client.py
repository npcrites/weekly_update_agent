"""Confluence API client using Atlassian MCP server."""
from typing import Optional, Dict, Any
from datetime import datetime
import config
from mcp_integration import MCPIntegration

class ConfluenceClient:
    """Client for interacting with Confluence via MCP."""
    
    def __init__(self, cloud_id: str = None):
        """Initialize the Confluence client."""
        self.cloud_id = cloud_id or config.Config.JIRA_CLOUD_ID
        self.space_id = config.Config.CONFLUENCE_SPACE_ID
        self.parent_page_id = config.Config.CONFLUENCE_PARENT_PAGE_ID
        self.mcp = MCPIntegration()
    
    def find_quarter_folder(self, date: datetime) -> Optional[str]:
        """Find or create the quarterly folder for a given date."""
        quarter_name = config.Config.get_quarter_folder_name(date)
        
        # Get descendants of parent page to find quarterly folders
        descendants = self.mcp.get_confluence_page_descendants(
            cloud_id=self.cloud_id,
            page_id=self.parent_page_id,
            limit=100
        )
        
        # Search for folder with matching title
        for descendant in descendants:
            if descendant.get("title") == quarter_name:
                return descendant.get("id")
        
        return None
    
    def find_weekly_page(self, title: str, parent_folder_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find an existing weekly page by title."""
        search_id = parent_folder_id or self.parent_page_id
        
        # Get descendants to search for page
        descendants = self.mcp.get_confluence_page_descendants(
            cloud_id=self.cloud_id,
            page_id=search_id,
            limit=100
        )
        
        # Search for page with matching title
        for descendant in descendants:
            if descendant.get("title") == title:
                return descendant
        
        return None
    
    def create_page(self, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page."""
        space_id = self.space_id
        parent_id = parent_id or self.parent_page_id
        
        result = self.mcp.create_confluence_page(
            cloud_id=self.cloud_id,
            space_id=space_id,
            title=title,
            body=content,
            parent_id=parent_id,
            format="markdown"
        )
        
        return result
    
    def update_page(self, page_id: str, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing Confluence page."""
        result = self.mcp.update_confluence_page(
            cloud_id=self.cloud_id,
            page_id=page_id,
            body=content,
            title=title,
            format="markdown"
        )
        
        return result
    
    def get_page_content(self, page_id: str) -> str:
        """Get the current content of a Confluence page."""
        result = self.mcp.get_confluence_page(
            cloud_id=self.cloud_id,
            page_id=page_id,
            format="markdown"
        )
        
        return result.get("body", "")
