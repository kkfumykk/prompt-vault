import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import DATA_DIR, STATIC_DIR
from app.infrastructure.database import init_db
from app.interfaces.api import router as api_router
from sync_service import run_sync


async def periodic_sync_worker():
    """1時間ごとに個人用Vaultから公開版へ自動で増分同期を行うバックグラウンドワーカー"""
    # 起動直後に1回同期
    try:
        res = run_sync()
        if res.get("new_images_added", 0) > 0:
            print(f"[SYNC] 起動時同期: {res.get('message')}")
    except Exception as e:
        print(f"[SYNC] 起動時同期エラー: {e}")

    # 1時間 (3600秒) おきに同期ループ
    while True:
        try:
            await asyncio.sleep(3600)
            res = run_sync()
            if res.get("new_images_added", 0) > 0:
                print(f"[SYNC] 1時間定期同期: {res.get('message')}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[SYNC] 定期同期エラー: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリ起動時にDB初期化
    init_db()
    # 1時間ごとのバックグラウンド自動同期タスクを開始
    sync_task = asyncio.create_task(periodic_sync_worker())
    yield
    # アプリ終了時にタスクを安全にキャンセル
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="prompt.archive / amkki",
    description="制作プロンプトと出力ログの個人アーカイブ（Xアカウント連携でプロンプト表示）",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(api_router)

# 画像・サムネイルデータの静的配信
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# 静的WebUIの配信
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
