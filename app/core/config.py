import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
DB_PATH = DATA_DIR / "database.sqlite"
STATIC_DIR = BASE_DIR / "static"

# 必要なディレクトリを自動作成
for p in [DATA_DIR, IMAGES_DIR, THUMBNAILS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8080))
THUMBNAIL_SIZE = (360, 360)

# デフォルト管理者パスワード（管理画面から変更可能）
DEFAULT_ADMIN_PASSWORD = "admin"
SECRET_KEY = os.environ.get("SECRET_KEY", "prompt-vault-public-secret-key-change-me")
