#!/usr/bin/env python3
"""
Persistent Usage Database for Cite-Agent
Tracks tokens, queries, conversations, and user metrics across sessions
"""

import sqlite3
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class UsageDatabase:
    """
    SQLite database for persistent usage tracking
    
    Tracks:
    - Token usage per day/user
    - Query counts per day/user
    - Conversation history with full context
    - Tool usage patterns
    - Performance metrics
    - Cost tracking
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize usage database
        
        Args:
            db_path: Path to SQLite database file. Defaults to ~/.cite_agent/usage.db
        """
        if db_path is None:
            db_path = Path.home() / ".cite_agent" / "usage.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
        
        logger.info(f"Initialized usage database: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_schema(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Token usage tracking (daily aggregates)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL DEFAULT 0,
                    query_count INTEGER NOT NULL DEFAULT 0,
                    cost_usd REAL NOT NULL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(date, user_id)
                )
            """)
            
            # Individual query log (full detail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT,
                    tokens_used INTEGER,
                    tools_used TEXT,
                    response_time_ms INTEGER,
                    success INTEGER NOT NULL DEFAULT 1,
                    error_message TEXT,
                    metadata TEXT
                )
            """)
            
            # Conversation metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    total_queries INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'active',
                    summary TEXT
                )
            """)
            
            # Tool usage stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    success_count INTEGER NOT NULL DEFAULT 0,
                    avg_response_time_ms INTEGER,
                    UNIQUE(date, tool_name)
                )
            """)
            
            # Performance metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_usage_date ON token_usage(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_usage_user ON token_usage(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_log_timestamp ON query_log(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_log_conversation ON query_log(conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_usage_date ON tool_usage(date)")
            
            conn.commit()
            logger.info("Database schema initialized successfully")
    
    def record_query(
        self,
        user_id: str,
        conversation_id: str,
        query: str,
        response: str,
        tokens_used: int,
        tools_used: List[str],
        response_time_ms: int,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a query with full details"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert query log
            cursor.execute("""
                INSERT INTO query_log 
                (timestamp, user_id, conversation_id, query, response, tokens_used, 
                 tools_used, response_time_ms, success, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                user_id,
                conversation_id,
                query,
                response,
                tokens_used,
                json.dumps(tools_used),
                response_time_ms,
                1 if success else 0,
                error_message,
                json.dumps(metadata) if metadata else None
            ))
            
            # Update daily token usage
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            # Note: cost_usd = 0 since Cerebras is free (and Groq is ~$0.0001 per 1k tokens)
            cursor.execute("""
                INSERT INTO token_usage (date, user_id, tokens_used, query_count, cost_usd, created_at, updated_at)
                VALUES (?, ?, ?, 1, 0, ?, ?)
                ON CONFLICT(date, user_id) DO UPDATE SET
                    tokens_used = tokens_used + ?,
                    query_count = query_count + 1,
                    updated_at = ?
            """, (
                date,
                user_id,
                tokens_used,
                timestamp,
                timestamp,
                tokens_used,
                timestamp
            ))
            
            # Update conversation metadata
            cursor.execute("""
                INSERT INTO conversations (conversation_id, user_id, started_at, last_activity, total_queries, total_tokens)
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    last_activity = ?,
                    total_queries = total_queries + 1,
                    total_tokens = total_tokens + ?
            """, (
                conversation_id,
                user_id,
                timestamp,
                timestamp,
                tokens_used,
                timestamp,
                tokens_used
            ))
            
            # Periodically cleanup old conversations (keep last 5 per user)
            # Only run cleanup occasionally to avoid overhead (every 10th query)
            cursor.execute("SELECT total_queries FROM conversations WHERE conversation_id = ?", (conversation_id,))
            total_queries = cursor.fetchone()[0]
            if total_queries % 10 == 0:  # Run every 10 queries
                try:
                    self.cleanup_old_conversations(max_conversations=5, user_id=user_id)
                except Exception as e:
                    logger.warning(f"Failed to cleanup old conversations: {e}")
            
            # Update tool usage stats
            for tool in tools_used:
                cursor.execute("""
                    INSERT INTO tool_usage (date, tool_name, usage_count, success_count, avg_response_time_ms)
                    VALUES (?, ?, 1, ?, ?)
                    ON CONFLICT(date, tool_name) DO UPDATE SET
                        usage_count = usage_count + 1,
                        success_count = success_count + ?,
                        avg_response_time_ms = (avg_response_time_ms * usage_count + ?) / (usage_count + 1)
                """, (
                    date,
                    tool,
                    1 if success else 0,
                    response_time_ms,
                    1 if success else 0,
                    response_time_ms
                ))
    
    def get_daily_usage(self, user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get token/query usage for a specific day"""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tokens_used, query_count, cost_usd
                FROM token_usage
                WHERE date = ? AND user_id = ?
            """, (date, user_id))
            
            row = cursor.fetchone()
            if row:
                return {
                    "date": date,
                    "tokens_used": row["tokens_used"],
                    "query_count": row["query_count"],
                    "cost_usd": row["cost_usd"]
                }
            else:
                return {
                    "date": date,
                    "tokens_used": 0,
                    "query_count": 0,
                    "cost_usd": 0.0
                }
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent queries from a conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, query, response, tokens_used, tools_used, response_time_ms
                FROM query_log
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (conversation_id, limit))
            
            rows = cursor.fetchall()
            return [
                {
                    "timestamp": row["timestamp"],
                    "query": row["query"],
                    "response": row["response"],
                    "tokens_used": row["tokens_used"],
                    "tools_used": json.loads(row["tools_used"]) if row["tools_used"] else [],
                    "response_time_ms": row["response_time_ms"]
                }
                for row in rows
            ]
    
    def get_usage_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get usage summary for last N days"""
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total usage over period
            cursor.execute("""
                SELECT 
                    SUM(tokens_used) as total_tokens,
                    SUM(query_count) as total_queries,
                    SUM(cost_usd) as total_cost
                FROM token_usage
                WHERE user_id = ? AND date >= ?
            """, (user_id, start_date))
            
            row = cursor.fetchone()
            
            # Daily breakdown
            cursor.execute("""
                SELECT date, tokens_used, query_count, cost_usd
                FROM token_usage
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC
            """, (user_id, start_date))
            
            daily = cursor.fetchall()
            
            return {
                "period_days": days,
                "total_tokens": row["total_tokens"] or 0,
                "total_queries": row["total_queries"] or 0,
                "total_cost_usd": row["total_cost"] or 0.0,
                "daily_breakdown": [
                    {
                        "date": d["date"],
                        "tokens": d["tokens_used"],
                        "queries": d["query_count"],
                        "cost": d["cost_usd"]
                    }
                    for d in daily
                ]
            }
    
    def get_tool_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get tool usage statistics"""
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    tool_name,
                    SUM(usage_count) as total_uses,
                    SUM(success_count) as total_successes,
                    AVG(avg_response_time_ms) as avg_response_time
                FROM tool_usage
                WHERE date >= ?
                GROUP BY tool_name
                ORDER BY total_uses DESC
            """, (start_date,))
            
            rows = cursor.fetchall()
            return [
                {
                    "tool": row["tool_name"],
                    "uses": row["total_uses"],
                    "successes": row["total_successes"],
                    "success_rate": row["total_successes"] / row["total_uses"] if row["total_uses"] > 0 else 0,
                    "avg_response_ms": row["avg_response_time"]
                }
                for row in rows
            ]
    
    def cleanup_old_conversations(self, max_conversations: int = 5, user_id: Optional[str] = None):
        """
        Keep only the N most recent conversations per user (sliding window).
        
        Args:
            max_conversations: Maximum number of conversations to keep per user
            user_id: Specific user ID to clean up, or None for all users
            
        Returns:
            Number of conversations deleted
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all users or specific user
            if user_id:
                users = [user_id]
            else:
                cursor.execute("SELECT DISTINCT user_id FROM conversations")
                users = [row[0] for row in cursor.fetchall()]
            
            total_deleted = 0
            
            for uid in users:
                # Find conversations to delete (keeping only last N)
                cursor.execute("""
                    SELECT conversation_id
                    FROM conversations
                    WHERE user_id = ?
                    ORDER BY last_activity DESC
                    LIMIT -1 OFFSET ?
                """, (uid, max_conversations))
                
                conversations_to_delete = [row[0] for row in cursor.fetchall()]
                
                if conversations_to_delete:
                    # Delete associated query logs
                    placeholders = ','.join('?' * len(conversations_to_delete))
                    cursor.execute(
                        f"DELETE FROM query_log WHERE conversation_id IN ({placeholders})",
                        conversations_to_delete
                    )
                    deleted_queries = cursor.rowcount
                    
                    # Delete conversations
                    cursor.execute(
                        f"DELETE FROM conversations WHERE conversation_id IN ({placeholders})",
                        conversations_to_delete
                    )
                    deleted_convs = cursor.rowcount
                    
                    total_deleted += deleted_convs
                    
                    logger.info(
                        f"Cleaned up {deleted_convs} old conversations for user {uid} "
                        f"({deleted_queries} query logs deleted)"
                    )
            
            return total_deleted
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove data older than N days"""
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Keep aggregated daily stats, but remove detailed query logs
            cursor.execute("DELETE FROM query_log WHERE date(timestamp) < ?", (cutoff_date,))
            deleted_queries = cursor.rowcount
            
            # Mark old conversations as archived
            cursor.execute("""
                UPDATE conversations 
                SET status = 'archived'
                WHERE date(last_activity) < ? AND status = 'active'
            """, (cutoff_date,))
            
            # Keep token_usage (it's already aggregated)
            # Keep tool_usage (it's already aggregated)
            
            logger.info(f"Cleaned up {deleted_queries} old query logs (before {cutoff_date})")
            return deleted_queries
    
    def get_database_size(self) -> Dict[str, Any]:
        """Get database size and row counts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get file size
            db_size_bytes = self.db_path.stat().st_size
            db_size_mb = db_size_bytes / (1024 * 1024)
            
            # Get row counts
            tables = ['token_usage', 'query_log', 'conversations', 'tool_usage', 'performance_metrics']
            row_counts = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                row_counts[table] = cursor.fetchone()[0]
            
            return {
                "size_bytes": db_size_bytes,
                "size_mb": round(db_size_mb, 2),
                "row_counts": row_counts,
                "total_rows": sum(row_counts.values())
            }


# Singleton instance
_db_instance: Optional[UsageDatabase] = None


def get_usage_db() -> UsageDatabase:
    """Get global usage database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = UsageDatabase()
    return _db_instance
