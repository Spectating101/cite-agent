"""
API Handler for external API integrations
Handles Archive API, FinSight API, and Files API calls
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class APIHandler:
    """
    Handles external API integrations

    Features:
    - Archive API (academic research)
    - FinSight API (financial data)
    - Files API (workspace operations)
    - Retry mechanisms with exponential backoff
    - Error handling and telemetry
    """

    async def call_files_api(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Any = None,
        session,
        files_base_url: str,
        ensure_backend_ready_fn,
        record_data_source_fn
    ) -> Dict[str, Any]:
        """
        Call Files API endpoint

        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint path
            params: Query parameters
            json_body: JSON body for request
            data: Raw data for request
            session: aiohttp ClientSession
            files_base_url: Base URL for Files API
            ensure_backend_ready_fn: Function to check backend availability
            record_data_source_fn: Function to record telemetry

        Returns:
            API response or error dict
        """
        if not session:
            return {"error": "HTTP session not initialized"}

        ok, detail = await ensure_backend_ready_fn()
        if not ok:
            record_data_source_fn("Files", f"{method.upper()} {endpoint}", False, detail)
            return {"error": f"Workspace API unavailable: {detail or 'backend offline'}"}

        url = f"{files_base_url}{endpoint}"
        request_method = getattr(session, method.lower(), None)
        if not request_method:
            return {"error": f"Unsupported HTTP method: {method}"}

        try:
            async with request_method(url, params=params, json=json_body, data=data, timeout=20) as response:
                payload: Any
                if response.content_type and "json" in response.content_type:
                    payload = await response.json()
                else:
                    payload = {"raw": await response.text()}

                success = response.status == 200
                record_data_source_fn(
                    "Files",
                    f"{method.upper()} {endpoint}",
                    success,
                    "" if success else f"HTTP {response.status}"
                )

                if success:
                    return payload if isinstance(payload, dict) else {"data": payload}

                detail_msg = payload.get("detail") if isinstance(payload, dict) else None
                return {"error": detail_msg or f"Files API error: {response.status}"}
        except Exception as exc:
            record_data_source_fn("Files", f"{method.upper()} {endpoint}", False, str(exc))
            return {"error": f"Files API call failed: {exc}"}

    async def call_archive_api(
        self,
        endpoint: str,
        data: Dict[str, Any],
        session,
        archive_base_url: str,
        auth_token: Optional[str],
        ensure_backend_ready_fn,
        record_data_source_fn
    ) -> Dict[str, Any]:
        """
        Call Archive API endpoint with retry mechanism

        Args:
            endpoint: API endpoint path
            data: Request payload
            session: aiohttp ClientSession
            archive_base_url: Base URL for Archive API
            auth_token: Optional JWT token
            ensure_backend_ready_fn: Function to check backend availability
            record_data_source_fn: Function to record telemetry

        Returns:
            API response or error dict
        """
        max_retries = 3
        retry_delay = 1

        ok, detail = await ensure_backend_ready_fn()
        if not ok:
            record_data_source_fn("Archive", f"POST {endpoint}", False, detail)
            return {"error": f"Archive backend unavailable: {detail or 'backend offline'}"}

        for attempt in range(max_retries):
            try:
                if not session:
                    return {"error": "HTTP session not initialized"}

                url = f"{archive_base_url}/{endpoint}"
                # Start fresh with headers
                headers = {}

                # Always use demo key for Archive (public research data)
                headers["X-API-Key"] = "demo-key-123"
                headers["Content-Type"] = "application/json"

                # Also add JWT if we have it
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"

                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    print(f"🔍 Archive headers: {list(headers.keys())}, X-API-Key={headers.get('X-API-Key')}")
                    print(f"🔍 Archive URL: {url}")
                    print(f"🔍 Archive data: {data}")

                async with session.post(url, json=data, headers=headers, timeout=30) as response:
                    if debug_mode:
                        print(f"🔍 Archive response status: {response.status}")

                    if response.status == 200:
                        payload = await response.json()
                        record_data_source_fn("Archive", f"POST {endpoint}", True)
                        return payload
                    elif response.status == 422:  # Validation error
                        try:
                            error_detail = await response.json()
                            logger.error(f"Archive API validation error (HTTP 422): {error_detail}")
                        except Exception:
                            error_detail = await response.text()
                            logger.error(f"Archive API validation error (HTTP 422): {error_detail}")

                        if attempt < max_retries - 1:
                            # Retry with simplified request
                            if "sources" in data and len(data["sources"]) > 1:
                                data["sources"] = [data["sources"][0]]  # Try single source
                                logger.info(f"Retrying with single source: {data['sources']}")
                            await asyncio.sleep(retry_delay)
                            continue
                        record_data_source_fn("Archive", f"POST {endpoint}", False, "422 validation error")
                        return {"error": f"Archive API validation error: {error_detail}"}
                    elif response.status == 429:  # Rate limited
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        record_data_source_fn("Archive", f"POST {endpoint}", False, "rate limited")
                        return {"error": "Archive API rate limited. Please try again later."}
                    elif response.status == 401:
                        record_data_source_fn("Archive", f"POST {endpoint}", False, "401 unauthorized")
                        return {"error": "Archive API authentication failed. Please check API key."}
                    else:
                        error_text = await response.text()
                        logger.error(f"Archive API error (HTTP {response.status}): {error_text}")
                        record_data_source_fn("Archive", f"POST {endpoint}", False, f"HTTP {response.status}")
                        return {"error": f"Archive API error: {response.status}"}

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                record_data_source_fn("Archive", f"POST {endpoint}", False, "timeout")
                return {"error": "Archive API timeout. Please try again later."}
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                record_data_source_fn("Archive", f"POST {endpoint}", False, str(e))
                return {"error": f"Archive API call failed: {e}"}

        return {"error": "Archive API call failed after all retries"}

    async def call_finsight_api(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        session=None,
        finsight_base_url: str = "",
        auth_token: Optional[str] = None,
        ensure_backend_ready_fn=None,
        record_data_source_fn=None
    ) -> Dict[str, Any]:
        """
        Call FinSight API endpoint with retry mechanism

        Args:
            endpoint: API endpoint path
            params: Query parameters
            session: aiohttp ClientSession
            finsight_base_url: Base URL for FinSight API
            auth_token: Optional JWT token
            ensure_backend_ready_fn: Function to check backend availability
            record_data_source_fn: Function to record telemetry

        Returns:
            API response or error dict
        """
        max_retries = 3
        retry_delay = 1

        ok, detail = await ensure_backend_ready_fn()
        if not ok:
            record_data_source_fn("FinSight", f"GET {endpoint}", False, detail)
            return {"error": f"FinSight backend unavailable: {detail or 'backend offline'}"}

        for attempt in range(max_retries):
            try:
                if not session:
                    return {"error": "HTTP session not initialized"}

                url = f"{finsight_base_url}/{endpoint}"
                # Start fresh with headers - don't use _default_headers which might be wrong
                headers = {}

                # Always use demo key for FinSight (SEC data is public)
                headers["X-API-Key"] = "demo-key-123"

                # Mark request as agent-mediated for product separation
                headers["X-Request-Source"] = "agent"

                # Also add JWT if we have it
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"

                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    print(f"🔍 FinSight headers: {list(headers.keys())}, X-API-Key={headers.get('X-API-Key')}")
                    print(f"🔍 FinSight URL: {url}")

                async with session.get(url, params=params, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        payload = await response.json()
                        record_data_source_fn("FinSight", f"GET {endpoint}", True)
                        return payload
                    elif response.status == 429:  # Rate limited
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        record_data_source_fn("FinSight", f"GET {endpoint}", False, "rate limited")
                        return {"error": "FinSight API rate limited. Please try again later."}
                    elif response.status == 401:
                        record_data_source_fn("FinSight", f"GET {endpoint}", False, "401 unauthorized")
                        return {"error": "FinSight API authentication failed. Please check API key."}
                    else:
                        record_data_source_fn("FinSight", f"GET {endpoint}", False, f"HTTP {response.status}")
                        return {"error": f"FinSight API error: {response.status}"}

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                record_data_source_fn("FinSight", f"GET {endpoint}", False, "timeout")
                return {"error": "FinSight API timeout. Please try again later."}
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                record_data_source_fn("FinSight", f"GET {endpoint}", False, str(e))
                return {"error": f"FinSight API call failed: {e}"}

        return {"error": "FinSight API call failed after all retries"}

    async def call_finsight_api_post(
        self,
        endpoint: str,
        data: Dict[str, Any] = None,
        session=None,
        finsight_base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        ensure_backend_ready_fn=None,
        record_data_source_fn=None
    ) -> Dict[str, Any]:
        """
        Call FinSight API endpoint with POST request

        Args:
            endpoint: API endpoint path
            data: Request payload
            session: aiohttp ClientSession
            finsight_base_url: Base URL for FinSight API
            default_headers: Default headers
            ensure_backend_ready_fn: Function to check backend availability
            record_data_source_fn: Function to record telemetry

        Returns:
            API response or error dict
        """
        ok, detail = await ensure_backend_ready_fn()
        if not ok:
            record_data_source_fn("FinSight", f"POST {endpoint}", False, detail)
            return {"error": f"FinSight backend unavailable: {detail or 'backend offline'}"}

        try:
            if not session:
                return {"error": "HTTP session not initialized"}

            url = f"{finsight_base_url}/{endpoint}"
            headers = dict(default_headers) if default_headers else None
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    payload = await response.json()
                    record_data_source_fn("FinSight", f"POST {endpoint}", True)
                    return payload
                record_data_source_fn("FinSight", f"POST {endpoint}", False, f"HTTP {response.status}")
                return {"error": f"FinSight API error: {response.status}"}

        except Exception as e:
            record_data_source_fn("FinSight", f"POST {endpoint}", False, str(e))
            return {"error": f"FinSight API call failed: {e}"}

    async def search_academic_papers(
        self,
        query: str,
        limit: int = 10,
        call_archive_api_fn=None
    ) -> Dict[str, Any]:
        """
        Search academic papers using Archive API with resilient fallbacks

        Args:
            query: Search query
            limit: Maximum number of results
            call_archive_api_fn: Function to call Archive API

        Returns:
            Search results with papers list
        """
        # Try cache first
        from cite_agent.cache import get_cache
        cache = get_cache()
        cached_result = cache.get("academic_search", query=query, limit=limit)
        if cached_result is not None:
            logger.info(f"📦 Cache HIT for query: {query[:50]}...")
            return cached_result

        source_sets: List[List[str]] = [
            ["semantic_scholar", "openalex"],
            ["semantic_scholar"],
            ["openalex"],
            ["pubmed"],
            ["offline"],
        ]

        tried: List[List[str]] = []
        provider_errors: List[Dict[str, Any]] = []
        aggregated_payload: Dict[str, Any] = {"results": []}

        for sources in source_sets:
            data = {"query": query, "limit": limit, "sources": sources}
            tried.append(list(sources))
            result = await call_archive_api_fn("search", data)

            if "error" in result:
                provider_errors.append({"sources": sources, "error": result["error"]})
                continue

            results = result.get("results") or result.get("papers") or []
            # Validate papers have minimal required fields
            validated_results = []
            for paper in results:
                if isinstance(paper, dict) and paper.get("title") and paper.get("year"):
                    validated_results.append(paper)
                else:
                    logger.warning(f"Skipping invalid paper: {paper}")

            if validated_results:
                aggregated_payload = dict(result)
                aggregated_payload["results"] = validated_results
                aggregated_payload["validation_note"] = f"Validated {len(validated_results)} out of {len(results)} papers"
                break

        aggregated_payload.setdefault("results", [])
        aggregated_payload["sources_tried"] = [",".join(s) for s in tried]

        if provider_errors:
            aggregated_payload["provider_errors"] = provider_errors

        # CRITICAL: Add explicit marker for empty results to prevent hallucination
        if not aggregated_payload["results"]:
            aggregated_payload["notes"] = (
                "No papers were returned by the research providers. This often occurs during "
                "temporary rate limits; please retry in a minute or adjust the query scope."
            )
            aggregated_payload["EMPTY_RESULTS"] = True
            aggregated_payload["warning"] = "DO NOT GENERATE FAKE PAPERS - API returned zero results"
        else:
            # Deduplicate results
            from cite_agent.deduplication import deduplicate_papers
            original_count = len(aggregated_payload["results"])
            aggregated_payload["results"] = deduplicate_papers(aggregated_payload["results"])
            dedup_count = len(aggregated_payload["results"])
            if original_count != dedup_count:
                logger.info(f"🔍 Deduplicated: {original_count} → {dedup_count} papers ({original_count - dedup_count} removed)")
                aggregated_payload["deduplicated"] = True
                aggregated_payload["duplicates_removed"] = original_count - dedup_count

        # Cache the result
        if aggregated_payload["results"]:
            cache.set("academic_search", aggregated_payload, ttl_hours=24, query=query, limit=limit)
            logger.debug(f"💾 Cached results for: {query[:50]}...")

            # Quietly read papers in background (no info dump)
            try:
                from cite_agent.paper_knowledge import quietly_read_papers, get_knowledge_base
                kb = get_knowledge_base()

                # Remember these papers for "first paper", "second paper" references
                dois = [p.get('doi') for p in aggregated_payload["results"] if p.get('doi')]
                kb.remember_search(dois)

                # Read PDFs in background (if available)
                # This runs quietly - no output unless user asks about papers
                # Note: We can't pass 'self' here, so PDF reading is skipped in delegated calls
                # This is acceptable as PDF reading is a background optimization

            except ImportError:
                pass  # PDF reading not available
            except Exception as e:
                logger.debug(f"Background PDF reading failed: {e}")

        return aggregated_payload

    async def synthesize_research(
        self,
        paper_ids: List[str],
        max_words: int = 500,
        call_archive_api_fn=None
    ) -> Dict[str, Any]:
        """
        Synthesize research papers using Archive API

        Args:
            paper_ids: List of paper IDs to synthesize
            max_words: Maximum words in synthesis
            call_archive_api_fn: Function to call Archive API

        Returns:
            Synthesis result
        """
        data = {
            "paper_ids": paper_ids,
            "max_words": max_words,
            "focus": "key_findings",
            "style": "academic"
        }
        return await call_archive_api_fn("synthesize", data)

    async def get_financial_data(
        self,
        ticker: str,
        metric: str,
        limit: int = 12,
        call_finsight_api_fn=None
    ) -> Dict[str, Any]:
        """
        Get financial data using FinSight API

        Args:
            ticker: Stock ticker symbol
            metric: Financial metric name
            limit: Number of periods to fetch
            call_finsight_api_fn: Function to call FinSight API

        Returns:
            Financial data
        """
        params = {
            "freq": "Q",
            "limit": limit
        }
        return await call_finsight_api_fn(f"kpis/{ticker}/{metric}", params)

    async def get_financial_metrics(
        self,
        ticker: str,
        metrics: List[str] = None,
        call_finsight_api_fn=None
    ) -> Dict[str, Any]:
        """
        Get financial metrics using FinSight KPI endpoints (with schema drift fixes)

        Args:
            ticker: Stock ticker symbol
            metrics: List of metric names
            call_finsight_api_fn: Function to call FinSight API

        Returns:
            Dict of metrics and their values
        """
        if metrics is None:
            metrics = ["revenue", "grossProfit", "operatingIncome", "netIncome"]

        if not metrics:
            return {}

        async def _fetch_metric(metric_name: str) -> Dict[str, Any]:
            params = {"period": "latest", "freq": "Q"}
            try:
                result = await call_finsight_api_fn(f"calc/{ticker}/{metric_name}", params)
            except Exception as exc:
                return {metric_name: {"error": str(exc)}}

            if "error" in result:
                return {metric_name: {"error": result["error"]}}
            return {metric_name: result}

        tasks = [asyncio.create_task(_fetch_metric(metric)) for metric in metrics]
        results: Dict[str, Any] = {}

        for payload in await asyncio.gather(*tasks):
            results.update(payload)

        return results
