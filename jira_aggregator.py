"""Jira data aggregation for weekly updates."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import config
from mcp_integration import MCPIntegration

class JiraAggregator:
    """Aggregates data from Jira for weekly updates."""
    
    def __init__(self, cloud_id: str = None):
        """Initialize the Jira aggregator."""
        self.cloud_id = cloud_id or config.Config.JIRA_CLOUD_ID
        self.mcp = MCPIntegration()
    
    def get_week_start(self) -> datetime:
        """Get the start of the current week (Monday)."""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        return monday
    
    def get_issues_updated_this_week(self) -> List[Dict[str, Any]]:
        """Get Jira issues assigned to current user and updated this week."""
        week_start = self.get_week_start()
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # JQL query: assignee = currentUser() AND updated >= startOfWeek()
        jql = f"assignee = currentUser() AND updated >= {week_start_str} ORDER BY updated DESC"
        
        issues = self.mcp.get_jira_issues(
            cloud_id=self.cloud_id,
            jql=jql,
            max_results=50
        )
        
        return issues
    
    def get_initiatives(self) -> List[Dict[str, Any]]:
        """Get initiatives/epics assigned to current user."""
        issues = self.get_issues_updated_this_week()
        
        # Filter for initiatives/epics
        initiatives = []
        for issue in issues:
            issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
            if issue_type in ["Initiative", "Epic"]:
                initiatives.append(issue)
        
        return initiatives
    
    def get_blockers(self) -> List[Dict[str, Any]]:
        """Get blocked issues or high-priority issues."""
        issues = self.get_issues_updated_this_week()
        
        blockers = []
        for issue in issues:
            status = issue.get("fields", {}).get("status", {}).get("name", "")
            priority = issue.get("fields", {}).get("priority", {})
            priority_name = priority.get("name", "") if priority else ""
            
            # Check if blocked or highest/high priority
            if "blocked" in status.lower() or priority_name in ["Highest", "High"]:
                blockers.append(issue)
        
        return blockers
    
    def get_completed_items(self) -> List[Dict[str, Any]]:
        """Get issues completed this week."""
        issues = self.get_issues_updated_this_week()
        
        completed = []
        for issue in issues:
            status = issue.get("fields", {}).get("status", {}).get("name", "")
            status_category = issue.get("fields", {}).get("status", {}).get("statusCategory", {})
            category_key = status_category.get("key", "") if status_category else ""
            
            if category_key == "done" or status.lower() == "done":
                completed.append(issue)
        
        return completed
    
    def get_in_progress_items(self) -> List[Dict[str, Any]]:
        """Get issues currently in progress."""
        issues = self.get_issues_updated_this_week()
        
        in_progress = []
        for issue in issues:
            status = issue.get("fields", {}).get("status", {}).get("name", "")
            status_category = issue.get("fields", {}).get("status", {}).get("statusCategory", {})
            category_key = status_category.get("key", "") if status_category else ""
            
            if category_key == "indeterminate" or "progress" in status.lower():
                in_progress.append(issue)
        
        return in_progress
    
    def format_issue_summary(self, issue: Dict[str, Any]) -> str:
        """Format an issue for display."""
        key = issue.get("key", "")
        summary = issue.get("fields", {}).get("summary", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        
        return f"{key}: {summary} ({status})"
