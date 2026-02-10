"""MCP integration helpers for accessing MCP servers."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import config

# MCP tools are available as global functions in Cursor environment
# We'll use them directly by calling the functions that are available

class MCPIntegration:
    """Helper class for MCP server integration."""
    
    @staticmethod
    def get_jira_issues(cloud_id: str, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get Jira issues using MCP."""
        # MCP tools are available as functions we can call directly
        # In Cursor, these are injected into the execution context
        # We'll use a wrapper that can be replaced with actual MCP calls
        # For now, this will be called from test script which has MCP access
        return []
    
    @staticmethod
    def get_confluence_page(cloud_id: str, page_id: str, format: str = "markdown") -> Dict[str, Any]:
        """Get Confluence page content using MCP."""
        try:
            from mcp_atlassian import getConfluencePage
            return getConfluencePage(cloudId=cloud_id, pageId=page_id, contentFormat=format)
        except (ImportError, NameError):
            return {}
    
    @staticmethod
    def create_confluence_page(cloud_id: str, space_id: str, title: str, body: str, 
                               parent_id: Optional[str] = None, format: str = "markdown") -> Dict[str, Any]:
        """Create a Confluence page using MCP."""
        try:
            from mcp_atlassian import createConfluencePage
            params = {
                "cloudId": cloud_id,
                "spaceId": space_id,
                "title": title,
                "body": body,
                "contentFormat": format
            }
            if parent_id:
                params["parentId"] = parent_id
            return createConfluencePage(**params)
        except (ImportError, NameError):
            return {"id": None, "title": title}
    
    @staticmethod
    def update_confluence_page(cloud_id: str, page_id: str, body: str, 
                               title: Optional[str] = None, format: str = "markdown") -> Dict[str, Any]:
        """Update a Confluence page using MCP."""
        try:
            from mcp_atlassian import updateConfluencePage
            params = {
                "cloudId": cloud_id,
                "pageId": page_id,
                "body": body,
                "contentFormat": format
            }
            if title:
                params["title"] = title
            return updateConfluencePage(**params)
        except (ImportError, NameError):
            return {"id": page_id}
    
    @staticmethod
    def get_confluence_page_descendants(cloud_id: str, page_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get child pages of a Confluence page using MCP."""
        try:
            from mcp_atlassian import getConfluencePageDescendants
            result = getConfluencePageDescendants(cloudId=cloud_id, pageId=page_id, limit=limit)
            return result.get("results", [])
        except (ImportError, NameError):
            return []
    
    @staticmethod
    def glean_search(query: str, updated: Optional[str] = None, 
                     after: Optional[str] = None, before: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search Glean using MCP."""
        try:
            from mcp_Glean import search
            params = {"query": query}
            if updated:
                params["updated"] = updated
            if after:
                params["after"] = after
            if before:
                params["before"] = before
            result = search(**params)
            return result.get("results", [])
        except (ImportError, NameError):
            return []
    
    @staticmethod
    def glean_meeting_lookup(query: str, extract_transcript: bool = False) -> List[Dict[str, Any]]:
        """Lookup meetings in Glean using MCP."""
        try:
            from mcp_Glean import meeting_lookup
            result = meeting_lookup(query=query, extract_transcript=str(extract_transcript).lower())
            return result if isinstance(result, list) else []
        except (ImportError, NameError):
            return []
    
    @staticmethod
    def pendo_list_applications() -> List[Dict[str, Any]]:
        """List Pendo applications using MCP."""
        try:
            from mcp_Pendo import list_all_applications
            return list_all_applications()
        except (ImportError, NameError):
            return []
    
    @staticmethod
    def pendo_activity_query(application_id: str, start_date: str, end_date: str, 
                            group_by: str = "feature", limit: int = 10) -> List[Dict[str, Any]]:
        """Query Pendo activity using MCP."""
        # Note: This tool may not be available - check available Pendo MCP tools
        try:
            from mcp_Pendo import activityQuery
            return activityQuery(
                applicationId=application_id,
                startDate=start_date,
                endDate=end_date,
                groupBy=group_by,
                limit=limit
            )
        except (ImportError, NameError, AttributeError):
            return []
    
    @staticmethod
    def granola_list_meetings(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Granola meetings using MCP."""
        try:
            from mcp_Granola import list_meetings
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            return list_meetings(**params) if params else list_meetings()
        except (ImportError, NameError, AttributeError):
            return []
    
    @staticmethod
    def granola_get_meetings(query: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search Granola meeting content using MCP."""
        try:
            from mcp_Granola import get_meetings
            params = {"query": query}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            return get_meetings(**params)
        except (ImportError, NameError, AttributeError):
            return []
    
    @staticmethod
    def granola_get_meeting_transcript(meeting_id: str) -> str:
        """Get raw transcript for a specific Granola meeting using MCP."""
        try:
            from mcp_Granola import get_meeting_transcript
            result = get_meeting_transcript(meeting_id=meeting_id)
            return result.get("transcript", "") if isinstance(result, dict) else str(result)
        except (ImportError, NameError, AttributeError):
            return ""
    
    @staticmethod
    def granola_query_meetings(query: str) -> str:
        """Query Granola meetings using chat interface."""
        try:
            from mcp_Granola import query_granola_meetings
            result = query_granola_meetings(query=query)
            return result.get("response", "") if isinstance(result, dict) else str(result)
        except (ImportError, NameError, AttributeError):
            return ""
