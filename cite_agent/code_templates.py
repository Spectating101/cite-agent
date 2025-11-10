"""
Code Templates - Generate code templates for common statistical analyses.

Provides ready-to-use code snippets for R and Python with proper citations.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeTemplate:
    """Code template with citation."""
    name: str
    language: str  # "R" or "Python"
    code: str
    description: str
    parameters: Dict[str, str]  # parameter_name: description
    citations: List[str]
    notes: List[str] = None


class CodeTemplateGenerator:
    """Generates code templates for statistical analyses."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, CodeTemplate]:
        """Load all available templates."""
        return {
            # ==================================================================
            # T-TESTS
            # ==================================================================
            "ttest_independent_r": CodeTemplate(
                name="Independent Samples t-test (R)",
                language="R",
                code="""# Independent samples t-test
# Compare {variable} between {group1} and {group2}

# Assumptions check
# 1. Normality
shapiro.test({data}${variable}[{data}${group_var} == "{group1}"])
shapiro.test({data}${variable}[{data}${group_var} == "{group2}"])

# 2. Homogeneity of variance
var.test({variable} ~ {group_var}, data = {data})

# Run t-test
result <- t.test({variable} ~ {group_var}, data = {data}, var.equal = TRUE)
print(result)

# Effect size (Cohen's d)
library(effsize)
cohen.d({data}${variable}[{data}${group_var} == "{group1}"],
        {data}${variable}[{data}${group_var} == "{group2}"])
""",
                description="Independent samples t-test with assumptions checks and effect size",
                parameters={
                    "data": "Name of your dataframe",
                    "variable": "Dependent variable (numeric)",
                    "group_var": "Grouping variable (2 levels)",
                    "group1": "Name of first group",
                    "group2": "Name of second group"
                },
                citations=[
                    "Student. (1908). The Probable Error of a Mean. Biometrika, 6(1), 1-25.",
                    "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum Associates."
                ],
                notes=[
                    "Check Shapiro-Wilk test: p > .05 indicates normality",
                    "If variances unequal, use var.equal=FALSE (Welch's t-test)",
                    "If normality violated, consider Mann-Whitney U test instead"
                ]
            ),

            "ttest_independent_python": CodeTemplate(
                name="Independent Samples t-test (Python)",
                language="Python",
                code="""# Independent samples t-test
import scipy.stats as stats
import numpy as np

# Split data by groups
group1 = {data}[{data}['{group_var}'] == '{group1}']['{variable}']
group2 = {data}[{data}['{group_var}'] == '{group2}']['{variable}']

# Assumptions check
# 1. Normality
print("Shapiro-Wilk test for normality:")
print(f"Group 1: {stats.shapiro(group1)}")
print(f"Group 2: {stats.shapiro(group2)}")

# 2. Homogeneity of variance
print(f"\\nLevene's test: {stats.levene(group1, group2)}")

# Run t-test
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"\\nt-test: t = {t_stat:.3f}, p = {p_value:.4f}")

# Effect size (Cohen's d)
pooled_std = np.sqrt((group1.std()**2 + group2.std()**2) / 2)
cohens_d = (group1.mean() - group2.mean()) / pooled_std
print(f"Cohen's d = {cohens_d:.3f}")
""",
                description="Independent samples t-test with assumptions checks and effect size",
                parameters={
                    "data": "Name of your DataFrame",
                    "variable": "Dependent variable (numeric)",
                    "group_var": "Grouping variable column name",
                    "group1": "Name of first group",
                    "group2": "Name of second group"
                },
                citations=[
                    "Student. (1908). The Probable Error of a Mean. Biometrika, 6(1), 1-25.",
                    "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.)."
                ]
            ),

            # ==================================================================
            # ANOVA
            # ==================================================================
            "anova_oneway_r": CodeTemplate(
                name="One-Way ANOVA (R)",
                language="R",
                code="""# One-way ANOVA
# Compare {variable} across {group_var}

# Assumptions check
# 1. Normality per group
library(dplyr)
{data} %>%
  group_by({group_var}) %>%
  summarize(shapiro_p = shapiro.test({variable})$p.value)

# 2. Homogeneity of variance
bartlett.test({variable} ~ {group_var}, data = {data})

# Run ANOVA
model <- aov({variable} ~ {group_var}, data = {data})
summary(model)

# Effect size (eta-squared)
library(effectsize)
eta_squared(model)

# Post-hoc tests (if significant)
TukeyHSD(model)

# Visualize
boxplot({variable} ~ {group_var}, data = {data},
        xlab = "{group_var}", ylab = "{variable}",
        main = "Distribution by Group")
""",
                description="One-way ANOVA with post-hoc tests and effect size",
                parameters={
                    "data": "Name of your dataframe",
                    "variable": "Dependent variable (numeric)",
                    "group_var": "Grouping variable (3+ levels)"
                },
                citations=[
                    "Fisher, R. A. (1925). Statistical Methods for Research Workers. Oliver and Boyd.",
                    "Tukey, J. W. (1949). Comparing Individual Means in the Analysis of Variance. Biometrics, 5(2), 99-114."
                ]
            ),

            # ==================================================================
            # REGRESSION
            # ==================================================================
            "regression_simple_r": CodeTemplate(
                name="Simple Linear Regression (R)",
                language="R",
                code="""# Simple linear regression
# Predict {dependent} from {independent}

# Fit model
model <- lm({dependent} ~ {independent}, data = {data})

# Model summary
summary(model)

# Assumptions check
par(mfrow = c(2, 2))
plot(model)

# Alternative assumptions tests
library(lmtest)
bptest(model)  # Heteroscedasticity
library(car)
durbinWatsonTest(model)  # Autocorrelation

# Confidence intervals
confint(model)

# Predictions
# predict(model, newdata = data.frame({independent} = c(1, 2, 3)))

# Visualize
plot({data}${independent}, {data}${dependent},
     xlab = "{independent}", ylab = "{dependent}",
     main = "Regression Line")
abline(model, col = "red", lwd = 2)
""",
                description="Simple linear regression with diagnostics",
                parameters={
                    "data": "Name of your dataframe",
                    "dependent": "Dependent variable (Y)",
                    "independent": "Independent variable (X)"
                },
                citations=[
                    "Cohen, J., Cohen, P., West, S. G., & Aiken, L. S. (2003). Applied Multiple Regression/Correlation Analysis for the Behavioral Sciences (3rd ed.). Routledge.",
                    "Fox, J. (2015). Applied Regression Analysis and Generalized Linear Models (3rd ed.). SAGE Publications."
                ]
            ),

            "regression_multiple_r": CodeTemplate(
                name="Multiple Linear Regression (R)",
                language="R",
                code="""# Multiple linear regression
# Predict {dependent} from multiple predictors

# Fit model
model <- lm({dependent} ~ {predictors}, data = {data})

# Model summary
summary(model)

# Standardized coefficients (betas)
library(EffectLiteR)
lm.beta(model)

# Multicollinearity check (VIF)
library(car)
vif(model)  # VIF > 10 indicates multicollinearity

# Assumptions diagnostics
par(mfrow = c(2, 2))
plot(model)

# Model comparison (if nested models)
# model2 <- lm({dependent} ~ {fewer_predictors}, data = {data})
# anova(model2, model)
""",
                description="Multiple regression with multicollinearity and diagnostics",
                parameters={
                    "data": "Name of your dataframe",
                    "dependent": "Dependent variable",
                    "predictors": "Predictors separated by + (e.g., 'x1 + x2 + x3')"
                },
                citations=[
                    "Cohen, J., Cohen, P., West, S. G., & Aiken, L. S. (2003). Applied Multiple Regression/Correlation Analysis for the Behavioral Sciences (3rd ed.).",
                    "Kutner, M. H., Nachtsheim, C. J., Neter, J., & Li, W. (2004). Applied Linear Statistical Models (5th ed.)."
                ],
                notes=[
                    "Sample size rule: n ≥ 50 + 8m (where m = number of predictors)",
                    "VIF > 10 indicates multicollinearity",
                    "Check residual plots for normality and homoscedasticity"
                ]
            ),

            # ==================================================================
            # CORRELATION
            # ==================================================================
            "correlation_r": CodeTemplate(
                name="Correlation Analysis (R)",
                language="R",
                code="""# Correlation analysis between {var1} and {var2}

# Visualize relationship
plot({data}${var1}, {data}${var2},
     xlab = "{var1}", ylab = "{var2}",
     main = "Scatterplot")

# Pearson correlation (assumes normality, linearity)
cor.test({data}${var1}, {data}${var2}, method = "pearson")

# Spearman correlation (non-parametric alternative)
cor.test({data}${var1}, {data}${var2}, method = "spearman")

# Correlation matrix for multiple variables
# cor({data}[, c("{var1}", "{var2}", "{var3}")])
# library(corrplot)
# corrplot(cor_matrix, method = "circle")
""",
                description="Correlation analysis with visualization",
                parameters={
                    "data": "Name of your dataframe",
                    "var1": "First variable",
                    "var2": "Second variable"
                },
                citations=[
                    "Pearson, K. (1895). Notes on regression and inheritance. Proceedings of the Royal Society of London, 58, 240-242.",
                    "Spearman, C. (1904). The Proof and Measurement of Association between Two Things. The American Journal of Psychology, 15(1), 72-101."
                ]
            ),
        }

    def get_template(self, template_name: str, **params) -> str:
        """
        Get a code template filled with parameters.

        Args:
            template_name: Name of template
            **params: Parameters to fill in template

        Returns:
            Filled code template
        """
        if template_name not in self.templates:
            available = ", ".join(self.templates.keys())
            return f"Template '{template_name}' not found. Available: {available}"

        template = self.templates[template_name]

        # Fill in parameters
        code = template.code
        for param, value in params.items():
            code = code.replace(f"{{{param}}}", str(value))

        return code

    def suggest_template(self, data_info: Dict[str, Any]) -> List[str]:
        """
        Suggest appropriate templates based on data characteristics.

        Args:
            data_info: Information about the data (from workspace inspector)

        Returns:
            List of suggested template names
        """
        suggestions = []

        # Check data characteristics
        numeric_cols = data_info.get('numeric_columns', [])
        categorical_cols = data_info.get('categorical_columns', [])
        shape = data_info.get('shape', (0, 0))

        # Simple regression if 2+ numeric variables
        if len(numeric_cols) >= 2:
            suggestions.append("regression_simple_r")
            suggestions.append("correlation_r")

        # Multiple regression if 3+ numeric variables
        if len(numeric_cols) >= 3:
            suggestions.append("regression_multiple_r")

        # t-test if 1 numeric + 1 categorical with 2 levels
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            suggestions.append("ttest_independent_r")
            suggestions.append("ttest_independent_python")

        # ANOVA if 1 numeric + 1 categorical with 3+ levels
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            suggestions.append("anova_oneway_r")

        return suggestions

    def list_templates(self, language: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List all available templates.

        Args:
            language: Optional language filter ("R" or "Python")

        Returns:
            List of template info dicts
        """
        result = []

        for name, template in self.templates.items():
            if language and template.language.lower() != language.lower():
                continue

            result.append({
                "name": name,
                "language": template.language,
                "description": template.description,
                "parameters": list(template.parameters.keys())
            })

        return result
