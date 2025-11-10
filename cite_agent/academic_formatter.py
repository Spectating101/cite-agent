"""
Academic Formatter - Convert analysis results to publication-ready text.

Formats statistical results in APA, MLA, or custom academic styles.
Generates tables, figures descriptions, and results sections.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class StatisticalResult:
    """Container for statistical test results."""
    test_name: str
    statistic: float
    statistic_name: str  # "t", "F", "χ²", "r", etc.
    df: Optional[Union[int, tuple]] = None  # degrees of freedom
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    effect_size_name: Optional[str] = None  # "Cohen's d", "η²", "R²", etc.
    confidence_interval: Optional[tuple] = None
    sample_size: Optional[int] = None
    additional_stats: Dict[str, Any] = None


class AcademicFormatter:
    """Formats statistical results for academic writing."""

    def __init__(self, style: str = "apa"):
        """
        Initialize formatter.

        Args:
            style: Citation/formatting style ("apa", "mla", "chicago")
        """
        self.style = style.lower()

    def format_ttest_result(self, result: Dict[str, Any]) -> str:
        """
        Format t-test result in APA style.

        Args:
            result: Dict with keys: t, df, p, mean1, mean2, sd1, sd2, n1, n2

        Returns:
            APA formatted string
        """
        try:
            t = result.get('t', 0)
            df = result.get('df', 0)
            p = result.get('p', 0)
            mean1 = result.get('mean1', 0)
            mean2 = result.get('mean2', 0)

            # Calculate Cohen's d if means and SDs provided
            cohens_d = None
            if 'sd1' in result and 'sd2' in result:
                sd_pooled = ((result['sd1']**2 + result['sd2']**2) / 2) ** 0.5
                if sd_pooled > 0:
                    cohens_d = abs(mean1 - mean2) / sd_pooled

            # Format p-value
            p_str = self._format_p_value(p)

            # Build result string
            if cohens_d:
                return (
                    f"An independent-samples t-test revealed a significant difference between "
                    f"groups, t({df}) = {t:.2f}, {p_str}, Cohen's d = {cohens_d:.2f}."
                )
            else:
                return f"t({df}) = {t:.2f}, {p_str}"

        except Exception as e:
            logger.error(f"Error formatting t-test result: {e}")
            return str(result)

    def format_anova_result(self, result: Dict[str, Any]) -> str:
        """
        Format ANOVA result in APA style.

        Args:
            result: Dict with F, df1, df2, p, eta_squared (optional), MSE

        Returns:
            APA formatted string
        """
        try:
            F = result.get('F', 0)
            df1 = result.get('df1', 0)
            df2 = result.get('df2', 0)
            p = result.get('p', 0)
            eta_sq = result.get('eta_squared')

            p_str = self._format_p_value(p)

            if eta_sq:
                return (
                    f"A one-way analysis of variance (ANOVA) revealed a significant effect, "
                    f"F({df1}, {df2}) = {F:.2f}, {p_str}, η² = {eta_sq:.3f}."
                )
            else:
                return f"F({df1}, {df2}) = {F:.2f}, {p_str}"

        except Exception as e:
            logger.error(f"Error formatting ANOVA result: {e}")
            return str(result)

    def format_regression_result(self, result: Dict[str, Any]) -> str:
        """
        Format regression result in APA style.

        Args:
            result: Dict with R2, F, df1, df2, p, coefficients, etc.

        Returns:
            APA formatted results section
        """
        try:
            R2 = result.get('R2', 0)
            F = result.get('F', 0)
            df1 = result.get('df1', 0)
            df2 = result.get('df2', 0)
            p = result.get('p', 0)
            coefficients = result.get('coefficients', [])

            p_str = self._format_p_value(p)

            # Overall model
            lines = []
            lines.append(
                f"A linear regression was conducted to predict the dependent variable. "
                f"The overall model was significant, F({df1}, {df2}) = {F:.2f}, {p_str}, "
                f"R² = {R2:.3f}, indicating that the predictors explained "
                f"{R2*100:.1f}% of the variance."
            )

            # Individual predictors
            if coefficients:
                lines.append("\nSignificant predictors included:")
                for coef in coefficients:
                    if coef.get('p', 1) < 0.05:
                        name = coef.get('name', 'predictor')
                        b = coef.get('b', 0)
                        se = coef.get('se', 0)
                        t = coef.get('t', 0)
                        p_coef = coef.get('p', 0)
                        beta = coef.get('beta')

                        p_coef_str = self._format_p_value(p_coef)
                        beta_str = f", β = {beta:.2f}" if beta else ""

                        lines.append(
                            f"  - {name} (b = {b:.2f}, SE = {se:.2f}, "
                            f"t = {t:.2f}, {p_coef_str}{beta_str})"
                        )

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting regression result: {e}")
            return str(result)

    def format_correlation_result(self, result: Dict[str, Any]) -> str:
        """Format correlation result in APA style."""
        try:
            r = result.get('r', 0)
            n = result.get('n', 0)
            p = result.get('p', 0)
            method = result.get('method', 'Pearson')

            p_str = self._format_p_value(p)

            return (
                f"A {method} correlation analysis revealed a "
                f"{'significant' if p < 0.05 else 'non-significant'} "
                f"{'positive' if r > 0 else 'negative'} relationship, "
                f"r({n-2}) = {r:.2f}, {p_str}."
            )

        except Exception as e:
            logger.error(f"Error formatting correlation result: {e}")
            return str(result)

    def format_chi_square_result(self, result: Dict[str, Any]) -> str:
        """Format chi-square result in APA style."""
        try:
            chi2 = result.get('chi2', 0)
            df = result.get('df', 0)
            p = result.get('p', 0)
            n = result.get('n', 0)

            p_str = self._format_p_value(p)

            return (
                f"A chi-square test of independence revealed a "
                f"{'significant' if p < 0.05 else 'non-significant'} association, "
                f"χ²({df}, N = {n}) = {chi2:.2f}, {p_str}."
            )

        except Exception as e:
            logger.error(f"Error formatting chi-square result: {e}")
            return str(result)

    def generate_descriptive_table(self, data_summary: Any,
                                   format: str = "apa") -> str:
        """
        Generate formatted descriptive statistics table.

        Args:
            data_summary: DataSummary object from DataAnalyzer
            format: Table format ("apa", "markdown", "latex")

        Returns:
            Formatted table string
        """
        if format == "markdown":
            return self._generate_markdown_table(data_summary)
        elif format == "latex":
            return self._generate_latex_table(data_summary)
        else:  # apa (text)
            return self._generate_apa_table(data_summary)

    def _generate_apa_table(self, data_summary: Any) -> str:
        """Generate APA-style text table."""
        lines = []
        lines.append(f"Table 1")
        lines.append(f"Descriptive Statistics for {data_summary.name}")
        lines.append("-" * 70)
        lines.append(f"{'Variable':<20} {'M':>10} {'SD':>10} {'Min':>10} {'Max':>10}")
        lines.append("-" * 70)

        for stat in data_summary.column_stats:
            if stat.dtype == "numeric":
                lines.append(
                    f"{stat.name:<20} "
                    f"{stat.mean:>10.2f} "
                    f"{stat.std:>10.2f} "
                    f"{stat.min:>10.2f} "
                    f"{stat.max:>10.2f}"
                )

        lines.append("-" * 70)
        lines.append(f"Note. N = {data_summary.shape[0]}. M = Mean, SD = Standard Deviation.")

        return "\n".join(lines)

    def _generate_markdown_table(self, data_summary: Any) -> str:
        """Generate Markdown table."""
        lines = []
        lines.append(f"## Table 1: Descriptive Statistics for {data_summary.name}")
        lines.append("")
        lines.append("| Variable | M | SD | Min | Max | N |")
        lines.append("|----------|---|----|----|-----|---|")

        for stat in data_summary.column_stats:
            if stat.dtype == "numeric":
                lines.append(
                    f"| {stat.name} "
                    f"| {stat.mean:.2f} "
                    f"| {stat.std:.2f} "
                    f"| {stat.min:.2f} "
                    f"| {stat.max:.2f} "
                    f"| {stat.count} |"
                )

        lines.append("")
        lines.append(f"*Note*. M = Mean, SD = Standard Deviation.")

        return "\n".join(lines)

    def _generate_latex_table(self, data_summary: Any) -> str:
        """Generate LaTeX table."""
        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        lines.append(f"\\caption{{Descriptive Statistics for {data_summary.name}}}")
        lines.append("\\begin{tabular}{lrrrr}")
        lines.append("\\hline")
        lines.append("Variable & M & SD & Min & Max \\\\")
        lines.append("\\hline")

        for stat in data_summary.column_stats:
            if stat.dtype == "numeric":
                lines.append(
                    f"{stat.name} & "
                    f"{stat.mean:.2f} & "
                    f"{stat.std:.2f} & "
                    f"{stat.min:.2f} & "
                    f"{stat.max:.2f} \\\\"
                )

        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append(f"\\label{{tab:descriptive_{data_summary.name}}}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    def generate_results_section(self, results: List[Dict[str, Any]],
                                 analysis_type: str = "auto") -> str:
        """
        Generate complete results section from multiple analyses.

        Args:
            results: List of result dictionaries
            analysis_type: Type of analysis (auto-detects if "auto")

        Returns:
            Formatted results section
        """
        lines = []
        lines.append("Results")
        lines.append("=" * 60)
        lines.append("")

        for i, result in enumerate(results, 1):
            # Auto-detect test type
            if analysis_type == "auto":
                if 't' in result and 'df' in result:
                    test_type = "ttest"
                elif 'F' in result and 'df1' in result:
                    test_type = "anova" if 'R2' not in result else "regression"
                elif 'r' in result:
                    test_type = "correlation"
                elif 'chi2' in result:
                    test_type = "chi_square"
                else:
                    test_type = "unknown"
            else:
                test_type = analysis_type

            # Format based on type
            if test_type == "ttest":
                lines.append(self.format_ttest_result(result))
            elif test_type == "anova":
                lines.append(self.format_anova_result(result))
            elif test_type == "regression":
                lines.append(self.format_regression_result(result))
            elif test_type == "correlation":
                lines.append(self.format_correlation_result(result))
            elif test_type == "chi_square":
                lines.append(self.format_chi_square_result(result))

            lines.append("")

        return "\n".join(lines)

    def _format_p_value(self, p: float) -> str:
        """Format p-value according to APA style."""
        if p < 0.001:
            return "p < .001"
        elif p < 0.01:
            return f"p = {p:.3f}"
        elif p < 0.05:
            return f"p = {p:.3f}"
        else:
            return f"p = {p:.3f}"

    def create_figure_caption(self, figure_type: str, variables: List[str],
                             description: str = "") -> str:
        """
        Generate APA-style figure caption.

        Args:
            figure_type: Type of figure ("scatterplot", "barplot", "histogram", etc.)
            variables: List of variables shown
            description: Additional description

        Returns:
            Formatted caption
        """
        var_str = ", ".join(variables[:2])
        if len(variables) > 2:
            var_str += f", and {len(variables) - 2} other variable(s)"

        caption = f"Figure. {figure_type.title()} showing {var_str}."

        if description:
            caption += f" {description}"

        return caption

    def generate_methods_section_from_summary(self, data_summary: Any) -> str:
        """
        Generate complete methods section from data summary.

        Args:
            data_summary: DataSummary object

        Returns:
            Formatted methods section
        """
        lines = []
        lines.append("Method")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Participants and Data")
        lines.append("-" * 60)
        lines.append("")

        # Use the auto-generated text from data analyzer
        lines.append(data_summary.methods_section_text)
        lines.append("")

        # Add data cleaning notes if there were quality issues
        critical_issues = [i for i in data_summary.quality_issues if i.severity == "critical"]
        if critical_issues:
            lines.append("Data Preparation")
            lines.append("-" * 60)
            lines.append("")
            lines.append("The following data quality procedures were applied:")
            for issue in critical_issues:
                if issue.suggestion:
                    lines.append(f"  - {issue.suggestion}")
            lines.append("")

        return "\n".join(lines)
