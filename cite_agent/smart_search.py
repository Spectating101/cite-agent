"""
Smart Search - Search across workspace objects for columns, values, patterns.

Enables quick discovery of data across multiple dataframes and objects.
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a search operation."""
    object_name: str
    column_name: Optional[str] = None
    match_type: str = ""  # "exact", "partial", "regex"
    context: str = ""
    object_type: str = ""
    dimensions: Optional[tuple] = None


class SmartSearch:
    """Smart search across workspace objects."""

    def __init__(self, workspace_manager):
        """
        Initialize smart search.

        Args:
            workspace_manager: MultiPlatformWorkspaceManager instance
        """
        self.workspace_manager = workspace_manager

    def find_columns(self, pattern: str, platform: Optional[str] = None,
                    exact_match: bool = False) -> List[SearchResult]:
        """
        Find columns matching a pattern across all dataframes.

        Args:
            pattern: Column name pattern to search for
            platform: Optional platform to search in
            exact_match: If True, only exact matches; else partial matches

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        pattern_lower = pattern.lower()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                for obj in workspace_info.objects:
                    # Check if object has columns (dataframe-like)
                    if hasattr(obj, 'columns') and obj.columns:
                        for col in obj.columns:
                            col_lower = col.lower()

                            # Check for match
                            if exact_match:
                                if col_lower == pattern_lower:
                                    results.append(SearchResult(
                                        object_name=obj.name,
                                        column_name=col,
                                        match_type="exact",
                                        context=f"Column in {obj.name}",
                                        object_type=obj.class_name,
                                        dimensions=obj.dimensions
                                    ))
                            else:
                                if pattern_lower in col_lower:
                                    results.append(SearchResult(
                                        object_name=obj.name,
                                        column_name=col,
                                        match_type="partial",
                                        context=f"Column in {obj.name}",
                                        object_type=obj.class_name,
                                        dimensions=obj.dimensions
                                    ))

            except Exception as e:
                logger.error(f"Error searching in {inspector.platform_name}: {e}")

        return results

    def find_dataframes_with_dates(self, year: Optional[int] = None,
                                  platform: Optional[str] = None) -> List[SearchResult]:
        """
        Find dataframes containing date/time columns.

        Args:
            year: Optional year to filter by
            platform: Optional platform to search in

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                for obj in workspace_info.objects:
                    if hasattr(obj, 'columns') and obj.columns:
                        # Look for date-like column names
                        date_columns = [
                            col for col in obj.columns
                            if any(keyword in col.lower() for keyword in
                                  ['date', 'time', 'year', 'month', 'day', 'timestamp'])
                        ]

                        if date_columns:
                            context = f"Date columns: {', '.join(date_columns)}"
                            results.append(SearchResult(
                                object_name=obj.name,
                                column_name=", ".join(date_columns),
                                match_type="temporal",
                                context=context,
                                object_type=obj.class_name,
                                dimensions=obj.dimensions
                            ))

            except Exception as e:
                logger.error(f"Error searching for dates in {inspector.platform_name}: {e}")

        return results

    def find_numeric_columns(self, platform: Optional[str] = None) -> List[SearchResult]:
        """
        Find all numeric columns across dataframes.

        Args:
            platform: Optional platform to search in

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                for obj in workspace_info.objects:
                    # Get detailed info if it's a dataframe
                    if hasattr(obj, 'columns') and obj.columns:
                        obj_info = inspector.get_object_info(obj.name)

                        if obj_info and obj_info.metadata and 'column_types' in obj_info.metadata:
                            numeric_cols = [
                                col for col, dtype in obj_info.metadata['column_types'].items()
                                if any(num_type in str(dtype).lower() for num_type in
                                      ['int', 'float', 'double', 'numeric', 'number'])
                            ]

                            if numeric_cols:
                                context = f"Numeric columns: {', '.join(numeric_cols)}"
                                results.append(SearchResult(
                                    object_name=obj.name,
                                    column_name=", ".join(numeric_cols),
                                    match_type="numeric",
                                    context=context,
                                    object_type=obj.class_name,
                                    dimensions=obj.dimensions
                                ))

            except Exception as e:
                logger.error(f"Error finding numeric columns in {inspector.platform_name}: {e}")

        return results

    def find_by_value(self, value: Any, platform: Optional[str] = None,
                     sample_size: int = 100) -> List[SearchResult]:
        """
        Find dataframes/objects containing a specific value.

        Args:
            value: Value to search for
            platform: Optional platform to search in
            sample_size: Number of rows to sample per dataframe

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        value_str = str(value).lower()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                for obj in workspace_info.objects:
                    # Get data sample
                    data = inspector.get_object_data(obj.name, limit=sample_size)

                    if data and data.get('type') == 'dataframe':
                        # Search in dataframe
                        df_data = data.get('data', [])
                        found_in_columns = set()

                        for row in df_data:
                            for col_name, col_value in row.items():
                                if value_str in str(col_value).lower():
                                    found_in_columns.add(col_name)

                        if found_in_columns:
                            context = f"Found in columns: {', '.join(found_in_columns)}"
                            results.append(SearchResult(
                                object_name=obj.name,
                                column_name=", ".join(found_in_columns),
                                match_type="value_match",
                                context=context,
                                object_type=obj.class_name
                            ))

                    elif data and data.get('type') in ['list', 'vector']:
                        # Search in list/vector
                        list_data = data.get('data', [])
                        if any(value_str in str(item).lower() for item in list_data):
                            results.append(SearchResult(
                                object_name=obj.name,
                                match_type="value_match",
                                context=f"Found in {obj.class_name}",
                                object_type=obj.class_name
                            ))

            except Exception as e:
                logger.error(f"Error searching by value in {inspector.platform_name}: {e}")

        return results

    def find_large_dataframes(self, min_rows: int = 1000,
                            platform: Optional[str] = None) -> List[SearchResult]:
        """
        Find large dataframes exceeding a minimum row count.

        Args:
            min_rows: Minimum number of rows
            platform: Optional platform to search in

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                for obj in workspace_info.objects:
                    if obj.dimensions and len(obj.dimensions) == 2:
                        rows, cols = obj.dimensions
                        if rows >= min_rows:
                            context = f"{rows:,} rows × {cols} columns"
                            results.append(SearchResult(
                                object_name=obj.name,
                                match_type="large_dataframe",
                                context=context,
                                object_type=obj.class_name,
                                dimensions=obj.dimensions
                            ))

            except Exception as e:
                logger.error(f"Error finding large dataframes in {inspector.platform_name}: {e}")

        return results

    def suggest_related_objects(self, object_name: str,
                               platform: Optional[str] = None) -> List[SearchResult]:
        """
        Suggest objects related to the given object (by name similarity, shared columns, etc.).

        Args:
            object_name: Name of object to find relations for
            platform: Optional platform to search in

        Returns:
            List of SearchResult objects
        """
        results = []

        # Get workspace inspector
        if platform:
            inspector = self.workspace_manager.get_inspector(platform)
            inspectors = [inspector] if inspector else []
        else:
            inspectors = self.workspace_manager.get_available_inspectors()

        object_name_lower = object_name.lower()

        for inspector in inspectors:
            try:
                workspace_info = inspector.describe_workspace()

                # Get target object info
                target_obj = inspector.get_object_info(object_name)
                if not target_obj:
                    continue

                target_columns = set(target_obj.columns or [])

                for obj in workspace_info.objects:
                    if obj.name == object_name:
                        continue  # Skip self

                    # Name similarity
                    name_similarity = self._string_similarity(object_name_lower, obj.name.lower())

                    if name_similarity > 0.5:  # Names are similar
                        results.append(SearchResult(
                            object_name=obj.name,
                            match_type="name_similarity",
                            context=f"Similar name ({name_similarity*100:.0f}% match)",
                            object_type=obj.class_name,
                            dimensions=obj.dimensions
                        ))

                    # Column overlap
                    if obj.columns:
                        obj_columns = set(obj.columns)
                        common_columns = target_columns.intersection(obj_columns)

                        if len(common_columns) > 0:
                            overlap_pct = len(common_columns) / max(len(target_columns), len(obj_columns)) * 100
                            results.append(SearchResult(
                                object_name=obj.name,
                                column_name=", ".join(list(common_columns)[:5]),
                                match_type="column_overlap",
                                context=f"Shares {len(common_columns)} columns ({overlap_pct:.0f}% overlap)",
                                object_type=obj.class_name,
                                dimensions=obj.dimensions
                            ))

            except Exception as e:
                logger.error(f"Error finding related objects in {inspector.platform_name}: {e}")

        return results

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity (Jaccard similarity on character bigrams)."""
        def bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))

        b1 = bigrams(s1)
        b2 = bigrams(s2)

        if not b1 and not b2:
            return 1.0 if s1 == s2 else 0.0

        if not b1 or not b2:
            return 0.0

        intersection = len(b1.intersection(b2))
        union = len(b1.union(b2))

        return intersection / union if union > 0 else 0.0
