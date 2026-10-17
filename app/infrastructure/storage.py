import shutil
import uuid
from pathlib import Path
from typing import Tuple
from PIL import Image

from app.core.config import IMAGES_DIR, THUMBNAILS_DIR, THUMBNAIL_SIZE


class ImageStorageService:
    """画像の永続ファイル保存およびサムネイル生成を担当するインフラサービス"""

    @staticmethod
    def save_image_file(source_stream, original_filename: str) -> Tuple[str, str, str]:
        """
        画像ファイルを保存し、サムネイルを生成する。
        
        戻り値:
        - entry_id: 一意のUUID
        - relative_stored_path: 原寸画像の相対パス
        - relative_thumbnail_path: サムネイルの相対パス
        """
        entry_id = str(uuid.uuid4())
        ext = Path(original_filename).suffix.lower()
        if not ext or ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]:
            ext = ".png"

        stored_filename = f"{entry_id}{ext}"
        thumb_filename = f"{entry_id}_thumb.webp"

        stored_full_path = IMAGES_DIR / stored_filename
        thumb_full_path = THUMBNAILS_DIR / thumb_filename

        # 原寸画像の保存
        with open(stored_full_path, "wb") as f:
            shutil.copyfileobj(source_stream, f)

        # サムネイルの生成（Pillow）
        try:
            with Image.open(stored_full_path) as img:
                # RGBに変換（RGBAやPモード対策）
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    # 透明背景を考慮してRGBAのままWebPで保存
                    thumb = img.copy()
                    thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    thumb.save(thumb_full_path, format="WEBP", quality=85)
                else:
                    thumb = img.convert("RGB")
                    thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    thumb.save(thumb_full_path, format="WEBP", quality=85)
        except Exception:
            # 万一サムネイル生成に失敗した場合は原寸画像をそのままコピー
            shutil.copyfile(stored_full_path, thumb_full_path)

        # 相対パスを返却（Web配信や可搬性のため）
        return entry_id, f"images/{stored_filename}", f"thumbnails/{thumb_filename}"

    @staticmethod
    def delete_image_files(stored_path: str, thumbnail_path: str) -> None:
        """物理画像ファイルを削除"""
        base = IMAGES_DIR.parent
        p1 = base / stored_path
        p2 = base / thumbnail_path
        if p1.exists():
            try:
                p1.unlink()
            except Exception:
                pass
        if p2.exists():
            try:
                p2.unlink()
            except Exception:
                pass
