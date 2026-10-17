import secrets
from typing import Dict, Any, Optional
from app.infrastructure.database import get_db_connection


class SettingsRepository:
    """サイト全体の設定・X認証セッション管理を行うリポジトリ"""

    # メモリ上のXユーザーセッション管理: token -> { "username": str, "is_admin": bool, "is_following": bool }
    _active_sessions: Dict[str, Dict[str, Any]] = {}

    ADMIN_USERNAME = "amkki_aipix"

    @classmethod
    def verify_admin_password(cls, plain_password: str) -> bool:
        """管理者パスワードの照合 (SHA-256)"""
        import hashlib
        if not plain_password:
            return False
        all_s = cls.get_all()
        stored_hash = all_s.get("admin_password_hash")
        if not stored_hash:
            return False
        input_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return secrets.compare_digest(input_hash, stored_hash)

    @classmethod
    def update_admin_password(cls, new_plain_password: str) -> None:
        """管理者パスワードの変更"""
        import hashlib
        new_hash = hashlib.sha256(new_plain_password.encode("utf-8")).hexdigest()
        cls.update_settings({"admin_password_hash": new_hash})

    @classmethod
    def create_x_session(
        cls, username: str, is_following: bool = True, is_admin: bool = False
    ) -> tuple[str, Dict[str, Any]]:
        """Xアカウント連携セッションを発行"""
        cleaned_username = username.strip().lstrip("@")
        token = secrets.token_hex(24)

        session_data = {
            "username": cleaned_username,
            "is_admin": is_admin,
            "is_following": is_following if not is_admin else True,
        }
        cls._active_sessions[token] = session_data
        return token, session_data

    @classmethod
    def get_session(cls, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        return cls._active_sessions.get(token)

    @classmethod
    def verify_admin(cls, token: Optional[str]) -> bool:
        session = cls.get_session(token)
        return bool(session and session.get("is_admin"))

    @classmethod
    def revoke_session(cls, token: str) -> None:
        cls._active_sessions.pop(token, None)

    @staticmethod
    def get_all() -> Dict[str, str]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings;")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}

    @staticmethod
    def get_public_settings() -> Dict[str, Any]:
        """一般公開設定"""
        all_s = SettingsRepository.get_all()
        return {
            "site_title": all_s.get("site_title", "prompt.archive / amkki"),
            "site_description": all_s.get("site_description", "制作プロンプトと出力ログのアーカイブ"),
            "x_username": all_s.get("x_username", "amkki_aipix"),
            "x_share_text": all_s.get("x_share_text", "制作プロンプトのアーカイブ"),
            "pixai_promo_enabled": all_s.get("pixai_promo_enabled", "1") == "1",
            "promo_main_text": all_s.get("promo_main_text", all_s.get("pixai_promo_badge", "便利な自動化ツールを有料で公開中")),
            "pixai_promo_title": all_s.get("pixai_promo_title", "便利な自動化ツールを有料で公開中"),
            "pixai_promo_desc": all_s.get("pixai_promo_desc", "クリックでツール一覧を表示"),
            "pixai_promo_url": all_s.get("pixai_promo_url", "#"),
            "pixai_promo_badge": all_s.get("pixai_promo_badge", "便利な自動化ツールを有料で公開中"),
            "environment_info": all_s.get("environment_info", ""),
        }

    @staticmethod
    def update_settings(updates: Dict[str, str]) -> None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for key, val in updates.items():
                cursor.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = ?;",
                    (key, str(val), str(val)),
                )
            conn.commit()
