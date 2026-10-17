import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.infrastructure.database import get_db_connection


class ToolRepository:
    """自作プログラム・自動化ツール一覧の管理リポジトリ"""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, description, badge, tags, url, status, sort_order, created_at
                FROM tools
                ORDER BY sort_order ASC, created_at ASC;
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "badge": row["badge"],
                    "tags": [t.strip() for t in row["tags"].split(",") if t.strip()] if row["tags"] else [],
                    "url": row["url"],
                    "status": row["status"],
                    "sort_order": row["sort_order"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

    @staticmethod
    def get_by_id(tool_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, badge, tags, url, status, sort_order, created_at FROM tools WHERE id = ?;",
                (tool_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "badge": row["badge"],
                "tags": [t.strip() for t in row["tags"].split(",") if t.strip()] if row["tags"] else [],
                "url": row["url"],
                "status": row["status"],
                "sort_order": row["sort_order"],
                "created_at": row["created_at"],
            }

    @staticmethod
    def create(
        title: str,
        description: str,
        badge: str = "",
        tags: str = "",
        url: str = "",
        status: str = "active",
        sort_order: int = 0,
    ) -> Dict[str, Any]:
        tool_id = f"tool-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tools (id, title, description, badge, tags, url, status, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (tool_id, title, description, badge, tags, url, status, sort_order, created_at),
            )
            conn.commit()

        return ToolRepository.get_by_id(tool_id)

    @staticmethod
    def update(tool_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fields = []
        values = []
        for key in ["title", "description", "badge", "tags", "url", "status", "sort_order"]:
            if key in updates and updates[key] is not None:
                fields.append(f"{key} = ?")
                values.append(updates[key])

        if not fields:
            return ToolRepository.get_by_id(tool_id)

        values.append(tool_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE tools SET {', '.join(fields)} WHERE id = ?;",
                values,
            )
            conn.commit()

        return ToolRepository.get_by_id(tool_id)

    @staticmethod
    def delete(tool_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tools WHERE id = ?;", (tool_id,))
            conn.commit()
            return cursor.rowcount > 0
