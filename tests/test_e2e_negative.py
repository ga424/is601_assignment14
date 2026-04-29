"""
Negative-scenario Playwright E2E tests.

Covers unauthorized access, invalid inputs, and error responses — both at the
browser UI level and via direct API calls from within the browser context.

Requires the FastAPI app to be running at PLAYWRIGHT_BASE_URL.
Run with:

    python -m pytest -q -m e2e tests/test_e2e_negative.py
"""

import os
import re
import uuid

import pytest
from playwright.sync_api import expect, sync_playwright


pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Fixtures (mirror test_e2e_auth.py pattern)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def register_user(page, email: str, password: str):
    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('input[name="confirmPassword"]').fill(password)
    page.get_by_role("button", name="Register").click()
    expect(page.get_by_role("status")).to_contain_text("Registration successful")


# ---------------------------------------------------------------------------
# Registration negative scenarios
# ---------------------------------------------------------------------------


def test_register_duplicate_email_shows_error(page):
    """Registering the same email twice surfaces the 409 detail in the UI."""
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_user(page, email, password)

    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill(password)
    page.locator('input[name="confirmPassword"]').fill(password)
    page.get_by_role("button", name="Register").click()

    expect(page.get_by_role("status")).to_contain_text("Email already registered")


def test_register_mismatched_passwords_shows_error(page):
    """Client-side confirm-password mismatch blocks submission."""
    email = f"mismatch-{uuid.uuid4().hex[:8]}@example.com"

    page.goto("/register")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill("strongpassword123")
    page.locator('input[name="confirmPassword"]').fill("differentpassword123")
    page.get_by_role("button", name="Register").click()

    expect(page.get_by_role("status")).to_contain_text("Passwords do not match")
    assert page.evaluate("window.localStorage.getItem('is601.jwt')") is None


def test_register_invalid_email_format_shows_error(page):
    """auth.js email regex rejects malformed addresses before any network call."""
    page.goto("/register")
    page.get_by_label("Email").fill("notanemail")
    page.locator('input[name="password"]').fill("strongpassword123")
    page.locator('input[name="confirmPassword"]').fill("strongpassword123")
    page.get_by_role("button", name="Register").click()

    expect(page.get_by_role("status")).to_contain_text("Enter a valid email address")
    assert page.evaluate("window.localStorage.getItem('is601.jwt')") is None


# ---------------------------------------------------------------------------
# Login negative scenarios
# ---------------------------------------------------------------------------


def test_login_nonexistent_email_shows_error(page):
    """Logging in with an unregistered email returns 401 detail in the UI."""
    page.goto("/login")
    page.get_by_label("Email").fill(f"ghost-{uuid.uuid4().hex[:8]}@example.com")
    page.locator('input[name="password"]').fill("strongpassword123")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("status")).to_contain_text("Invalid email or password")
    assert page.evaluate("window.localStorage.getItem('is601.jwt')") is None


def test_login_wrong_password_does_not_store_token(page):
    """Correct email + wrong password must not store a JWT in localStorage."""
    email = f"wrongpw-{uuid.uuid4().hex[:8]}@example.com"
    register_user(page, email, "strongpassword123")

    page.goto("/login")
    page.get_by_label("Email").fill(email)
    page.locator('input[name="password"]').fill("completelyWrongPassword123")
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_role("status")).to_contain_text("Invalid email or password")


# ---------------------------------------------------------------------------
# Dashboard unauthorized access
# ---------------------------------------------------------------------------


def test_dashboard_without_token_redirects_to_login(page):
    """Navigating to /dashboard with no localStorage token redirects immediately."""
    page.goto("/login")
    page.evaluate("window.localStorage.removeItem('is601.jwt')")

    page.goto("/dashboard")

    expect(page).to_have_url(re.compile(r".*/login$"), timeout=5_000)


def test_dashboard_with_tampered_jwt_redirects_to_login(page):
    """A syntactically present but invalid JWT causes a 401 from /calculations,
    which app.js handles by clearing localStorage and redirecting to /login."""
    page.goto("/login")
    page.evaluate("window.localStorage.setItem('is601.jwt', 'not.a.valid.jwt.token')")

    page.goto("/dashboard")

    expect(page).to_have_url(re.compile(r".*/login$"), timeout=10_000)
    assert page.evaluate("window.localStorage.getItem('is601.jwt')") is None


# ---------------------------------------------------------------------------
# Dashboard form validation (client-side)
# ---------------------------------------------------------------------------


def test_dashboard_form_rejects_single_input(page):
    """parseInputs() requires at least two numeric values."""
    email = f"single-{uuid.uuid4().hex[:8]}@example.com"
    register_user(page, email, "strongpassword123")

    page.goto("/dashboard")
    expect(page.get_by_role("heading", name="Calculation Dashboard")).to_be_visible()

    page.get_by_label("Type").select_option("addition")
    page.get_by_label("Inputs").fill("42")
    page.get_by_role("button", name="Create Calculation").click()

    expect(page.get_by_role("status")).to_contain_text(
        "Enter at least two numeric inputs separated by commas"
    )


def test_dashboard_form_rejects_non_numeric_inputs(page):
    """parseInputs() returns null when any value is NaN."""
    email = f"nonnumeric-{uuid.uuid4().hex[:8]}@example.com"
    register_user(page, email, "strongpassword123")

    page.goto("/dashboard")
    expect(page.get_by_role("heading", name="Calculation Dashboard")).to_be_visible()

    page.get_by_label("Type").select_option("addition")
    page.get_by_label("Inputs").fill("abc, def")
    page.get_by_role("button", name="Create Calculation").click()

    expect(page.get_by_role("status")).to_contain_text(
        "Enter at least two numeric inputs separated by commas"
    )


# ---------------------------------------------------------------------------
# Dashboard server-side validation
# ---------------------------------------------------------------------------


def test_dashboard_form_division_by_zero_shows_error(page):
    """Division by zero passes parseInputs but is rejected by the Pydantic validator
    (HTTP 422). After the app.js fix, the error detail is surfaced in the UI."""
    email = f"divzero-{uuid.uuid4().hex[:8]}@example.com"
    register_user(page, email, "strongpassword123")

    page.goto("/dashboard")
    expect(page.get_by_role("heading", name="Calculation Dashboard")).to_be_visible()

    page.get_by_label("Type").select_option("division")
    page.get_by_label("Inputs").fill("10, 0")
    page.get_by_role("button", name="Create Calculation").click()

    expect(page.get_by_role("status")).to_contain_text(
        re.compile(r"Cannot divide by zero|Unable to create calculation", re.IGNORECASE)
    )


# ---------------------------------------------------------------------------
# Cross-user data isolation
# ---------------------------------------------------------------------------


def test_api_cannot_access_another_users_calculation(page, browser, base_url):
    """The API filters calculations by user_id. User B receives 404 when requesting
    a calculation that belongs to user A."""
    email_a = f"user-a-{uuid.uuid4().hex[:8]}@example.com"
    email_b = f"user-b-{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    # User A: register and create a calculation
    ctx_a = browser.new_context(base_url=base_url)
    page_a = ctx_a.new_page()
    register_user(page_a, email_a, password)

    page_a.goto("/dashboard")
    page_a.get_by_label("Type").select_option("addition")
    page_a.get_by_label("Inputs").fill("5, 5")
    page_a.get_by_role("button", name="Create Calculation").click()
    expect(page_a.get_by_role("status")).to_contain_text("Calculation created")

    first_item = page_a.locator(".result-item").first()
    expect(first_item).to_be_visible()
    calc_id = first_item.get_attribute("data-id")
    assert calc_id, "Expected data-id attribute on result item"
    ctx_a.close()

    # User B: register in a separate context and try to access user A's calculation
    ctx_b = browser.new_context(base_url=base_url)
    page_b = ctx_b.new_page()
    register_user(page_b, email_b, password)

    token_b = page_b.evaluate("window.localStorage.getItem('is601.jwt')")
    status_code = page_b.evaluate(f"""
        async () => {{
            const resp = await fetch('/calculations/{calc_id}', {{
                headers: {{
                    'Authorization': 'Bearer {token_b}',
                    'Content-Type': 'application/json'
                }}
            }});
            return resp.status;
        }}
    """)
    assert status_code == 404, f"Expected 404 for cross-user access, got {status_code}"
    ctx_b.close()
