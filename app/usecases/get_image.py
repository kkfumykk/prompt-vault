from typing import Optional
from app.domain.models import ImageEntry
from app.domain.repositories import IImageRepository
from app.infrastructure.storage import ImageStorageService


class GetImageUseCase:
    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    def execute(self, entry_id: str) -> Optional[ImageEntry]:
        return self.image_repo.find_by_id(entry_id)


class DeleteImageUseCase:
    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    def execute(self, entry_id: str) -> bool:
        entry = self.image_repo.find_by_id(entry_id)
        if not entry:
            return False
        # 物理ファイルの削除
        ImageStorageService.delete_image_files(entry.stored_path, entry.thumbnail_path)
        # DBレコードの削除
        return self.image_repo.delete(entry_id)
