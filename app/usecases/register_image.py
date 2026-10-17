from typing import BinaryIO, Optional
from datetime import datetime

from app.domain.models import ImageEntry
from app.domain.repositories import IImageRepository
from app.domain.services import TagParser
from app.infrastructure.storage import ImageStorageService


class RegisterImageUseCase:
    """画像とプロンプトを1対1でリンク付けして保存するユースケース"""

    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    def execute(self, file_stream: BinaryIO, original_filename: str, raw_prompt: str) -> ImageEntry:
        # 1. 画像ファイルとサムネイルの永続化
        entry_id, stored_path, thumb_path = ImageStorageService.save_image_file(
            file_stream, original_filename
        )

        # 2. プロンプトのパースとタグ正規化（「,」分割、半角スペース除外）
        tags = TagParser.parse(raw_prompt)

        # 3. エンティティの構築
        entry = ImageEntry(
            id=entry_id,
            filename=original_filename,
            stored_path=stored_path,
            thumbnail_path=thumb_path,
            raw_prompt=raw_prompt.strip(),
            tags=tags,
            created_at=datetime.now(),
        )

        # 4. データベースへの保存
        return self.image_repo.save(entry)
