"""Content generation for weekly updates."""
import re
from typing import List, Dict, Any, Set
from datetime import datetime
from jira_aggregator import JiraAggregator
from glean_aggregator import GleanAggregator
from pendo_aggregator import PendoAggregator
from granola_aggregator import GranolaAggregator
from tone_analyzer import ToneAnalyzer
from svp_filter import SVPFilter
import config

class ContentGenerator:
    """Generates content for weekly update documents."""
    
    def __init__(self):
        """Initialize the content generator."""
        self.jira = JiraAggregator()
        self.glean = GleanAggregator()
        self.pendo = PendoAggregator()
        self.granola = GranolaAggregator()
        self.tone_analyzer = ToneAnalyzer()
        self.svp_filter = SVPFilter()
        self.added_content_hashes: Set[str] = set()
    
    def generate_highlights(self, existing_content: str = "") -> str:
        """Generate Highlights section."""
        highlights = []
        
        # Get SVP-relevant items from Jira
        jira_issues = self.jira.get_issues_updated_this_week()
        svp_relevant = self.svp_filter.filter_for_highlights(jira_issues, "jira")
        
        # Get completed items (accomplishments)
        completed = self.jira.get_completed_items()
        for item in completed[:3]:  # Top 3 accomplishments
            summary = self.jira.format_issue_summary(item)
            highlights.append(f"* {summary}")
        
        # Get blockers
        blockers = self.jira.get_blockers()
        for blocker in blockers[:2]:  # Top 2 blockers
            summary = self.jira.format_issue_summary(blocker)
            highlights.append(f"* Blocker: {summary}")
        
        # Get key project milestones from Glean
        project_insights = self.glean.get_project_insights()
        for insight in project_insights[:2]:  # Top 2 insights
            title = insight.get("title", "")
            if title:
                highlights.append(f"* {title}")
        
        # Limit to max highlights
        highlights = highlights[:config.Config.MAX_HIGHLIGHTS]
        
        # Apply tone
        content = "\n".join(highlights)
        content = self.tone_analyzer.apply_tone(content, "highlights")
        
        return content
    
    def generate_this_week(self, existing_content: str = "") -> str:
        """Generate This Week section."""
        sections = []
        
        # Get initiatives from Jira
        initiatives = self.jira.get_initiatives()
        if initiatives:
            sections.append("* Team roadmap")
            for initiative in initiatives[:5]:  # Top 5 initiatives
                key = initiative.get("key", "")
                summary = initiative.get("fields", {}).get("summary", "")
                status = initiative.get("fields", {}).get("status", {}).get("name", "")
                
                sections.append(f"    * **{summary}** ({key}) - {status}")
        
        # Get project updates from Glean
        project_insights = self.glean.get_project_insights()
        if project_insights:
            sections.append("* Project Updates")
            for insight in project_insights[:5]:
                title = insight.get("title", "")
                snippet = insight.get("snippet", "")
                if title:
                    sections.append(f"    * {title}")
                    if snippet:
                        sections.append(f"        * {snippet[:200]}...")
        
        # Get in-progress items
        in_progress = self.jira.get_in_progress_items()
        if in_progress:
            sections.append("* Active Work")
            for item in in_progress[:5]:
                summary = self.jira.format_issue_summary(item)
                sections.append(f"    * {summary}")
        
        content = "\n".join(sections)
        content = self.tone_analyzer.apply_tone(content, "this_week")
        
        return content
    
    def generate_next_week(self, existing_content: str = "") -> str:
        """Generate Next Week section."""
        items = []
        
        # Get in-progress items that need follow-up
        in_progress = self.jira.get_in_progress_items()
        for item in in_progress[:5]:
            summary = self.jira.format_issue_summary(item)
            items.append(f"* Continue work on {summary}")
        
        # Get high-priority items assigned
        jira_issues = self.jira.get_issues_updated_this_week()
        high_priority = [i for i in jira_issues if self.svp_filter.is_svp_relevant(i, "jira")]
        for item in high_priority[:3]:
            summary = self.jira.format_issue_summary(item)
            items.append(f"* {summary}")
        
        # Get planned next steps from project documents
        project_insights = self.glean.get_project_insights()
        for insight in project_insights[:3]:
            title = insight.get("title", "")
            if "next" in title.lower() or "plan" in title.lower():
                items.append(f"* {title}")
        
        content = "\n".join(items)
        content = self.tone_analyzer.apply_tone(content, "next_week")
        
        return content
    
    def generate_customer_corner(self, existing_content: str = "") -> str:
        """Generate Customer Corner section."""
        items = []
        
        # Try Granola first (more reliable for meeting data)
        try:
            customer_calls = self.granola.get_customer_calls()
            for call in customer_calls:
                formatted = self.granola.format_customer_call(call)
                customer_name = formatted.get("customer_name", "Customer")
                title = formatted.get("title", "")
                url = formatted.get("url", "")
                date = formatted.get("date", "")
                
                if url:
                    items.append(f"{customer_name} - {title}\n\n{url}")
                elif title:
                    items.append(f"{customer_name} - {title}")
        except Exception as e:
            # Fallback to Glean if Granola fails
            try:
                customer_calls = self.glean.get_customer_calls()
                for call in customer_calls:
                    formatted = self.glean.format_customer_call(call)
                    customer_name = formatted.get("customer_name", "Customer")
                    url = formatted.get("url", "")
                    
                    if url:
                        items.append(f"{customer_name} - Customer Call\n\n{url}")
                    else:
                        items.append(f"{customer_name} - Customer Call")
            except:
                pass
        
        if not items:
            return "No customer calls this week."
        
        return "\n\n".join(items)
    
    def generate_full_content(self, existing_content: str = "") -> str:
        """Generate full weekly update content."""
        sections = []
        
        # Highlights
        highlights = self.generate_highlights(existing_content)
        if highlights:
            sections.append("## Highlights\n\n" + highlights)
        
        # This Week
        this_week = self.generate_this_week(existing_content)
        if this_week:
            sections.append("\n## This Week\n\n" + this_week)
        
        # Next Week
        next_week = self.generate_next_week(existing_content)
        if next_week:
            sections.append("\n## Next Week\n\n" + next_week)
        
        # Customer Corner
        customer_corner = self.generate_customer_corner(existing_content)
        if customer_corner:
            sections.append("\n## Customer Corner\n\n" + customer_corner)
        
        return "\n".join(sections)
    
    @staticmethod
    def compile_and_dedupe_sections(raw_content: str) -> str:
        """
        Parse page content that may have repeated sections (from daily appends)
        and return a single cohesive document with one section each, no duplicates.
        """
        section_order = ["Highlights", "This Week", "Next Week", "Customer Corner"]
        # Split by ## and keep header + body (handle optional leading newline)
        parts = re.split(r"\n## ", raw_content.strip())
        sections: Dict[str, List[str]] = {name: [] for name in section_order}
        seen: Dict[str, Set[str]] = {name: set() for name in section_order}

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            lines = part.split("\n")
            header = lines[0].strip()
            if header.startswith("## "):
                header = header[3:].strip()
            # First part might be leading text with no section header
            if i == 0 and not re.match(r"^Highlights|^This Week|^Next Week|^Customer Corner", header, re.I):
                continue
            # Normalize header to match section_order (e.g. "Highlights" or "highlights" -> "Highlights")
            section_name = None
            for name in section_order:
                if header.lower() == name.lower():
                    section_name = name
                    break
            if section_name is None:
                continue
            body_lines = lines[1:]
            for line in body_lines:
                line = line.strip()
                if not line:
                    continue
                # Normalize for dedupe: lowercase, collapse whitespace
                key = re.sub(r"\s+", " ", line.lower()).strip()
                if key and key not in seen[section_name]:
                    seen[section_name].add(key)
                    sections[section_name].append(line)

        out = []
        for name in section_order:
            if sections[name]:
                out.append("## " + name + "\n\n" + "\n".join(sections[name]))
        return "\n\n".join(out) if out else raw_content.strip()

    def append_to_section(self, section_content: str, new_items: List[str]) -> str:
        """Append new items to an existing section without duplicates."""
        # Simple deduplication by checking if item already exists
        existing_lines = set(section_content.split("\n"))
        new_content = section_content
        
        for item in new_items:
            # Check if similar content already exists
            item_hash = hash(item.lower().strip())
            if item_hash not in self.added_content_hashes:
                new_content += "\n" + item
                self.added_content_hashes.add(item_hash)
        
        return new_content
    
    def _hash_content(self, content: str) -> str:
        """Generate a hash for content deduplication."""
        import hashlib
        return hashlib.md5(content.lower().strip().encode()).hexdigest()
