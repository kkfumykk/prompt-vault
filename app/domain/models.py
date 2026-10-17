from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class Tag:
    """正規化されたタグのエンティティ"""
    name: str
    usage_count: int = 1


@dataclass
class ImageEntry:
    """画像とプロンプトが1対1でリンクされたメインエンティティ"""
    id: str
    filename: str
    stored_path: str
    thumbnail_path: str
    raw_prompt: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def prompt_excerpt(self) -> str:
        """一覧プレビュー用の短いプロンプト抜粋（最大100文字）"""
        clean = " ".join(self.raw_prompt.split())
        if len(clean) > 100:
            return clean[:97] + "..."
        return clean
