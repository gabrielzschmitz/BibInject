from typing import Any, Dict, List, Optional
from .gen import Generator

# Local Imports
from .error_handler import ErrorHandler, OrderingError, GroupingError

# Initialize Error Handling
error_handler = ErrorHandler()


class GroupHTMLGenerator:
    """
    Generates grouped HTML blocks using the existing Generator class.
    Handles:
      - year grouping
      - year → month grouping
      - author grouping
      - default grouping
      - group headers <h2>
      - month headers <h3>
      - correct month ordering
    """

    MONTH_ORDER = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
        "Unknown",
    ]

    def __init__(self, style):
        self.style = style

    def _render_entry(self, entry):
        return Generator(entry, self.style).generate_html()

    def _sort_group_keys(self, keys, reverse):
        """
        Sort group keys (years, authors, etc.) cleanly.
        Numerical years sorted numerically, fallback: string compare.
        """

        def sort_key(k):
            try:
                return int(k)
            except Exception:
                return str(k).lower()

        return sorted(keys, key=sort_key, reverse=reverse)

    def _sort_months(self, months):
        return sorted(
            months,
            key=lambda m: self.MONTH_ORDER.index(m) if m in self.MONTH_ORDER else 999,
        )

    @error_handler.handle
    def order_entries(
        self,
        entries: Optional[List[Dict[str, Any]]] = None,
        reverse: bool = False,
        group: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Order entries:
        - if group == "author": alphanumeric by primary author's last name
        - else: by (year, month)
        reverse: True for DESC (Z->A or newest->oldest)
        """
        if entries is None:
            raise OrderingError()

        month_map = {
            "jan": 1,
            "january": 1,
            "feb": 2,
            "february": 2,
            "mar": 3,
            "march": 3,
            "apr": 4,
            "april": 4,
            "may": 5,
            "jun": 6,
            "june": 6,
            "jul": 7,
            "july": 7,
            "aug": 8,
            "august": 8,
            "sep": 9,
            "september": 9,
            "oct": 10,
            "october": 10,
            "nov": 11,
            "november": 11,
            "dec": 12,
            "december": 12,
        }

        def get_last_name(author_field: Any) -> str:
            if not author_field:
                return ""

            if isinstance(author_field, list):
                authors = author_field
            else:
                s = str(author_field).strip()
                s = (
                    s.replace(" AND ", " and ")
                    .replace(" And ", " and ")
                    .replace(" AND", " and ")
                    .replace("and", " and ")
                )
                authors = [a.strip() for a in s.split(" and ") if a.strip()]

            if not authors:
                return ""

            primary = authors[0]

            if "," in primary:
                last = primary.split(",", 1)[0]
            else:
                parts = primary.split()
                last = parts[-1] if parts else ""

            return last.lower().strip()

        def year_month_key(entry):
            fields = entry.get("fields", {})
            year_raw = fields.get("year", "")
            year = int(str(year_raw)) if str(year_raw).isdigit() else 0
            month_raw = str(fields.get("month", "")).strip().lower()
            month = month_map.get(month_raw, 0)
            return (year, month)

        def author_key(entry):
            fields = entry.get("fields", {})
            return get_last_name(fields.get("author", ""))

        if group == "author":
            return sorted(entries, key=author_key, reverse=reverse)
        # default: year/month
        return sorted(entries, key=year_month_key, reverse=reverse)

    @error_handler.handle
    def group_entries(
        self,
        entries: Optional[List[Dict[str, Any]]] = None,
        by: str = "year",
        reverse: bool = True,
    ) -> Dict[str, Any]:

        if entries is None:
            raise GroupingError()

        month_names = self.MONTH_ORDER[:-1]

        is_year_month_group = by in ("year/month", "ym", "month")

        # ---- AUTHOR GROUPING -----------------------------------------
        if by == "author":
            grouped_authors: Dict[str, List[Dict[str, Any]]] = {}

            for entry in entries:
                fields = entry.get("fields", {})
                authors = fields.get("author", [])

                if isinstance(authors, str):
                    if " and " in authors.lower():
                        authors = [a.strip() for a in authors.split(" and ")]
                    else:
                        authors = [authors]

                for author in authors:
                    grouped_authors.setdefault(author, []).append(entry)

            return grouped_authors

        # ---- YEAR/MONTH OR YEAR GROUPING -----------------------------
        if is_year_month_group:
            grouped_nested: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        else:
            grouped_flat: Dict[str, List[Dict[str, Any]]] = {}

        for entry in entries:
            fields = entry.get("fields", {})
            year = fields.get("year", "Unknown")

            # Month parsing
            month_val = str(fields.get("month", "")).strip().lower()
            month = None
            if month_val:
                if month_val.isdigit():
                    idx = int(month_val)
                    if 1 <= idx <= 12:
                        month = month_names[idx - 1]
                else:
                    for name in month_names:
                        if name.lower().startswith(month_val[:3]):
                            month = name
                            break

            # YEAR/MONTH grouping
            if is_year_month_group:
                year_bucket = grouped_nested.setdefault(year, {})
                month_key = month or "Unknown"
                year_bucket.setdefault(month_key, []).append(entry)

            # YEAR-ONLY grouping
            else:
                grouped_flat.setdefault(year, []).append(entry)

        # Return correct shape
        return grouped_nested if is_year_month_group else grouped_flat

    def render_groups(self, grouped_entries, reverse=False):
        """
        Accepts the output of parser.group_entries() and returns clean HTML.
        """
        blocks = []
        group_keys = self._sort_group_keys(list(grouped_entries.keys()), reverse)

        for group_name in group_keys:
            group_items = grouped_entries[group_name]
            html_parts = []

            if isinstance(group_items, dict):
                months = self._sort_months(list(group_items.keys()))
                for month in months:
                    html_parts.append(f"<h3>{month}</h3>")
                    for entry in group_items[month]:
                        html_parts.append(self._render_entry(entry))

            else:
                for entry in group_items:
                    html_parts.append(self._render_entry(entry))

            block = f"<h2>{group_name}</h2>\n" + "\n\n".join(html_parts)
            blocks.append(block)

        return "\n\n".join(blocks)
