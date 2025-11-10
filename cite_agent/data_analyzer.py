"""
Data Analyzer - Statistical summaries and auto-description for datasets.

Provides comprehensive statistical analysis, descriptive statistics, and
auto-generates text for methods sections.

RESOURCE OPTIMIZATION:
All operations respect memory limits defined in workspace_inspector for 8GB RAM environments.
Large datasets are automatically sampled before analysis.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import statistics

# Import resource limits from workspace_inspector
try:
    from .workspace_inspector import (
        MAX_ROWS_DEFAULT,
        MAX_ROWS_ANALYSIS,
        LARGE_DATASET_THRESHOLD,
        MAX_OBJECT_SIZE_MB
    )
except ImportError:
    # Fallback if workspace_inspector not available
    MAX_ROWS_DEFAULT = 1000
    MAX_ROWS_ANALYSIS = 10000
    LARGE_DATASET_THRESHOLD = 50000
    MAX_OBJECT_SIZE_MB = 100

logger = logging.getLogger(__name__)


@dataclass
class ColumnStatistics:
    """Statistics for a single column."""
    name: str
    dtype: str  # "numeric", "categorical", "temporal", "boolean", "other"
    count: int
    missing: int
    missing_pct: float

    # Numeric stats
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None

    # Categorical stats
    unique_count: Optional[int] = None
    top_value: Optional[str] = None
    top_count: Optional[int] = None
    value_counts: Optional[Dict[str, int]] = None

    # Temporal stats
    earliest: Optional[str] = None
    latest: Optional[str] = None
    time_span: Optional[str] = None

    # Data quality flags
    has_outliers: bool = False
    outlier_count: int = 0
    outlier_indices: List[int] = field(default_factory=list)


@dataclass
class DataQualityIssue:
    """Represents a data quality issue."""
    severity: str  # "critical", "warning", "info"
    category: str  # "missing", "outlier", "inconsistent", "invalid", "duplicate"
    column: Optional[str] = None
    description: str = ""
    affected_rows: List[int] = field(default_factory=list)
    suggestion: str = ""
    citation: Optional[str] = None


@dataclass
class DataSummary:
    """Complete summary of a dataset."""
    name: str
    shape: tuple  # (rows, cols)
    total_size_mb: float
    column_stats: List[ColumnStatistics]
    quality_issues: List[DataQualityIssue]
    numeric_columns: List[str]
    categorical_columns: List[str]
    temporal_columns: List[str]
    methods_section_text: str = ""
    descriptive_stats_table: str = ""


class DataAnalyzer:
    """Analyzes datasets and generates statistical summaries."""

    def __init__(self):
        self.outlier_threshold_sd = 3.0  # Standard deviations for outlier detection

    def analyze_dataframe(self, data: Any, name: str = "dataset", sample_if_large: bool = True) -> DataSummary:
        """
        Analyze a dataframe-like object and return comprehensive summary.

        Supports:
        - pandas DataFrames
        - List of dicts (from workspace inspector)
        - R data.frames (via workspace inspector)

        Args:
            data: Data to analyze
            name: Name of dataset
            sample_if_large: If True, automatically sample large datasets for 8GB RAM efficiency

        Returns:
            DataSummary with statistics and quality checks
        """
        try:
            # Detect data type and convert to standard format
            data_dict, shape = self._normalize_data(data)

            if data_dict is None:
                raise ValueError(f"Could not analyze data type: {type(data)}")

            # RESOURCE OPTIMIZATION: Sample large datasets for 8GB RAM
            was_sampled = False
            original_shape = shape
            if sample_if_large and shape[0] > LARGE_DATASET_THRESHOLD:
                logger.info(
                    f"Dataset has {shape[0]:,} rows. Sampling {MAX_ROWS_ANALYSIS:,} rows "
                    f"for analysis (8GB RAM optimization)"
                )
                data_dict, shape = self._sample_data(data_dict, MAX_ROWS_ANALYSIS)
                was_sampled = True

            # Analyze each column
            column_stats = []
            for col_name, col_data in data_dict.items():
                stats = self._analyze_column(col_name, col_data)
                column_stats.append(stats)

            # Categorize columns by type
            numeric_cols = [s.name for s in column_stats if s.dtype == "numeric"]
            categorical_cols = [s.name for s in column_stats if s.dtype == "categorical"]
            temporal_cols = [s.name for s in column_stats if s.dtype == "temporal"]

            # Detect quality issues
            quality_issues = self._detect_quality_issues(column_stats, data_dict, shape)

            # Generate descriptive text
            methods_text = self._generate_methods_section(
                name, shape, column_stats, numeric_cols, categorical_cols, temporal_cols
            )

            # Generate stats table
            stats_table = self._generate_stats_table(column_stats)

            # Calculate total size
            total_size_mb = self._estimate_size_mb(data_dict, shape)

            return DataSummary(
                name=name,
                shape=shape,
                total_size_mb=total_size_mb,
                column_stats=column_stats,
                quality_issues=quality_issues,
                numeric_columns=numeric_cols,
                categorical_columns=categorical_cols,
                temporal_columns=temporal_cols,
                methods_section_text=methods_text,
                descriptive_stats_table=stats_table
            )

        except Exception as e:
            logger.error(f"Error analyzing dataframe: {e}")
            raise

    def _normalize_data(self, data: Any) -> tuple:
        """Convert various data types to dict of columns."""
        try:
            # pandas DataFrame
            if hasattr(data, 'to_dict') and hasattr(data, 'shape'):
                data_dict = data.to_dict('list')
                shape = data.shape
                return data_dict, shape

            # List of dicts (from workspace inspector)
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Convert list of dicts to dict of lists
                data_dict = {}
                for key in data[0].keys():
                    data_dict[key] = [row.get(key) for row in data]
                shape = (len(data), len(data_dict))
                return data_dict, shape

            # Dict of lists (already normalized)
            elif isinstance(data, dict):
                # Verify all values are lists
                if all(isinstance(v, list) for v in data.values()):
                    lengths = [len(v) for v in data.values()]
                    if len(set(lengths)) == 1:  # All same length
                        shape = (lengths[0], len(data))
                        return data, shape

            return None, (0, 0)

        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            return None, (0, 0)

    def _sample_data(self, data_dict: Dict[str, List[Any]], sample_size: int) -> tuple:
        """
        Sample data for memory efficiency on 8GB RAM systems.

        Args:
            data_dict: Dict of column_name -> list of values
            sample_size: Number of rows to sample

        Returns:
            (sampled_data_dict, new_shape)
        """
        try:
            import random

            # Get original row count
            row_count = len(next(iter(data_dict.values())))

            if row_count <= sample_size:
                return data_dict, (row_count, len(data_dict))

            # Generate random indices
            indices = sorted(random.sample(range(row_count), sample_size))

            # Sample each column
            sampled_dict = {}
            for col_name, col_data in data_dict.items():
                sampled_dict[col_name] = [col_data[i] for i in indices]

            new_shape = (sample_size, len(data_dict))
            logger.info(f"Sampled {sample_size:,} rows from {row_count:,} (memory optimization)")

            return sampled_dict, new_shape

        except Exception as e:
            logger.error(f"Error sampling data: {e}")
            # Fall back to original data
            return data_dict, (len(next(iter(data_dict.values()))), len(data_dict))

    def _analyze_column(self, col_name: str, col_data: List[Any]) -> ColumnStatistics:
        """Analyze a single column and return statistics."""
        # Filter out None/null values
        valid_data = [x for x in col_data if x is not None and str(x).lower() != 'nan']
        total_count = len(col_data)
        missing = total_count - len(valid_data)
        missing_pct = (missing / total_count * 100) if total_count > 0 else 0

        # Determine data type
        dtype = self._detect_column_type(valid_data)

        # Initialize stats
        stats = ColumnStatistics(
            name=col_name,
            dtype=dtype,
            count=len(valid_data),
            missing=missing,
            missing_pct=missing_pct
        )

        # Compute type-specific statistics
        if dtype == "numeric" and len(valid_data) > 0:
            self._compute_numeric_stats(stats, valid_data)
        elif dtype == "categorical" and len(valid_data) > 0:
            self._compute_categorical_stats(stats, valid_data)
        elif dtype == "temporal" and len(valid_data) > 0:
            self._compute_temporal_stats(stats, valid_data)

        return stats

    def _detect_column_type(self, data: List[Any]) -> str:
        """Detect the type of a column."""
        if len(data) == 0:
            return "other"

        # Sample first few non-null values
        sample = data[:min(100, len(data))]

        # Check for numeric
        numeric_count = 0
        for val in sample:
            try:
                float(val)
                numeric_count += 1
            except (ValueError, TypeError):
                pass

        if numeric_count / len(sample) > 0.9:  # 90% numeric
            return "numeric"

        # Check for temporal (common date patterns)
        temporal_indicators = ['date', 'time', 'year', 'month', 'day', 'timestamp']

        # Check for boolean
        unique_vals = set(str(v).lower() for v in sample)
        if unique_vals.issubset({'true', 'false', '0', '1', 't', 'f', 'yes', 'no'}):
            return "boolean"

        # Check unique ratio for categorical
        unique_ratio = len(set(str(v) for v in data)) / len(data)
        if unique_ratio < 0.5:  # Less than 50% unique -> probably categorical
            return "categorical"

        return "other"

    def _compute_numeric_stats(self, stats: ColumnStatistics, data: List[Any]):
        """Compute statistics for numeric column."""
        try:
            numeric_data = [float(x) for x in data]

            stats.mean = statistics.mean(numeric_data)
            stats.median = statistics.median(numeric_data)
            stats.std = statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0.0
            stats.min = min(numeric_data)
            stats.max = max(numeric_data)

            # Quartiles
            sorted_data = sorted(numeric_data)
            n = len(sorted_data)
            stats.q25 = sorted_data[n // 4] if n > 0 else None
            stats.q75 = sorted_data[3 * n // 4] if n > 0 else None

            # Outlier detection (values > 3 SD from mean)
            if stats.std and stats.std > 0:
                outliers = []
                for i, val in enumerate(numeric_data):
                    if abs(val - stats.mean) > self.outlier_threshold_sd * stats.std:
                        outliers.append(i)

                stats.has_outliers = len(outliers) > 0
                stats.outlier_count = len(outliers)
                stats.outlier_indices = outliers[:10]  # Keep first 10

        except Exception as e:
            logger.error(f"Error computing numeric stats: {e}")

    def _compute_categorical_stats(self, stats: ColumnStatistics, data: List[Any]):
        """Compute statistics for categorical column."""
        try:
            # Convert to strings
            str_data = [str(x) for x in data]

            # Count unique values
            value_counts = {}
            for val in str_data:
                value_counts[val] = value_counts.get(val, 0) + 1

            stats.unique_count = len(value_counts)
            stats.value_counts = dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10])

            # Most common value
            if value_counts:
                top = max(value_counts.items(), key=lambda x: x[1])
                stats.top_value = top[0]
                stats.top_count = top[1]

        except Exception as e:
            logger.error(f"Error computing categorical stats: {e}")

    def _compute_temporal_stats(self, stats: ColumnStatistics, data: List[Any]):
        """Compute statistics for temporal column."""
        try:
            # Try to parse dates (simplified - would need more robust parsing)
            dates = []
            for val in data:
                try:
                    # Handle various date formats
                    val_str = str(val)
                    # This is simplified - real implementation would use dateutil.parser
                    dates.append(val_str)
                except:
                    pass

            if dates:
                sorted_dates = sorted(dates)
                stats.earliest = sorted_dates[0]
                stats.latest = sorted_dates[-1]
                stats.time_span = f"{stats.earliest} to {stats.latest}"

        except Exception as e:
            logger.error(f"Error computing temporal stats: {e}")

    def _detect_quality_issues(self, column_stats: List[ColumnStatistics],
                               data_dict: Dict[str, List], shape: tuple) -> List[DataQualityIssue]:
        """Detect data quality issues."""
        issues = []

        for stats in column_stats:
            # Missing values
            if stats.missing > 0:
                severity = "critical" if stats.missing_pct > 20 else "warning"
                issues.append(DataQualityIssue(
                    severity=severity,
                    category="missing",
                    column=stats.name,
                    description=f"{stats.missing} missing values ({stats.missing_pct:.1f}%)",
                    suggestion="Consider mean imputation, forward fill, or removal: na.omit() or fillna()",
                    citation="Little, R. J., & Rubin, D. B. (2019). Statistical Analysis with Missing Data"
                ))

            # Outliers
            if stats.has_outliers:
                issues.append(DataQualityIssue(
                    severity="warning",
                    category="outlier",
                    column=stats.name,
                    description=f"{stats.outlier_count} potential outliers detected (>3 SD from mean)",
                    affected_rows=stats.outlier_indices,
                    suggestion="Investigate outliers - may be data errors or valid extreme values",
                    citation="Rousseeuw, P. J., & Hubert, M. (2011). Robust statistics for outlier detection"
                ))

            # Low variance (constant or near-constant columns)
            if stats.dtype == "numeric" and stats.std is not None and stats.std < 0.01:
                issues.append(DataQualityIssue(
                    severity="info",
                    category="inconsistent",
                    column=stats.name,
                    description=f"Very low variance (SD={stats.std:.4f}) - column may be constant",
                    suggestion="Consider removing constant columns from analysis"
                ))

            # Categorical with too many unique values
            if stats.dtype == "categorical" and stats.unique_count:
                if stats.unique_count > shape[0] * 0.9:  # >90% unique
                    issues.append(DataQualityIssue(
                        severity="info",
                        category="inconsistent",
                        column=stats.name,
                        description=f"High cardinality: {stats.unique_count} unique values",
                        suggestion="May need to be treated as identifier rather than categorical variable"
                    ))

        # Check for duplicate rows (sample first 1000 rows)
        if shape[0] <= 1000:
            rows_to_check = shape[0]
        else:
            rows_to_check = 1000

        # Convert to tuples for duplicate detection
        rows_as_tuples = []
        for i in range(rows_to_check):
            row = tuple(data_dict[col][i] if i < len(data_dict[col]) else None for col in data_dict.keys())
            rows_as_tuples.append(row)

        duplicates = len(rows_as_tuples) - len(set(rows_as_tuples))
        if duplicates > 0:
            issues.append(DataQualityIssue(
                severity="warning",
                category="duplicate",
                description=f"Found {duplicates} duplicate rows (checked first {rows_to_check} rows)",
                suggestion="Remove duplicates: df <- df[!duplicated(df), ] or df.drop_duplicates()"
            ))

        return issues

    def _generate_methods_section(self, name: str, shape: tuple,
                                  column_stats: List[ColumnStatistics],
                                  numeric_cols: List[str],
                                  categorical_cols: List[str],
                                  temporal_cols: List[str]) -> str:
        """Generate methods section text."""
        lines = []

        # Overview
        lines.append(f"The {name} dataset comprises {shape[0]} observations across {shape[1]} variables.")

        # Numeric variables
        if numeric_cols:
            lines.append(f"\nNumeric variables ({len(numeric_cols)}):")
            for col in numeric_cols[:5]:  # Limit to first 5
                stats = next((s for s in column_stats if s.name == col), None)
                if stats and stats.mean is not None:
                    lines.append(
                        f"  - {col}: M={stats.mean:.2f}, SD={stats.std:.2f}, "
                        f"Range=[{stats.min:.2f}, {stats.max:.2f}]"
                    )

        # Categorical variables
        if categorical_cols:
            lines.append(f"\nCategorical variables ({len(categorical_cols)}):")
            for col in categorical_cols[:5]:
                stats = next((s for s in column_stats if s.name == col), None)
                if stats and stats.unique_count:
                    lines.append(f"  - {col}: {stats.unique_count} categories")

        # Missing data
        missing_cols = [s for s in column_stats if s.missing > 0]
        if missing_cols:
            lines.append(f"\nMissing data was observed in {len(missing_cols)} variable(s):")
            for stats in missing_cols[:3]:
                lines.append(f"  - {stats.name}: {stats.missing} missing ({stats.missing_pct:.1f}%)")

        return "\n".join(lines)

    def _generate_stats_table(self, column_stats: List[ColumnStatistics]) -> str:
        """Generate formatted statistics table."""
        lines = []
        lines.append("=" * 80)
        lines.append("DESCRIPTIVE STATISTICS")
        lines.append("=" * 80)

        # Numeric columns
        numeric_stats = [s for s in column_stats if s.dtype == "numeric"]
        if numeric_stats:
            lines.append("\nNumeric Variables:")
            lines.append("-" * 80)
            lines.append(f"{'Variable':<20} {'Mean':>10} {'SD':>10} {'Min':>10} {'Max':>10} {'Missing':>10}")
            lines.append("-" * 80)
            for s in numeric_stats:
                lines.append(
                    f"{s.name:<20} "
                    f"{s.mean:>10.2f} "
                    f"{s.std:>10.2f} "
                    f"{s.min:>10.2f} "
                    f"{s.max:>10.2f} "
                    f"{s.missing:>10}"
                )

        # Categorical columns
        cat_stats = [s for s in column_stats if s.dtype == "categorical"]
        if cat_stats:
            lines.append("\nCategorical Variables:")
            lines.append("-" * 80)
            lines.append(f"{'Variable':<20} {'Unique':>10} {'Top Value':<20} {'Freq':>10} {'Missing':>10}")
            lines.append("-" * 80)
            for s in cat_stats:
                top_val = (s.top_value[:17] + "...") if s.top_value and len(s.top_value) > 20 else (s.top_value or "N/A")
                lines.append(
                    f"{s.name:<20} "
                    f"{s.unique_count or 0:>10} "
                    f"{top_val:<20} "
                    f"{s.top_count or 0:>10} "
                    f"{s.missing:>10}"
                )

        lines.append("=" * 80)
        return "\n".join(lines)

    def _estimate_size_mb(self, data_dict: Dict[str, List], shape: tuple) -> float:
        """Estimate dataset size in MB."""
        try:
            import sys
            total_bytes = 0
            for col_data in data_dict.values():
                for val in col_data[:100]:  # Sample first 100
                    total_bytes += sys.getsizeof(val)

            # Extrapolate to full dataset
            avg_bytes_per_cell = total_bytes / (len(data_dict) * min(100, shape[0]))
            total_bytes_est = avg_bytes_per_cell * shape[0] * shape[1]
            return total_bytes_est / (1024 * 1024)
        except:
            return 0.0
