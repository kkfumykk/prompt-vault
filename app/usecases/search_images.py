from typing import List
from app.domain.models import ImageEntry
from app.domain.repositories import IImageRepository
from app.domain.services import TagParser


class SearchImagesUseCase:
    """タグまたはキーワードで画像を検索するユースケース"""

    def __init__(self, image_repo: IImageRepository):
        self.image_repo = image_repo

    def execute(self, query: str = "", limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        query = query.strip()
        if not query:
            return self.image_repo.get_all(limit=limit, offset=offset)

        # カンマが含まれている場合は複数タグのAND検索として処理
        if "," in query:
            tags = TagParser.parse(query)
            if tags:
                return self.image_repo.search_by_tags(tags, limit=limit, offset=offset)

        # 単一語句の場合: まず完全一致するタグがあるか検索し、なければキーワード部分一致検索
        single_tag = query.strip()
        exact_results = self.image_repo.search_by_tags([single_tag], limit=limit, offset=offset)
        if exact_results:
            return exact_results

        # 部分一致検索フォールバック
        return self.image_repo.search_by_keyword(single_tag, limit=limit, offset=offset)
