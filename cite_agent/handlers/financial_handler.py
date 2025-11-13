"""
Financial Handler for financial data processing
Handles ticker extraction and financial metrics formatting
"""

import re
from typing import List, Tuple, Dict, Any, Set, Optional


class FinancialHandler:
    """
    Handles financial data processing

    Features:
    - Ticker extraction from text
    - Company name to ticker mapping
    - Financial metrics planning
    - Currency value formatting
    """

    def extract_tickers_from_text(self, text: str, company_name_to_ticker: Dict[str, str]) -> List[str]:
        """
        Find tickers either as explicit symbols or from known company names

        Args:
            text: Text to extract tickers from
            company_name_to_ticker: Mapping of company names to ticker symbols

        Returns:
            List of ticker symbols (max 4)
        """
        text_lower = text.lower()
        # Explicit ticker-like symbols
        ticker_candidates: List[str] = []
        for token in re.findall(r"\b[A-Z]{1,5}(?:\d{0,2})\b", text):
            ticker_candidates.append(token)
        # Company name matches
        for name, sym in company_name_to_ticker.items():
            if name and name in text_lower:
                ticker_candidates.append(sym)
        # Deduplicate preserve order
        seen = set()
        ordered: List[str] = []
        for t in ticker_candidates:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered[:4]

    def plan_financial_request(
        self,
        question: str,
        company_name_to_ticker: Dict[str, str],
        session_topics: Optional[Dict] = None,
        session_key: Optional[str] = None
    ) -> Tuple[List[str], List[str]]:
        """
        Derive ticker and metric targets for a financial query

        Args:
            question: User's question
            company_name_to_ticker: Mapping of company names to ticker symbols
            session_topics: Session topic tracking
            session_key: Optional session key for context

        Returns:
            Tuple of (tickers, metrics)
        """
        tickers = list(self.extract_tickers_from_text(question, company_name_to_ticker))
        question_lower = question.lower()

        if not tickers:
            if "apple" in question_lower:
                tickers.append("AAPL")
            if "microsoft" in question_lower:
                tickers.append("MSFT" if "AAPL" not in tickers else "MSFT")

        metrics_to_fetch: List[str] = []
        keyword_map = [
            ("revenue", ["revenue", "sales", "top line"]),
            ("grossProfit", ["gross profit", "gross margin", "margin"]),
            ("operatingIncome", ["operating income", "operating profit", "ebit"]),
            ("netIncome", ["net income", "profit", "earnings", "bottom line"]),
        ]

        for metric, keywords in keyword_map:
            if any(kw in question_lower for kw in keywords):
                metrics_to_fetch.append(metric)

        if session_key and session_topics:
            last_topic = session_topics.get(session_key)
        else:
            last_topic = None

        if not metrics_to_fetch and last_topic and last_topic.get("metrics"):
            metrics_to_fetch = list(last_topic["metrics"])

        if not metrics_to_fetch:
            metrics_to_fetch = ["revenue", "grossProfit"]

        deduped: List[str] = []
        seen: Set[str] = set()
        for symbol in tickers:
            if symbol and symbol not in seen:
                seen.add(symbol)
                deduped.append(symbol)

        return deduped[:2], metrics_to_fetch

    def format_currency_value(self, value: float) -> str:
        """
        Format currency value with appropriate scale (trillion/billion/million)

        Args:
            value: Numeric value

        Returns:
            Formatted string like "$1.23 billion"
        """
        try:
            abs_val = abs(value)
            if abs_val >= 1e12:
                return f"${value / 1e12:.2f} trillion"
            if abs_val >= 1e9:
                return f"${value / 1e9:.2f} billion"
            if abs_val >= 1e6:
                return f"${value / 1e6:.2f} million"
            return f"${value:,.2f}"
        except Exception:
            return str(value)
