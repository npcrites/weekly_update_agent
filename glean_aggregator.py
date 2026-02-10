"""Glean data aggregation for weekly updates."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import config
from mcp_integration import MCPIntegration

class GleanAggregator:
    """Aggregates data from Glean for weekly updates."""
    
    def __init__(self):
        """Initialize the Glean aggregator."""
        self.mcp = MCPIntegration()
    
    def get_week_start(self) -> datetime:
        """Get the start of the current week (Monday)."""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        return monday
    
    def get_previous_week_start(self) -> datetime:
        """Get the start of the previous week."""
        return self.get_week_start() - timedelta(days=7)
    
    def get_previous_week_end(self) -> datetime:
        """Get the end of the previous week (Sunday)."""
        return self.get_week_start() - timedelta(days=1)
    
    def search_project_updates(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search Glean for project-related documents updated recently."""
        # Query: project updates initiatives SingleOps migration Kiro Cloudinary performance
        query = "project updates initiatives SingleOps migration Kiro Cloudinary performance"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        results = self.mcp.glean_search(
            query=query,
            after=start_str,
            before=end_str
        )
        
        return results
    
    def get_customer_calls(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get customer call meetings from Glean."""
        if start_date is None:
            start_date = self.get_previous_week_start()
        if end_date is None:
            end_date = self.get_previous_week_end()
        
        # Format dates for Glean query
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Query: meeting_lookup with "Customer Call" in topic
        query = f'participants:"Nick Crites" topic:"Customer Call" after:{start_str} before:{end_str}'
        
        meetings = self.mcp.glean_meeting_lookup(
            query=query,
            extract_transcript=False
        )
        
        return meetings
    
    def format_customer_call(self, meeting: Dict[str, Any]) -> Dict[str, str]:
        """Format a customer call meeting for display."""
        # Extract customer name and meeting URL
        title = meeting.get("title", "")
        url = meeting.get("url", "")
        
        # Try to extract customer name from title
        # Format might be "Customer Call - [Customer Name]" or "[Customer Name] - Customer Call"
        customer_name = title
        if "Customer Call" in title:
            parts = title.split("Customer Call")
            customer_name = parts[0].strip(" -") if parts[0].strip() else parts[1].strip(" -") if len(parts) > 1 else title
        
        return {
            "customer_name": customer_name,
            "url": url,
            "title": title
        }
    
    def get_project_insights(self) -> List[str]:
        """Extract key project insights from Glean search results."""
        updates = self.search_project_updates()
        
        insights = []
        for update in updates:
            # Extract key information from documents
            title = update.get("title", "")
            snippet = update.get("snippet", "")
            url = update.get("url", "")
            
            if title or snippet:
                insights.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url
                })
        
        return insights
