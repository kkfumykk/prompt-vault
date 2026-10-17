from datetime import datetime
from typing import List, Optional, Tuple

from app.domain.models import ImageEntry
from app.domain.repositories import IImageRepository, ITagRepository
from app.infrastructure.database import get_db_connection


class SqliteImageRepository(IImageRepository):
    """SQLiteによる画像エントリ永続化リポジトリ"""

    def save(self, entry: ImageEntry) -> ImageEntry:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 画像本体のUPSERT
            cursor.execute(
                """
                INSERT INTO images (id, filename, stored_path, thumbnail_path, raw_prompt, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    filename = excluded.filename,
                    stored_path = excluded.stored_path,
                    thumbnail_path = excluded.thumbnail_path,
                    raw_prompt = excluded.raw_prompt,
                    created_at = excluded.created_at;
                """,
                (
                    entry.id,
                    entry.filename,
                    entry.stored_path,
                    entry.thumbnail_path,
                    entry.raw_prompt,
                    entry.created_at.isoformat(),
                ),
            )

            # 既存の紐付けタグを一旦クリアして再登録
            cursor.execute("DELETE FROM image_tags WHERE image_id = ?;", (entry.id,))

            for tag_name in entry.tags:
                # tagsテーブルに登録（なければ挿入、あれば使用カウント+1）
                cursor.execute(
                    """
                    INSERT INTO tags (name, usage_count)
                    VALUES (?, 1)
                    ON CONFLICT(name) DO UPDATE SET usage_count = usage_count + 1;
                    """,
                    (tag_name,),
                )

                # image_tagsテーブルに紐付け
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO image_tags (image_id, tag_name)
                    VALUES (?, ?);
                    """,
                    (entry.id, tag_name),
                )

            conn.commit()
            return entry

    def find_by_id(self, entry_id: str) -> Optional[ImageEntry]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM images WHERE id = ?;", (entry_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT tag_name FROM image_tags WHERE image_id = ?;", (entry_id,))
            tags = [r["tag_name"] for r in cursor.fetchall()]

            return ImageEntry(
                id=row["id"],
                filename=row["filename"],
                stored_path=row["stored_path"],
                thumbnail_path=row["thumbnail_path"],
                raw_prompt=row["raw_prompt"],
                tags=tags,
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def search_by_tags(self, tags: List[str], limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        if not tags:
            return self.get_all(limit=limit, offset=offset)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 指定されたすべてのタグを持つエントリをAND検索
            placeholders = ",".join(["?"] * len(tags))
            query = f"""
                SELECT i.id, i.filename, i.stored_path, i.thumbnail_path, i.raw_prompt, i.created_at
                FROM images i
                JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_name IN ({placeholders})
                GROUP BY i.id
                HAVING COUNT(DISTINCT it.tag_name) = ?
                ORDER BY i.created_at DESC
                LIMIT ? OFFSET ?;
            """
            params = tags + [len(tags), limit, offset]
            cursor.execute(query, params)
            rows = cursor.fetchall()

            entries = []
            for row in rows:
                cursor.execute("SELECT tag_name FROM image_tags WHERE image_id = ?;", (row["id"],))
                t_list = [r["tag_name"] for r in cursor.fetchall()]
                entries.append(
                    ImageEntry(
                        id=row["id"],
                        filename=row["filename"],
                        stored_path=row["stored_path"],
                        thumbnail_path=row["thumbnail_path"],
                        raw_prompt=row["raw_prompt"],
                        tags=t_list,
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                )
            return entries

    def search_by_keyword(self, keyword: str, limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        kw = f"%{keyword}%"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT i.id, i.filename, i.stored_path, i.thumbnail_path, i.raw_prompt, i.created_at
                FROM images i
                LEFT JOIN image_tags it ON i.id = it.image_id
                WHERE i.raw_prompt LIKE ? OR it.tag_name LIKE ?
                ORDER BY i.created_at DESC
                LIMIT ? OFFSET ?;
            """
            cursor.execute(query, (kw, kw, limit, offset))
            rows = cursor.fetchall()

            entries = []
            for row in rows:
                cursor.execute("SELECT tag_name FROM image_tags WHERE image_id = ?;", (row["id"],))
                t_list = [r["tag_name"] for r in cursor.fetchall()]
                entries.append(
                    ImageEntry(
                        id=row["id"],
                        filename=row["filename"],
                        stored_path=row["stored_path"],
                        thumbnail_path=row["thumbnail_path"],
                        raw_prompt=row["raw_prompt"],
                        tags=t_list,
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                )
            return entries

    def get_all(self, limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename, stored_path, thumbnail_path, raw_prompt, created_at
                FROM images
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()

            entries = []
            for row in rows:
                cursor.execute("SELECT tag_name FROM image_tags WHERE image_id = ?;", (row["id"],))
                t_list = [r["tag_name"] for r in cursor.fetchall()]
                entries.append(
                    ImageEntry(
                        id=row["id"],
                        filename=row["filename"],
                        stored_path=row["stored_path"],
                        thumbnail_path=row["thumbnail_path"],
                        raw_prompt=row["raw_prompt"],
                        tags=t_list,
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                )
            return entries

    def count(self) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM images;")
            return cursor.fetchone()[0]

    def delete(self, entry_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM images WHERE id = ?;", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0


class SqliteTagRepository(ITagRepository):
    """SQLiteによるタグ辞書・サジェストリポジトリ"""

    def suggest(self, prefix: str, limit: int = 15) -> List[str]:
        prefix = prefix.strip()
        if not prefix:
            return [t[0] for t in self.get_popular(limit)]

        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 1. 前方一致を最優先、その後に部分一致を結合して返却
            query = """
                SELECT name, usage_count,
                    CASE
                        WHEN name LIKE ? THEN 1
                        ELSE 2
                    END as match_priority
                FROM tags
                WHERE name LIKE ?
                ORDER BY match_priority ASC, usage_count DESC
                LIMIT ?;
            """
            starts_with = f"{prefix}%"
            contains = f"%{prefix}%"
            cursor.execute(query, (starts_with, contains, limit))
            rows = cursor.fetchall()
            return [row["name"] for row in rows]

    def get_popular(self, limit: int = 50) -> List[Tuple[str, int]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, usage_count
                FROM tags
                ORDER BY usage_count DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [(row["name"], row["usage_count"]) for row in cursor.fetchall()]
