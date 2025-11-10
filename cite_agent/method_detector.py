"""
Method Detector - Automatically detect statistical methods used and suggest citations.

Analyzes R and Python code to identify statistical methods, tests, and models,
then suggests appropriate academic citations.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class MethodCitation:
    """Citation for a statistical method."""
    method_name: str
    category: str  # "regression", "test", "clustering", "visualization", etc.
    detected_from: List[str] = field(default_factory=list)  # Function calls that triggered this
    primary_citation: str = ""
    additional_citations: List[str] = field(default_factory=list)
    description: str = ""
    sample_size_note: Optional[str] = None


# Comprehensive method database
METHOD_DATABASE = {
    # ============================================================================
    # REGRESSION MODELS
    # ============================================================================
    "linear_regression": MethodCitation(
        method_name="Linear Regression",
        category="regression",
        detected_from=["lm(", "lm ", "LinearRegression(", "OLS(", "ols("],
        primary_citation=(
            "Cohen, J., Cohen, P., West, S. G., & Aiken, L. S. (2003). "
            "Applied Multiple Regression/Correlation Analysis for the Behavioral Sciences (3rd ed.). "
            "Routledge. https://doi.org/10.4324/9780203774441"
        ),
        additional_citations=[
            "Fox, J. (2015). Applied Regression Analysis and Generalized Linear Models (3rd ed.). SAGE Publications.",
            "Kutner, M. H., Nachtsheim, C. J., Neter, J., & Li, W. (2004). Applied Linear Statistical Models (5th ed.). McGraw-Hill."
        ],
        description="Ordinary least squares (OLS) linear regression",
        sample_size_note="For multiple regression, recommend n ≥ 50 + 8m (where m = number of predictors)"
    ),

    "logistic_regression": MethodCitation(
        method_name="Logistic Regression",
        category="regression",
        detected_from=["glm(", "family=binomial", "LogisticRegression(", "logit("],
        primary_citation=(
            "Hosmer, D. W., Lemeshow, S., & Sturdivant, R. X. (2013). "
            "Applied Logistic Regression (3rd ed.). Wiley. https://doi.org/10.1002/9781118548387"
        ),
        additional_citations=[
            "Menard, S. (2010). Logistic Regression: From Introductory to Advanced Concepts and Applications. SAGE Publications.",
            "Agresti, A. (2018). An Introduction to Categorical Data Analysis (3rd ed.). Wiley."
        ],
        description="Binary or multinomial logistic regression",
        sample_size_note="Minimum 10 events per predictor variable recommended"
    ),

    "poisson_regression": MethodCitation(
        method_name="Poisson Regression",
        category="regression",
        detected_from=["glm(", "family=poisson", "family=\"poisson\""],
        primary_citation=(
            "Cameron, A. C., & Trivedi, P. K. (2013). "
            "Regression Analysis of Count Data (2nd ed.). Cambridge University Press. "
            "https://doi.org/10.1017/CBO9781139013567"
        ),
        description="Poisson regression for count data"
    ),

    # ============================================================================
    # STATISTICAL TESTS
    # ============================================================================
    "t_test": MethodCitation(
        method_name="Student's t-test",
        category="test",
        detected_from=["t.test(", "ttest_ind(", "ttest_rel(", "ttest_1samp("],
        primary_citation=(
            "Student. (1908). The Probable Error of a Mean. Biometrika, 6(1), 1-25. "
            "https://doi.org/10.2307/2331554"
        ),
        additional_citations=[
            "Welch, B. L. (1947). The generalization of 'Student's' problem when several different population variances are involved. Biometrika, 34(1-2), 28-35."
        ],
        description="Independent or paired samples t-test"
    ),

    "anova": MethodCitation(
        method_name="Analysis of Variance (ANOVA)",
        category="test",
        detected_from=["aov(", "anova(", "f_oneway(", "ANOVA("],
        primary_citation=(
            "Maxwell, S. E., & Delaney, H. D. (2004). Designing Experiments and Analyzing Data: "
            "A Model Comparison Perspective (2nd ed.). Psychology Press."
        ),
        additional_citations=[
            "Keppel, G., & Wickens, T. D. (2004). Design and Analysis: A Researcher's Handbook (4th ed.). Pearson.",
            "Fisher, R. A. (1925). Statistical Methods for Research Workers. Oliver and Boyd."
        ],
        description="One-way or multi-way ANOVA"
    ),

    "chi_square": MethodCitation(
        method_name="Chi-Square Test",
        category="test",
        detected_from=["chisq.test(", "chi2_contingency(", "chi2("],
        primary_citation=(
            "Pearson, K. (1900). On the criterion that a given system of deviations from the probable "
            "in the case of a correlated system of variables is such that it can be reasonably supposed "
            "to have arisen from random sampling. The London, Edinburgh, and Dublin Philosophical Magazine "
            "and Journal of Science, 50(302), 157-175."
        ),
        description="Chi-square test of independence or goodness of fit"
    ),

    "mann_whitney": MethodCitation(
        method_name="Mann-Whitney U Test",
        category="test",
        detected_from=["wilcox.test(", "mannwhitneyu(", "ranksum("],
        primary_citation=(
            "Mann, H. B., & Whitney, D. R. (1947). On a Test of Whether one of Two Random Variables "
            "is Stochastically Larger than the Other. The Annals of Mathematical Statistics, 18(1), 50-60."
        ),
        description="Non-parametric test for two independent samples"
    ),

    "kruskal_wallis": MethodCitation(
        method_name="Kruskal-Wallis Test",
        category="test",
        detected_from=["kruskal.test(", "kruskal("],
        primary_citation=(
            "Kruskal, W. H., & Wallis, W. A. (1952). Use of Ranks in One-Criterion Variance Analysis. "
            "Journal of the American Statistical Association, 47(260), 583-621."
        ),
        description="Non-parametric alternative to one-way ANOVA"
    ),

    # ============================================================================
    # POST-HOC TESTS
    # ============================================================================
    "tukey_hsd": MethodCitation(
        method_name="Tukey's Honest Significant Difference",
        category="post_hoc",
        detected_from=["TukeyHSD(", "pairwise_tukeyhsd("],
        primary_citation=(
            "Tukey, J. W. (1949). Comparing Individual Means in the Analysis of Variance. "
            "Biometrics, 5(2), 99-114. https://doi.org/10.2307/3001913"
        ),
        description="Post-hoc pairwise comparisons after ANOVA"
    ),

    "bonferroni": MethodCitation(
        method_name="Bonferroni Correction",
        category="post_hoc",
        detected_from=["p.adjust.*bonferroni", "bonferroni", "p_adjust=.*bonferroni"],
        primary_citation=(
            "Dunn, O. J. (1961). Multiple Comparisons Among Means. "
            "Journal of the American Statistical Association, 56(293), 52-64."
        ),
        description="Conservative correction for multiple comparisons"
    ),

    # ============================================================================
    # CORRELATION & ASSOCIATION
    # ============================================================================
    "pearson_correlation": MethodCitation(
        method_name="Pearson Correlation",
        category="correlation",
        detected_from=["cor.test(", "method.*pearson", "pearsonr("],
        primary_citation=(
            "Pearson, K. (1895). Notes on regression and inheritance in the case of two parents. "
            "Proceedings of the Royal Society of London, 58, 240-242."
        ),
        description="Pearson product-moment correlation coefficient"
    ),

    "spearman_correlation": MethodCitation(
        method_name="Spearman Correlation",
        category="correlation",
        detected_from=["cor.test(", "method.*spearman", "spearmanr("],
        primary_citation=(
            "Spearman, C. (1904). The Proof and Measurement of Association between Two Things. "
            "The American Journal of Psychology, 15(1), 72-101."
        ),
        description="Spearman rank-order correlation coefficient"
    ),

    # ============================================================================
    # TIME SERIES
    # ============================================================================
    "arima": MethodCitation(
        method_name="ARIMA Models",
        category="time_series",
        detected_from=["arima(", "ARIMA(", "auto.arima("],
        primary_citation=(
            "Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). "
            "Time Series Analysis: Forecasting and Control (5th ed.). Wiley."
        ),
        additional_citations=[
            "Hamilton, J. D. (1994). Time Series Analysis. Princeton University Press."
        ],
        description="Autoregressive Integrated Moving Average models"
    ),

    # ============================================================================
    # MACHINE LEARNING
    # ============================================================================
    "random_forest": MethodCitation(
        method_name="Random Forest",
        category="machine_learning",
        detected_from=["RandomForest(", "randomForest(", "rf("],
        primary_citation=(
            "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32. "
            "https://doi.org/10.1023/A:1010933404324"
        ),
        description="Ensemble learning method using decision trees"
    ),

    "kmeans": MethodCitation(
        method_name="K-Means Clustering",
        category="clustering",
        detected_from=["kmeans(", "KMeans("],
        primary_citation=(
            "MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. "
            "Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297."
        ),
        description="Partitional clustering algorithm"
    ),

    "pca": MethodCitation(
        method_name="Principal Component Analysis",
        category="dimension_reduction",
        detected_from=["prcomp(", "PCA(", "princomp("],
        primary_citation=(
            "Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: a review and recent developments. "
            "Philosophical Transactions of the Royal Society A, 374(2065), 20150202. "
            "https://doi.org/10.1098/rsta.2015.0202"
        ),
        additional_citations=[
            "Hotelling, H. (1933). Analysis of a complex of statistical variables into principal components. Journal of Educational Psychology, 24(6), 417-441."
        ],
        description="Dimensionality reduction technique"
    ),

    # ============================================================================
    # DATA MANIPULATION (cite packages)
    # ============================================================================
    "dplyr": MethodCitation(
        method_name="dplyr Package",
        category="data_manipulation",
        detected_from=["library(dplyr)", "filter(", "select(", "mutate(", "group_by("],
        primary_citation=(
            "Wickham, H., François, R., Henry, L., & Müller, K. (2023). dplyr: A Grammar of Data Manipulation. "
            "R package version 1.1.0. https://CRAN.R-project.org/package=dplyr"
        ),
        description="Data manipulation package for R"
    ),

    "pandas": MethodCitation(
        method_name="pandas Library",
        category="data_manipulation",
        detected_from=["import pandas", "pd.read_csv", "pd.DataFrame"],
        primary_citation=(
            "McKinney, W. (2010). Data Structures for Statistical Computing in Python. "
            "Proceedings of the 9th Python in Science Conference, 56-61. "
            "https://doi.org/10.25080/Majora-92bf1922-00a"
        ),
        description="Data analysis and manipulation library for Python"
    ),
}


class MethodDetector:
    """Detects statistical methods from code and suggests citations."""

    def __init__(self):
        self.detected_methods: Set[str] = set()
        self.code_history: List[str] = []

    def analyze_code(self, code: str) -> List[MethodCitation]:
        """
        Analyze code string and detect statistical methods.

        Args:
            code: R or Python code string

        Returns:
            List of detected methods with citations
        """
        self.code_history.append(code)
        detected = []

        for method_key, method_info in METHOD_DATABASE.items():
            for pattern in method_info.detected_from:
                # Use regex for flexible matching
                if re.search(re.escape(pattern), code, re.IGNORECASE):
                    if method_key not in self.detected_methods:
                        self.detected_methods.add(method_key)
                        detected.append(method_info)
                    break

        return detected

    def analyze_session_history(self, commands: List[str]) -> Dict[str, List[MethodCitation]]:
        """
        Analyze entire session history and categorize detected methods.

        Args:
            commands: List of code commands from session

        Returns:
            Dict mapping category to list of methods
        """
        all_methods = []
        for cmd in commands:
            methods = self.analyze_code(cmd)
            all_methods.extend(methods)

        # Remove duplicates
        unique_methods = []
        seen = set()
        for method in all_methods:
            if method.method_name not in seen:
                seen.add(method.method_name)
                unique_methods.append(method)

        # Categorize
        categorized = {}
        for method in unique_methods:
            if method.category not in categorized:
                categorized[method.category] = []
            categorized[method.category].append(method)

        return categorized

    def generate_methods_bibliography(self, methods: List[MethodCitation],
                                     format: str = "apa") -> str:
        """
        Generate formatted bibliography for detected methods.

        Args:
            methods: List of method citations
            format: Citation format ("apa", "bibtex", "markdown")

        Returns:
            Formatted bibliography string
        """
        if format == "apa":
            return self._generate_apa_bibliography(methods)
        elif format == "bibtex":
            return self._generate_bibtex_bibliography(methods)
        elif format == "markdown":
            return self._generate_markdown_bibliography(methods)
        else:
            return self._generate_apa_bibliography(methods)

    def _generate_apa_bibliography(self, methods: List[MethodCitation]) -> str:
        """Generate APA format bibliography."""
        lines = ["References", "=" * 60, ""]

        for method in methods:
            lines.append(f"{method.method_name}:")
            lines.append(f"  {method.primary_citation}")
            if method.additional_citations:
                lines.append("  Additional references:")
                for citation in method.additional_citations:
                    lines.append(f"    - {citation}")
            lines.append("")

        return "\n".join(lines)

    def _generate_bibtex_bibliography(self, methods: List[MethodCitation]) -> str:
        """Generate BibTeX format bibliography."""
        # Simplified - real implementation would parse citations properly
        lines = []
        for i, method in enumerate(methods, 1):
            key = method.method_name.lower().replace(" ", "_")
            lines.append(f"@article{{{key}{i},")
            lines.append(f"  title = {{{method.method_name}}},")
            lines.append(f"  note = {{{method.primary_citation}}}")
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def _generate_markdown_bibliography(self, methods: List[MethodCitation]) -> str:
        """Generate Markdown format bibliography."""
        lines = ["## Methods & Citations", ""]

        for method in methods:
            lines.append(f"### {method.method_name}")
            lines.append(f"**Category:** {method.category}")
            lines.append(f"**Description:** {method.description}")
            lines.append(f"\n**Primary Citation:**")
            lines.append(f"- {method.primary_citation}")

            if method.additional_citations:
                lines.append(f"\n**Additional References:**")
                for citation in method.additional_citations:
                    lines.append(f"- {citation}")

            if method.sample_size_note:
                lines.append(f"\n**Note:** {method.sample_size_note}")

            lines.append("")

        return "\n".join(lines)

    def suggest_citations_for_analysis(self, data_summary: Any) -> List[MethodCitation]:
        """
        Suggest relevant citations based on data characteristics.

        Args:
            data_summary: DataSummary object from DataAnalyzer

        Returns:
            List of suggested method citations
        """
        suggestions = []

        # Basic descriptive statistics
        if len(data_summary.numeric_columns) > 0:
            suggestions.append(MethodCitation(
                method_name="Descriptive Statistics",
                category="descriptive",
                primary_citation=(
                    "Tukey, J. W. (1977). Exploratory Data Analysis. Addison-Wesley."
                ),
                description="Standard descriptive statistics (mean, median, SD, etc.)"
            ))

        # Suggest missing data handling if needed
        if any(issue.category == "missing" for issue in data_summary.quality_issues):
            suggestions.append(METHOD_DATABASE["linear_regression"])  # Has missing data citation

        return suggestions
