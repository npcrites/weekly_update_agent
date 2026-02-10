"""Granola meeting aggregation for weekly updates.

Provides meeting/customer-call data. When MCP Granola is not available,
this stub returns empty results so tests and content generation can run.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import config


class GranolaAggregator:
    """Aggregates meeting data from Granola (or stub for tests)."""

    def get_previous_week_start(self) -> datetime:
        """Get the Monday of the previous week."""
        last_friday = config.Config.get_week_friday(
            datetime.now() - timedelta(days=7)
        )
        return last_friday - timedelta(days=4)

    def get_previous_week_end(self) -> datetime:
        """Get the Friday of the previous week (week end date)."""
        return config.Config.get_week_friday(
            datetime.now() - timedelta(days=7)
        )

    def get_meetings_for_week(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get meetings in the given date range. Stub returns empty list."""
        return []

    def get_customer_calls(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get customer call meetings. Stub returns empty list."""
        return []

    def format_customer_call(self, call: Dict[str, Any]) -> Dict[str, str]:
        """Format a customer call for display."""
        return {
            "customer_name": call.get("customer_name", "Customer"),
            "title": call.get("title", ""),
            "url": call.get("url", ""),
            "date": call.get("date", ""),
        }

    def search_meeting_content(
        self, query: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Search meeting content. Stub returns empty list."""
        return []
