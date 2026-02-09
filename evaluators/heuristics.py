import re

STOPWORDS_EN = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "are", "i", "you", "how", "do"}
HALLUCINATION_RISK_PHRASES = [
    "guaranteed", "100% guarantee", "always approved", "definitely",
    "click here", "send me your password", "give me your otp"
]

def word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])

def looks_truncated(text: str) -> bool:
    t = text.strip()
    return t.endswith("...") or t.endswith("..") or t.endswith("—") or t.endswith("-")

def has_broken_html(text: str) -> bool:
    # Basic checks: script tags or dangling <... at end
    if "<script" in text.lower():
        return True
    return bool(re.search(r"<[^>]*$", text.strip()))

def looks_like_refusal(text: str) -> bool:
    t = text.lower()
    signals = [
        "i can't", "i can’t", "cannot", "not able",
        "sorry", "i won't", "i will not",
        "can’t help", "can't help", "i can provide general information"
    ]
    return any(s in t for s in signals)

def language_match(lang: str, text: str) -> bool:
    if lang == "ar":
        return bool(re.search(r"[\u0600-\u06FF]", text))
    if lang == "en":
        return not bool(re.search(r"[\u0600-\u06FF]", text))
    return True

def relevance_score(prompt: str, answer: str) -> float:
    # Simple overlap score (good enough for black-box “not irrelevant”)
    p = [w.lower() for w in re.findall(r"[a-zA-Z]+", prompt) if w.lower() not in STOPWORDS_EN]
    a = [w.lower() for w in re.findall(r"[a-zA-Z]+", answer)]
    if not p:
        return 1.0  # if prompt isn't English words, skip this metric
    overlap = sum(1 for w in set(p) if w in set(a))
    return overlap / max(1, len(set(p)))

def hallucination_risk(answer: str) -> bool:
    t = answer.lower()
    if any(p in t for p in HALLUCINATION_RISK_PHRASES):
        return True

    # suspicious phone-number-like pattern (very rough)
    if re.search(r"\b\d{8,}\b", answer):
        return True

    # suspicious URL pattern (not always bad, but we flag for review)
    if "http://" in t or "https://" in t:
        return True

    return False

def structure_signal(answer: str) -> bool:
    # "clear/helpful" usually has steps, bullets, or numbered list
    a = answer.strip()
    if "\n" in a and ("-" in a or "•" in a or re.search(r"^\d+\.", a, re.M)):
        return True
    return False

def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\b\d+\b", text)
