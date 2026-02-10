"""Filter content for SVP relevance."""
from typing import List, Dict, Any

class SVPFilter:
    """Filters content to identify items relevant to SVP of Product."""
    
    def __init__(self):
        """Initialize the SVP filter."""
        self.high_priority_keywords = {
            "strategic", "cross-functional", "escalation", "blocker", "critical",
            "performance", "revenue", "churn", "retention", "migration", "customer"
        }
    
    def is_svp_relevant(self, item: Dict[str, Any], source: str = "jira") -> bool:
        """Determine if an item is relevant to SVP."""
        if source == "jira":
            return self._is_jira_svp_relevant(item)
        elif source == "glean":
            return self._is_glean_svp_relevant(item)
        elif source == "pendo":
            return self._is_pendo_svp_relevant(item)
        
        return False
    
    def _is_jira_svp_relevant(self, issue: Dict[str, Any]) -> bool:
        """Check if a Jira issue is SVP-relevant."""
        fields = issue.get("fields", {})
        
        # High priority issues
        priority = fields.get("priority", {})
        priority_name = priority.get("name", "") if priority else ""
        if priority_name in ["Highest", "High"]:
            return True
        
        # Blocked issues
        status = fields.get("status", {}).get("name", "")
        if "blocked" in status.lower():
            return True
        
        # Strategic initiatives
        issue_type = fields.get("issuetype", {}).get("name", "")
        if issue_type in ["Initiative", "Epic"]:
            return True
        
        # Check summary for keywords
        summary = fields.get("summary", "").lower()
        for keyword in self.high_priority_keywords:
            if keyword in summary:
                return True
        
        return False
    
    def _is_glean_svp_relevant(self, item: Dict[str, Any]) -> bool:
        """Check if a Glean item is SVP-relevant."""
        title = item.get("title", "").lower()
        snippet = item.get("snippet", "").lower()
        content = f"{title} {snippet}"
        
        # Check for strategic keywords
        for keyword in self.high_priority_keywords:
            if keyword in content:
                return True
        
        # Customer escalations
        if "escalation" in content or "customer complaint" in content:
            return True
        
        return False
    
    def _is_pendo_svp_relevant(self, metric: Dict[str, Any]) -> bool:
        """Check if a Pendo metric is SVP-relevant."""
        # Performance metrics with significant impact
        change_percent = abs(metric.get("change_percent", 0))
        if change_percent > 20:  # Significant change
            return True
        
        # Feature adoption metrics
        if "adoption" in metric.get("name", "").lower():
            return True
        
        return False
    
    def filter_for_highlights(self, items: List[Dict[str, Any]], source: str = "jira") -> List[Dict[str, Any]]:
        """Filter items that should appear in Highlights section."""
        return [item for item in items if self.is_svp_relevant(item, source)]
    
    def prioritize_items(self, items: List[Dict[str, Any]], source: str = "jira") -> List[Dict[str, Any]]:
        """Prioritize items by SVP relevance."""
        # Sort by relevance (most relevant first)
        scored_items = []
        
        for item in items:
            score = self._calculate_relevance_score(item, source)
            scored_items.append((score, item))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for _, item in scored_items]
    
    def _calculate_relevance_score(self, item: Dict[str, Any], source: str) -> int:
        """Calculate a relevance score for an item."""
        score = 0
        
        if source == "jira":
            fields = item.get("fields", {})
            priority = fields.get("priority", {})
            priority_name = priority.get("name", "") if priority else ""
            
            if priority_name == "Highest":
                score += 10
            elif priority_name == "High":
                score += 5
            
            if "blocked" in fields.get("status", {}).get("name", "").lower():
                score += 8
            
            issue_type = fields.get("issuetype", {}).get("name", "")
            if issue_type in ["Initiative", "Epic"]:
                score += 3
        
        elif source == "glean":
            title = item.get("title", "").lower()
            if "escalation" in title or "critical" in title:
                score += 10
            if "customer" in title:
                score += 5
        
        elif source == "pendo":
            change = abs(item.get("change_percent", 0))
            if change > 50:
                score += 10
            elif change > 20:
                score += 5
        
        return score
