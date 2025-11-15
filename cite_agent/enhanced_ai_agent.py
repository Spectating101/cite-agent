#!/usr/bin/env python3
"""
Enhanced Nocturnal AI Agent - Production-Ready Research Assistant
Integrates with Archive API and FinSight API for comprehensive research capabilities
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import shlex
import subprocess
import time
from importlib import resources

import aiohttp
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set
from urllib.parse import urlparse
from dataclasses import dataclass, field
from pathlib import Path
import platform

from .telemetry import TelemetryManager
from .setup_config import DEFAULT_QUERY_LIMIT
from .conversation_archive import ConversationArchive

# Suppress noise
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Removed: No direct Groq import in production
# All LLM calls go through backend API for monetization
# Backend has the API keys, not the client

@dataclass
class ChatRequest:
    question: str
    user_id: str = "default"
    conversation_id: str = "default"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatResponse:
    response: str
    tools_used: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    model: str = "enhanced-nocturnal-agent"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tokens_used: int = 0
    confidence_score: float = 0.0
    execution_results: Dict[str, Any] = field(default_factory=dict)
    api_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class EnhancedNocturnalAgent:
    """
    Enhanced AI Agent with full API integration:
    - Archive API for academic research
    - FinSight API for financial data
    - Shell access for system operations
    - Memory system for context retention
    """
    
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.shell_session = None
        self.memory = {}
        self.daily_token_usage = 0
        self.daily_limit = 100000
        self.daily_query_limit = self._resolve_daily_query_limit()
        self.per_user_query_limit = self.daily_query_limit
        
        # Initialize web search for fallback
        self.web_search = None
        try:
            from .web_search import WebSearchIntegration
            self.web_search = WebSearchIntegration()
        except Exception:
            pass  # Web search optional
        self.daily_query_count = 0
        self.total_cost = 0.0
        self.cost_per_1k_tokens = 0.0001  # Groq pricing estimate
        self._auto_update_enabled = True
        
        # Workflow integration
        from .workflow import WorkflowManager
        self.workflow = WorkflowManager()
        self.last_paper_result = None  # Track last paper mentioned for "save that"
        self.archive = ConversationArchive()

        # Integration handler for Zotero, Mendeley, Notion
        from .handlers import IntegrationHandler, QueryAnalyzer, FileOperations, ShellHandler, FinancialHandler, AgentUtilities, APIHandler
        self.integration_handler = IntegrationHandler()
        self.query_analyzer = QueryAnalyzer()
        self.file_ops = FileOperations()
        self.shell_handler = ShellHandler()
        self.financial_handler = FinancialHandler()
        self.utilities = AgentUtilities()
        self.api_handler = APIHandler()

        # File context tracking (for pronoun resolution and multi-turn)
        self.file_context = {
            'last_file': None,           # Last file mentioned/read
            'last_directory': None,      # Last directory mentioned/navigated
            'recent_files': [],          # Last 5 files (for "those files")
            'recent_dirs': [],           # Last 5 directories
            'current_cwd': None,         # Track shell's current directory
        }
        self._is_windows = os.name == "nt"
        try:
            self.per_user_token_limit = int(os.getenv("GROQ_PER_USER_TOKENS", 50000))
        except (TypeError, ValueError):
            self.per_user_token_limit = 50000  # 50 queries at ~1000 tokens each
        self.user_token_usage: Dict[str, int] = {}
        self.user_query_counts: Dict[str, int] = {}
        self._usage_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._initialized = False
        self._env_loaded = False
        self._init_lock: Optional[asyncio.Lock] = None
        self._default_headers: Dict[str, str] = {}

        # API clients
        self.archive_client = None
        self.finsight_client = None
        self.session = None
        self.company_name_to_ticker = {}

        # Groq key rotation state
        self.api_keys: List[str] = []
        self.current_key_index: int = 0
        self.current_api_key: Optional[str] = None
        self.exhausted_keys: Dict[str, float] = {}
        try:
            self.key_recheck_seconds = float(
                os.getenv("GROQ_KEY_RECHECK_SECONDS", 3600)
            )
        except Exception:
            self.key_recheck_seconds = 3600.0
        
        self._service_roots: List[str] = []
        self._backend_health_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize authentication
        self.auth_token = None
        self.user_id = None
        self._load_authentication()
        try:
            self._health_ttl = float(os.getenv("NOCTURNAL_HEALTH_TTL", 30))
        except Exception:
            self._health_ttl = 30.0
        self._recent_sources: List[Dict[str, Any]] = []

    def _remove_expired_temp_key(self, session_file):
        """Remove expired temporary API key from session file"""
        try:
            import json
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            # Remove temp key fields
            session_data.pop('temp_api_key', None)
            session_data.pop('temp_key_expires', None)
            session_data.pop('temp_key_provider', None)

            # Write back
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to remove expired temp key: {e}")

    def _load_authentication(self):
        """Load authentication from session file"""
        use_local_keys = os.getenv("USE_LOCAL_KEYS", "false").lower() == "true"
        
        debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
        if debug_mode:
            print(f"🔍 _load_authentication: USE_LOCAL_KEYS={os.getenv('USE_LOCAL_KEYS')}, use_local_keys={use_local_keys}")
        
        if not use_local_keys:
            # Backend mode - load auth token from session
            from pathlib import Path
            session_file = Path.home() / ".nocturnal_archive" / "session.json"
            if debug_mode:
                print(f"🔍 _load_authentication: session_file exists={session_file.exists()}")
            if session_file.exists():
                try:
                    import json
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        self.auth_token = session_data.get('auth_token')
                        self.user_id = session_data.get('account_id')

                        # NEW: Check for temporary local API key with expiration
                        temp_key = session_data.get('temp_api_key')
                        temp_key_expires = session_data.get('temp_key_expires')

                        if temp_key and temp_key_expires:
                            # Check if key is still valid
                            from datetime import datetime, timezone
                            try:
                                expires_at = datetime.fromisoformat(temp_key_expires.replace('Z', '+00:00'))
                                now = datetime.now(timezone.utc)

                                if now < expires_at:
                                    # Key is still valid - use local mode for speed!
                                    self.temp_api_key = temp_key
                                    self.temp_key_provider = session_data.get('temp_key_provider', 'cerebras')
                                    if debug_mode:
                                        time_left = (expires_at - now).total_seconds() / 3600
                                        print(f"✅ Using temporary local key (expires in {time_left:.1f}h)")
                                else:
                                    # Key expired - remove it and fall back to backend
                                    if debug_mode:
                                        print(f"⏰ Temporary key expired, using backend mode")
                                    self._remove_expired_temp_key(session_file)
                                    self.temp_api_key = None
                            except Exception as e:
                                if debug_mode:
                                    print(f"⚠️ Error parsing temp key expiration: {e}")
                                self.temp_api_key = None
                        else:
                            self.temp_api_key = None

                        if debug_mode:
                            print(f"🔍 _load_authentication: loaded auth_token={self.auth_token}, user_id={self.user_id}")
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 _load_authentication: ERROR loading session: {e}")
                    self.auth_token = None
                    self.user_id = None
                    self.temp_api_key = None
            else:
                # FALLBACK: Check if config.env has credentials but session.json is missing
                # This handles cases where old setup didn't create session.json
                import json
                email = os.getenv("NOCTURNAL_ACCOUNT_EMAIL")
                account_id = os.getenv("NOCTURNAL_ACCOUNT_ID")
                auth_token = os.getenv("NOCTURNAL_AUTH_TOKEN")
                
                if email and account_id and auth_token:
                    # Auto-create session.json from config.env
                    try:
                        session_data = {
                            "email": email,
                            "account_id": account_id,
                            "auth_token": auth_token,
                            "refresh_token": "auto_generated",
                            "issued_at": datetime.now(timezone.utc).isoformat()
                        }
                        session_file.parent.mkdir(parents=True, exist_ok=True)
                        session_file.write_text(json.dumps(session_data, indent=2))
                        
                        self.auth_token = auth_token
                        self.user_id = account_id
                        
                        if debug_mode:
                            print(f"🔍 _load_authentication: Auto-created session.json from config.env")
                    except Exception as e:
                        if debug_mode:
                            print(f"🔍 _load_authentication: Failed to auto-create session: {e}")
                        self.auth_token = None
                        self.user_id = None
                else:
                    self.auth_token = None
                    self.user_id = None
        else:
            # Local keys mode
            if debug_mode:
                print(f"🔍 _load_authentication: Local keys mode, not loading session")
            self.auth_token = None
            self.user_id = None
        self._session_topics: Dict[str, Dict[str, Any]] = {}

        # Initialize API clients
        self._init_api_clients()
        self._load_ticker_map()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics and cost information"""
        limit = self.daily_limit if self.daily_limit > 0 else 1
        remaining = max(self.daily_limit - self.daily_token_usage, 0)
        usage_percentage = (self.daily_token_usage / limit) * 100 if limit else 0.0
        return {
            "daily_tokens_used": self.daily_token_usage,
            "daily_token_limit": self.daily_limit,
            "remaining_tokens": remaining,
            "usage_percentage": usage_percentage,
            "total_cost": self.total_cost,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "estimated_monthly_cost": self.total_cost * 30,  # Rough estimate
            "per_user_token_limit": self.per_user_token_limit,
            "daily_queries_used": self.daily_query_count,
            "daily_query_limit": self.daily_query_limit,
            "per_user_query_limit": self.per_user_query_limit,
        }
    
    async def close(self):
        """Cleanly close resources (HTTP session and shell)."""
        lock = self._get_init_lock()
        async with lock:
            await self._close_resources()

    async def _close_resources(self):
        try:
            if self.session and not self.session.closed:
                await self.session.close()
        except Exception:
            pass
        finally:
            self.session = None

        try:
            if self.shell_session:
                self.shell_session.terminate()
        except Exception:
            pass
        finally:
            self.shell_session = None

        self.client = None
        self.current_api_key = None
        self.current_key_index = 0
        self._initialized = False
        self.exhausted_keys.clear()
        
    def _init_api_clients(self):
        """Initialize API clients for Archive and FinSight"""
        try:
            def _normalize_base(value: Optional[str], fallback: str) -> str:
                candidate = (value or fallback).strip()
                return candidate[:-1] if candidate.endswith('/') else candidate

            archive_env = (
                os.getenv("ARCHIVE_API_URL")
                or os.getenv("NOCTURNAL_ARCHIVE_API_URL")
            )
            finsight_env = (
                os.getenv("FINSIGHT_API_URL")
                or os.getenv("NOCTURNAL_FINSIGHT_API_URL")
            )

            # Archive API client
            self.archive_base_url = _normalize_base(archive_env, "https://cite-agent-api-720dfadd602c.herokuapp.com/api")

            # FinSight API client
            self.finsight_base_url = _normalize_base(finsight_env, "https://cite-agent-api-720dfadd602c.herokuapp.com/v1/finance")

            # Workspace Files API client
            files_env = os.getenv("FILES_API_URL")
            self.files_base_url = _normalize_base(files_env, "http://127.0.0.1:8000/v1/files")

            # Shared API key handling for protected routes
            self.api_key = (
                os.getenv("NOCTURNAL_KEY")
                or os.getenv("NOCTURNAL_API_KEY")
                or os.getenv("X_API_KEY")
                or "demo-key-123"
            )
            self._default_headers.clear()
            if self.api_key:
                self._default_headers["X-API-Key"] = self.api_key
            
            self._update_service_roots()
            
            # Only show init messages in debug mode
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            if debug_mode:
                if self.api_key == "demo-key-123":
                    print("⚠️ Using demo API key")
                print(f"✅ API clients initialized (Archive={self.archive_base_url}, FinSight={self.finsight_base_url})")
            
        except Exception as e:
            print(f"⚠️ API client initialization warning: {e}")

    def _update_service_roots(self) -> None:
        roots = set()
        for base in (getattr(self, "archive_base_url", None), getattr(self, "finsight_base_url", None), getattr(self, "files_base_url", None)):
            if not base:
                continue
            parsed = urlparse(base)
            if parsed.scheme and parsed.netloc:
                roots.add(f"{parsed.scheme}://{parsed.netloc}")

        if not roots:
            roots.add("http://127.0.0.1:8000")

        self._service_roots = sorted(roots)
        # Drop caches for roots that no longer exist
        for cached in list(self._backend_health_cache.keys()):
            if cached not in self._service_roots:
                self._backend_health_cache.pop(cached, None)

    async def _probe_health_endpoint(self, root: str) -> Tuple[bool, str]:
        if not self.session:
            return False, "HTTP session not initialized"

        if not hasattr(self.session, "get"):
            # Assume healthy when using lightweight mocks that lack GET semantics
            return True, ""

        candidates = ["/readyz", "/health", "/api/health", "/livez"]
        last_detail = ""

        for endpoint in candidates:
            try:
                async with self.session.get(f"{root}{endpoint}", timeout=5) as response:
                    if response.status == 200:
                        return True, ""
                    body = await response.text()
                    if response.status == 404:
                        # Endpoint absent—record detail but keep probing
                        last_detail = (
                            f"{endpoint} missing (404)."
                            if not body else f"{endpoint} missing (404): {body.strip()}"
                        )
                        continue
                    last_detail = (
                        f"{endpoint} returned {response.status}"
                        if not body else f"{endpoint} returned {response.status}: {body.strip()}"
                    )
            except Exception as exc:
                last_detail = f"{endpoint} failed: {exc}"

        # Fall back to a lightweight root probe so services without explicit
        # health endpoints don't register as offline.
        try:
            async with self.session.get(root, timeout=5) as response:
                if response.status < 500:
                    fallback_detail = f"fallback probe returned {response.status}"
                    if response.status == 200:
                        detail = (f"{last_detail}; {fallback_detail}" if last_detail else "")
                    else:
                        detail = (
                            f"{last_detail}; {fallback_detail}"
                            if last_detail else f"Health endpoint unavailable; {fallback_detail}"
                        )
                    return True, detail
        except Exception as exc:  # pragma: no cover - network failure already captured above
            last_detail = last_detail or f"Fallback probe failed: {exc}"

        return False, last_detail or f"Health check failed for {root}"

    async def _check_backend_health(self, force: bool = False) -> Dict[str, Any]:
        now = time.monotonic()
        overall_ok = True
        details: List[str] = []

        if not self._service_roots:
            self._update_service_roots()

        for root in self._service_roots:
            cache = self._backend_health_cache.get(root)
            if cache and not force and now - cache.get("timestamp", 0.0) < self._health_ttl:
                if not cache.get("ok", False) and cache.get("detail"):
                    details.append(cache["detail"])
                    overall_ok = False
                overall_ok = overall_ok and cache.get("ok", False)
                continue

            ok, detail = await self._probe_health_endpoint(root)
            self._backend_health_cache[root] = {"ok": ok, "detail": detail, "timestamp": now}
            if not ok and detail:
                details.append(detail)
            overall_ok = overall_ok and ok

        return {"ok": overall_ok, "detail": "; ".join(details) if details else ""}

    async def _ensure_backend_ready(self) -> Tuple[bool, str]:
        status = await self._check_backend_health()
        return status["ok"], status.get("detail", "")

    def _record_data_source(self, service: str, endpoint: str, success: bool, detail: str = "") -> None:
        entry = {
            "service": service,
            "endpoint": endpoint,
            "success": success,
            "detail": detail,
        }
        self._recent_sources.append(entry)
        if len(self._recent_sources) > 10:
            self._recent_sources = self._recent_sources[-10:]

    def _format_data_sources_footer(self) -> str:
        if not self._recent_sources:
            return ""

        snippets: List[str] = []
        for item in self._recent_sources[:4]:
            status = "ok" if item.get("success") else f"error ({item.get('detail')})" if item.get("detail") else "error"
            snippets.append(f"{item.get('service')} {item.get('endpoint')} – {status}")
        if len(self._recent_sources) > 4:
            snippets.append("…")
        return "Data sources: " + "; ".join(snippets)

    def _reset_data_sources(self) -> None:
        self._recent_sources = []

    def _load_ticker_map(self):
        """Load a simple company name -> ticker map for FinSight lookups."""
        # Start with common aliases
        mapping = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "alphabet": "GOOGL",
            "google": "GOOGL",
            "amazon": "AMZN",
            "nvidia": "NVDA",
            "palantir": "PLTR",
            "shopify": "SHOP",
            "target": "TGT",
            "amd": "AMD",
            "tesla": "TSLA",
            "meta": "META",
            "netflix": "NFLX",
            "goldman sachs": "GS",
            "goldman": "GS",
            "exxonmobil": "XOM",
            "exxon": "XOM",
            "jpmorgan": "JPM",
            "square": "SQ"
        }

        def _augment_from_records(records: List[Dict[str, Any]]) -> None:
            for item in records:
                name = str(item.get("name", "")).lower()
                symbol = item.get("symbol")
                if name and symbol:
                    mapping.setdefault(name, symbol)
                    short = (
                        name.replace("inc.", "")
                        .replace("inc", "")
                        .replace("corporation", "")
                        .replace("corp.", "")
                        .strip()
                    )
                    if short and short != name:
                        mapping.setdefault(short, symbol)

        try:
            supplemental: List[Dict[str, Any]] = []

            try:
                package_resource = resources.files("nocturnal_archive.data").joinpath("company_tickers.json")
                if package_resource.is_file():
                    supplemental = json.loads(package_resource.read_text(encoding="utf-8"))
            except (FileNotFoundError, ModuleNotFoundError, AttributeError):
                supplemental = []

            if not supplemental:
                candidate_paths = [
                    Path(__file__).resolve().parent / "data" / "company_tickers.json",
                    Path("./data/company_tickers.json"),
                ]
                for data_path in candidate_paths:
                    if data_path.exists():
                        supplemental = json.loads(data_path.read_text(encoding="utf-8"))
                        break

            if supplemental:
                _augment_from_records(supplemental)

            override_candidates: List[Path] = []
            override_env = os.getenv("NOCTURNAL_TICKER_MAP")
            if override_env:
                override_candidates.append(Path(override_env).expanduser())

            default_override = Path.home() / ".nocturnal_archive" / "tickers.json"
            override_candidates.append(default_override)

            for override_path in override_candidates:
                if not override_path or not override_path.exists():
                    continue
                try:
                    override_records = json.loads(override_path.read_text(encoding="utf-8"))
                    if isinstance(override_records, list):
                        _augment_from_records(override_records)
                except Exception as override_exc:
                    logger.warning(f"Failed to load ticker override from {override_path}: {override_exc}")
        except Exception:
            pass

        self.company_name_to_ticker = mapping

    def _ensure_environment_loaded(self):
        if self._env_loaded:
            return

        try:
            from .setup_config import NocturnalConfig

            config = NocturnalConfig()
            config.setup_environment()
        except ImportError:
            pass
        except Exception as exc:
            print(f"⚠️ Environment setup warning: {exc}")

        try:
            from dotenv import load_dotenv
            from pathlib import Path
            
            # ONLY load from user's config directory (never from cwd/project root)
            # Project .env.local is for developers, not end users
            env_local = Path.home() / ".nocturnal_archive" / ".env.local"
            if env_local.exists():
                load_dotenv(env_local, override=False)  # Don't override existing env vars
        except ImportError:
            pass  # python-dotenv not installed
        except Exception as exc:
            pass  # Silently fail - not critical
        finally:
            self._env_loaded = True

    def _get_init_lock(self) -> asyncio.Lock:
        if self._init_lock is None:
            self._init_lock = asyncio.Lock()
        return self._init_lock

    async def _get_workspace_listing(self, limit: int = 20) -> Dict[str, Any]:
        params = {"path": ".", "limit": limit, "include_hidden": "false"}
        result = await self._call_files_api("GET", "/", params=params)
        if "error" not in result:
            return result

        fallback = self._fallback_workspace_listing(limit)
        fallback["error"] = result["error"]
        return fallback

    def _fallback_workspace_listing(self, limit: int = 20) -> Dict[str, Any]:
        base = Path.cwd().resolve()
        items: List[Dict[str, str]] = []
        try:
            for entry in sorted(base.iterdir(), key=lambda e: e.name.lower()):
                if entry.name.startswith('.'):
                    continue
                item = {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file"
                }
                items.append(item)
                if len(items) >= limit:
                    break
        except Exception as exc:
            return {
                "base": str(base),
                "items": [],
                "error": f"Unable to list workspace: {exc}"
            }

        return {
            "base": str(base),
            "items": items,
            "note": "Showing up to first {limit} non-hidden entries.".format(limit=limit)
        }

    def _format_workspace_listing_response(self, listing: Dict[str, Any]) -> str:
        base = listing.get("base", Path.cwd().resolve())
        items = listing.get("items")
        if not items:
            items = listing.get("entries", []) or []
        note = listing.get("note")
        error = listing.get("error")
        truncated_flag = listing.get("truncated")

        if not items:
            summary_lines = ["(no visible files in the current directory)"]
        else:
            max_entries = min(len(items), 12)
            summary_lines = [
                f"- {item.get('name')} ({item.get('type', 'unknown')})"
                for item in items[:max_entries]
            ]
            if len(items) > max_entries:
                remaining = len(items) - max_entries
                summary_lines.append(f"… and {remaining} more")

        message_parts = [
            f"Workspace root: {base}",
            "Here are the first entries I can see:",
            "\n".join(summary_lines)
        ]

        if note:
            message_parts.append(note)
        if error:
            message_parts.append(f"Workspace API warning: {error}")
        if truncated_flag:
            message_parts.append("(Listing truncated by workspace service)")

        footer = self._format_data_sources_footer()
        if footer:
            message_parts.append(f"_{footer}_")

        return "\n\n".join(part for part in message_parts if part)

    def _respond_with_workspace_listing(self, request: ChatRequest, listing: Dict[str, Any]) -> ChatResponse:
        message = self._format_workspace_listing_response(listing)

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(request.user_id, request.conversation_id, f"Q: {request.question[:100]}... A: {message[:100]}...")

        items = listing.get("items") or listing.get("entries") or []
        success = "error" not in listing
        self._emit_telemetry(
            "workspace_listing",
            request,
            success=success,
            extra={
                "item_count": len(items),
                "truncated": bool(listing.get("truncated")),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=["files_listing"],
            reasoning_steps=["Direct workspace listing response"],
            tokens_used=0,
            confidence_score=0.7,
            api_results={"workspace_listing": listing}
        )

    def _respond_with_shell_command(self, request: ChatRequest, command: str) -> ChatResponse:
        command_stub = command.split()[0] if command else ""
        if not self._is_safe_shell_command(command):
            message = (
                "I couldn't run that command because it violates the safety policy. "
                "Please try a simpler shell command (no pipes, redirection, or file writes)."
            )
            tools = ["shell_blocked"]
            execution_results = {"command": command, "output": "Command blocked by safety policy", "success": False}
            telemetry_event = "shell_blocked"
            success = False
            output_len = 0
        else:
            output = self.execute_command(command)
            truncated_output = output if len(output) <= 2000 else output[:2000] + "\n… (truncated)"
            message = (
                f"Running the command: `{command}`\n\n"
                "Output:\n```\n"
                f"{truncated_output}\n"
                "```"
            )
            tools = ["shell_execution"]
            success = not output.startswith("ERROR:")
            execution_results = {"command": command, "output": truncated_output, "success": success}
            telemetry_event = "shell_execution"
            output_len = len(truncated_output)

        footer = self._format_data_sources_footer()
        if footer:
            message = f"{message}\n\n_{footer}_"

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            telemetry_event,
            request,
            success=success,
            extra={
                "command": command_stub,
                "output_len": output_len,
            },
        )

        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Direct shell execution"],
            tokens_used=0,
            confidence_score=0.75 if tools == ["shell_execution"] else 0.4,
            execution_results=execution_results
        )
    def _format_currency_value(self, value: float) -> str:
        """Delegate to FinancialHandler"""
        return self.financial_handler.format_currency_value(value)

    def _respond_with_financial_metrics(self, request: ChatRequest, payload: Dict[str, Any]) -> ChatResponse:
        ticker, metrics = next(iter(payload.items()))
        headline = [f"{ticker} key metrics:"]
        citations: List[str] = []

        for metric_name, metric_data in metrics.items():
            if not isinstance(metric_data, dict):
                continue
            value = metric_data.get("value")
            if value is None:
                inner_inputs = metric_data.get("inputs", {})
                entry = inner_inputs.get(metric_name) or next(iter(inner_inputs.values()), {})
                value = entry.get("value")
            formatted_value = self._format_currency_value(value) if value is not None else "(value unavailable)"
            period = metric_data.get("period")
            if not period or (isinstance(period, str) and period.lower().startswith("latest")):
                inner_inputs = metric_data.get("inputs", {})
                entry = inner_inputs.get(metric_name) or next(iter(inner_inputs.values()), {})
                period = entry.get("period")
            sources = metric_data.get("citations") or []
            if sources:
                source_url = sources[0].get("source_url")
                if source_url:
                    citations.append(source_url)
            label = metric_name.replace("Gross", "Gross ").replace("Income", " Income").replace("Net", "Net ")
            label = label.replace("operating", "operating ").replace("Ratio", " Ratio").title()
            if period:
                headline.append(f"• {label}: {formatted_value} (as of {period})")
            else:
                headline.append(f"• {label}: {formatted_value}")

        unique_citations = []
        for c in citations:
            if c not in unique_citations:
                unique_citations.append(c)

        message_parts = ["\n".join(headline)]
        if unique_citations:
            message_parts.append("Sources:\n" + "\n".join(unique_citations))

        footer = self._format_data_sources_footer()
        if footer:
            message_parts.append(f"_{footer}_")

        message = "\n\n".join(message_parts)

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            "financial_metrics",
            request,
            success=True,
            extra={
                "ticker": ticker,
                "metric_count": len(metrics),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=["finsight_api"],
            reasoning_steps=["Direct financial metrics response"],
            tokens_used=0,
            confidence_score=0.8,
            api_results={"financial": payload}
        )

    def _local_file_preview(self, path_str: str) -> Optional[Dict[str, Any]]:
        try:
            p = Path(path_str)
            if not p.exists():
                return None
            if p.is_dir():
                entries = sorted([e.name for e in p.iterdir()][:10])
                return {
                    "path": str(p),
                    "type": "directory",
                    "preview": "\n".join(entries),
                    "encoding": "utf-8",
                    "truncated": False,
                    "size": None,
                }

            stat_result = p.stat()
            if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".parquet", ".zip", ".gif"}:
                return {
                    "path": str(p),
                    "type": "binary",
                    "preview": "(binary file preview skipped)",
                    "encoding": "binary",
                    "truncated": False,
                    "size": stat_result.st_size,
                }

            content = p.read_text(errors="ignore")
            truncated = len(content) > 65536
            snippet = content[:65536]
            preview = "\n".join(snippet.splitlines()[:60])
            return {
                "path": str(p),
                "type": "text",
                "preview": preview,
                "encoding": "utf-8",
                "truncated": truncated,
                "size": stat_result.st_size,
            }
        except Exception as exc:
            return {
                "path": path_str,
                "type": "error",
                "preview": f"error: {exc}",
                "encoding": "utf-8",
                "truncated": False,
                "size": None,
            }

    async def _preview_file(self, path_str: str) -> Optional[Dict[str, Any]]:
        params = {"path": path_str}
        result = await self._call_files_api("GET", "/preview", params=params)
        if "error" not in result:
            encoding = result.get("encoding", "utf-8")
            return {
                "path": result.get("path", path_str),
                "type": "text" if encoding == "utf-8" else "binary",
                "preview": result.get("content", ""),
                "encoding": encoding,
                "truncated": bool(result.get("truncated", False)),
                "size": result.get("size"),
            }

        message = result.get("error", "")
        if message and "does not exist" in message.lower():
            return None

        fallback = self._local_file_preview(path_str)
        if fallback:
            fallback.setdefault("error", message)
            return fallback
        return {
            "path": path_str,
            "type": "error",
            "preview": "",
            "encoding": "utf-8",
            "truncated": False,
            "size": None,
            "error": message,
        }

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        return False

    def _is_simple_greeting(self, text: str) -> bool:
        """Delegate to QueryAnalyzer"""
        return self.query_analyzer.is_simple_greeting(text)

    def _is_casual_acknowledgment(self, text: str) -> bool:
        """Delegate to QueryAnalyzer"""
        return self.query_analyzer.is_casual_acknowledgment(text)

    def _detect_language_preference(self, text: str) -> None:
        """
        Detect and store user's language preference from input text.
        Supports Traditional Chinese (繁體中文), English, and other languages.
        """
        text_lower = text.lower()
        
        # Check for Chinese characters (CJK)
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        # Explicit language requests
        if 'chinese' in text_lower or '中文' in text or 'traditional' in text_lower:
            self.language_preference = 'zh-TW'
        elif 'english' in text_lower:
            self.language_preference = 'en'
        elif has_chinese:
            # Detected Chinese characters
            self.language_preference = 'zh-TW'
        else:
            # Default to English if not specified
            if not hasattr(self, 'language_preference'):
                self.language_preference = 'en'

    def _is_generic_test_prompt(self, text: str) -> bool:
        """Delegate to QueryAnalyzer"""
        return self.query_analyzer.is_generic_test_prompt(text)

    def _is_location_query(self, text: str) -> bool:
        """Delegate to QueryAnalyzer"""
        return self.query_analyzer.is_location_query(text)

    def _format_api_results_for_prompt(self, api_results: Dict[str, Any]) -> str:
        if not api_results:
            logger.info("🔍 DEBUG: _format_api_results_for_prompt called with EMPTY api_results")
            return "No API results yet."

        # Special formatting for shell results to make them VERY clear
        if "shell_info" in api_results:
            shell_info = api_results["shell_info"]
            formatted_parts = ["=" * 60]
            formatted_parts.append("🔧 SHELL COMMAND EXECUTION RESULTS (ALREADY EXECUTED)")
            formatted_parts.append("=" * 60)

            if "command" in shell_info:
                formatted_parts.append(f"\n📝 Command that was executed:")
                formatted_parts.append(f"   $ {shell_info['command']}")

            if "output" in shell_info:
                formatted_parts.append(f"\n📤 Command output (THIS IS THE RESULT):")
                # Check if this is a file read command
                command = shell_info.get("command", "")
                if any(cmd in command for cmd in ["cat", "head", "tail", "less", "read_file"]):
                    formatted_parts.append(f"FILE CONTENTS BELOW - USE THIS TO ANSWER THE QUESTION:")
                formatted_parts.append(f"{shell_info['output']}")

            if "error" in shell_info:
                formatted_parts.append(f"\n❌ Error occurred:")
                formatted_parts.append(f"{shell_info['error']}")

            if "directory_contents" in shell_info:
                formatted_parts.append(f"\n📂 Directory listing (THIS IS THE RESULT):")
                formatted_parts.append(f"{shell_info['directory_contents']}")

            if "search_results" in shell_info:
                formatted_parts.append(f"\n🔍 Search results (THIS IS THE RESULT):")
                formatted_parts.append(f"{shell_info['search_results']}")

            formatted_parts.append("\n" + "=" * 60)
            formatted_parts.append("🚨 CRITICAL INSTRUCTION 🚨")
            formatted_parts.append("The command was ALREADY executed. The output above is the result.")
            # Check if this is a file read to give specific instructions
            command = shell_info.get("command", "")
            if any(cmd in command for cmd in ["cat", "head", "tail", "less", "read_file"]):
                formatted_parts.append("THIS IS A FILE READ OPERATION.")
                formatted_parts.append("The file contents are provided above.")
                formatted_parts.append("ANALYZE THE ACTUAL FILE CONTENT and answer based on what you see.")
                formatted_parts.append("DO NOT say 'based on provided content' or 'the snippet shows' - just answer directly.")
                formatted_parts.append("DO NOT suggest running commands - the file was already read.")
            else:
                formatted_parts.append("Present the KEY information concisely - summarize, don't paste everything.")
                formatted_parts.append("For file listings: list key files/directories, skip metadata unless asked.")
                formatted_parts.append("For search results: answer directly, cite relevant findings.")
                formatted_parts.append("For file content: show relevant sections only.")
            formatted_parts.append("If output is empty: say 'No results found'.")
            formatted_parts.append("DO NOT ask the user to run commands - results are already here.")
            formatted_parts.append("=" * 60)

            # Add other api_results
            other_results = {k: v for k, v in api_results.items() if k != "shell_info"}
            if other_results:
                try:
                    serialized = json.dumps(other_results, indent=2)
                except Exception:
                    serialized = str(other_results)
                formatted_parts.append(f"\nOther data:\n{serialized}")

            return "\n".join(formatted_parts)

        # Normal formatting for non-shell results
        try:
            serialized = json.dumps(api_results, indent=2)
        except Exception:
            serialized = str(api_results)
        max_len = 3000  # Aggressive limit to prevent token explosion
        if len(serialized) > max_len:
            serialized = serialized[:max_len] + "\n... (truncated for length)"

        # DEBUG: Log formatted results length and preview
        logger.info(f"🔍 DEBUG: _format_api_results_for_prompt returning {len(serialized)} chars")
        if "research" in api_results:
            papers_count = len(api_results.get("research", {}).get("results", []))
            logger.info(f"🔍 DEBUG: api_results contains 'research' with {papers_count} papers")

        return serialized

    def _build_system_prompt(
        self,
        request_analysis: Dict[str, Any],
        memory_context: str,
        api_results: Dict[str, Any]
    ) -> str:
        sections: List[str] = []
        apis = request_analysis.get("apis", [])

        # TRUTH-SEEKING CORE IDENTITY
        analysis_mode = request_analysis.get("analysis_mode", "quantitative")
        dev_mode = self.client is not None

        # Identity and capabilities
        intro = (
            "You are Cite Agent, a research and analysis assistant with access to:\n"
            "• Persistent shell (Python, R, SQL, Bash)\n"
            "• File operations (read, write, edit, search)\n"
            "• Academic papers (Archive API - 200M+ papers)\n"
            "• Financial data (FinSight API - SEC filings)\n"
            "• Web search\n\n"
            "Communication style: Be natural, direct, and helpful. "
            "Think like a capable research partner, not a rigid assistant."
        )
        sections.append(intro)

        # Behavioral guidelines
        guidelines = [
            "Use tools proactively - search files, run commands, query APIs when needed.",
            "Cite sources: papers (title+authors), files (path:line), API data.",
            "shell_info shows already-executed commands. Present RESULTS concisely - no commands shown.",
            "For follow-up questions with pronouns ('it', 'that'), infer from conversation context.",
            "",
            "🚨 CRITICAL - VAGUE QUERY HANDLING:",
            "• If api_results contains query_analysis with is_vague=True: The query is TOO VAGUE.",
            "• DO NOT guess, search files, or make assumptions.",
            "• RESPOND NATURALLY: Ask what they meant or acknowledge their message.",
            "• Examples: 'test' → 'Sure, what would you like to test?'",
            "•           'hello' → 'Hi! How can I help you today?'",
            "•           'thanks' → 'You're welcome! Let me know if you need anything else.'",
            "",
            "Be honest about uncertainty.",
            "",
            "CRITICAL - ANSWER WHAT WAS ASKED:",
            "• When query asks for SPECIFIC file types:",
            "  - Use shell_execution with 'find' or 'ls' filtered to match",
            "  - Example: 'Python files' → run `find . -name '*.py'` or `ls **/*.py`",
            "  - Example: 'test files' → run `find . -name '*test*.py'`",
            "  - If files_listing used, extract ONLY matching files from result",
            "• 'Find X' → Use tools to locate, return concise path",
            "• 'Read X' or 'explain function in file.py' → ALWAYS read the file first using `cat` command",
            "  - If api_results shows 'files_missing', the file exists but wasn't auto-read - use cat to read it",
            "  - Example: 'Read main() in cli.py' → run `cat cite_agent/cli.py | grep -A 50 'def main'`",
            "  - NEVER hallucinate file contents or say 'based on provided content' without actually reading",
            "• 'What does X do?' → Answer from visible code/context, no re-execution",
            "• 'What version' → Include word 'version' in answer (e.g. 'Version is v1.4.0')",
            "",
            "- If asked \"who built you?\" or \"who is your developer?\" or \"whats the name of your developer\" → Answer: \"I was built by Phyrexian.\" (If the user asks you to say his name, you should say \"Phyrexian\" as his name)",
            "",
            "- LANGUAGE:",
            "- If asked to reply in chinese, you MUST reply in Traditional Chinese (繁體中文).",
            "- You MUST use Chinese characters (漢字), NOT pinyin romanization.",
            "",
            "CONCISE RESPONSE STYLE:",
            "• Direct answers - state result, minimal elaboration",
            "• NO code blocks showing bash/python commands unless explicitly asked",
            "• NO 'Let me check...' preambles",
            "• File listings: Max 5-10 items (filtered to query)",
            "• Balance: complete but concise"
        ]

        guidelines.extend([
            "",
            "- COMMUNICATION RULES:",
            "- You MUST NOT return an empty response. EVER.",
            "- Before using a tool (like running a shell command or reading a file), you MUST first state your intent to the user in a brief, natural message. (e.g., \"Okay, I'll check the contents of that directory,\" or \"I will search for that file.\")",
        ])

        guidelines.extend([
            "",
            "- PROACTIVE FILE SEARCH:",
            "- If a user asks to find a file or directory and you are not sure where it is, use the `find` command with wildcards to search for it.",
            "- If a `cd` command fails, automatically run `ls -F` on the current or parent directory to understand the directory structure and find the correct path.",
        ])

        sections.append("\n".join(guidelines))

        # Add memory context if available
        if memory_context:
            sections.append("\nRecent context:\n" + memory_context.strip())

        # Add API results if available
        api_results_text = self._format_api_results_for_prompt(api_results)
        if api_results_text.strip():
            # Check if we have research data
            if api_results.get("research"):
                sections.append("\n🔬 RESEARCH DATA (ALREADY FETCHED):\n" +
                              "The papers below were retrieved from Archive API. " +
                              "Present THESE papers to the user - do NOT hallucinate or search for more.\n" +
                              api_results_text)
            elif api_results.get("financial"):
                sections.append("\n💰 FINANCIAL DATA (ALREADY FETCHED):\n" +
                              "The metrics below were retrieved from FinSight API. " +
                              "Present THESE numbers to the user - do NOT search for more.\n" +
                              api_results_text)
            else:
                sections.append("\nData available:\n" + api_results_text)

        return "\n\n".join(sections)

    def _quick_reply(
        self,
        request: ChatRequest,
        message: str,
        tools_used: Optional[List[str]] = None,
        confidence: float = 0.6
    ) -> ChatResponse:
        tools = tools_used or []
        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )
        self._emit_telemetry(
            "quick_reply",
            request,
            success=True,
            extra={
                "tools_used": tools,
            },
        )
        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Quick reply without LLM"],
            timestamp=datetime.now().isoformat(),
            tokens_used=0,
            confidence_score=confidence,
            execution_results={},
            api_results={}
        )

    def _select_model(
        self,
        request: ChatRequest,
        request_analysis: Dict[str, Any],
        api_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        question = request.question.strip()
        apis = request_analysis.get("apis", [])
        use_light_model = False

        if len(question) <= 180 and not api_results and not apis:
            use_light_model = True
        elif len(question) <= 220 and set(apis).issubset({"shell"}):
            use_light_model = True
        elif len(question.split()) <= 40 and request_analysis.get("type") in {"general", "system"} and not api_results:
            use_light_model = True

        # Select model based on LLM provider
        if getattr(self, 'llm_provider', 'groq') == 'cerebras':
            if use_light_model:
                return {
                    "model": "llama3.1-8b",  # Cerebras 8B model
                    "max_tokens": 520,
                    "temperature": 0.2
                }
            return {
                "model": "gpt-oss-120b",  # PRODUCTION: Cerebras gpt-oss-120b - 100% test pass, 60K TPM
                "max_tokens": 900,
                "temperature": 0.3
            }
        else:
            # Groq models
            if use_light_model:
                return {
                    "model": "llama-3.1-8b-instant",
                    "max_tokens": 520,
                    "temperature": 0.2
                }
            return {
                "model": "openai/gpt-oss-120b",  # PRODUCTION: 120B model - 100% test pass rate
                "max_tokens": 900,
                "temperature": 0.3
            }

    def _mark_current_key_exhausted(self, reason: str = "rate_limit"):
        if not self.api_keys:
            return
        key = self.api_keys[self.current_key_index]
        self.exhausted_keys[key] = time.time()
        logger.warning(f"Groq key index {self.current_key_index} marked exhausted ({reason})")

    def _rotate_to_next_available_key(self) -> bool:
        if not self.api_keys:
            return False

        attempts = 0
        total = len(self.api_keys)
        now = time.time()

        while attempts < total:
            self.current_key_index = (self.current_key_index + 1) % total
            key = self.api_keys[self.current_key_index]
            exhausted_at = self.exhausted_keys.get(key)
            if exhausted_at:
                if now - exhausted_at >= self.key_recheck_seconds:
                    del self.exhausted_keys[key]
                else:
                    attempts += 1
                    continue
            try:
                if self.llm_provider == "cerebras":
                    from openai import OpenAI
                    self.client = OpenAI(
                        api_key=key,
                        base_url="https://api.cerebras.ai/v1"
                    )
                else:
                    self.client = Groq(api_key=key)
                self.current_api_key = key
                return True
            except Exception as e:
                logger.error(f"Failed to initialize {self.llm_provider.upper()} client for rotated key: {e}")
                self.exhausted_keys[key] = now
                attempts += 1
        return False

    def _ensure_client_ready(self) -> bool:
        if self.client and self.current_api_key:
            return True

        if not self.api_keys:
            return False

        total = len(self.api_keys)
        attempts = 0
        now = time.time()

        while attempts < total:
            key = self.api_keys[self.current_key_index]
            exhausted_at = self.exhausted_keys.get(key)
            if exhausted_at and (now - exhausted_at) < self.key_recheck_seconds:
                attempts += 1
                self.current_key_index = (self.current_key_index + 1) % total
                continue

            if exhausted_at and (now - exhausted_at) >= self.key_recheck_seconds:
                del self.exhausted_keys[key]

            try:
                if self.llm_provider == "cerebras":
                    from openai import OpenAI
                    self.client = OpenAI(
                        api_key=key,
                        base_url="https://api.cerebras.ai/v1"
                    )
                else:
                    self.client = Groq(api_key=key)
                self.current_api_key = key
                return True
            except Exception as e:
                logger.error(f"Failed to initialize {self.llm_provider.upper()} client for key index {self.current_key_index}: {e}")
                self.exhausted_keys[key] = now
                attempts += 1
                self.current_key_index = (self.current_key_index + 1) % total

        return False

    def _schedule_next_key_rotation(self):
        if len(self.api_keys) <= 1:
            return
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        new_key = self.api_keys[self.current_key_index]
        self.current_api_key = new_key

        # Reinitialize client with new key
        try:
            if self.llm_provider == "cerebras":
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=new_key,
                    base_url="https://api.cerebras.ai/v1"
                )
            else:
                from groq import Groq
                self.client = Groq(api_key=new_key)
        except Exception as e:
            # If initialization fails, set to None to fallback to backend
            self.client = None
            self.current_api_key = None

    def _is_rate_limit_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "rate limit" in message or "429" in message

    def _respond_with_fallback(
        self,
        request: ChatRequest,
        tools_used: List[str],
        api_results: Dict[str, Any],
        failure_reason: str,
        error_message: Optional[str] = None
    ) -> ChatResponse:
        tools = list(tools_used) if tools_used else []
        if "fallback" not in tools:
            tools.append("fallback")

        header = "⚠️ Temporary LLM downtime\n\n"

        if self._is_simple_greeting(request.question):
            body = (
                "Hi there! I'm currently at my Groq capacity, so I can't craft a full narrative response just yet. "
                "You're welcome to try again in a little while, or I can still fetch finance and research data for you."
            )
        else:
            details: List[str] = []

            financial = api_results.get("financial")
            if financial:
                payload_full = json.dumps(financial, indent=2)
                payload = payload_full[:1500]
                if len(payload_full) > 1500:
                    payload += "\n…"
                details.append(f"**Finance API snapshot**\n```json\n{payload}\n```")

            research = api_results.get("research")
            if research:
                # Format research results conversationally (no JSON dump)
                results = research.get("results", [])

                if not results:
                    details.append("📚 No papers found for your query. Try different search terms or broader keywords.")
                else:
                    # Create conversational paper list
                    paper_list = []
                    for i, paper in enumerate(results[:10], 1):
                        title = paper.get("title", "Untitled")
                        authors = paper.get("authors", [])
                        author_str = ", ".join([a.get("name", "") for a in authors[:2]])
                        if len(authors) > 2:
                            author_str += f" et al."
                        year = paper.get("year", "n.d.")
                        citations = paper.get("citationCount", 0)

                        paper_entry = f"{i}. **{title}**"
                        if author_str:
                            paper_entry += f"\n   Authors: {author_str}"
                        paper_entry += f"\n   Year: {year} | Citations: {citations:,}"

                        # Add abstract preview if available
                        abstract = paper.get("abstract", "")
                        if abstract:
                            preview = abstract[:150].strip()
                            if len(abstract) > 150:
                                preview += "..."
                            paper_entry += f"\n   {preview}"

                        paper_list.append(paper_entry)

                    details.append(f"📚 **Found {len(results)} papers:**\n\n" + "\n\n".join(paper_list))

            files_context = api_results.get("files_context")
            if files_context:
                preview = files_context[:600]
                if len(files_context) > 600:
                    preview += "\n…"
                details.append(f"**File preview**\n{preview}")

            if details:
                body = (
                    "I've gathered the information you requested. While I'm temporarily at Groq capacity for detailed analysis, "
                    "here's what I found:"
                ) + "\n\n" + "\n\n".join(details)
            else:
                body = (
                    "I'm temporarily out of Groq quota, so I can't compose a full answer. "
                    "Please try again in a bit, or ask me to queue this work for later."
                )

        footer = (
            "\n\nNext steps:\n"
            "• Wait for the Groq daily quota to reset (usually within 24 hours).\n"
            "• Add another API key in your environment for automatic rotation.\n"
            "• Keep the conversation open—I’ll resume normal replies once capacity returns."
        )

        message = header + body + footer

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            "fallback_response",
            request,
            success=False,
            extra={
                "failure_reason": failure_reason,
                "has_financial_payload": bool(api_results.get("financial")),
                "has_research_payload": bool(api_results.get("research")),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Fallback response activated"],
            timestamp=datetime.now().isoformat(),
            tokens_used=0,
            confidence_score=0.2,
            execution_results={},
            api_results=api_results,
            error_message=error_message or failure_reason
        )

    def _extract_tickers_from_text(self, text: str) -> List[str]:
        """Delegate to FinancialHandler"""
        return self.financial_handler.extract_tickers_from_text(text, self.company_name_to_ticker)

    def _plan_financial_request(self, question: str, session_key: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """Delegate to FinancialHandler"""
        return self.financial_handler.plan_financial_request(
            question, self.company_name_to_ticker, self._session_topics, session_key
        )
    
    async def initialize(self, force_reload: bool = False):
        """Initialize the agent with API keys and shell session."""
        lock = self._get_init_lock()
        async with lock:
            if self._initialized and not force_reload:
                return True

            if self._initialized and force_reload:
                await self._close_resources()

            # Check for updates automatically (silent background check)
            self._check_updates_background()
            self._ensure_environment_loaded()
            self._init_api_clients()
            
            # Suppress verbose initialization messages in production
            import logging
            logging.getLogger("aiohttp").setLevel(logging.ERROR)
            logging.getLogger("asyncio").setLevel(logging.ERROR)

            # SECURITY FIX: No API keys on client!
            # All API calls go through our secure backend
            # This prevents key extraction and piracy
            # DISABLED for beta testing - set USE_LOCAL_KEYS=false to enable backend-only mode

            # SECURITY: Production users MUST use backend for monetization
            # Priority: 1) Session exists → backend, 2) USE_LOCAL_KEYS → dev mode
            from pathlib import Path
            session_file = Path.home() / ".nocturnal_archive" / "session.json"
            has_session = session_file.exists()
            use_local_keys_env = os.getenv("USE_LOCAL_KEYS", "").lower()

            # Priority order for key mode:
            # 1. USE_LOCAL_KEYS env var (explicit override)
            # 2. Temp API key from session (fast mode)
            # 3. Default to backend if session exists

            # Debug temp key detection
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            if debug_mode:
                print(f"🔍 initialize: has_session={has_session}, hasattr(temp_api_key)={hasattr(self, 'temp_api_key')}, temp_api_key={getattr(self, 'temp_api_key', None)}")
                print(f"🔍 initialize: use_local_keys_env='{use_local_keys_env}'")

            if use_local_keys_env == "true":
                # Explicit local keys mode - always respect this
                use_local_keys = True
            elif use_local_keys_env == "false":
                # Explicit backend mode
                use_local_keys = False
            elif has_session and hasattr(self, 'temp_api_key') and self.temp_api_key:
                # Session exists with temp key → use local mode (fast!)
                use_local_keys = True
                if debug_mode:
                    print(f"✅ Detected temp key - using LOCAL mode!")
            elif has_session:
                # Session exists but no temp key → use backend mode
                use_local_keys = False
                if debug_mode:
                    print(f"ℹ️  Session exists but no temp key - using BACKEND mode")
            else:
                # No session, no explicit setting → default to backend
                use_local_keys = False

            if not use_local_keys:
                self.api_keys = []  # Empty - keys stay on server
                self.current_key_index = 0
                self.current_api_key = None
                self.client = None  # Will use HTTP client instead

                # Get backend API URL from config
                self.backend_api_url = os.getenv(
                    "NOCTURNAL_API_URL",
                    "https://cite-agent-api-720dfadd602c.herokuapp.com/api"  # Production Heroku backend
                )

                # Get auth token from session (set by auth.py after login)
                from pathlib import Path
                session_file = Path.home() / ".nocturnal_archive" / "session.json"
                if session_file.exists():
                    try:
                        import json
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                            self.auth_token = session_data.get('auth_token')
                            self.user_id = session_data.get('account_id')
                    except Exception:
                        self.auth_token = None
                        self.user_id = None
                else:
                    self.auth_token = None
                    self.user_id = None

                # Suppress messages in production (only show in debug mode)
                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    if self.auth_token:
                        print(f"✅ Enhanced Nocturnal Agent Ready! (Authenticated)")
                    else:
                        print("⚠️ Not authenticated. Please log in to use the agent.")
            else:
                # Local keys mode - use temporary key if available, otherwise load from env

                # Check if we have a temporary key (for speed + security)
                if hasattr(self, 'temp_api_key') and self.temp_api_key:
                    # Use temporary key provided by backend
                    self.api_keys = [self.temp_api_key]
                    self.llm_provider = getattr(self, 'temp_key_provider', 'cerebras')
                else:
                    # Fallback: Load permanent keys from environment (dev mode only)
                    self.auth_token = None
                    self.user_id = None

                    # Load Cerebras keys from environment (PRIMARY)
                    self.api_keys = []
                    for i in range(1, 10):  # Check CEREBRAS_API_KEY_1 through CEREBRAS_API_KEY_9
                        key = os.getenv(f"CEREBRAS_API_KEY_{i}") or os.getenv(f"CEREBRAS_API_KEY")
                        if key and key not in self.api_keys:
                            self.api_keys.append(key)

                # Fallback to Groq keys if no Cerebras keys found
                if not self.api_keys:
                    for i in range(1, 10):
                        key = os.getenv(f"GROQ_API_KEY_{i}") or os.getenv(f"GROQ_API_KEY")
                        if key and key not in self.api_keys:
                            self.api_keys.append(key)
                    self.llm_provider = "groq"
                else:
                    self.llm_provider = "cerebras"

                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if not self.api_keys:
                    if debug_mode:
                        print("⚠️ No LLM API keys found. Set CEREBRAS_API_KEY or GROQ_API_KEY")
                else:
                    if debug_mode:
                        print(f"✅ Loaded {len(self.api_keys)} {self.llm_provider.upper()} API key(s)")
                    # Initialize first client - Cerebras uses OpenAI-compatible API
                    try:
                        if self.llm_provider == "cerebras":
                            # Cerebras uses OpenAI client with custom base URL
                            from openai import OpenAI
                            self.client = OpenAI(
                                api_key=self.api_keys[0],
                                base_url="https://api.cerebras.ai/v1"
                            )
                        else:
                            # Groq fallback
                            from groq import Groq
                            self.client = Groq(api_key=self.api_keys[0])
                        self.current_api_key = self.api_keys[0]
                        self.current_key_index = 0
                    except Exception as e:
                        print(f"⚠️ Failed to initialize {self.llm_provider.upper()} client: {e}")

            # Initialize shell session for BOTH production and dev mode
            # Production users need code execution too (like Cursor/Aider)
            if self.shell_session and self.shell_session.poll() is not None:
                self.shell_session = None

            if self.shell_session is None:
                try:
                    if self._is_windows:
                        command = ['powershell', '-NoLogo', '-NoProfile']
                    else:
                        command = ['bash']
                    self.shell_session = subprocess.Popen(
                        command,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=os.getcwd()
                    )
                except Exception as exc:
                    print(f"⚠️ Unable to launch persistent shell session: {exc}")
                    self.shell_session = None

            if self.session is None or getattr(self.session, "closed", False):
                if self.session and not self.session.closed:
                    await self.session.close()
                default_headers = dict(getattr(self, "_default_headers", {}))
                self.session = aiohttp.ClientSession(headers=default_headers)

            self._initialized = True
            return True
    
    def _check_updates_background(self):
        """Check for updates and auto-install if available"""
        if not self._auto_update_enabled:
            return
        
        # Check for updates (synchronous, fast)
        try:
            from .updater import NocturnalUpdater
            updater = NocturnalUpdater()
            update_info = updater.check_for_updates()
            
            if update_info and update_info["available"]:
                # Auto-update silently in background
                import threading
                def do_update():
                    try:
                        updater.update_package(silent=True)
                    except:
                        pass
                threading.Thread(target=do_update, daemon=True).start()
                
        except Exception:
            # Silently ignore update check failures
            pass
    
    async def call_backend_query(self, query: str, conversation_history: Optional[List[Dict]] = None, 
                                 api_results: Optional[Dict[str, Any]] = None, tools_used: Optional[List[str]] = None) -> ChatResponse:
        """
        Call backend /query endpoint instead of Groq directly
        This is the SECURE method - all API keys stay on server
        Includes API results (Archive, FinSight) in context for better responses
        """
        # DEBUG: Print auth status
        debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
        if debug_mode:
            print(f"🔍 call_backend_query: auth_token={self.auth_token}, user_id={self.user_id}")
        
        if not self.auth_token:
            return ChatResponse(
                response="❌ Not authenticated. Please log in first.",
                error_message="Authentication required"
            )
        
        if not self.session:
            return ChatResponse(
                response="❌ HTTP session not initialized",
                error_message="Session not initialized"
            )
        
        try:
            # Detect language preference from stored state
            language = getattr(self, 'language_preference', 'en')
            
            # Build system instruction for language enforcement
            system_instruction = ""
            if language == 'zh-TW':
                system_instruction = "CRITICAL: You MUST respond entirely in Traditional Chinese (繁體中文). Use Chinese characters (漢字), NOT pinyin romanization. All explanations, descriptions, and responses must be in Chinese characters."
            
            # Build request with API context as separate field
            payload = {
                "query": query,  # Keep query clean
                "conversation_history": conversation_history or [],
                "api_context": api_results,  # Send API results separately
                "model": "openai/gpt-oss-120b",  # PRODUCTION: 120B - best test results
                "temperature": 0.2,  # Low temp for accuracy
                "max_tokens": 4000,
                "language": language,  # Pass language preference
                "system_instruction": system_instruction if system_instruction else None  # Only include if set
            }
            
            # Call backend
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.backend_api_url}/query/"
            
            async with self.session.post(url, json=payload, headers=headers, timeout=60) as response:
                if response.status == 401:
                    return ChatResponse(
                        response="❌ Authentication expired. Please log in again.",
                        error_message="Authentication expired"
                    )
                
                elif response.status == 429:
                    # Rate limit exceeded
                    data = await response.json()
                    detail = data.get('detail', {})
                    tokens_remaining = detail.get('tokens_remaining', 0)
                    return ChatResponse(
                        response=f"❌ Daily token limit reached. You have {tokens_remaining} tokens remaining today. The limit resets tomorrow.",
                        error_message="Rate limit exceeded",
                        tokens_used=detail.get('tokens_used_today', 0)
                    )
                
                elif response.status == 503:
                    # Backend AI service temporarily unavailable (Cerebras/Groq rate limited)
                    # Auto-retry silently with exponential backoff

                    print("\n💭 Thinking... (backend is busy, retrying automatically)")

                    retry_delays = [5, 15, 30]  # Exponential backoff
                    
                    for retry_num, delay in enumerate(retry_delays):
                        await asyncio.sleep(delay)
                        
                        # Retry the request
                        async with self.session.post(url, json=payload, headers=headers, timeout=60) as retry_response:
                            if retry_response.status == 200:
                                # Success!
                                data = await retry_response.json()
                                response_text = data.get('response', '')
                                tokens = data.get('tokens_used', 0)
                                
                                all_tools = tools_used or []
                                all_tools.append("backend_llm")
                                
                                self.workflow.save_query_result(
                                    query=query,
                                    response=response_text,
                                    metadata={
                                        "tools_used": all_tools,
                                        "tokens_used": tokens,
                                        "model": data.get('model'),
                                        "provider": data.get('provider'),
                                        "retries": retry_num + 1
                                    }
                                )
                                
                                return ChatResponse(
                                    response=response_text,
                                    tokens_used=tokens,
                                    tools_used=all_tools,
                                    model=data.get('model', 'openai/gpt-oss-120b'),
                                    timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                                    api_results=api_results
                                )
                            elif retry_response.status != 503:
                                # Different error, stop retrying
                                break
                    
                    # All retries exhausted
                    return ChatResponse(
                        response="❌ Service unavailable. Please try again in a few minutes.",
                        error_message="Service unavailable after retries"
                    )
                
                elif response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '')
                    tokens = data.get('tokens_used', 0)
                    
                    # Combine tools used
                    all_tools = tools_used or []
                    all_tools.append("backend_llm")
                    
                    # Save to workflow history
                    self.workflow.save_query_result(
                        query=query,
                        response=response_text,
                        metadata={
                            "tools_used": all_tools,
                            "tokens_used": tokens,
                            "model": data.get('model'),
                            "provider": data.get('provider')
                        }
                    )
                    
                    return ChatResponse(
                        response=response_text,
                        tokens_used=tokens,
                        tools_used=all_tools,
                        model=data.get('model', 'openai/gpt-oss-120b'),
                        timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                        api_results=api_results
                    )
                
                else:
                    error_text = await response.text()
                    return ChatResponse(
                        response=f"❌ Backend error (HTTP {response.status}): {error_text}",
                        error_message=f"HTTP {response.status}"
                    )
        
        except asyncio.TimeoutError:
            return ChatResponse(
                response="❌ Request timeout. Please try again.",
                error_message="Timeout"
            )
        except Exception as e:
            return ChatResponse(
                response=f"❌ Error calling backend: {str(e)}",
                error_message=str(e)
            )
    
    async def _call_files_api(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Any = None,
    ) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.call_files_api(
            method, endpoint,
            params=params,
            json_body=json_body,
            data=data,
            session=self.session,
            files_base_url=self.files_base_url,
            ensure_backend_ready_fn=self._ensure_backend_ready,
            record_data_source_fn=self._record_data_source
        )

    async def _call_archive_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.call_archive_api(
            endpoint, data,
            session=self.session,
            archive_base_url=self.archive_base_url,
            auth_token=self.auth_token,
            ensure_backend_ready_fn=self._ensure_backend_ready,
            record_data_source_fn=self._record_data_source
        )
    
    async def _call_finsight_api(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.call_finsight_api(
            endpoint, params,
            session=self.session,
            finsight_base_url=self.finsight_base_url,
            auth_token=self.auth_token,
            ensure_backend_ready_fn=self._ensure_backend_ready,
            record_data_source_fn=self._record_data_source
        )
    
    async def _call_finsight_api_post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        default_headers = getattr(self, "_default_headers", None)
        return await self.api_handler.call_finsight_api_post(
            endpoint, data,
            session=self.session,
            finsight_base_url=self.finsight_base_url,
            default_headers=default_headers,
            ensure_backend_ready_fn=self._ensure_backend_ready,
            record_data_source_fn=self._record_data_source
        )
    
    async def search_academic_papers(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.search_academic_papers(
            query, limit,
            call_archive_api_fn=self._call_archive_api
        )

    async def synthesize_research(self, paper_ids: List[str], max_words: int = 500) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.synthesize_research(
            paper_ids, max_words,
            call_archive_api_fn=self._call_archive_api
        )

    async def get_financial_data(self, ticker: str, metric: str, limit: int = 12) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.get_financial_data(
            ticker, metric, limit,
            call_finsight_api_fn=self._call_finsight_api
        )

    async def get_financial_metrics(self, ticker: str, metrics: List[str] = None) -> Dict[str, Any]:
        """Delegate to APIHandler"""
        return await self.api_handler.get_financial_metrics(
            ticker, metrics,
            call_finsight_api_fn=self._call_finsight_api
        )

    def _detect_integration_request(self, question: str) -> Optional[Dict[str, Any]]:
        """Delegate to IntegrationHandler"""
        return self.integration_handler.detect_integration_request(question)

    def _extract_papers_from_context(self, api_results: Dict[str, Any], question: str) -> List[Dict[str, Any]]:
        """Delegate to IntegrationHandler"""
        return self.integration_handler.extract_papers_from_context(api_results, question)

    async def _push_to_integration_conversational(
        self,
        target: str,
        papers: List[Dict[str, Any]],
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delegate to IntegrationHandler"""
        return await self.integration_handler.push_to_integration(target, papers, collection)

    def _looks_like_user_prompt(self, command: str) -> bool:
        """Delegate to ShellHandler"""
        return self.shell_handler.looks_like_user_prompt(command)

    def _infer_shell_command(self, question: str) -> str:
        """Delegate to ShellHandler"""
        return self.shell_handler.infer_shell_command(question)

    def execute_command(self, command: str) -> str:
        """Delegate to ShellHandler"""
        return self.shell_handler.execute_command(command, self.shell_session, self._is_windows)

    def _format_shell_output(self, output: str, command: str) -> Dict[str, Any]:
        """Delegate to ShellHandler"""
        return self.shell_handler.format_shell_output(output, command)

    # ========================================================================
    # DIRECT FILE OPERATIONS (Claude Code / Cursor Parity)
    # ========================================================================

    def read_file(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        """Delegate to FileOperations"""
        return self.file_ops.read_file(file_path, offset, limit, self.file_context)

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Delegate to FileOperations"""
        return self.file_ops.write_file(file_path, content, self.file_context)

    def edit_file(self, file_path: str, old_string: str, new_string: str,
                  replace_all: bool = False) -> Dict[str, Any]:
        """Delegate to FileOperations"""
        return self.file_ops.edit_file(file_path, old_string, new_string, replace_all, self.file_context)

    def glob_search(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """Delegate to FileOperations"""
        return self.file_ops.glob_search(pattern, path)

    def grep_search(self, pattern: str, path: str = ".",
                    file_pattern: str = "*",
                    output_mode: str = "files_with_matches",
                    context_lines: int = 0,
                    ignore_case: bool = False,
                    max_results: int = 100) -> Dict[str, Any]:
        """Delegate to FileOperations"""
        return self.file_ops.grep_search(pattern, path, file_pattern, output_mode,
                                         context_lines, ignore_case, max_results)

    async def batch_edit_files(self, edits: List[Dict[str, str]]) -> Dict[str, Any]:
        """Delegate to FileOperations"""
        return await self.file_ops.batch_edit_files(edits, self.file_context)

    # ========================================================================
    # END DIRECT FILE OPERATIONS
    # ========================================================================

    def _classify_command_safety(self, cmd: str) -> str:
        """Delegate to ShellHandler"""
        return self.shell_handler.classify_command_safety(cmd)

    def _format_archive_summary(
        self,
        question: str,
        response: str,
        api_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare compact summary payload for the conversation archive."""
        clean_question = question.strip().replace("\n", " ")
        summary_text = response.strip().replace("\n", " ")
        if len(summary_text) > 320:
            summary_text = summary_text[:317].rstrip() + "..."

        citations: List[str] = []
        research = api_results.get("research")
        if isinstance(research, dict):
            for item in research.get("results", [])[:3]:
                title = item.get("title") or item.get("paperTitle")
                if title:
                    citations.append(title)

        financial = api_results.get("financial")
        if isinstance(financial, dict):
            tickers = ", ".join(sorted(financial.keys()))
            if tickers:
                citations.append(f"Financial data: {tickers}")

        return {
            "question": clean_question,
            "summary": summary_text,
            "citations": citations,
        }

    def _is_safe_shell_command(self, cmd: str) -> bool:
        """Delegate to ShellHandler"""
        return self.shell_handler.is_safe_shell_command(cmd)
    
    def _check_token_budget(self, estimated_tokens: int) -> bool:
        """Delegate to AgentUtilities"""
        self._ensure_usage_day()
        return self.utilities.check_token_budget(self.daily_token_usage, self.daily_limit, estimated_tokens)

    def _check_user_token_budget(self, user_id: str, estimated_tokens: int) -> bool:
        """Delegate to AgentUtilities"""
        self._ensure_usage_day()
        return self.utilities.check_user_token_budget(self.user_token_usage, self.per_user_token_limit, user_id, estimated_tokens)

    def _resolve_daily_query_limit(self) -> int:
        limit_env = os.getenv("NOCTURNAL_QUERY_LIMIT")
        if limit_env and limit_env != str(DEFAULT_QUERY_LIMIT):
            logger.warning("Ignoring attempted query-limit override (%s); enforcing default %s", limit_env, DEFAULT_QUERY_LIMIT)
        os.environ["NOCTURNAL_QUERY_LIMIT"] = str(DEFAULT_QUERY_LIMIT)
        os.environ.pop("NOCTURNAL_QUERY_LIMIT_SIG", None)
        return DEFAULT_QUERY_LIMIT

    def _check_query_budget(self, user_id: Optional[str]) -> bool:
        """Delegate to AgentUtilities"""
        self._ensure_usage_day()
        return self.utilities.check_query_budget(
            self.daily_query_count, self.daily_query_limit,
            self.user_query_counts, self.per_user_query_limit, user_id
        )

    def _record_query_usage(self, user_id: Optional[str]):
        self._ensure_usage_day()
        self.daily_query_count += 1
        if user_id:
            self.user_query_counts[user_id] = self.user_query_counts.get(user_id, 0) + 1

    def _ensure_usage_day(self):
        current_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if current_day != self._usage_day:
            self._usage_day = current_day
            self.daily_token_usage = 0
            self.user_token_usage = {}
            self.daily_query_count = 0
            self.user_query_counts = {}

    def _charge_tokens(self, user_id: Optional[str], tokens: int):
        """Charge tokens to daily and per-user usage"""
        self._ensure_usage_day()
        self.daily_token_usage += tokens
        if user_id:
            self.user_token_usage[user_id] = self.user_token_usage.get(user_id, 0) + tokens

    def _finalize_interaction(
        self,
        request: ChatRequest,
        response: ChatResponse,
        tools_used: Optional[List[str]],
        api_results: Optional[Dict[str, Any]],
        request_analysis: Optional[Dict[str, Any]],
        *,
        log_workflow: bool = True,
    ) -> ChatResponse:
        """Common tail logic: history, memory, workflow logging, archive save."""
        merged_tools: List[str] = []
        seen: Set[str] = set()
        for tool in (tools_used or []) + (response.tools_used or []):
            if tool and tool not in seen:
                merged_tools.append(tool)
                seen.add(tool)
        response.tools_used = merged_tools

        if request_analysis and not response.confidence_score:
            response.confidence_score = request_analysis.get("confidence", response.confidence_score) or 0.0

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": response.response})

        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {response.response[:100]}...",
        )

        if log_workflow:
            try:
                self.workflow.save_query_result(
                    query=request.question,
                    response=response.response,
                    metadata={
                        "tools_used": response.tools_used,
                        "tokens_used": response.tokens_used,
                        "confidence_score": response.confidence_score,
                    },
                )
            except Exception:
                logger.debug("Workflow logging failed", exc_info=True)

        if getattr(self, "archive", None):
            try:
                archive_payload = self._format_archive_summary(
                    request.question,
                    response.response,
                    api_results or {},
                )
                self.archive.record_entry(
                    request.user_id,
                    request.conversation_id,
                    archive_payload["question"],
                    archive_payload["summary"],
                    response.tools_used,
                    archive_payload["citations"],
                )
            except Exception as archive_error:
                logger.debug("Archive write failed", error=str(archive_error))

        return response
    
    def _get_memory_context(self, user_id: str, conversation_id: str) -> str:
        """Delegate to AgentUtilities"""
        return self.utilities.get_memory_context(self.memory, user_id, conversation_id)

    def _update_memory(self, user_id: str, conversation_id: str, interaction: str):
        """Delegate to AgentUtilities"""
        self.utilities.update_memory(self.memory, user_id, conversation_id, interaction)

    @staticmethod
    def _hash_identifier(value: Optional[str]) -> Optional[str]:
        """Hash identifier for privacy - returns first 16 chars of SHA256 hash"""
        if not value:
            return None
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    def _emit_telemetry(
        self,
        event: str,
        request: Optional[ChatRequest] = None,
        *,
        success: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        manager = TelemetryManager.get()
        if not manager:
            return

        payload: Dict[str, Any] = {}
        if request:
            payload["user"] = self._hash_identifier(request.user_id)
            payload["conversation"] = self._hash_identifier(request.conversation_id)
        if success is not None:
            payload["success"] = bool(success)
        if extra:
            for key, value in extra.items():
                if value is None:
                    continue
                payload[key] = value

        manager.record(event, payload)

    @staticmethod
    def _format_model_error(details: str) -> str:
        """Delegate to AgentUtilities"""
        return AgentUtilities.format_model_error(details)

    def _summarize_command_output(
        self,
        request: ChatRequest,
        command: str,
        truncated_output: str,
        base_response: str
    ) -> Tuple[str, int]:
        """Attach a deterministic shell output block to the agent response."""

        rendered_output = truncated_output.rstrip()
        if not rendered_output:
            rendered_output = "(no output)"

        formatted = (
            f"{base_response.strip()}\n\n"
            "```shell\n"
            f"$ {command}\n"
            f"{rendered_output}\n"
            "```"
        )

        return formatted, 0
    
    async def _handle_workflow_commands(self, request: ChatRequest) -> Optional[ChatResponse]:
        """Handle natural language workflow commands directly"""
        question_lower = request.question.lower()
        
        # Show library
        if any(phrase in question_lower for phrase in ["show my library", "list my papers", "what's in my library", "my saved papers"]):
            papers = self.workflow.list_papers()
            if not papers:
                message = "Your library is empty. As you find papers, I can save them for you."
            else:
                paper_list = []
                for i, paper in enumerate(papers[:10], 1):
                    authors_str = paper.authors[0] if paper.authors else "Unknown"
                    if len(paper.authors) > 1:
                        authors_str += " et al."
                    paper_list.append(f"{i}. {paper.title} ({authors_str}, {paper.year})")
                
                message = f"You have {len(papers)} paper(s) in your library:\n\n" + "\n".join(paper_list)
                if len(papers) > 10:
                    message += f"\n\n...and {len(papers) - 10} more."
            
            return self._quick_reply(request, message, tools_used=["workflow_library"], confidence=1.0)
        
        # Export to BibTeX
        if any(phrase in question_lower for phrase in ["export to bibtex", "export bibtex", "generate bibtex", "bibtex export"]):
            success = self.workflow.export_to_bibtex()
            if success:
                message = f"✅ Exported {len(self.workflow.list_papers())} papers to BibTeX.\n\nFile: {self.workflow.bibtex_file}\n\nYou can import this into Zotero, Mendeley, or use it in your LaTeX project."
            else:
                message = "❌ Failed to export BibTeX. Make sure you have papers in your library first."
            
            return self._quick_reply(request, message, tools_used=["workflow_export"], confidence=1.0)
        
        # Export to Markdown
        if any(phrase in question_lower for phrase in ["export to markdown", "export markdown", "markdown export"]):
            success = self.workflow.export_to_markdown()
            if success:
                message = f"✅ Exported to Markdown. Check {self.workflow.exports_dir} for the file.\n\nYou can open it in Obsidian, Notion, or any markdown editor."
            else:
                message = "❌ Failed to export Markdown."
            
            return self._quick_reply(request, message, tools_used=["workflow_export"], confidence=1.0)
        
        # Show history
        if any(phrase in question_lower for phrase in ["show history", "my history", "recent queries", "what did i search"]):
            history = self.workflow.get_history()[:10]
            if not history:
                message = "No query history yet."
            else:
                history_list = []
                for i, entry in enumerate(history, 1):
                    timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%m/%d %H:%M")
                    query = entry['query'][:60] + "..." if len(entry['query']) > 60 else entry['query']
                    history_list.append(f"{i}. [{timestamp}] {query}")
                
                message = "Recent queries:\n\n" + "\n".join(history_list)
            
            return self._quick_reply(request, message, tools_used=["workflow_history"], confidence=1.0)
        
        # Search library
        search_match = re.match(r".*(?:search|find).*(?:in|my).*library.*[\"'](.+?)[\"']", question_lower)
        if not search_match:
            search_match = re.match(r".*search library (?:for )?(.+)", question_lower)
        
        if search_match:
            query_term = search_match.group(1).strip()
            results = self.workflow.search_library(query_term)
            if not results:
                message = f"No papers found matching '{query_term}' in your library."
            else:
                result_list = []
                for i, paper in enumerate(results[:5], 1):
                    authors_str = paper.authors[0] if paper.authors else "Unknown"
                    if len(paper.authors) > 1:
                        authors_str += " et al."
                    result_list.append(f"{i}. {paper.title} ({authors_str}, {paper.year})")
                
                message = f"Found {len(results)} paper(s) matching '{query_term}':\n\n" + "\n".join(result_list)
                if len(results) > 5:
                    message += f"\n\n...and {len(results) - 5} more."
            
            return self._quick_reply(request, message, tools_used=["workflow_search"], confidence=1.0)
        
        # No workflow command detected
        return None

    async def _analyze_request_type(self, question: str) -> Dict[str, Any]:
        """Delegate to QueryAnalyzer"""
        return await self.query_analyzer.analyze_request_type(question)
    
    def _is_query_too_vague_for_apis(self, question: str) -> bool:
        """Delegate to QueryAnalyzer"""
        return self.query_analyzer.is_query_too_vague_for_apis(question)
    
    async def process_request(self, request: ChatRequest) -> ChatResponse:
        """Process request with full AI capabilities and API integration"""
        try:
            # Check workflow commands first (both modes)
            workflow_response = await self._handle_workflow_commands(request)
            if workflow_response:
                return workflow_response
            
            # Detect and store language preference from user input
            self._detect_language_preference(request.question)
            
            # Initialize
            api_results = {}
            tools_used = []
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

            # Removed hardcoded test reply - let agent respond naturally

            if self._is_location_query(request.question):
                cwd_line = ""
                tools: List[str] = []

                if self.shell_session:
                    pwd_output = self.execute_command("pwd")
                    if pwd_output and not pwd_output.startswith("ERROR"):
                        cwd_line = pwd_output.strip().splitlines()[-1]
                        tools.append("shell_execution")

                if not cwd_line:
                    try:
                        cwd_line = os.getcwd()
                    except Exception:
                        cwd_line = ""

                if cwd_line:
                    self.file_context["current_cwd"] = cwd_line
                    self.file_context["last_directory"] = cwd_line
                    message = (
                        f"We're in {cwd_line}."
                        if "shell_execution" not in tools
                        else f"We're in {cwd_line} (via `pwd`)."
                    )
                    return self._quick_reply(
                        request,
                        message,
                        tools_used=tools or ["quick_reply"],
                        confidence=0.85,
                    )
                else:
                    return self._quick_reply(
                        request,
                        "I couldn't determine the working directory just now, but you can run `pwd` to double-check.",
                        tools_used=tools or ["quick_reply"],
                        confidence=0.3,
                    )

            # ========================================================================
            # INTEGRATION PUSH DETECTION (Zotero, Mendeley, Notion)
            # ========================================================================
            # Check if user wants to push papers to an integration
            integration_request = self._detect_integration_request(request.question)
            if integration_request:
                target = integration_request["target"]
                collection = integration_request.get("collection")

                # Extract papers from api_results or conversation history
                papers = self._extract_papers_from_context(api_results, request.question)

                # If no papers found in context, check if this is a combined request
                # e.g., "find papers on transformers and add them to zotero"
                if not papers:
                    # Check if query contains both search request AND integration push
                    question_lower = request.question.lower()
                    is_combined_request = any(word in question_lower for word in [
                        "find", "search", "get", "look for", "show me", "papers on", "research on"
                    ])

                    if is_combined_request:
                        # Extract the search query part (before "and add/push/save")
                        # Split on integration patterns
                        split_patterns = [
                            r'\s+and\s+(add|push|save|send|put|export|store)',
                            r'\s+then\s+(add|push|save|send|put|export|store)',
                            r',\s+(add|push|save|send|put|export|store)'
                        ]

                        search_query = request.question
                        for pattern in split_patterns:
                            match = re.split(pattern, request.question, flags=re.IGNORECASE)
                            if len(match) > 1:
                                search_query = match[0].strip()
                                break

                        # Perform academic search
                        search_result = await self.search_academic_papers(search_query, limit=10)

                        if "error" not in search_result:
                            papers = search_result.get("results") or search_result.get("papers") or []
                            api_results["research"] = search_result
                            tools_used.append("archive_api")

                # Now push papers if we have them
                if papers:
                    integration_result = await self._push_to_integration_conversational(
                        target=target,
                        papers=papers,
                        collection=collection
                    )

                    # Format response message
                    if integration_result.get("success"):
                        paper_count = len(papers)
                        message = f"✅ {integration_result['message']}\n\n"

                        # Add paper summary
                        message += f"Papers added ({paper_count}):\n"
                        for i, paper in enumerate(papers[:5], 1):  # Show first 5
                            title = paper.get("title", "Untitled")
                            authors = paper.get("authors", [])
                            author_str = authors[0] if authors else "Unknown"
                            if len(authors) > 1:
                                author_str += " et al."
                            year = paper.get("year", "N/A")
                            message += f"{i}. {title} - {author_str} ({year})\n"

                        if paper_count > 5:
                            message += f"... and {paper_count - 5} more\n"

                        # Add view link if available
                        if "library_url" in integration_result:
                            message += f"\n🔗 View in {target.capitalize()}: {integration_result['library_url']}\n"
                        elif "url" in integration_result:
                            message += f"\n🔗 View in {target.capitalize()}: {integration_result['url']}\n"

                        # Add integration result to api_results
                        api_results["integration"] = integration_result

                        return ChatResponse(
                            response=message,
                            tools_used=tools_used + [f"{target}_push"],
                            reasoning_steps=[f"Pushed {paper_count} papers to {target}"],
                            tokens_used=0,
                            confidence_score=0.95,
                            api_results=api_results
                        )
                    else:
                        # Integration push failed
                        error_message = f"❌ {integration_result['message']}\n\n"

                        # Check for common issues and provide helpful guidance
                        message_lower = integration_result['message'].lower()
                        if "credentials" in message_lower or "not found" in message_lower:
                            error_message += f"💡 **Setup Required**: Run `cite-agent --setup-integrations` to configure {target.capitalize()}.\n"
                            error_message += f"📖 See AUTHENTICATION.md for step-by-step setup instructions.\n"
                        elif "authentication" in message_lower or "unauthorized" in message_lower:
                            error_message += f"💡 **Authentication Issue**: Your {target.capitalize()} credentials may be invalid.\n"
                            error_message += f"Run `cite-agent --test-integrations` to diagnose the problem.\n"

                        # Add integration result to api_results
                        api_results["integration"] = integration_result

                        return ChatResponse(
                            response=error_message,
                            tools_used=tools_used + [f"{target}_push_failed"],
                            reasoning_steps=[f"Failed to push to {target}"],
                            tokens_used=0,
                            confidence_score=0.6,
                            api_results=api_results
                        )
                else:
                    # No papers found to push
                    message = f"❌ No papers found to push to {target.capitalize()}.\n\n"
                    message += "💡 Try searching for papers first:\n"
                    message += f'  Example: "find papers on transformers and add them to {target}"\n'

                    return ChatResponse(
                        response=message,
                        tools_used=["integration_request_no_papers"],
                        reasoning_steps=["Integration requested but no papers available"],
                        tokens_used=0,
                        confidence_score=0.4,
                        api_results=api_results
                    )

            # ========================================================================
            # PRIORITY 0: ANALYZE REQUEST TYPE FIRST
            # ========================================================================
            # Determine what kind of query this is BEFORE deciding to run shell planner
            # Prevents shell planner from running on research/financial queries
            request_analysis_early = await self._analyze_request_type(request.question)
            apis_needed = set(request_analysis_early.get("apis", []))

            # ========================================================================
            # PRIORITY 1: SHELL PLANNING (Only for shell/system queries)
            # ========================================================================
            # Skip shell planner if this is clearly an API query (research/financial)
            shell_action = "none"  # Will be: execute|none
            question_lower = request.question.lower()

            # Only run shell planner if:
            # 1. Shell session available
            # 2. NOT a pure API query (research/financial)
            skip_shell_planning = (apis_needed & {"archive", "finsight"}) and not (apis_needed & {"shell"})

            if self.shell_session and not skip_shell_planning:
                # Get current directory and context for intelligent planning
                try:
                    current_dir = self.execute_command("pwd").strip()
                    self.file_context['current_cwd'] = current_dir
                except:
                    current_dir = "~"
                
                last_file = self.file_context.get('last_file') or 'None'
                last_dir = self.file_context.get('last_directory') or 'None'
                
                # Ask LLM planner: What shell command should we run?
                planner_prompt = f"""You are a shell command planner. Determine what shell command to run, if any.

User query: "{request.question}"
Previous conversation: {json.dumps(self.conversation_history[-2:]) if self.conversation_history else "None"}
Current directory: {current_dir}
Last file mentioned: {last_file}
Last directory mentioned: {last_dir}

Respond ONLY with JSON:
{{
  "action": "execute|none",
  "command": "pwd" (the actual shell command to run, if action=execute),
  "reason": "Show current directory" (why this command is needed),
  "updates_context": true (set to true if command changes files/directories)
}}

IMPORTANT RULES:
1. Return "none" for conversational queries ("hello", "test", "thanks", "how are you")
2. Return "none" when query is ambiguous without more context
3. Return "none" for questions about data that don't need shell (e.g., "Tesla revenue", "Apple stock price")
4. Use ACTUAL shell commands (pwd, ls, cd, mkdir, cat, grep, find, touch, etc.)
5. Resolve pronouns using context: "it"={last_file}, "there"/{last_dir}
6. For reading SPECIFIC FUNCTIONS in a file: grep -A 50 'def function_name' filename (shows function with 50 lines)
7. For reading entire files: cat filename (for small files) OR head -100 filename (for large files)
8. For finding files/directories, use: find ~ -maxdepth 4 -name '*pattern*' 2>/dev/null
9. For creating files: touch filename OR echo "content" > filename
9. For creating directories: mkdir dirname
10. ALWAYS include 2>/dev/null to suppress errors from find and grep
11. 🚨 MULTI-STEP QUERIES: For queries like "read X and do Y", ONLY generate the FIRST step (reading X). The LLM will handle subsequent steps after seeing the file contents.
12. 🚨 NEVER EXECUTE CODE: Do NOT run python, node, bash scripts, or any interpreters
13. 🚨 FOR EXPLANATION QUERIES: "explain function X" → grep -A 50 'def X' filename (READ, don't execute!)
14. 🚨 FILE PATH INFERENCE: If file mentioned exists in a known subdirectory, include the path
    - "enhanced_ai_agent.py" → cite_agent/enhanced_ai_agent.py
    - "cli.py" → cite_agent/cli.py
    - Use find to locate file if path unknown: find . -name 'filename' 2>/dev/null | head -1
15. 🚨 NEVER use python -m py_compile or other code execution for finding bugs - just read the file with cat/head
16. 🚨 FOR GREP: When searching in a DIRECTORY (not a specific file), ALWAYS use -r flag for recursive search: grep -rn 'pattern' /path/to/dir 2>/dev/null

Examples:
"where am i?" → {{"action": "execute", "command": "pwd", "reason": "Show current directory", "updates_context": false}}
"list files" → {{"action": "execute", "command": "ls -lah", "reason": "List all files with details", "updates_context": false}}
"find cm522" → {{"action": "execute", "command": "find ~ -maxdepth 4 -name '*cm522*' -type d 2>/dev/null | head -20", "reason": "Search for cm522 directory", "updates_context": false}}
"go to Downloads" → {{"action": "execute", "command": "cd ~/Downloads && pwd", "reason": "Navigate to Downloads directory", "updates_context": true}}
"show me calc.R" → {{"action": "execute", "command": "head -100 calc.R", "reason": "Display file contents", "updates_context": true}}
"read the main function in cli.py" → {{"action": "execute", "command": "grep -A 50 'def main' cli.py", "reason": "Show main function definition", "updates_context": false}}
"explain the process function in analyzer.py" → {{"action": "execute", "command": "grep -A 50 'def process' analyzer.py", "reason": "Show process function", "updates_context": false}}
"explain what _analyze_request_type does in enhanced_ai_agent.py" → {{"action": "execute", "command": "grep -A 50 'def _analyze_request_type' cite_agent/enhanced_ai_agent.py", "reason": "Show function to explain", "updates_context": false}}
"what libraries does cli.py import?" → {{"action": "execute", "command": "head -50 cite_agent/cli.py | grep '^import\\|^from'", "reason": "Show imports", "updates_context": false}}
"create test directory" → {{"action": "execute", "command": "mkdir test && echo 'Created test/'", "reason": "Create new directory", "updates_context": true}}
"create empty config.json" → {{"action": "execute", "command": "touch config.json && echo 'Created config.json'", "reason": "Create empty file", "updates_context": true}}
"write hello.txt with content Hello World" → {{"action": "execute", "command": "echo 'Hello World' > hello.txt", "reason": "Create file with content", "updates_context": true}}
"create results.txt with line 1 and line 2" → {{"action": "execute", "command": "echo 'line 1' > results.txt && echo 'line 2' >> results.txt", "reason": "Create file with multiple lines", "updates_context": true}}
"fix bug in script.py change OLD to NEW" → {{"action": "execute", "command": "sed -i 's/OLD/NEW/g' script.py && echo 'Fixed script.py'", "reason": "Edit file to fix bug", "updates_context": true}}
"search for TODO in py files here" → {{"action": "execute", "command": "grep -n 'TODO' *.py 2>/dev/null", "reason": "Find TODO in current directory py files", "updates_context": false}}
"search for TODO in /some/directory" → {{"action": "execute", "command": "grep -rn 'TODO' /some/directory 2>/dev/null", "reason": "Recursively search directory for TODO", "updates_context": false}}
"search for TODO comments in /tmp/test" → {{"action": "execute", "command": "grep -rn 'TODO' /tmp/test 2>/dev/null", "reason": "Recursively search directory for TODO", "updates_context": false}}
"find all bugs in code" → {{"action": "execute", "command": "grep -rn 'BUG:' . 2>/dev/null", "reason": "Search for bug markers in code", "updates_context": false}}
"read analyze.py and find bugs" → {{"action": "execute", "command": "head -200 analyze.py", "reason": "Read file to analyze bugs", "updates_context": false}}
"show me calc.py completely" → {{"action": "execute", "command": "cat calc.py", "reason": "Display entire file", "updates_context": false}}
"git status" → {{"action": "execute", "command": "git status", "reason": "Check repository status", "updates_context": false}}
"what's in that file?" + last_file=data.csv → {{"action": "execute", "command": "head -100 data.csv", "reason": "Show file contents", "updates_context": false}}
"hello" → {{"action": "none", "reason": "Conversational greeting, no command needed"}}
"test" → {{"action": "none", "reason": "Ambiguous query, needs clarification"}}
"thanks" → {{"action": "none", "reason": "Conversational acknowledgment"}}
"Tesla revenue" → {{"action": "none", "reason": "Finance query, will use FinSight API not shell"}}
"what does the error mean?" → {{"action": "none", "reason": "Explanation request, no command needed"}}

JSON:"""

                try:
                    # Use LOCAL LLM for planning (don't recurse into call_backend_query)
                    # This avoids infinite recursion and uses temp key if available
                    if hasattr(self, 'client') and self.client:
                        # Local mode with temp key or dev keys
                        # Use gpt-oss-120b for Cerebras (100% test pass, better accuracy)
                        model_name = "gpt-oss-120b" if self.llm_provider == "cerebras" else "llama-3.1-70b-versatile"
                        response = self.client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": "user", "content": planner_prompt}],
                            max_tokens=500,
                            temperature=0.3
                        )
                        plan_text = response.choices[0].message.content.strip()
                        plan_response = ChatResponse(response=plan_text)
                    else:
                        # Backend mode - make a simplified backend call
                        plan_response = await self.call_backend_query(
                            query=planner_prompt,
                            conversation_history=[],
                            api_results={},
                            tools_used=[]
                        )
                    
                    plan_text = plan_response.response.strip()
                    if '```' in plan_text:
                        plan_text = plan_text.split('```')[1].replace('json', '').strip()
                    
                    plan = json.loads(plan_text)
                    shell_action = plan.get("action", "none")
                    command = plan.get("command", "")
                    reason = plan.get("reason", "")
                    updates_context = plan.get("updates_context", False)
                    
                    # Only show planning details with explicit verbose flag (don't leak to users)
                    verbose_planning = debug_mode and os.getenv("NOCTURNAL_VERBOSE_PLANNING", "").lower() == "1"
                    if verbose_planning:
                        print(f"🔍 SHELL PLAN: {plan}")

                    # GENERIC COMMAND EXECUTION - Trust the planner's decision
                    # If planner says "none", respect that - no fallback inference

                    if shell_action == "execute" and not command:
                        command = self._infer_shell_command(request.question)
                        plan["command"] = command
                        if verbose_planning:
                            print(f"🔄 Planner omitted command, inferred {command}")

                    if shell_action == "execute" and command:
                        if self._looks_like_user_prompt(command):
                            command = self._infer_shell_command(request.question)
                            plan["command"] = command
                            if debug_mode:
                                print(f"🔄 Replacing delegating plan with command: {command}")
                        # Check command safety
                        safety_level = self._classify_command_safety(command)
                        
                        if debug_mode:
                            print(f"🔍 Command: {command}")
                            print(f"🔍 Safety: {safety_level}")
                        
                        if safety_level in ('BLOCKED', 'DANGEROUS'):
                            reason = (
                                "Command classified as destructive; requires manual confirmation"
                                if safety_level == 'DANGEROUS'
                                else "This command could cause system damage"
                            )
                            api_results["shell_info"] = {
                                "error": f"Command blocked for safety: {command}",
                                "reason": reason
                            }
                        else:
                            # ========================================
                            # COMMAND INTERCEPTOR: Translate shell commands to file operations
                            # (Claude Code / Cursor parity)
                            # ========================================
                            intercepted = False
                            output = ""

                            # Check for file reading commands (cat, head, tail)
                            if command.startswith(('cat ', 'head ', 'tail ')):
                                import shlex
                                try:
                                    parts = shlex.split(command)
                                    cmd = parts[0]

                                    # Extract filename (last non-flag argument)
                                    filename = None
                                    for part in reversed(parts[1:]):
                                        if not part.startswith('-'):
                                            filename = part
                                            break

                                    if filename:
                                        # Use read_file instead of cat/head/tail
                                        if cmd == 'head':
                                            # head -n 100 file OR head file
                                            limit = 100  # default
                                            if '-n' in parts or '-' in parts[0]:
                                                try:
                                                    idx = parts.index('-n') if '-n' in parts else 0
                                                    limit = int(parts[idx + 1])
                                                except:
                                                    pass
                                            output = self.read_file(filename, offset=0, limit=limit)
                                        elif cmd == 'tail':
                                            # For tail, read last N lines (harder, so just read all and show it's tail)
                                            output = self.read_file(filename)
                                            if "ERROR" not in output:
                                                lines = output.split('\n')
                                                output = '\n'.join(lines[-100:])  # last 100 lines
                                        else:  # cat
                                            output = self.read_file(filename)

                                        intercepted = True
                                        tools_used.append("read_file")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → read_file({filename})")
                                except:
                                    pass  # Fall back to shell execution

                            # Check for file search commands (find)
                            if not intercepted and 'find' in command and '-name' in command:
                                try:
                                    # import re removed - using module-level import
                                    # Extract pattern: find ... -name '*pattern*'
                                    name_match = re.search(r"-name\s+['\"]?\*?([^'\"*\s]+)\*?['\"]?", command)
                                    if name_match:
                                        pattern = f"**/*{name_match.group(1)}*"
                                        path_match = re.search(r"find\s+([^\s]+)", command)
                                        search_path = path_match.group(1) if path_match else "."

                                        result = self.glob_search(pattern, search_path)
                                        output = '\n'.join(result['files'][:20])  # Show first 20 matches
                                        intercepted = True
                                        tools_used.append("glob_search")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → glob_search({pattern}, {search_path})")
                                except:
                                    pass

                            # Check for file writing commands (echo > file, grep > file, etc.) - CHECK THIS FIRST!
                            # This must come BEFORE the plain grep interceptor
                            # BUT: Ignore 2>/dev/null which is error redirection, not file writing
                            if not intercepted and ('>' in command or '>>' in command) and '2>' not in command:
                                try:
                                    # import re removed - using module-level import

                                    # Handle grep ... > file (intercept and execute grep, then write output)
                                    if 'grep' in command and '>' in command:
                                        # Extract: grep -rn 'pattern' path > output.txt
                                        grep_match = re.search(r"grep\s+(.*)\s>\s*(\S+)", command)
                                        if grep_match:
                                            grep_part = grep_match.group(1).strip()
                                            output_file = grep_match.group(2)

                                            # Extract pattern and options from grep command
                                            pattern_match = re.search(r"['\"]([^'\"]+)['\"]", grep_part)
                                            if pattern_match:
                                                pattern = pattern_match.group(1)
                                                search_path = "."
                                                file_pattern = "*.py" if "*.py" in command else "*"

                                                if debug_mode:
                                                    print(f"🔄 Intercepted: {command} → grep_search('{pattern}', '{search_path}', '{file_pattern}') + write_file({output_file})")

                                                # Execute grep_search
                                                try:
                                                    grep_result = self.grep_search(
                                                        pattern=pattern,
                                                        path=search_path,
                                                        file_pattern=file_pattern,
                                                        output_mode="content"
                                                    )

                                                    # Format matches as text (like grep -rn output)
                                                    output_lines = []
                                                    for file_path, matches in grep_result.get('matches', {}).items():
                                                        for line_num, line_content in matches:
                                                            output_lines.append(f"{file_path}:{line_num}:{line_content}")

                                                    content_to_write = '\n'.join(output_lines) if output_lines else "(no matches found)"

                                                    # Write grep output to file
                                                    write_result = self.write_file(output_file, content_to_write)
                                                    if write_result['success']:
                                                        output = f"Found {len(output_lines)} lines with '{pattern}' → Created {output_file} ({write_result['bytes_written']} bytes)"
                                                        intercepted = True
                                                        tools_used.extend(["grep_search", "write_file"])
                                                except Exception as e:
                                                    if debug_mode:
                                                        print(f"⚠️ Grep > file interception error: {e}")
                                                    # Fall back to normal execution
                                                    pass

                                    # Extract: echo 'content' > filename OR cat << EOF > filename
                                    if not intercepted and 'echo' in command and '>' in command:
                                        # echo 'content' > file OR echo "content" > file
                                        match = re.search(r"echo\s+['\"](.+?)['\"].*?>\s*(\S+)", command)
                                        if match:
                                            content = match.group(1)
                                            filename = match.group(2)
                                            # Unescape common sequences
                                            content = content.replace('\\n', '\n').replace('\\t', '\t')
                                            result = self.write_file(filename, content + '\n')
                                            if result['success']:
                                                output = f"Created {filename} ({result['bytes_written']} bytes)"
                                                intercepted = True
                                                tools_used.append("write_file")
                                                if debug_mode:
                                                    print(f"🔄 Intercepted: {command} → write_file({filename}, ...)")
                                except:
                                    pass

                            # Check for sed editing commands
                            if not intercepted and command.startswith('sed '):
                                try:
                                    # import re removed - using module-level import
                                    # sed 's/old/new/g' file OR sed -i 's/old/new/' file
                                    match = re.search(r"sed.*?['\"]s/([^/]+)/([^/]+)/", command)
                                    if match:
                                        old_text = match.group(1)
                                        new_text = match.group(2)
                                        # Extract filename (last argument)
                                        parts = command.split()
                                        filename = parts[-1]

                                        # Determine if replace_all based on /g flag
                                        replace_all = '/g' in command

                                        result = self.edit_file(filename, old_text, new_text, replace_all=replace_all)
                                        if result['success']:
                                            output = result['message']
                                            intercepted = True
                                            tools_used.append("edit_file")
                                            if debug_mode:
                                                print(f"🔄 Intercepted: {command} → edit_file({filename}, {old_text}, {new_text})")
                                except:
                                    pass

                            # Check for heredoc file creation (cat << EOF > file)
                            if not intercepted and '<<' in command and ('EOF' in command or 'HEREDOC' in command):
                                try:
                                    # import re removed - using module-level import
                                    # Extract: cat << EOF > filename OR cat > filename << EOF
                                    # Note: We can't actually get the heredoc content from a single command line
                                    # This would need to be handled differently (multi-line input)
                                    # For now, just detect and warn
                                    if debug_mode:
                                        print(f"⚠️  Heredoc detected but not intercepted: {command[:80]}")
                                except:
                                    pass

                            # Check for content search commands (grep -r) WITHOUT redirection
                            # This comes AFTER grep > file interceptor to avoid conflicts
                            if not intercepted and 'grep' in command and ('-r' in command or '-R' in command):
                                try:
                                    # import re removed - using module-level import
                                    # Extract pattern: grep -r 'pattern' path
                                    pattern_match = re.search(r"grep.*?['\"]([^'\"]+)['\"]", command)
                                    if pattern_match:
                                        pattern = pattern_match.group(1)
                                        # Extract path - skip flags and options
                                        parts = [p for p in command.split() if not p.startswith('-') and p != 'grep' and p != '2>/dev/null']
                                        # Path is after pattern (skip the quoted pattern)
                                        search_path = parts[-1] if len(parts) >= 2 else "."

                                        # Detect file pattern from command (e.g., *.py, *.txt) or use *
                                        file_pattern = "*"
                                        if '*.py' in command:
                                            file_pattern = "*.py"
                                        elif '*.txt' in command:
                                            file_pattern = "*.txt"

                                        result = self.grep_search(pattern, search_path, file_pattern, output_mode="content")

                                        # Format grep results
                                        if 'matches' in result and result['matches']:
                                            output_parts = []
                                            for file_path, matches in result['matches'].items():
                                                output_parts.append(f"{file_path}:")
                                                for line_num, line_content in matches[:10]:  # Limit per file
                                                    output_parts.append(f"  {line_num}: {line_content}")
                                            output = '\n'.join(output_parts)
                                        else:
                                            output = f"No matches found for '{pattern}'"

                                        intercepted = True
                                        tools_used.append("grep_search")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → grep_search({pattern}, {search_path}, {file_pattern})")
                                except Exception as e:
                                    if debug_mode:
                                        print(f"⚠️  Grep interceptor failed: {e}")
                                    pass

                            # If not intercepted, execute as shell command
                            if not intercepted:
                                output = self.execute_command(command)
                            
                            if not output.startswith("ERROR"):
                                # Success - store results with formatted preview
                                formatted_output = self._format_shell_output(output, command)
                                api_results["shell_info"] = {
                                    "command": command,
                                    "output": output,
                                    "formatted": formatted_output,  # Add formatted version
                                    "reason": reason,
                                    "safety_level": safety_level
                                }
                                tools_used.append("shell_execution")
                                if debug_mode:
                                    print(f"✅ Stored shell_info: command={command[:50]}..., output_len={len(output)}")
                                    print(f"🔍 Output preview: {output[:200]}...")
                                
                                # Update file context if needed
                                if updates_context:
                                    # import re removed - using module-level import
                                    # Extract file paths from command
                                    file_patterns = r'([a-zA-Z0-9_\-./]+\.(py|r|csv|txt|json|md|ipynb|rmd))'
                                    files_mentioned = re.findall(file_patterns, command, re.IGNORECASE)
                                    if files_mentioned:
                                        file_path = files_mentioned[0][0]
                                        self.file_context['last_file'] = file_path
                                        if file_path not in self.file_context['recent_files']:
                                            self.file_context['recent_files'].append(file_path)
                                            self.file_context['recent_files'] = self.file_context['recent_files'][-5:]  # Keep last 5
                                    
                                    # Extract directory paths
                                    dir_patterns = r'cd\s+([^\s&|;]+)|mkdir\s+([^\s&|;]+)'
                                    dirs_mentioned = re.findall(dir_patterns, command)
                                    if dirs_mentioned:
                                        for dir_tuple in dirs_mentioned:
                                            dir_path = dir_tuple[0] or dir_tuple[1]
                                            if dir_path:
                                                self.file_context['last_directory'] = dir_path
                                                if dir_path not in self.file_context['recent_dirs']:
                                                    self.file_context['recent_dirs'].append(dir_path)
                                                    self.file_context['recent_dirs'] = self.file_context['recent_dirs'][-5:]  # Keep last 5
                                    
                                    # If cd command, update current_cwd
                                    if command.startswith('cd '):
                                        try:
                                            new_cwd = self.execute_command("pwd").strip()
                                            self.file_context['current_cwd'] = new_cwd
                                        except:
                                            pass
                            else:
                                # Command failed
                                api_results["shell_info"] = {
                                    "error": output,
                                    "command": command
                                }
                    
                    # Backwards compatibility: support old hardcoded actions if LLM still returns them
                    elif shell_action == "pwd":
                        target = plan.get("target_path")
                        if target:
                            ls_output = self.execute_command(f"ls -lah {target}")
                            api_results["shell_info"] = {
                                "directory_contents": ls_output,
                                "target_path": target
                            }
                        else:
                            ls_output = self.execute_command("ls -lah")
                            api_results["shell_info"] = {"directory_contents": ls_output}
                        tools_used.append("shell_execution")
                    
                    elif shell_action == "find":
                        search_target = plan.get("search_target", "")
                        search_path = plan.get("search_path", "~")
                        if search_target:
                            find_cmd = f"find {search_path} -maxdepth 4 -type d -iname '*{search_target}*' 2>/dev/null | head -20"
                            find_output = self.execute_command(find_cmd)
                            if debug_mode:
                                print(f"🔍 FIND: {find_cmd}")
                                print(f"🔍 OUTPUT: {repr(find_output)}")
                            if find_output.strip():
                                api_results["shell_info"] = {
                                    "search_results": f"Searched for '*{search_target}*' in {search_path}:\n{find_output}"
                                }
                            else:
                                api_results["shell_info"] = {
                                    "search_results": f"No directories matching '{search_target}' found in {search_path}"
                                }
                            tools_used.append("shell_execution")
                    
                    elif shell_action == "cd":
                        # NEW: Change directory
                        target = plan.get("target_path")
                        if target:
                            # Expand ~ to home directory
                            if target.startswith("~"):
                                home = os.path.expanduser("~")
                                target = target.replace("~", home, 1)
                            
                            # Execute cd command
                            cd_cmd = f"cd {target} && pwd"
                            cd_output = self.execute_command(cd_cmd)
                            
                            if not cd_output.startswith("ERROR"):
                                api_results["shell_info"] = {
                                    "directory_changed": True,
                                    "new_directory": cd_output.strip(),
                                    "target_path": target
                                }
                                tools_used.append("shell_execution")
                            else:
                                api_results["shell_info"] = {
                                    "directory_changed": False,
                                    "error": f"Failed to change to {target}: {cd_output}"
                                }
                    
                    elif shell_action == "read_file":
                        # NEW: Read and inspect file (R, Python, CSV, etc.)
                        # import re removed - using module-level import
                        
                        file_path = plan.get("file_path", "")
                        if not file_path:
                            # Try to infer from query (e.g., "show me calculate_betas.R")
                            filenames = re.findall(r'([a-zA-Z0-9_-]+\.[a-zA-Z]{1,4})', request.question)
                            if filenames:
                                # Check if file exists in current directory
                                pwd = self.execute_command("pwd").strip()
                                file_path = f"{pwd}/{filenames[0]}"
                        
                        if file_path:
                            if debug_mode:
                                print(f"🔍 READING FILE: {file_path}")
                            
                            # Read file content (first 100 lines to detect structure)
                            cat_output = self.execute_command(f"head -100 {file_path}")
                            
                            if not cat_output.startswith("ERROR"):
                                # Detect file type and extract structure
                                file_ext = file_path.split('.')[-1].lower()
                                
                                # Extract column/variable info based on file type
                                columns_info = ""
                                if file_ext in ['csv', 'tsv']:
                                    # CSV: first line is usually headers
                                    first_line = cat_output.split('\n')[0] if cat_output else ""
                                    columns_info = f"CSV columns: {first_line}"
                                elif file_ext in ['r', 'rmd']:
                                    # R script: look for dataframe column references (df$columnname)
                                    column_refs = re.findall(r'\$(\w+)', cat_output)
                                    unique_cols = list(dict.fromkeys(column_refs))[:10]
                                    if unique_cols:
                                        columns_info = f"Detected columns/variables: {', '.join(unique_cols)}"
                                elif file_ext == 'py':
                                    # Python: look for DataFrame['column'] or df.column
                                    column_refs = re.findall(r'\[[\'""](\w+)[\'"]\]|\.(\w+)', cat_output)
                                    unique_cols = list(dict.fromkeys([c[0] or c[1] for c in column_refs if c[0] or c[1]]))[:10]
                                    if unique_cols:
                                        columns_info = f"Detected columns/attributes: {', '.join(unique_cols)}"
                                
                                api_results["file_context"] = {
                                    "file_path": file_path,
                                    "file_type": file_ext,
                                    "content_preview": cat_output[:2000],  # First 2000 chars
                                    "structure": columns_info,
                                    "full_content": cat_output  # Full content for analysis
                                }
                                tools_used.append("file_read")
                                
                                if debug_mode:
                                    print(f"🔍 FILE STRUCTURE: {columns_info}")
                            else:
                                api_results["file_context"] = {
                                    "error": f"Could not read file: {file_path}"
                                }
                
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 Shell planner failed: {e}, continuing without shell")
                    shell_action = "none"
            
            # ========================================================================
            # PRIORITY 2: DATA APIs (Only if shell didn't fully handle the query)
            # ========================================================================
            # If shell_action = pwd/ls/find, we might still want data APIs
            # But we skip vague queries to save tokens

            # Use early request analysis (already done before shell planning)
            request_analysis = request_analysis_early
            if debug_mode:
                print(f"🔍 Request analysis: {request_analysis}")
            
            is_vague = self._is_query_too_vague_for_apis(request.question)
            if debug_mode and is_vague:
                print(f"🔍 Query is VAGUE - skipping expensive APIs")
            
            # If query is vague, hint to backend LLM to ask clarifying questions
            if is_vague:
                api_results["query_analysis"] = {
                    "is_vague": True,
                    "suggestion": "Ask clarifying questions instead of guessing",
                    "reason": "Query needs more specificity to provide accurate answer"
                }
            
            # Skip Archive/FinSight if query is too vague, but still allow web search later
            if not is_vague:
                # Archive API for research
                if "archive" in request_analysis.get("apis", []):
                    result = await self.search_academic_papers(request.question, 3)  # Reduced from 5 to save tokens
                    if "error" not in result:
                        # Strip abstracts to save tokens - only keep essential fields
                        if "results" in result:
                            for paper in result["results"]:
                                # Remove heavy fields
                                paper.pop("abstract", None)
                                paper.pop("tldr", None)
                                paper.pop("full_text", None)
                                # Keep only: title, authors, year, doi, url
                        api_results["research"] = result
                        tools_used.append("archive_api")
                
                # FinSight API for financial data - Use LLM for ticker/metric extraction
                if "finsight" in request_analysis.get("apis", []):
                    session_key = f"{request.user_id}:{request.conversation_id}"
                    tickers, metrics_to_fetch = self._plan_financial_request(request.question, session_key)
                    financial_payload: Dict[str, Any] = {}

                    for ticker in tickers:
                        result = await self.get_financial_metrics(ticker, metrics_to_fetch)
                        financial_payload[ticker] = result

                    if financial_payload:
                        self._session_topics[session_key] = {
                            "tickers": tickers,
                            "metrics": metrics_to_fetch,
                        }
                        api_results["financial"] = financial_payload
                        tools_used.append("finsight_api")

            # ========================================================================
            # PRIORITY 3: WEB SEARCH (Fallback - only if shell didn't handle AND no data yet)
            # ========================================================================
            # Only web search if:
            # - Shell said "none" (not a directory/file operation)
            # - We don't have enough data from Archive/FinSight
            
            # First check: Is this a conversational query that doesn't need web search?
            def is_conversational_query(query: str) -> bool:
                """Detect if query is conversational (greeting, thanks, testing, etc.)"""
                query_lower = query.lower().strip()
                
                # Single word queries that are conversational
                conversational_words = {
                    'hello', 'hi', 'hey', 'thanks', 'thank', 'ok', 'okay', 'yes', 'no',
                    'test', 'testing', 'cool', 'nice', 'great', 'awesome', 'perfect',
                    'bye', 'goodbye', 'quit', 'exit', 'help'
                }
                
                # Short conversational phrases
                conversational_phrases = [
                    'how are you', 'thank you', 'thanks!', 'ok', 'got it', 'i see',
                    'makes sense', 'sounds good', 'that works', 'no problem'
                ]
                
                words = query_lower.split()
                
                # Single word check
                if len(words) == 1 and words[0] in conversational_words:
                    return True
                
                # Short phrase check
                if len(words) <= 3 and any(phrase in query_lower for phrase in conversational_phrases):
                    return True
                
                # Question marks with no content words (just pronouns)
                if '?' in query_lower and len(words) <= 2:
                    return True
                
                return False
            
            skip_web_search = is_conversational_query(request.question)
            
            if self.web_search and shell_action == "none" and not skip_web_search:
                # Ask LLM: Should we web search for this?
                web_decision_prompt = f"""You are a tool selection expert. Decide if web search is needed.

User query: "{request.question}"
Data already available: {list(api_results.keys())}
Tools already used: {tools_used}

AVAILABLE TOOLS YOU SHOULD KNOW:
1. FinSight API: Company financial data (revenue, income, margins, ratios, cash flow, balance sheet, SEC filings)
   - Covers: All US public companies (~8,000)
   - Data: SEC EDGAR + Yahoo Finance
   - Metrics: 50+ financial KPIs
   
2. Archive API: Academic research papers
   - Covers: Semantic Scholar, OpenAlex, PubMed
   - Data: Papers, citations, abstracts
   
3. Web Search: General information, current events
   - Covers: Anything on the internet
   - Use for: Market share, industry news, non-financial company info

DECISION RULES:
- If query is about company financials (revenue, profit, margins, etc.) → Check if FinSight already provided data
- If FinSight has data in api_results → Web search is NOT needed
- If FinSight was called but no data → Web search as fallback is OK
- If query is about market share, industry size, trends → Web search (FinSight doesn't have this)
- If query is about research papers → Archive handles it, not web
- If query is conversational → Already filtered, you won't see these

Respond with JSON:
{{
  "use_web_search": true/false,
  "reason": "explain why based on tools available and data already fetched"
}}

JSON:"""

                try:
                    # Use LOCAL LLM for web search decision (avoid recursion)
                    if hasattr(self, 'client') and self.client:
                        # Local mode
                        # Use gpt-oss-120b for Cerebras (100% test pass, better accuracy)
                        model_name = "gpt-oss-120b" if self.llm_provider == "cerebras" else "llama-3.1-70b-versatile"
                        response = self.client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": "user", "content": web_decision_prompt}],
                            max_tokens=300,
                            temperature=0.2
                        )
                        decision_text = response.choices[0].message.content.strip()
                        web_decision_response = ChatResponse(response=decision_text)
                    else:
                        # Backend mode
                        web_decision_response = await self.call_backend_query(
                            query=web_decision_prompt,
                            conversation_history=[],
                            api_results={},
                            tools_used=[]
                        )
                    
                    import json as json_module
                    decision_text = web_decision_response.response.strip()
                    if '```' in decision_text:
                        decision_text = decision_text.split('```')[1].replace('json', '').strip()
                    
                    decision = json_module.loads(decision_text)
                    needs_web_search = decision.get("use_web_search", False)
                    
                    if debug_mode:
                        print(f"🔍 WEB SEARCH DECISION: {needs_web_search}, reason: {decision.get('reason')}")
                    
                    if needs_web_search:
                        web_results = await self.web_search.search_web(request.question, num_results=3)
                        if web_results and "results" in web_results:
                            api_results["web_search"] = web_results
                            tools_used.append("web_search")
                            if debug_mode:
                                print(f"🔍 Web search returned: {len(web_results.get('results', []))} results")
                
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 Web search decision failed: {e}")
            
            # PRODUCTION MODE: Call backend LLM with all gathered data
            if self.client is None:
                # DEBUG: Log what we're sending
                if debug_mode and api_results.get("shell_info"):
                    print(f"🔍 SENDING TO BACKEND: shell_info keys = {list(api_results.get('shell_info', {}).keys())}")
                
                # Call backend and UPDATE CONVERSATION HISTORY
                response = await self.call_backend_query(
                    query=request.question,
                    conversation_history=self.conversation_history[-10:],
                    api_results=api_results,
                    tools_used=tools_used
                )
                
                # VALIDATION: Ensure we got a valid response (not planning JSON)
                if not response or not hasattr(response, 'response'):
                    # Backend failed - create friendly error with available data
                    if debug_mode:
                        print(f"⚠️ Backend response invalid or missing")
                    return ChatResponse(
                        response="I ran into a technical issue processing that. Let me try to help with what I found:",
                        error_message="Backend response invalid",
                        tools_used=tools_used,
                        api_results=api_results
                    )
                
                # Check if response contains planning JSON instead of final answer
                response_text = response.response.strip()
                if response_text.startswith('{') and '"action"' in response_text and '"command"' in response_text:
                    # This is planning JSON, not a final response!
                    if debug_mode:
                        print(f"⚠️ Backend returned planning JSON instead of final response")
                    
                    # Extract real output from api_results and generate friendly response
                    shell_output = api_results.get('shell_info', {}).get('output', '')
                    if shell_output:
                        return ChatResponse(
                            response=f"I found what you were looking for:\n\n{shell_output}",
                            tools_used=tools_used,
                            api_results=api_results
                        )
                    else:
                        return ChatResponse(
                            response=f"I completed the action: {api_results.get('shell_info', {}).get('command', '')}",
                            tools_used=tools_used,
                            api_results=api_results
                        )

                # POST-PROCESSING: Auto-extract code blocks and write files if user requested file creation
                # This fixes the issue where LLM shows corrected code but doesn't create the file
                if any(keyword in request.question.lower() for keyword in ['create', 'write', 'save', 'generate', 'fixed', 'corrected']):
                    # Extract filename from query (e.g., "write to foo.py", "create bar_fixed.py")
                    # Note: re is already imported at module level (line 12)
                    filename_match = re.search(r'(?:to|create|write|save|generate)\s+(\w+[._-]\w+\.[\w]+)', request.question, re.IGNORECASE)
                    if not filename_match:
                        # Try pattern: "foo_fixed.py" or "bar.py"
                        filename_match = re.search(r'(\w+_fixed\.[\w]+|\w+\.[\w]+)', request.question)

                    if filename_match:
                        target_filename = filename_match.group(1)

                        # Extract code block from response (```python ... ``` or ``` ... ```)
                        code_block_pattern = r'```(?:python|bash|sh|r|sql)?\n(.*?)```'
                        code_blocks = re.findall(code_block_pattern, response.response, re.DOTALL)

                        if code_blocks:
                            # Use the LARGEST code block (likely the complete file)
                            largest_block = max(code_blocks, key=len)

                            # Write to file
                            try:
                                write_result = self.write_file(target_filename, largest_block)
                                if write_result['success']:
                                    # Append confirmation to response
                                    response.response += f"\n\n✅ File created: {target_filename} ({write_result['bytes_written']} bytes)"
                                    if debug_mode:
                                        print(f"🔄 Auto-extracted code block → write_file({target_filename})")
                            except Exception as e:
                                if debug_mode:
                                    print(f"⚠️ Auto-write failed: {e}")

                return self._finalize_interaction(
                    request,
                    response,
                    tools_used,
                    api_results,
                    request_analysis,
                    log_workflow=False,
                )

            # DEV MODE ONLY: Direct Groq calls (only works with local API keys)
            # This code path won't execute in production since self.client = None

            if not self._check_query_budget(request.user_id):
                effective_limit = self.daily_query_limit if self.daily_query_limit > 0 else self.per_user_query_limit
                if effective_limit <= 0:
                    effective_limit = 25
                message = (
                    "Daily query limit reached. You've hit the "
                    f"{effective_limit} request cap for today. "
                    "Try again tomorrow or reach out if you need the limit raised."
                )
                return self._quick_reply(
                    request,
                    message,
                    tools_used=["rate_limit"],
                    confidence=0.35,
                )

            self._record_query_usage(request.user_id)

            # Analyze request type
            request_analysis = await self._analyze_request_type(request.question)
            question_lower = request.question.lower()
            
            self._reset_data_sources()

            direct_shell = re.match(r"^(?:run|execute)\s*:?\s*(.+)$", request.question.strip(), re.IGNORECASE)
            if direct_shell:
                return self._respond_with_shell_command(request, direct_shell.group(1).strip())

            # Get memory context
            memory_context = self._get_memory_context(request.user_id, request.conversation_id)
            archive_context = self.archive.get_recent_context(
                request.user_id,
                request.conversation_id,
                limit=3,
            ) if getattr(self, "archive", None) else ""
            if archive_context:
                if memory_context:
                    memory_context = f"{memory_context}\n\n{archive_context}"
                else:
                    memory_context = archive_context
            archive_context = self.archive.get_recent_context(
                request.user_id,
                request.conversation_id,
                limit=3,
            ) if getattr(self, "archive", None) else ""
            if archive_context:
                if memory_context:
                    memory_context = f"{memory_context}\n\n{archive_context}"
                else:
                    memory_context = archive_context

            # Let LLM handle greetings and acknowledgments naturally via vague query detection
            # (Removed hardcoded quick replies - trust gpt-oss-120b intelligence)
            
            # Check for workflow commands (natural language)
            workflow_response = await self._handle_workflow_commands(request)
            if workflow_response:
                return workflow_response

            # IMPORTANT: Don't reset api_results here - it was already populated by shell planner
            # in the shared production path (lines 2517-3268)
            # api_results = {}  # REMOVED - was clearing shell_info
            # tools_used = []  # REMOVED - was clearing tools

            # Auto file-reading: detect filenames in the prompt and attach previews
            def _extract_filenames(text: str) -> List[str]:
                # Match common file patterns (no spaces) and simple quoted paths
                patterns = [
                    r"[\w\-./]+\.(?:py|md|txt|json|csv|yml|yaml|toml|ini|ts|tsx|js|ipynb)",
                    r"(?:\./|/)?[\w\-./]+/"  # directories
                ]
                matches: List[str] = []
                for pat in patterns:
                    matches.extend(re.findall(pat, text))
                # Deduplicate and keep reasonable length
                uniq = []
                for m in matches:
                    if len(m) <= 256 and m not in uniq:
                        uniq.append(m)
                return uniq[:5]

            mentioned = _extract_filenames(request.question)
            file_previews: List[Dict[str, Any]] = []
            files_forbidden: List[str] = []
            base_dir = Path.cwd().resolve()
            sensitive_roots = {Path('/etc'), Path('/proc'), Path('/sys'), Path('/dev'), Path('/root'), Path('/usr'), Path('/bin'), Path('/sbin'), Path('/var')}
            def _is_safe_path(path_str: str) -> bool:
                try:
                    rp = Path(path_str).resolve()
                    if any(str(rp).startswith(str(sr)) for sr in sensitive_roots):
                        return False
                    return str(rp).startswith(str(base_dir))
                except Exception:
                    return False
            for m in mentioned:
                if not _is_safe_path(m):
                    files_forbidden.append(m)
                    continue
                pr = await self._preview_file(m)
                if pr:
                    file_previews.append(pr)
            if file_previews:
                api_results["files"] = file_previews
                # Build grounded context from first text preview
                text_previews = [fp for fp in file_previews if fp.get("type") == "text" and fp.get("preview")]
                files_context = ""
                if text_previews:
                    fp = text_previews[0]
                    quoted = "\n".join(fp["preview"].splitlines()[:20])
                    files_context = f"File: {fp['path']} (first lines)\n" + quoted
                api_results["files_context"] = files_context
            elif mentioned:
                # Mentioned files but none found
                api_results["files_missing"] = mentioned
            if files_forbidden:
                api_results["files_forbidden"] = files_forbidden

            workspace_listing: Optional[Dict[str, Any]] = None
            # Only use workspace listing if shell command wasn't already executed
            if debug_mode:
                print(f"🔍 Workspace listing check: file_previews={bool(file_previews)}, shell_info={bool(api_results.get('shell_info'))}")
            if not file_previews and not api_results.get("shell_info"):
                file_browse_keywords = (
                    "list files",
                    "show files",
                    "show me files",
                    "file browser",
                    "file upload",
                    "upload file",
                    "files?",
                    "browse files",
                    "what files",
                    "available files"
                )
                describe_files = (
                    "file" in question_lower or "directory" in question_lower
                ) and any(verb in question_lower for verb in ("show", "list", "what", "which", "display"))
                if any(keyword in question_lower for keyword in file_browse_keywords) or describe_files:
                    workspace_listing = await self._get_workspace_listing()
                    api_results["workspace_listing"] = workspace_listing

            # Only return workspace listing if no shell command was executed
            if workspace_listing and set(request_analysis.get("apis", [])) <= {"shell"} and not api_results.get("shell_info"):
                return self._respond_with_workspace_listing(request, workspace_listing)
            
            if "finsight" in request_analysis["apis"]:
                session_key = f"{request.user_id}:{request.conversation_id}"
                tickers, metrics_to_fetch = self._plan_financial_request(request.question, session_key)
                financial_payload: Dict[str, Any] = {}

                for ticker in tickers:
                    result = await self.get_financial_metrics(ticker, metrics_to_fetch)
                    financial_payload[ticker] = result

                if financial_payload:
                    self._session_topics[session_key] = {
                        "tickers": tickers,
                        "metrics": metrics_to_fetch,
                    }
                    direct_finance = (
                        len(financial_payload) == 1
                        and set(request_analysis.get("apis", [])) == {"finsight"}
                        and not api_results.get("research")
                        and not file_previews
                        and not workspace_listing
                    )
                    if direct_finance:
                        return self._respond_with_financial_metrics(request, financial_payload)
                    api_results["financial"] = financial_payload
                    tools_used.append("finsight_api")
            
            if "archive" in request_analysis["apis"]:
                # Extract research query
                result = await self.search_academic_papers(request.question, 5)
                if debug_mode:
                    print(f"🔍 Archive API result keys: {list(result.keys())}")
                if "error" not in result:
                    api_results["research"] = result
                    # DEBUG: Log what we got from the API
                    papers_count = len(result.get("results", []))
                    if debug_mode:
                        print(f"🔍 Got {papers_count} papers from Archive API")
                    if papers_count > 0 and debug_mode:
                        print(f"🔍 First paper: {result['results'][0].get('title', 'NO TITLE')[:80]}")
                else:
                    api_results["research"] = {"error": result["error"]}
                    if debug_mode:
                        print(f"⚠️ Archive API returned error: {result['error']}")
                tools_used.append("archive_api")
            
            # Build enhanced system prompt with trimmed sections based on detected needs
            system_prompt = self._build_system_prompt(request_analysis, memory_context, api_results)
            if debug_mode:
                if api_results.get("research"):
                    papers_in_prompt = len(api_results.get("research", {}).get("results", []))
                    print(f"🔍 System prompt includes {papers_in_prompt} papers from Archive API")
                if api_results.get("shell_info"):
                    output_len = len(api_results["shell_info"].get("output", ""))
                    print(f"🔍 System prompt includes shell_info with {output_len} chars of output")
                    print(f"🔍 Shell command was: {api_results['shell_info'].get('command', 'NONE')}")
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            # If we have file context, inject it as an additional grounding message
            fc = api_results.get("files_context")
            if fc:
                messages.append({"role": "system", "content": f"Grounding from mentioned file(s):\n{fc}\n\nAnswer based strictly on this content when relevant. Do not run shell commands."})
            missing = api_results.get("files_missing")
            if missing:
                messages.append({"role": "system", "content": f"User mentioned file(s) not found: {missing}. Respond explicitly that the file was not found and avoid speculation."})
            forbidden = api_results.get("files_forbidden")
            if forbidden:
                messages.append({"role": "system", "content": f"User mentioned file(s) outside the allowed workspace or sensitive paths: {forbidden}. Refuse to access and explain the restriction succinctly."})
            
            # Add conversation history with smart context management
            if len(self.conversation_history) > 12:
                # For long conversations, summarize early context and keep recent history
                early_history = self.conversation_history[:-6]
                recent_history = self.conversation_history[-6:]
                
                # Create a summary of early conversation
                summary_prompt = "Summarize the key points from this conversation history in 2-3 sentences:"
                summary_messages = [
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": str(early_history)}
                ]
                
                try:
                    if self._ensure_client_ready():
                        summary_response = self.client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=summary_messages,
                            max_tokens=160,
                            temperature=0.2
                        )
                        conversation_summary = summary_response.choices[0].message.content
                        if summary_response.usage and summary_response.usage.total_tokens:
                            summary_tokens = summary_response.usage.total_tokens
                            self._charge_tokens(request.user_id, summary_tokens)
                            self.total_cost += (summary_tokens / 1000) * self.cost_per_1k_tokens
                        else:
                            summary_tokens = 0
                        messages.append({"role": "system", "content": f"Previous conversation summary: {conversation_summary}"})
                        self._emit_telemetry(
                            "history_summarized",
                            request,
                            success=True,
                            extra={
                                "history_length": len(self.conversation_history),
                                "summary_tokens": summary_tokens,
                            },
                        )
                except:
                    # If summary fails, just use recent history
                    pass
                
                messages.extend(recent_history)
            else:
                # For shorter conversations, use full history
                messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": request.question})

            model_config = self._select_model(request, request_analysis, api_results)
            target_model = model_config["model"]
            max_completion_tokens = model_config["max_tokens"]
            temperature = model_config["temperature"]
            
            # Check token budget
            estimated_tokens = (len(str(messages)) // 4) + max_completion_tokens  # Rough estimate incl. completion budget
            if not self._check_token_budget(estimated_tokens):
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="Daily Groq token budget exhausted",
                    error_message="Daily token limit reached"
                )

            if not self._check_user_token_budget(request.user_id, estimated_tokens):
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="Per-user Groq token budget exhausted",
                    error_message="Per-user token limit reached"
                )

            if not self._ensure_client_ready():
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="No available Groq API key"
                )

            response_text: Optional[str] = None
            tokens_used = 0
            attempts_remaining = len(self.api_keys) if self.api_keys else (1 if self.client else 0)
            last_error: Optional[Exception] = None

            while attempts_remaining > 0:
                attempts_remaining -= 1
                try:
                    response = self.client.chat.completions.create(
                        model=target_model,
                        messages=messages,
                        max_tokens=max_completion_tokens,
                        temperature=temperature
                    )

                    response_text = response.choices[0].message.content
                    tokens_used = response.usage.total_tokens if response.usage else estimated_tokens
                    self._charge_tokens(request.user_id, tokens_used)
                    cost = (tokens_used / 1000) * self.cost_per_1k_tokens
                    self.total_cost += cost
                    break
                except Exception as e:
                    last_error = e
                    if self._is_rate_limit_error(e):
                        self._mark_current_key_exhausted(str(e))
                        if not self._rotate_to_next_available_key():
                            break
                        continue
                    else:
                        error_str = str(e)
                        friendly = self._format_model_error(error_str)
                        return ChatResponse(
                            response=friendly,
                            timestamp=datetime.now().isoformat(),
                            tools_used=tools_used,
                            api_results=api_results,
                            error_message=error_str
                        )

            if response_text is None:
                rate_limit_error = last_error if last_error and self._is_rate_limit_error(last_error) else None
                if rate_limit_error:
                    return self._respond_with_fallback(
                        request,
                        tools_used,
                        api_results,
                        failure_reason="All Groq API keys exhausted",
                        error_message=str(rate_limit_error)
                    )
                error_str = str(last_error) if last_error else "Unknown error"
                friendly = self._format_model_error(error_str)
                return ChatResponse(
                    response=friendly,
                    timestamp=datetime.now().isoformat(),
                    tools_used=tools_used,
                    api_results=api_results,
                    error_message=error_str
                )

            self._schedule_next_key_rotation()
            
            allow_shell_commands = "shell" in request_analysis.get("apis", []) or request_analysis.get("type") in {"system", "comprehensive+system"}
            if api_results.get("files_context") or api_results.get("files_missing") or api_results.get("files_forbidden"):
                allow_shell_commands = False
            # CRITICAL: If shell planner already executed commands, do NOT extract more from LLM response
            # (shell_info means shell planner already ran in the production path)
            if api_results.get("shell_info"):
                allow_shell_commands = False

            commands = re.findall(r'`([^`]+)`', response_text) if allow_shell_commands else []
            execution_results = {}
            final_response = response_text

            if commands:
                command = commands[0].strip()
                if self._is_safe_shell_command(command):
                    print(f"\n🔧 Executing: {command}")
                    output = self.execute_command(command)
                    print(f"✅ Command completed")
                    execution_results = {
                        "command": command,
                        "output": output,
                        "success": not output.startswith("ERROR:")
                    }
                    tools_used.append("shell_execution")
                else:
                    execution_results = {
                        "command": command,
                        "output": "Command blocked by safety policy",
                        "success": False
                    }
                    if "⚠️ Shell command skipped for safety." not in final_response:
                        final_response = f"{final_response.strip()}\n\n⚠️ Shell command skipped for safety."
                
                # Create analysis prompt only if we actually executed and have output
                if execution_results.get("success") and isinstance(execution_results.get("output"), str):
                    truncated_output = execution_results["output"]
                    truncated_flag = False
                    if len(truncated_output) > 1000:
                        truncated_output = truncated_output[:1000]
                        truncated_flag = True

                    summarised_text, summary_tokens = self._summarize_command_output(
                        request,
                        command,
                        truncated_output,
                        response_text
                    )

                    final_response = summarised_text
                    if truncated_flag:
                        final_response += "\n\n(Output truncated to first 1000 characters.)"
                    if summary_tokens:
                        self._charge_tokens(request.user_id, summary_tokens)
                        tokens_used += summary_tokens
            else:
                final_response = response_text
            
            footer = self._format_data_sources_footer()
            if footer:
                final_response = f"{final_response}\n\n_{footer}_"

            # TRUTH-SEEKING VERIFICATION: Check if response matches actual shell output
            if "shell_info" in api_results and api_results["shell_info"]:
                shell_output = api_results["shell_info"].get("output", "")

                # If shell output was empty or says "no results", but response lists specific items
                # This indicates hallucination
                if (not shell_output or "no" in shell_output.lower() and "found" in shell_output.lower()):
                    # Check if response contains made-up file paths or code
                    response_lower = final_response.lower()
                    if any(indicator in response_lower for indicator in [".py:", "found in", "route", "@app", "@router", "file1", "file2"]):
                        # Hallucination detected - replace with honest answer
                        final_response = "I searched but found no matches. The search returned no results."
                        logger.warning("🚨 Hallucination prevented: LLM tried to make up results when shell output was empty")

            expected_tools: Set[str] = set()
            if "finsight" in request_analysis.get("apis", []):
                expected_tools.add("finsight_api")
            if "archive" in request_analysis.get("apis", []):
                expected_tools.add("archive_api")
            for expected in expected_tools:
                if expected not in tools_used:
                    self._emit_telemetry(
                        "tool_missing",
                        request,
                        success=False,
                        extra={"expected": expected},
                    )

            response_obj = ChatResponse(
                response=final_response,
                tools_used=tools_used,
                reasoning_steps=[f"Request type: {request_analysis['type']}", f"APIs used: {request_analysis['apis']}"],
                timestamp=datetime.now().isoformat(),
                tokens_used=tokens_used,
                confidence_score=request_analysis['confidence'],
                execution_results=execution_results,
                api_results=api_results
            )
            return self._finalize_interaction(
                request,
                response_obj,
                tools_used,
                api_results,
                request_analysis,
                log_workflow=True,
            )
            
        except Exception as e:
            import traceback
            details = str(e)
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            if debug_mode:
                print("🔴 FULL TRACEBACK:")
                traceback.print_exc()
            message = (
                "⚠️ Something went wrong while orchestrating your request, but no actions were performed. "
                "Please retry, and if the issue persists share this detail with the team: {details}."
            ).format(details=details)
            return ChatResponse(
                response=message,
                timestamp=datetime.now().isoformat(),
                confidence_score=0.0,
                error_message=details
            )
    
    async def process_request_streaming(self, request: ChatRequest):
        """
        Process request with streaming response from Groq API
        Returns a Groq stream object that yields chunks as they arrive

        This enables real-time character-by-character streaming in the UI
        """
        # PRODUCTION MODE: Backend doesn't support streaming yet, use regular response
        if self.client is None:
            response = await self.call_backend_query(request.question, self.conversation_history[-10:])
            async def single_yield():
                yield response.response
            return single_yield()

        # DEV MODE ONLY
        try:
            # Quick budget checks
            if not self._check_query_budget(request.user_id):
                effective_limit = self.daily_query_limit if self.daily_query_limit > 0 else self.per_user_query_limit
                if effective_limit <= 0:
                    effective_limit = 25
                error_msg = (
                    f"Daily query limit reached. You've hit the {effective_limit} request cap for today. "
                    "Try again tomorrow or reach out if you need the limit raised."
                )
                async def error_gen():
                    yield error_msg
                return error_gen()

            self._record_query_usage(request.user_id)
            
            # Analyze request
            request_analysis = await self._analyze_request_type(request.question)
            question_lower = request.question.lower()
            self._reset_data_sources()

            # Direct shell commands (non-streaming fallback)
            direct_shell = re.match(r"^(?:run|execute)\s*:?\s*(.+)$", request.question.strip(), re.IGNORECASE)
            if direct_shell:
                result = self._respond_with_shell_command(request, direct_shell.group(1).strip())
                async def shell_gen():
                    yield result.response
                return shell_gen()

            # Memory context
            memory_context = self._get_memory_context(request.user_id, request.conversation_id)

            # Quick greetings (non-streaming)
            if self._is_simple_greeting(request.question):
                async def greeting_gen():
                    yield "Hi there! I'm up and ready whenever you want to dig into finance or research."
                return greeting_gen()

            if self._is_casual_acknowledgment(request.question):
                async def ack_gen():
                    yield "Happy to help! Feel free to fire off another question whenever you're ready."
                return ack_gen()
            
            # Gather API results (same logic as process_request but abbreviated)
            api_results = {}
            tools_used = []

            # File preview
            def _extract_filenames(text: str) -> List[str]:
                patterns = [
                    r"[\w\-./]+\.(?:py|md|txt|json|csv|yml|yaml|toml|ini|ts|tsx|js|ipynb)",
                    r"(?:\./|/)?[\w\-./]+/"
                ]
                matches: List[str] = []
                for pat in patterns:
                    matches.extend(re.findall(pat, text))
                uniq = []
                for m in matches:
                    if len(m) <= 256 and m not in uniq:
                        uniq.append(m)
                return uniq[:5]

            mentioned = _extract_filenames(request.question)
            file_previews: List[Dict[str, Any]] = []
            files_forbidden: List[str] = []
            base_dir = Path.cwd().resolve()
            sensitive_roots = {Path('/etc'), Path('/proc'), Path('/sys'), Path('/dev'), Path('/root'), Path('/usr'), Path('/bin'), Path('/sbin'), Path('/var')}
            
            def _is_safe_path(path_str: str) -> bool:
                try:
                    rp = Path(path_str).resolve()
                    if any(str(rp).startswith(str(sr)) for sr in sensitive_roots):
                        return False
                    return str(rp).startswith(str(base_dir))
                except Exception:
                    return False
                    
            for m in mentioned:
                if not _is_safe_path(m):
                    files_forbidden.append(m)
                    continue
                pr = await self._preview_file(m)
                if pr:
                    file_previews.append(pr)
                    
            if file_previews:
                api_results["files"] = file_previews
                text_previews = [fp for fp in file_previews if fp.get("type") == "text" and fp.get("preview")]
                files_context = ""
                if text_previews:
                    fp = text_previews[0]
                    quoted = "\n".join(fp["preview"].splitlines()[:20])
                    files_context = f"File: {fp['path']} (first lines)\n" + quoted
                api_results["files_context"] = files_context
            elif mentioned:
                api_results["files_missing"] = mentioned
            if files_forbidden:
                api_results["files_forbidden"] = files_forbidden

            # Workspace listing
            workspace_listing: Optional[Dict[str, Any]] = None
            if not file_previews:
                file_browse_keywords = ("list files", "show files", "what files")
                describe_files = ("file" in question_lower or "directory" in question_lower)
                if any(keyword in question_lower for keyword in file_browse_keywords) or describe_files:
                    workspace_listing = await self._get_workspace_listing()
                    api_results["workspace_listing"] = workspace_listing

            if workspace_listing and set(request_analysis.get("apis", [])) <= {"shell"}:
                result = self._respond_with_workspace_listing(request, workspace_listing)
                async def workspace_gen():
                    yield result.response
                return workspace_gen()
            
            # FinSight API (abbreviated)
            if "finsight" in request_analysis["apis"]:
                session_key = f"{request.user_id}:{request.conversation_id}"
                tickers, metrics_to_fetch = self._plan_financial_request(request.question, session_key)
                financial_payload = {}

                for ticker in tickers:
                    result = await self.get_financial_metrics(ticker, metrics_to_fetch)
                    financial_payload[ticker] = result

                if financial_payload:
                    api_results["financial"] = financial_payload
                    tools_used.append("finsight_api")
            
            # Archive API (abbreviated)
            if "archive" in request_analysis["apis"]:
                result = await self.search_academic_papers(request.question, 5)
                if "error" not in result:
                    api_results["research"] = result
                else:
                    api_results["research"] = {"error": result["error"]}
                tools_used.append("archive_api")
            
            # Build messages
            system_prompt = self._build_system_prompt(request_analysis, memory_context, api_results)
            messages = [{"role": "system", "content": system_prompt}]
            
            fc = api_results.get("files_context")
            if fc:
                messages.append({"role": "system", "content": f"Grounding from mentioned file(s):\n{fc}"})
            
            # Add conversation history (abbreviated - just recent)
            if len(self.conversation_history) > 6:
                messages.extend(self.conversation_history[-6:])
            else:
                messages.extend(self.conversation_history)
            
            messages.append({"role": "user", "content": request.question})

            # Model selection
            model_config = self._select_model(request, request_analysis, api_results)
            target_model = model_config["model"]
            max_completion_tokens = model_config["max_tokens"]
            temperature = model_config["temperature"]
            
            # Token budget check
            estimated_tokens = (len(str(messages)) // 4) + max_completion_tokens
            if not self._check_token_budget(estimated_tokens):
                async def budget_gen():
                    yield "⚠️ Daily Groq token budget exhausted. Please try again tomorrow."
                return budget_gen()

            if not self._ensure_client_ready():
                async def no_key_gen():
                    yield "⚠️ No available Groq API key."
                return no_key_gen()

            # **STREAMING: Call Groq with stream=True**
            try:
                stream = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    max_tokens=max_completion_tokens,
                    temperature=temperature,
                    stream=True  # Enable streaming!
                )
                
                # Update conversation history (add user message now, assistant message will be added after streaming completes)
                self.conversation_history.append({"role": "user", "content": request.question})
                
                # Return the stream directly - groq_stream_to_generator() in streaming_ui.py will handle it
                return stream
                
            except Exception as e:
                if self._is_rate_limit_error(e):
                    self._mark_current_key_exhausted(str(e))
                    if self._rotate_to_next_available_key():
                        try:
                            stream = self.client.chat.completions.create(
                                model=target_model,
                                messages=messages,
                                max_tokens=max_completion_tokens,
                                temperature=temperature,
                                stream=True
                            )
                            self.conversation_history.append({"role": "user", "content": request.question})
                            return stream
                        except:
                            pass
                async def error_gen():
                    yield f"⚠️ Groq API error: {str(e)}"
                return error_gen()
                        
        except Exception as e:
            async def exception_gen():
                yield f"⚠️ Request failed: {str(e)}"
            return exception_gen()
    
    async def run_interactive(self):
        """Run interactive chat session"""
        if not await self.initialize():
            return
            
        print("\n" + "="*70)
        print("🤖 ENHANCED NOCTURNAL AI AGENT")
        print("="*70)
        print("Research Assistant with Archive API + FinSight API Integration")
        print("Type 'quit' to exit")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    await self.close()
                    break
                
                # Process request
                request = ChatRequest(question=user_input)
                response = await self.process_request(request)
                
                print(f"\n🤖 Agent: {response.response}")
                
                if response.api_results:
                    print(f"📊 API Results: {len(response.api_results)} sources used")
                
                if response.execution_results:
                    print(f"🔧 Command: {response.execution_results['command']}")
                    print(f"📊 Success: {response.execution_results['success']}")
                
                print(f"📈 Tokens used: {response.tokens_used}")
                print(f"🎯 Confidence: {response.confidence_score:.2f}")
                print(f"🛠️ Tools used: {', '.join(response.tools_used) if response.tools_used else 'None'}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                await self.close()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

async def main():
    """Main entry point"""
    agent = EnhancedNocturnalAgent()
    await agent.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
