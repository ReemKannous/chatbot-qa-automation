from pages.chat_page import ChatPage


# Requirement: Chat widget loads correctly
def test_widget_loads(page):
    chat = ChatPage(page)
    chat.loaded()


# Requirement: User can send messages via input box
# Requirement: AI responses are rendered properly in the conversation area
# Requirement: Input is cleared after sending
def test_send_message_and_get_reply(page):
    chat = ChatPage(page)
    chat.loaded()

    chat.send("Hello")
    chat.input_is_cleared()

    chat.wait_bot_reply()
    assert chat.last_bot_text().strip() != ""


# Requirement: Multilingual support (LTR for English, RTL for Arabic)
# Note: This will skip if the UI does not support language switching
def test_multilingual_english_ltr(page):
    chat = ChatPage(page)
    chat.loaded()

    chat.set_language_or_skip("en")
    chat.assert_direction("ltr")


# Requirement: Multilingual support (LTR for English, RTL for Arabic)
# Note: This will skip if the UI does not support language switching
def test_multilingual_arabic_rtl(page):
    chat = ChatPage(page)
    chat.loaded()

    chat.set_language_or_skip("ar")
    chat.assert_direction("rtl")


# Requirement: Scroll works as expected
def test_scroll_latest_message_visible(page):
    chat = ChatPage(page)
    chat.loaded()

    for i in range(6):
        chat.send(f"Message {i}")
        chat.wait_bot_reply()

    chat.last_bot_is_visible()


# Requirement: Accessibility works as expected (basic checks)
def test_accessibility_basics(page):
    chat = ChatPage(page)
    chat.loaded()

    chat.accessibility_basics()
