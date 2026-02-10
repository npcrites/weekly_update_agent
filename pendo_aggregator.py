"""Pendo data aggregation for weekly updates."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import config
from mcp_integration import MCPIntegration

class PendoAggregator:
    """Aggregates data from Pendo for weekly updates."""
    
    def __init__(self, integration_key: str = None):
        """Initialize the Pendo aggregator."""
        self.integration_key = integration_key or config.Config.PENDO_INTEGRATION_KEY
        self.default_application_id = "4859144687124480"  # SingleOps
        self.mcp = MCPIntegration()
    
    def get_week_start(self) -> datetime:
        """Get the start of the current week (Monday)."""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        return monday
    
    def get_week_end(self) -> datetime:
        """Get the end of the current week (Sunday)."""
        week_start = self.get_week_start()
        return week_start + timedelta(days=6)
    
    def get_activity_metrics(self, application_id: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get activity metrics from Pendo for the specified period."""
        app_id = application_id or self.default_application_id
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Note: Pendo MCP may not have activityQuery tool available
        # Check available Pendo MCP tools and use appropriate one
        metrics = self.mcp.pendo_activity_query(
            application_id=app_id,
            start_date=start_str,
            end_date=end_str,
            group_by="feature",
            limit=10
        )
        
        return metrics
    
    def get_top_features(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top features by usage."""
        metrics = self.get_activity_metrics()
        
        # Sort by usage and return top N
        # This is a placeholder - actual implementation would process Pendo response
        return metrics[:limit]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance-related metrics."""
        metrics = self.get_activity_metrics()
        
        # Extract performance indicators
        # This is a placeholder
        return {
            "response_time_improvements": [],
            "feature_adoption": [],
            "usage_trends": []
        }
    
    def format_feature_insight(self, feature: Dict[str, Any]) -> str:
        """Format a feature insight for display."""
        feature_name = feature.get("name", "")
        usage_count = feature.get("usage_count", 0)
        change = feature.get("change_percent", 0)
        
        if change > 0:
            return f"{feature_name}: {usage_count} uses (+{change}%)"
        elif change < 0:
            return f"{feature_name}: {usage_count} uses ({change}%)"
        else:
            return f"{feature_name}: {usage_count} uses"
