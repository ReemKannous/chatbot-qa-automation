import pytest
from playwright.sync_api import expect
from selectors import Sel


class ChatPage:
    def __init__(self, page):
        self.page = page

    def loaded(self):
        expect(self.page.locator(Sel.CONTAINER)).to_be_visible()

    def send(self, text: str):
        self.page.fill(Sel.INPUT, text)
        self.page.click(Sel.SEND)

    def input_is_cleared(self):
        expect(self.page.locator(Sel.INPUT)).to_have_value("")

    def wait_bot_reply(self):
        loading = self.page.locator(Sel.LOADING)
        if loading.count() > 0:
            try:
                expect(loading).to_be_visible(timeout=2000)
            except Exception:
                pass
            expect(loading).to_be_hidden(timeout=30000)

        expect(self.page.locator(Sel.BOT_MSG).last).to_be_visible(timeout=30000)

    def last_bot_text(self) -> str:
        return self.page.locator(Sel.BOT_MSG).last.inner_text()

    def last_user_text(self) -> str:
        return self.page.locator(Sel.USER_MSG).last.inner_text()

    def set_language_or_skip(self, lang: str):
        toggle = self.page.locator(Sel.LANG_TOGGLE)
        if toggle.count() == 0:
            pytest.skip("Language toggle not available in this UI")

        toggle.click()
        if lang.lower() == "ar":
            self.page.click(Sel.LANG_AR)
        else:
            self.page.click(Sel.LANG_EN)

    def assert_direction(self, expected: str):
        container = self.page.locator(Sel.CONTAINER)

        dir_attr = container.get_attribute("dir")
        if dir_attr:
            assert dir_attr.lower() == expected
            return

        direction = self.page.evaluate(
            "(el) => getComputedStyle(el).direction",
            container.element_handle()
        )
        assert direction.lower() == expected

    def last_bot_is_visible(self):
        expect(self.page.locator(Sel.BOT_MSG).last).to_be_visible()

    def accessibility_basics(self):
        inp = self.page.locator(Sel.INPUT)
        expect(inp).to_be_visible()

        inp.click()
        expect(inp).to_be_focused()

        aria = inp.get_attribute("aria-label")
        placeholder = inp.get_attribute("placeholder")

        assert (aria and aria.strip()) or (placeholder and placeholder.strip()), \
            "Input should have aria-label or placeholder"

    def fallback_is_visible_or_skip(self):
        fb = self.page.locator(Sel.FALLBACK)
        if fb.count() == 0:
            pytest.skip("Fallback selector not found in this UI")
        expect(fb).to_be_visible(timeout=10000)
