import re
def count_words(text: str) -> int:
    return len(text.strip())
def is_blank(text: str) -> bool:
    return not text or not text.strip()
def is_pure_symbols(text: str) -> bool:
    cleaned = re.sub(r"[\s\W]+", "", text)
    return len(cleaned) == 0
def truncate_text(text: str, max_len: int = 5000) -> str:
    return text[:max_len] if len(text) > max_len else text
def split_paragraphs(text: str) -> list:
    return [p.strip() for p in re.split(r"\n+", text) if p.strip()]
