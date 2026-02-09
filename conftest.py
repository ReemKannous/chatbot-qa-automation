import os
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(20000)
    page.goto(BASE_URL)
    yield page
    context.close()
