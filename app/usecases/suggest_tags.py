from typing import List
from app.domain.repositories import ITagRepository


class SuggestTagsUseCase:
    """入力文字列からタグ予測候補を提示するユースケース"""

    def __init__(self, tag_repo: ITagRepository):
        self.tag_repo = tag_repo

    def execute(self, prefix: str, limit: int = 12) -> List[str]:
        # カンマ区切り入力中の場合、末尾のトークンに対してサジェストを行う
        if "," in prefix:
            prefix = prefix.split(",")[-1]
        
        prefix = prefix.strip()
        return self.tag_repo.suggest(prefix, limit=limit)
