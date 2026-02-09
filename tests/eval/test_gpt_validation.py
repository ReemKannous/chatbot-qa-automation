import json
import pytest
from pathlib import Path

from pages.chat_page import ChatPage
from evaluators.heuristics import (
    word_count, structure_signal, has_broken_html, looks_truncated,
    relevance_score, hallucination_risk, language_match, extract_numbers
)

TESTSET = json.loads((Path("testdata") / "test-data.json").read_text(encoding="utf-8"))

def by_intent_group(group: str):
    return [t for t in TESTSET if t["intent_group"] == group]


# Requirement: AI provides a clear and helpful response to common public service queries
@pytest.mark.parametrize("tc", [t for t in TESTSET if t["intent_group"] in ["visa_renewal", "emirates_id"]])
def test_clear_and_helpful_response(page, tc):
    chat = ChatPage(page)
    chat.loaded()

    chat.send(tc["prompt"])
    chat.input_is_cleared()
    chat.wait_bot_reply()
    answer = chat.last_bot_text()

    assert language_match(tc["lang"], answer)
    assert word_count(answer) >= tc["expect"]["min_words"]
    assert structure_signal(answer) or word_count(answer) >= (tc["expect"]["min_words"] + 10)


# Requirement: Responses are not hallucinated (i.e., fabricated or irrelevant)
@pytest.mark.parametrize("tc", [t for t in TESTSET if t["intent_group"] in ["visa_renewal", "emirates_id"]])
def test_not_irrelevant_and_low_hallucination_risk(page, tc):
    chat = ChatPage(page)
    chat.loaded()

    chat.send(tc["prompt"])
    chat.wait_bot_reply()
    answer = chat.last_bot_text()

    assert language_match(tc["lang"], answer)

    score = relevance_score(tc["prompt"], answer)
    assert score >= 0.2  # low threshold (black-box)

    assert not hallucination_risk(answer)


# Requirement: Responses stay consistent for similar intent in both English and Arabic
def test_consistency_between_english_and_arabic_for_same_intent(page):
    for group in ["visa_renewal", "emirates_id"]:
        cases = by_intent_group(group)
        en = next((c for c in cases if c["lang"] == "en"), None)
        ar = next((c for c in cases if c["lang"] == "ar"), None)
        if not en or not ar:
            continue

        chat = ChatPage(page)
        chat.loaded()

        chat.send(en["prompt"])
        chat.wait_bot_reply()
        en_answer = chat.last_bot_text()

        chat.send(ar["prompt"])
        chat.wait_bot_reply()
        ar_answer = chat.last_bot_text()

        assert word_count(en_answer) >= en["expect"]["min_words"]
        assert word_count(ar_answer) >= ar["expect"]["min_words"]
        assert language_match("en", en_answer)
        assert language_match("ar", ar_answer)

        en_nums = set(extract_numbers(en_answer))
        ar_nums = set(extract_numbers(ar_answer))
        if en_nums and ar_nums:
            assert len(en_nums.intersection(ar_nums)) >= 1


# Requirement: Response formatting is clean (no broken HTML or incomplete thoughts)
@pytest.mark.parametrize("tc", TESTSET)
def test_clean_formatting(page, tc):
    chat = ChatPage(page)
    chat.loaded()

    chat.send(tc["prompt"])
    chat.wait_bot_reply()
    answer = chat.last_bot_text()

    assert not has_broken_html(answer)
    assert not looks_truncated(answer)


# Requirement: Loading states and fallback messages appear properly when expected
def test_loading_and_fallback_message_when_offline(page):
    chat = ChatPage(page)
    chat.loaded()

    page.context.set_offline(True)
    chat.send("Test fallback behavior")

    chat.fallback_is_visible_or_skip()

    page.context.set_offline(False)
