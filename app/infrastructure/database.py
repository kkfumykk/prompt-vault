import hashlib
import sqlite3
from pathlib import Path
from app.core.config import DB_PATH, DEFAULT_ADMIN_PASSWORD


def hash_password(password: str) -> str:
    """パスワードのSHA-256ハッシュを計算"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


DEFAULT_ENV_INFO = """### 🎨 推奨AI生成環境 & ワークフロー
- **推奨モデル**: Illustrious-XL / Animagine XL / Pony Diffusion / Flux.1
- **推奨サンプラー**: Euler a / DPM++ 2M Karras
- **ステップ数 / CFG**: 28〜32 Steps / CFG Scale 5.0〜7.0
- **推奨解像度**: 832×1216 (ポスター/美女特化縦長) / Hires.fix 1.5x
- **ツール環境**: ComfyUI / WebUI Forge 推奨
"""


def init_db() -> None:
    """データベーステーブルとインデックスの初期化"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 画像エントリテーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                thumbnail_path TEXT NOT NULL,
                raw_prompt TEXT NOT NULL,
                model_name TEXT DEFAULT '',
                created_at TIMESTAMP NOT NULL
            );
            """
        )

        # タグ辞書テーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL COLLATE NOCASE,
                usage_count INTEGER DEFAULT 1
            );
            """
        )

        # 画像とタグの多対多リレーション
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id TEXT NOT NULL,
                tag_name TEXT NOT NULL COLLATE NOCASE,
                PRIMARY KEY (image_id, tag_name),
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_name) REFERENCES tags(name) ON DELETE CASCADE
            );
            """
        )

        # サイト・管理画面設定テーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        # 制作・自動化ツール一覧テーブル (拡張可能なプログラムリスト)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tools (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                badge TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                url TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL
            );
            """
        )

        # 高速検索用インデックス
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_usage ON tags(usage_count DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_tags_tag ON image_tags(tag_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_created ON images(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_order ON tools(sort_order ASC, created_at ASC);")

        # デフォルト設定値の登録（存在しない場合のみ）
        initial_settings = {
            "admin_password_hash": hash_password(DEFAULT_ADMIN_PASSWORD),
            "x_username": "amkki_aipix",
            "x_share_text": "【AIイラスト】プロンプト公開中！✨ プロンプトをチェック👇",
            "pixai_promo_enabled": "1",
            "promo_main_text": "便利な自動化ツールを有料で公開中",
            "pixai_promo_title": "便利な自動化ツールを有料で公開中",
            "pixai_promo_desc": "クリックでツール一覧を表示",
            "pixai_promo_url": "https://brain-market.com/u/kkfumykk/a/bwADNwcjMgoTZsNWa0JXY",
            "pixai_promo_badge": "便利な自動化ツールを有料で公開中",
            "environment_info": DEFAULT_ENV_INFO,
            "site_title": "prompt.archive / amkki",
            "site_description": "制作プロンプトと出力ログのアーカイブ",
        }

        for k, v in initial_settings.items():
            cursor.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);",
                (k, v),
            )

        # デフォルトの自作プログラム・ツール群の初期登録
        default_tools = [
            (
                "tool-pixai-credit",
                "PixAI デイリークレジット自動回収スクリプト",
                "複数アカウントのログインボーナスやデイリータスクを完全自動で取得・巡回。手動での受取作業をゼロにし、効率よくクレジットを蓄積するPythonスクリプト。",
                "有料公開中",
                "Python, RPA / 自動化, PixAI, 複数アカウント",
                "https://brain-market.com/u/kkfumykk/a/bwADNwcjMgoTZsNWa0JXY",
                "active",
                1,
                "2026-10-18 00:00:00",
            ),
            (
                "tool-comfyui-batch",
                "ComfyUI プロンプト・LoRA一括生成アシスタント",
                "プロンプトのバリエーション展開やLoRA強度テストを自動化し、大量の候補画像をバックグラウンドで効率的に生成・選別するワークフロースクリプト。",
                "開発中",
                "ComfyUI, バッチ生成, 効率化",
                "#",
                "coming_soon",
                2,
                "2026-10-18 00:00:01",
            ),
            (
                "tool-image-tag-sorter",
                "画像メタデータ・タグ自動分類アーカイブツール",
                "ローカルに蓄積された大量のAI生成画像からプロンプト・モデル・LoRAメタデータを高速抽出し、キャラクター・衣装・スタイル別に自動分類する整理ツール。",
                "準備中",
                "Python, メタデータ, アーカイブ整理",
                "#",
                "coming_soon",
                3,
                "2026-10-18 00:00:02",
            ),
        ]

        for tool in default_tools:
            cursor.execute(
                """
                INSERT OR IGNORE INTO tools (id, title, description, badge, tags, url, status, sort_order, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                tool,
            )

        conn.commit()
