import re
from typing import List


class TagParser:
    """
    プロンプト文字列を「,」でパースし、仕様に沿って正規化されたタグリストを生成するドメインサービス。
    
    仕様:
    - 「,」で分割する。
    - 各タグの前後の半角スペース・全角スペースを除外（トリミング）する。
    - 単語内部のスペース（例: "master piece", "black hair"）の扱いに配慮しつつ、
      不要な連続空白を正規化し、タグ境界の空白を完全に排除する。
    - 空文字タグを除外する。
    - 重複タグを除外（出現順序を維持）。
    """

    @staticmethod
    def parse(raw_prompt: str) -> List[str]:
        if not raw_prompt:
            return []

        # カンマで分割
        raw_tokens = raw_prompt.split(",")
        tags: List[str] = []
        seen = set()

        for token in raw_tokens:
            # 前後の半角空白・全角空白・改行文字を徹底除去
            cleaned = token.strip(" \t\r\n\u3000")
            
            # 内部の余分な連続スペースも1つに正規化
            cleaned = re.sub(r"[ \t\u3000]+", " ", cleaned)

            if cleaned:
                # 重複排除（大文字小文字は区別を保持しつつ、小文字比較で重複排除）
                lower_key = cleaned.lower()
                if lower_key not in seen:
                    seen.add(lower_key)
                    tags.append(cleaned)

        return tags

    # エイリアス
    parse_tags = parse
