import os
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = Path("c:/business/prompt_image_vault/data")
DST_DIR = BASE_DIR / "data"

SRC_DB = SRC_DIR / "database.sqlite"
DST_DB = DST_DIR / "database.sqlite"
SRC_IMAGES = SRC_DIR / "images"
DST_IMAGES = DST_DIR / "images"
SRC_THUMBS = SRC_DIR / "thumbnails"
DST_THUMBS = DST_DIR / "thumbnails"


def push_to_github(added_count: int) -> bool:
    """
    新規画像が追加された場合に、自動でGitHubへコミット＆プッシュして
    クラウド（Render）のWebサイトを自動最新化（Auto-Deploy）する。
    """
    try:
        # dataディレクトリの変更をステージング
        subprocess.run(["git", "add", "data"], cwd=BASE_DIR, check=True, capture_output=True)
        # コミットする変更があるか確認
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE_DIR)
        if diff.returncode != 0:
            commit_msg = f"sync: auto-sync {added_count} new images"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True, capture_output=True)
            print(f"[SYNC] GitHubへの自動プッシュ成功: {added_count}件の差分をクラウドへ反映中")
            return True
        return False
    except Exception as e:
        print(f"[SYNC] GitHub自動プッシュ警告 (クラウド同期スキップ): {e}")
        return False


def run_sync() -> Dict[str, Any]:
    """
    個人用Vault (prompt_image_vault) から 公開用Vault (prompt_vault_public) へ
    新規・差分画像およびプロンプト・タグデータを安全に増分同期し、
    新規追加がある場合は自動でGitHubへプッシュしてクラウド本番環境を更新する。
    """
    if not SRC_DB.exists():
        return {"status": "error", "message": f"同期元のデータベースが見つかりません: {SRC_DB}"}

    DST_IMAGES.mkdir(parents=True, exist_ok=True)
    DST_THUMBS.mkdir(parents=True, exist_ok=True)

    added_images = 0
    copied_files = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. データベース同期
    src_conn = sqlite3.connect(SRC_DB)
    src_conn.row_factory = sqlite3.Row
    dst_conn = sqlite3.connect(DST_DB)
    dst_conn.row_factory = sqlite3.Row

    try:
        # 既存の公開版エントリIDを取得
        dst_cursor = dst_conn.cursor()
        dst_cursor.execute("SELECT id FROM images;")
        existing_ids = {row["id"] for row in dst_cursor.fetchall()}

        # 個人用Vaultから全エントリを取得
        src_cursor = src_conn.cursor()
        src_cursor.execute("SELECT id, filename, stored_path, thumbnail_path, raw_prompt, created_at FROM images;")
        src_rows = src_cursor.fetchall()

        new_images = [r for r in src_rows if r["id"] not in existing_ids]

        if new_images:
            for r in new_images:
                # DBレコードを公開版に登録
                dst_cursor.execute(
                    """
                    INSERT OR IGNORE INTO images (id, filename, stored_path, thumbnail_path, raw_prompt, model_name, created_at)
                    VALUES (?, ?, ?, ?, ?, '', ?);
                    """,
                    (r["id"], r["filename"], r["stored_path"], r["thumbnail_path"], r["raw_prompt"], r["created_at"])
                )

                # 画像ファイルの実体コピー
                img_src = SRC_DIR / r["stored_path"]
                img_dst = DST_DIR / r["stored_path"]
                if img_src.exists() and not img_dst.exists():
                    img_dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img_src, img_dst)
                    copied_files += 1

                # サムネイルファイルの実体コピー
                thumb_src = SRC_DIR / r["thumbnail_path"]
                thumb_dst = DST_DIR / r["thumbnail_path"]
                if thumb_src.exists() and not thumb_dst.exists():
                    thumb_dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(thumb_src, thumb_dst)
                    copied_files += 1

                added_images += 1

            # タグリレーション（image_tags）の同期
            src_cursor.execute("SELECT image_id, tag_name FROM image_tags;")
            for r in src_cursor.fetchall():
                dst_cursor.execute(
                    "INSERT OR IGNORE INTO image_tags (image_id, tag_name) VALUES (?, ?);",
                    (r["image_id"], r["tag_name"])
                )

            # タグマスター（tags）の再集計・更新
            dst_cursor.execute(
                """
                INSERT OR IGNORE INTO tags (name, usage_count)
                SELECT tag_name, COUNT(*) FROM image_tags GROUP BY tag_name;
                """
            )
            # 既存タグの使用回数カウントを最新化
            dst_cursor.execute(
                """
                UPDATE tags
                SET usage_count = (SELECT COUNT(*) FROM image_tags WHERE image_tags.tag_name = tags.name);
                """
            )

            dst_conn.commit()

        # 新規画像がある場合、自動でGitHubへプッシュしてクラウド本番を最新化
        pushed = False
        if added_images > 0:
            pushed = push_to_github(added_images)

        cloud_status = " (クラウド本番へ自動反映中)" if pushed else ""
        msg = f"同期完了: {added_images} 件の作品を公開版に反映しました{cloud_status}" if added_images > 0 else "差分なし（最新状態です）"

        result = {
            "status": "ok",
            "timestamp": now_str,
            "new_images_added": added_images,
            "files_copied": copied_files,
            "cloud_pushed": pushed,
            "message": msg
        }
        return result

    except Exception as e:
        dst_conn.rollback()
        return {"status": "error", "message": f"同期エラー: {str(e)}", "timestamp": now_str}
    finally:
        src_conn.close()
        dst_conn.close()


if __name__ == "__main__":
    res = run_sync()
    print(f"[{res.get('timestamp')}] {res.get('message')} (新規追加: {res.get('new_images_added', 0)}件)")
