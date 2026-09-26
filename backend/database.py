import sqlite3
import json
from typing import List, Optional, Dict, Any
from backend.config import DB_PATH
from backend.models import AnalysisResult, HistorySummary

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                platform TEXT,
                verdict TEXT,
                trust_score INTEGER,
                confidence INTEGER,
                analysis_timestamp TEXT,
                full_json TEXT
            )
        """)
        conn.commit()

# Ensure table creation immediately
init_db()

def save_analysis(result: AnalysisResult):
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO analyses (
                id, url, title, platform, verdict, trust_score, confidence, analysis_timestamp, full_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.id,
            result.url,
            result.title,
            result.platform,
            result.overall_verdict,
            result.trust_score,
            result.confidence,
            result.analysis_timestamp,
            result.model_dump_json()
        ))
        conn.commit()

def get_history(limit: int = 50) -> List[HistorySummary]:
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, url, title, platform, verdict, trust_score, confidence, analysis_timestamp
            FROM analyses
            ORDER BY analysis_timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            HistorySummary(
                id=row["id"],
                url=row["url"],
                title=row["title"] or "Untitled Content",
                platform=row["platform"],
                verdict=row["verdict"],
                trust_score=row["trust_score"],
                confidence=row["confidence"],
                analysis_timestamp=row["analysis_timestamp"]
            )
            for row in rows
        ]

def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.execute("SELECT full_json FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row["full_json"])
        return None

def delete_analysis(analysis_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_history() -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()
        return True
