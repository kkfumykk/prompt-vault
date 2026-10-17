from typing import List, Optional, Dict, Any
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile, Depends
from pydantic import BaseModel

from app.infrastructure.sqlite_repository import SqliteImageRepository, SqliteTagRepository
from app.infrastructure.settings_repository import SettingsRepository
from app.infrastructure.tool_repository import ToolRepository
from app.usecases.register_image import RegisterImageUseCase
from app.usecases.search_images import SearchImagesUseCase
from app.usecases.suggest_tags import SuggestTagsUseCase
from app.usecases.get_image import GetImageUseCase, DeleteImageUseCase

router = APIRouter(prefix="/api")

# リポジトリの初期化
image_repo = SqliteImageRepository()
tag_repo = SqliteTagRepository()
settings_repo = SettingsRepository()
tool_repo = ToolRepository()

# ユースケースの初期化
register_usecase = RegisterImageUseCase(image_repo)
search_usecase = SearchImagesUseCase(image_repo)
suggest_usecase = SuggestTagsUseCase(tag_repo)
get_usecase = GetImageUseCase(image_repo)
delete_usecase = DeleteImageUseCase(image_repo)


# --------------------------------------------------------------------------
# 認証依存性（Dependency Injection）
# --------------------------------------------------------------------------
def get_current_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    return None


def require_admin(authorization: Optional[str] = Header(None)) -> bool:
    """管理者Xアカウント (@amkki_aipix) のトークンを検証するガード"""
    token = get_current_token(authorization)
    if not token or not SettingsRepository.verify_admin(token):
        raise HTTPException(
            status_code=403,
            detail="管理者権限が必要です (@amkki_aipix のXアカウントでログインしてください)",
        )
    return True


def is_unlocked_user(authorization: Optional[str] = Header(None)) -> bool:
    """フォロワーまたは管理者としてアンロックされているかを判定"""
    token = get_current_token(authorization)
    if not token:
        return False
    session = SettingsRepository.get_session(token)
    return bool(session and (session.get("is_admin") or session.get("is_following")))


# --------------------------------------------------------------------------
# DTO (Data Transfer Objects)
# --------------------------------------------------------------------------
class EntryResponse(BaseModel):
    id: str
    filename: str
    stored_path: str
    thumbnail_path: str
    raw_prompt: str
    prompt_excerpt: str
    tags: List[str]
    created_at: str


class XLoginRequest(BaseModel):
    username: str
    following_confirmed: bool = True
    password: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class XSessionResponse(BaseModel):
    token: str
    username: str
    is_admin: bool
    is_following: bool


class SettingsUpdateRequest(BaseModel):
    x_username: Optional[str] = None
    x_share_text: Optional[str] = None
    promo_main_text: Optional[str] = None
    pixai_promo_enabled: Optional[str] = None
    pixai_promo_title: Optional[str] = None
    pixai_promo_desc: Optional[str] = None
    pixai_promo_url: Optional[str] = None
    pixai_promo_badge: Optional[str] = None
    environment_info: Optional[str] = None


class ToolItem(BaseModel):
    id: str
    title: str
    description: str
    badge: str
    tags: List[str]
    url: str
    status: str
    sort_order: int
    created_at: str


class ToolCreateRequest(BaseModel):
    title: str
    description: str
    badge: Optional[str] = ""
    tags: Optional[str] = ""
    url: Optional[str] = ""
    status: Optional[str] = "active"
    sort_order: Optional[int] = 0


class ToolUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    badge: Optional[str] = None
    tags: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


# --------------------------------------------------------------------------
# Xアカウント認証 API (X Authentication Endpoints)
# --------------------------------------------------------------------------
@router.post("/auth/x/login", response_model=XSessionResponse)
def x_login(req: XLoginRequest):
    """
    Xアカウント連携エンドポイント。
    一般ユーザー: パスワード不要でフォロワー判定・閲覧セッション発行。
    @amkki_aipix (管理者): 正しい管理者パスワードが必須。不一致の場合は401エラー。
    """
    if not req.username or not req.username.strip():
        raise HTTPException(status_code=400, detail="Xアカウント名を入力してください")

    cleaned_username = req.username.strip().lstrip("@")
    is_target_admin = cleaned_username.lower() == SettingsRepository.ADMIN_USERNAME.lower()
    is_admin = False

    if is_target_admin:
        if not req.password:
            raise HTTPException(
                status_code=401,
                detail="管理者アカウント (@amkki_aipix) にはパスワードが必要です",
            )
        if not SettingsRepository.verify_admin_password(req.password):
            raise HTTPException(
                status_code=401,
                detail="管理者パスワードが正しくありません",
            )
        is_admin = True

    token, session_data = SettingsRepository.create_x_session(
        username=cleaned_username,
        is_following=req.following_confirmed if not is_admin else True,
        is_admin=is_admin,
    )
    return XSessionResponse(
        token=token,
        username=session_data["username"],
        is_admin=session_data["is_admin"],
        is_following=session_data["is_following"],
    )


@router.post("/auth/change-password")
def change_password(req: PasswordChangeRequest, is_admin: bool = Depends(require_admin)):
    """管理者パスワードの変更"""
    if not SettingsRepository.verify_admin_password(req.current_password):
        raise HTTPException(status_code=400, detail="現在のパスワードが正しくありません")
    if len(req.new_password) < 4:
        raise HTTPException(status_code=400, detail="新しいパスワードは4文字以上で設定してください")
    SettingsRepository.update_admin_password(req.new_password)
    return {"status": "ok", "message": "管理者パスワードを変更しました"}


@router.get("/auth/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    """現在ログイン中のXアカウント情報を取得"""
    token = get_current_token(authorization)
    session = SettingsRepository.get_session(token)
    if not session:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "username": session["username"],
        "is_admin": session["is_admin"],
        "is_following": session["is_following"],
    }


@router.post("/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    """ログアウト"""
    token = get_current_token(authorization)
    if token:
        SettingsRepository.revoke_session(token)
    return {"status": "ok", "message": "ログアウトしました"}


# --------------------------------------------------------------------------
# 一般公開 API (Public Endpoints)
# --------------------------------------------------------------------------
@router.get("/settings/public")
def get_public_settings() -> Dict[str, Any]:
    """サイト設定・プロモーション情報・生成環境を取得"""
    return SettingsRepository.get_public_settings()


@router.get("/entries", response_model=List[EntryResponse])
def search_entries(
    q: str = "",
    limit: int = 60,
    offset: int = 0,
    authorization: Optional[str] = Header(None),
):
    """画像・プロンプトの検索および一覧取得（未認証時はプロンプトを完全マスク）"""
    unlocked = is_unlocked_user(authorization)
    results = search_usecase.execute(query=q, limit=limit, offset=offset)
    return [
        EntryResponse(
            id=e.id,
            filename=e.filename,
            stored_path=e.stored_path,
            thumbnail_path=e.thumbnail_path,
            raw_prompt=e.raw_prompt if unlocked else "",
            prompt_excerpt=e.prompt_excerpt if unlocked else "🔒 X連携でプロンプト表示",
            tags=e.tags if unlocked else [],
            created_at=e.created_at.strftime("%Y-%m-%d %H:%M"),
        )
        for e in results
    ]


@router.get("/entries/{entry_id}", response_model=EntryResponse)
def get_entry(
    entry_id: str,
    authorization: Optional[str] = Header(None),
):
    """単一エントリの詳細取得（未認証時はプロンプト・タグを完全マスク）"""
    entry = get_usecase.execute(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    unlocked = is_unlocked_user(authorization)
    return EntryResponse(
        id=entry.id,
        filename=entry.filename,
        stored_path=entry.stored_path,
        thumbnail_path=entry.thumbnail_path,
        raw_prompt=entry.raw_prompt if unlocked else "",
        prompt_excerpt=entry.prompt_excerpt if unlocked else "🔒 X連携でプロンプト表示",
        tags=entry.tags if unlocked else [],
        created_at=entry.created_at.strftime("%Y-%m-%d %H:%M"),
    )


@router.get("/tags/suggest")
def suggest_tags(prefix: str = "", limit: int = 10):
    """タグ予測サジェストAPI（Tabキー自動補完用）"""
    suggestions = suggest_usecase.execute(prefix=prefix, limit=limit)
    return {"prefix": prefix, "suggestions": suggestions}


@router.get("/tags/popular")
def get_popular_tags(limit: int = 30):
    """タグ例（使用頻度順）を取得"""
    popular = tag_repo.get_popular(limit=limit)
    return [{"name": name, "count": count} for name, count in popular]


# --------------------------------------------------------------------------
# 管理者専用 操作 API (Protected Endpoints: @amkki_aipix のみ)
# --------------------------------------------------------------------------
@router.get("/admin/settings")
def get_admin_settings(is_admin: bool = Depends(require_admin)) -> Dict[str, str]:
    """管理者用 全設定取得"""
    return SettingsRepository.get_all()


@router.put("/admin/settings")
def update_admin_settings(
    req: SettingsUpdateRequest,
    is_admin: bool = Depends(require_admin),
):
    """管理者用 設定更新"""
    data = req.model_dump(exclude_unset=True)
    SettingsRepository.update_settings(data)
    return {"status": "ok", "message": "設定を保存しました"}


@router.post("/admin/sync")
def trigger_sync(is_admin: bool = Depends(require_admin)):
    """個人用Vault (prompt_image_vault) からの手動即時同期"""
    from sync_service import run_sync
    res = run_sync()
    return res


@router.post("/entries", response_model=EntryResponse)
def create_entry(
    file: UploadFile = File(...),
    prompt: str = Form(""),
    is_admin: bool = Depends(require_admin),
):
    """画像の新規登録（@amkki_aipix 専用）"""
    try:
        entry = register_usecase.execute(
            file_stream=file.file,
            original_filename=file.filename or "image.png",
            raw_prompt=prompt,
        )
        return EntryResponse(
            id=entry.id,
            filename=entry.filename,
            stored_path=entry.stored_path,
            thumbnail_path=entry.thumbnail_path,
            raw_prompt=entry.raw_prompt,
            prompt_excerpt=entry.prompt_excerpt,
            tags=entry.tags,
            created_at=entry.created_at.strftime("%Y-%m-%d %H:%M"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}")
def delete_entry(
    entry_id: str,
    is_admin: bool = Depends(require_admin),
):
    """画像の削除（@amkki_aipix 専用）"""
    success = delete_usecase.execute(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "ok", "deleted_id": entry_id}


# --------------------------------------------------------------------------
# ツール管理 API (Tools & Scripts Endpoints)
# --------------------------------------------------------------------------
@router.get("/tools", response_model=List[ToolItem])
def list_tools():
    """公開中のプログラム・ツール一覧を取得（誰でも閲覧可能）"""
    return tool_repo.get_all()


@router.post("/tools", response_model=ToolItem)
def create_tool(
    req: ToolCreateRequest,
    is_admin: bool = Depends(require_admin),
):
    """ツールの新規追加（@amkki_aipix 専用）"""
    created = tool_repo.create(
        title=req.title,
        description=req.description,
        badge=req.badge or "",
        tags=req.tags or "",
        url=req.url or "",
        status=req.status or "active",
        sort_order=req.sort_order or 0,
    )
    return created


@router.put("/tools/{tool_id}", response_model=ToolItem)
def update_tool(
    tool_id: str,
    req: ToolUpdateRequest,
    is_admin: bool = Depends(require_admin),
):
    """ツールの更新（@amkki_aipix 専用）"""
    data = req.model_dump(exclude_unset=True)
    updated = tool_repo.update(tool_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Tool not found")
    return updated


@router.delete("/tools/{tool_id}")
def delete_tool(
    tool_id: str,
    is_admin: bool = Depends(require_admin),
):
    """ツールの削除（@amkki_aipix 専用）"""
    success = tool_repo.delete(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"status": "ok", "deleted_id": tool_id}
