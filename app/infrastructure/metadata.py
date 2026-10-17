import json
from pathlib import Path
from typing import Optional
from PIL import Image


class MetadataExtractor:
    """PNG画像等のメタデータからプロンプトを自動抽出する補助サービス"""

    @staticmethod
    def extract_prompt_from_path(image_path: Path) -> Optional[str]:
        try:
            with Image.open(image_path) as img:
                info = img.info or {}

                # 1. ComfyUI 形式のメタデータ
                if "prompt" in info:
                    try:
                        data = json.loads(info["prompt"])
                        # CLIPTextEncode や ImpactWildcardProcessor のテキストを抽出
                        prompts = []
                        for node in data.values():
                            inputs = node.get("inputs", {})
                            class_type = node.get("class_type", "")
                            if "text" in inputs and isinstance(inputs["text"], str):
                                t = inputs["text"].strip()
                                if t and len(t) > 3 and not t.startswith("low quality"):
                                    prompts.append(t)
                            elif "wildcard_text" in inputs and isinstance(inputs["wildcard_text"], str):
                                t = inputs["wildcard_text"].strip()
                                if t and len(t) > 3:
                                    prompts.append(t)
                            elif "prompt" in inputs and isinstance(inputs["prompt"], str):
                                t = inputs["prompt"].strip()
                                if t and len(t) > 3:
                                    prompts.append(t)
                        if prompts:
                            return "\n".join(prompts)
                    except Exception:
                        pass

                # 2. Stable Diffusion WebUI (A1111) 形式
                if "parameters" in info:
                    raw = info["parameters"]
                    # Negative prompt: の前の部分を抽出
                    lines = raw.split("Negative prompt:")
                    return lines[0].strip()

                # 3. NovelAI 形式
                if "Description" in info:
                    return info["Description"].strip()
                if "Comment" in info:
                    try:
                        c_data = json.loads(info["Comment"])
                        if "prompt" in c_data:
                            return c_data["prompt"].strip()
                    except Exception:
                        pass

        except Exception:
            pass
        return None
