from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from app.domain.models import ImageEntry, Tag


class IImageRepository(ABC):
    """画像・プロンプトエントリの永続化インターフェース"""

    @abstractmethod
    def save(self, entry: ImageEntry) -> ImageEntry:
        """エントリを保存（新規作成または更新）"""
        pass

    @abstractmethod
    def find_by_id(self, entry_id: str) -> Optional[ImageEntry]:
        """IDでエントリを取得"""
        pass

    @abstractmethod
    def search_by_tags(self, tags: List[str], limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        """指定された全タグを含む（AND検索）エントリを検索"""
        pass

    @abstractmethod
    def search_by_keyword(self, keyword: str, limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        """プロンプト本文またはタグによるフリーワード検索"""
        pass

    @abstractmethod
    def get_all(self, limit: int = 50, offset: int = 0) -> List[ImageEntry]:
        """最新順に全エントリを取得"""
        pass

    @abstractmethod
    def count(self) -> int:
        """総エントリ数を取得"""
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """IDでエントリを削除"""
        pass


class ITagRepository(ABC):
    """タグ集計・サジェスト用のインターフェース"""

    @abstractmethod
    def suggest(self, prefix: str, limit: int = 15) -> List[str]:
        """
        入力中の接頭辞（prefix）から、存在するタグを予測サジェストする。
        前方一致および部分一致で、使用頻度（usage_count）降順に返却。
        """
        pass

    @abstractmethod
    def get_popular(self, limit: int = 50) -> List[Tuple[str, int]]:
        """よく使われているタグ一覧（タグ名, 使用回数）を取得"""
        pass
