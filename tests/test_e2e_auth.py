import os
import re
import uuid

import pytest
from playwright.sync_api import expect, sync_playwright


pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://127.0.0.1:8013")


@pytest.fixture(scope="session")
def playwright_driver():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_driver):
    browser = playwright_driver.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser, base_url):
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    yield page
    context.close()


def register_user(page, email: str, password: str):
    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('input[name="confirmPassword"]').fill(password)
    page.get_by_role("button", name="Register").click()
    expect(page).to_have_url(re.compile(r".*/dashboard$"), timeout=10_000)
    assert page.evaluate("window.localStorage.getItem('is601.jwt')")


def test_register_page_success(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('input[name="confirmPassword"]').fill(password)
    page.get_by_role("button", name="Register").click()

    expect(page).to_have_url(re.compile(r".*/dashboard$"), timeout=10_000)
    token = page.evaluate("window.localStorage.getItem('is601.jwt')")
    assert token


def test_login_page_success(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_user(page, email, password)

    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill(password)
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(re.compile(r".*/dashboard$"), timeout=10_000)
    token = page.evaluate("window.localStorage.getItem('is601.jwt')")
    assert token


def test_register_page_rejects_short_password(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"

    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill("short")
    page.get_by_role("button", name="Register").click()

    expect(page.get_by_role("status")).to_contain_text("Password must be at least 8 characters.")
    assert page.evaluate("window.localStorage.getItem('is601.jwt')") is None


def test_login_page_rejects_wrong_password(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_user(page, email, password)

    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill("wrongpassword123")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("status")).to_contain_text("Invalid email or password")


def test_dashboard_redirects_to_login_without_token(page):
    page.goto("/dashboard")
    expect(page).to_have_url(re.compile(r".*/login$"))


def test_dashboard_creates_and_lists_calculation(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_user(page, email, password)

    page.goto("/dashboard")
    expect(page.get_by_role("heading", name="Calculation Dashboard")).to_be_visible()

    page.get_by_label("Type").select_option("addition")
    page.get_by_label("Inputs").fill("1, 2, 3")
    page.get_by_role("button", name="Create Calculation").click()

    expect(page.get_by_role("status")).to_contain_text("Calculation created: 6")
    expect(page.locator("[data-result-list]")).to_contain_text("addition(1, 2, 3) = 6")


def test_dashboard_read_update_delete_calculation(page):
    email = f"student-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_user(page, email, password)

    page.goto("/dashboard")

    # create
    page.get_by_label("Type").select_option("addition")
    page.get_by_label("Inputs").fill("2, 3")
    page.get_by_role("button", name="Create Calculation").click()
    expect(page.get_by_role("status")).to_contain_text("Calculation created")

    # wait for list and grab first item
    firstItem = page.locator('.result-item').first()
    expect(firstItem).to_be_visible()

    # view details
    firstItem.get_by_role("button", name="View").click()
    expect(page.get_by_role("status")).to_contain_text("Calculation:")

    # edit: switch to multiplication and new inputs
    firstItem.get_by_role("button", name="Edit").click()
    page.get_by_label("Type").select_option("multiplication")
    page.get_by_label("Inputs").fill("2, 3, 4")
    page.get_by_role("button", name="Create Calculation").click()
    expect(page.get_by_role("status")).to_contain_text("updated")
    expect(page.locator("[data-result-list]")).to_contain_text("multiplication(2, 3, 4) = 24")

    # delete (confirm dialog)
    def handle_dialog(dialog):
        dialog.accept()

    page.once("dialog", handle_dialog)
    firstItem.get_by_role("button", name="Delete").click()

    # after deletion the list should not contain the multiplication result
    list_text = page.locator("[data-result-list]").inner_text()
    assert "multiplication(2, 3, 4) = 24" not in list_text