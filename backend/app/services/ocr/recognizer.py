"""OCR 识别服务
   生产环境建议安装 PaddleOCR：pip install paddleocr
   当前实现使用 Pillow 图片预处理 + 清晰的结构封装
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image


class OCRService:
    """OCR 识别服务封装

    当前状态：
    - 提供了完整的预处理模块（Pillow）
    - 文本识别需要安装 PaddleOCR 后启用
    - 未安装 OCR 引擎时返回占位响应
    """

    _instance: OCRService | None = None
    _engine: Any = None  # 保留给 PaddleOCR 实例

    def __init__(self) -> None:
        self._available = False
        self._init_engine()

    def _init_engine(self) -> None:
        """尝试初始化 OCR 引擎（PaddleOCR > easyocr > 无）"""
        try:
            from paddleocr import PaddleOCR
            self._engine = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
            self._available = True
        except ImportError:
            try:
                import easyocr
                self._engine = easyocr.Reader(["ch_sim", "en"], gpu=False)
                self._available = True
            except ImportError:
                self._available = False

    @classmethod
    def get_instance(cls) -> OCRService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def is_available(self) -> bool:
        return self._available

    def preprocess(self, image: Image.Image) -> Image.Image:
        """图片预处理：压缩、增强对比度"""
        # 限制尺寸
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.LANCZOS)

        # 转为灰度
        if image.mode != "L":
            image = image.convert("L")

        return image

    def recognize(self, image_data: bytes, post_process: bool = True) -> dict[str, Any]:
        """识别图片中的文字

        Args:
            image_data: 图片二进制数据
            post_process: 是否执行后处理（过滤水印等）

        Returns:
            {"text": "...", "word_count": 0, "available": bool}
        """
        if not self._available:
            # 无 OCR 引擎时尝试用基础图像处理
            return self._fallback_recognize(image_data)

        try:
            image = Image.open(BytesIO(image_data))
            processed = self.preprocess(image)

            # 保存处理后的图片到临时文件（OCR 引擎需要）
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            processed.save(tmp.name)

            if "paddleocr" in type(self._engine).__module__:
                result = self._engine.ocr(tmp.name, cls=True)
                texts = []
                for line_group in result:
                    for line in line_group:
                        if line and len(line) >= 2:
                            texts.append(line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1]))
                raw_text = "\n".join(texts)
            else:
                result = self._engine.readtext(tmp.name)
                texts = [item[1] for item in result if item and len(item) >= 2]
                raw_text = "\n".join(texts)

            Path(tmp.name).unlink(missing_ok=True)

            if post_process:
                text = self._post_process(raw_text)
            else:
                text = raw_text

            return {
                "text": text,
                "word_count": len(text),
                "available": True,
            }

        except Exception as e:
            return {
                "text": "",
                "word_count": 0,
                "available": True,
                "error": str(e),
            }

    def _post_process(self, text: str) -> str:
        """过滤水印文字、无关字符、多余换行"""
        import re

        # 常见水印词过滤
        watermark_patterns = [
            "小红书", "抖音", "快手", "微博", "微信公众号",
            "转载请注明出处", "未经允许不得转载", "来源网络",
            "关注我", "点赞收藏", "一键三连",
        ]
        for pattern in watermark_patterns:
            text = text.replace(pattern, "")

        # 过滤多余换行
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        text = "\n".join(lines)

        # 过滤非文字字符
        text = re.sub(r"[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffefa-zA-Z0-9\s。，！？、；：""''（）《》【】\-]", "", text)

        return text.strip()

    def _fallback_recognize(self, image_data: bytes) -> dict[str, Any]:
        """回退方案：无 OCR 引擎时的基础处理"""
        return {
            "text": "",
            "word_count": 0,
            "available": False,
            "message": "OCR 引擎未安装。请执行: pip install paddleocr",
        }


# 全局单例
ocr_service = OCRService()