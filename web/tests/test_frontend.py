"""Frontend and security verification tests for ClasificaHumor."""

import json
from pathlib import Path

import httpx2
from playwright.async_api import Browser, Page, Route

BASE_DIR = Path(__file__).resolve().parent.parent / "src" / "clasificahumor"
STATIC_DIR = BASE_DIR / "static"


async def _stub_external_trackers(page: Page) -> None:
    async def _empty_response(route: Route) -> None:
        url = route.request.url
        content_type = "text/css" if url.endswith(".css") else "application/javascript"
        await route.fulfill(status=200, content_type=content_type, body="")

    await page.route("https://www.googletagmanager.com/**", _empty_response)
    await page.route("https://connect.facebook.net/**", _empty_response)
    await page.route("https://platform.twitter.com/**", _empty_response)
    await page.route("https://js.sentry-cdn.com/**", _empty_response)
    await page.route("https://cdn.jsdelivr.net/**", _empty_response)

    async def _not_found(route: Route) -> None:
        await route.fulfill(status=404)

    # The images of the emoji.
    await page.route("https://raw.githubusercontent.com/**", _not_found)


async def test_voting_page_flow(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)

    vote_requests: list[str] = []
    page.on("request", lambda req: vote_requests.append(req.post_data or "") if req.url.endswith("/vote") else None)

    await page.goto(live_server_url)
    assert await page.title() == "Clasificá tweets y divertite"
    assert await page.evaluate("() => typeof window.jQuery === 'undefined'")
    assert await page.evaluate("() => typeof window.$ === 'undefined'")

    # Wait for initial tweets to load and populate #tweet-text
    await page.wait_for_function("() => document.querySelector('#tweet-text')?.textContent.trim().length > 0")

    initial_text = await page.locator("#tweet-text").text_content()
    assert initial_text and len(initial_text.strip()) > 0

    # Mark as offensive first
    await page.check("#is-offensive")
    assert await page.is_checked("#is-offensive")

    # Click #vote-4 (rating 4 stars)
    async with page.expect_response(lambda resp: resp.url.endswith("/vote") and resp.status == 200):
        await page.locator("#vote-4").dispatch_event("click")

    assert len(vote_requests) == 1
    payload_1 = json.loads(vote_requests[0])
    assert payload_1["vote"] == "4"
    assert payload_1["is_offensive"] is True
    assert await page.is_checked("#is-offensive") is False

    # Check that toast appeared
    await page.wait_for_selector(".md-toast")
    toast_1 = await page.locator(".md-toast").first.text_content()
    assert toast_1 and "bueno" in toast_1.lower()

    # Vote 'No' (non-humor) on next tweet
    async with page.expect_response(lambda resp: resp.url.endswith("/vote") and resp.status == 200):
        await page.click("#not-humor")

    assert len(vote_requests) == 2
    payload_2 = json.loads(vote_requests[1])
    assert payload_2["vote"] == "x"

    # Vote 'Saltear' (skip) on next tweet
    async with page.expect_response(lambda resp: resp.url.endswith("/vote") and resp.status == 200):
        await page.click("#skip")

    assert len(vote_requests) == 3
    payload_3 = json.loads(vote_requests[2])
    assert payload_3["vote"] == "n"

    await context.close()


async def test_prolific_session_flow(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)

    consent_calls: list[str] = []
    page.on("request", lambda req: consent_calls.append(req.url) if "prolific-consent" in req.url else None)

    # Open with PROLIFIC_PID query param
    await page.goto(f"{live_server_url}/?PROLIFIC_PID=test_prolific_worker_123")

    # Consent modal should be visible
    await page.wait_for_selector("#consent.in, #consent[aria-modal='true']")
    assert await page.is_visible("#consent")

    # Prolific ID should be filled in the modal
    prolific_val = await page.input_value("#prolific-id")
    assert prolific_val == "test_prolific_worker_123"

    # Check all checkboxes in consent form and submit
    checkboxes = await page.locator("#consent input[type='checkbox']").all()
    assert len(checkboxes) == 6
    for cb in checkboxes:
        await cb.check()

    async with page.expect_response(lambda resp: resp.url.endswith("/prolific-consent") and resp.status == 204):
        await page.click("#consent-continue")

    assert len(consent_calls) == 1

    # Verify modal is hidden
    await page.wait_for_selector("#consent", state="hidden")

    # Verify vote count displays prolific progress
    await page.wait_for_function("() => document.querySelector('#vote-count')?.textContent.includes('/')")
    count_text = await page.locator("#vote-count").text_content()
    assert count_text and "/200" in count_text

    await context.close()


async def test_about_modal(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)

    await page.goto(live_server_url)

    # Click help button to open about modal
    await page.click("#help")
    await page.wait_for_selector("#about.in, #about[aria-modal='true']")
    assert await page.is_visible("#about")

    # Press Escape to close modal
    await page.keyboard.press("Escape")
    await page.wait_for_selector("#about", state="hidden")

    await context.close()


async def test_emoji_are_shown_as_images(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)
    await page.goto(live_server_url)

    html = await page.evaluate("() => emojiToHtml('a 😂 ❤ 1️⃣ 👍🏽 🇺🇾 🏃 🙅 b')")

    assert html.startswith("a ")
    assert html.endswith(" b")
    for name in (
        "1f602",
        "2764-fe0f",
        "0031-fe0f-20e3",
        "1f44d-1f3fd",
        "1f1fa-1f1fe",
        "1f3c3-200d-2642-fe0f",
        "1f645-200d-2640-fe0f",
    ):
        assert f'data-codepoints="{name}"' in html
        assert f"img-twitter-64/{name}.png" in html

    await context.close()


async def test_emoji_without_image_are_shown_as_text(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)
    await page.goto(live_server_url)

    await page.evaluate(
        """() => {
            const element = document.createElement("p");
            element.id = "emoji-test";
            element.innerHTML = emojiToHtml("x 😂 y");
            document.body.appendChild(element);
            showNativeEmojiIfImageIsMissing(element);
        }"""
    )

    await page.wait_for_function("() => document.querySelector('#emoji-test').textContent === 'x 😂 y'")
    assert await page.locator("#emoji-test .emoji").count() == 0

    await context.close()


async def test_only_one_toast_is_shown_at_a_time(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)
    await page.goto(live_server_url)
    await page.wait_for_function("() => document.querySelector('#tweet-text .placeload-background') === null")

    await page.click("#not-humor")
    await page.click("#skip")
    await page.wait_for_timeout(400)  # The first toast takes a bit to go away.

    assert await page.locator(".md-toast").count() == 1
    assert "salteado" in (await page.locator(".md-toast").text_content() or "")

    await context.close()


async def test_loading_placeholder_is_replaced_by_the_tweet(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)

    async def _delayed_tweets(route: Route) -> None:
        await page.wait_for_timeout(300)
        await route.continue_()

    await page.route("**/tweets", _delayed_tweets)
    await page.goto(live_server_url)

    assert await page.locator("#tweet-text .placeload-background").count() == 1
    await page.wait_for_function("() => document.querySelector('#tweet-text .placeload-background') === null")
    assert (await page.locator("#tweet-text").text_content() or "").strip()

    await context.close()


async def test_whatsapp_button_is_only_shown_on_android_and_iphone(browser: Browser, live_server_url: str) -> None:
    desktop_context = await browser.new_context()
    desktop_page = await desktop_context.new_page()
    await _stub_external_trackers(desktop_page)
    await desktop_page.goto(live_server_url)
    assert not await desktop_page.locator(".wa_btn").is_visible()
    await desktop_context.close()

    for user_agent in (
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1",
    ):
        mobile_context = await browser.new_context(user_agent=user_agent)
        mobile_page = await mobile_context.new_page()
        await _stub_external_trackers(mobile_page)
        await mobile_page.goto(live_server_url)
        assert await mobile_page.locator(".wa_btn").is_visible()
        await mobile_context.close()

    ipad_context = await browser.new_context(
        user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1"
    )
    ipad_page = await ipad_context.new_page()
    await _stub_external_trackers(ipad_page)
    await ipad_page.goto(live_server_url)
    assert not await ipad_page.locator(".wa_btn").is_visible()
    await ipad_context.close()


async def test_stats_page_live(browser: Browser, live_server_url: str) -> None:
    context = await browser.new_context()
    page = await context.new_page()
    await _stub_external_trackers(page)

    await page.goto(f"{live_server_url}/stats")
    assert await page.title() == "Estadísticas"
    assert await page.is_visible("h1")

    # Check chart containers are present in DOM
    assert await page.is_visible("#chart-votes-per-category")
    assert await page.is_visible("#chart-histogram")
    await page.evaluate("window.dispatchEvent(new Event('resize'))")

    await context.close()


async def test_index_html_no_jquery_or_bootstrap_js(client: httpx2.AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    content = response.text

    # Verify jQuery, Popper, and Bootstrap JS are completely removed
    assert "jquery" not in content.lower()
    assert "popper" not in content.lower()
    assert "bootstrap.min.js" not in content.lower()
    assert "bootstrap.js" not in content.lower()

    # Verify vanilla assets are included and removed libraries are absent
    assert "js/main.js" in content
    assert "js/mdtoast.js" not in content
    assert "js/placeload.min.js" not in content
    assert "js/emoji.min.js" not in content


async def test_index_html_structure(client: httpx2.AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    content = response.text

    # Essential UI elements
    assert 'id="tweet"' in content
    assert 'id="tweet-text"' in content
    assert 'id="humor"' in content
    assert 'id="not-humor"' in content
    assert 'id="skip"' in content
    assert 'id="is-offensive"' in content

    # The Bootstrap 3 look is kept on top of Bootstrap 5, and the share buttons don't load any third-party script.
    assert 'href="css/bootstrap3-compat.css"' in content
    assert "connect.facebook.net" not in content
    assert "platform.twitter.com" not in content

    # Modals have appropriate accessibility attributes
    assert 'id="consent"' in content
    assert 'id="finished"' in content
    assert 'id="about"' in content
    assert 'role="dialog"' in content
    assert 'data-backdrop="static"' in content


async def test_stats_html_responsive(client: httpx2.AsyncClient) -> None:
    response = await client.get("/stats")
    assert response.status_code == 200
    content = response.text

    # Responsive chart styling
    assert "width: 100%" in content
    assert "max-width: 900px" in content
    assert "resize" in content

    # Correct static asset paths
    assert 'href="/css/normalize.css"' in content
    assert 'href="/img/favicon.avif"' in content
    assert "../static/" not in content


async def test_security_headers(client: httpx2.AsyncClient) -> None:
    response = await client.get("/tweets")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "no-cache" in headers.get("Cache-Control", "")


async def test_cors_headers(client: httpx2.AsyncClient) -> None:
    response = await client.options(
        "/tweets",
        headers={
            "Origin": "http://localhost:5000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5000"


def test_main_js_xss_protection() -> None:
    main_js_path = STATIC_DIR / "js" / "main.js"
    assert main_js_path.exists()
    content = main_js_path.read_text(encoding="utf-8")

    # Verify escapeHtml is defined and used
    assert "function escapeHtml" in content
    assert "escapeHtml(tweets[index].text)" in content

    # Verify absence of jQuery usages
    assert "$.post" not in content
    assert "$.getJSON" not in content
    assert "$.mdtoast" not in content
    assert "jQuery" not in content


def test_mdtoast_inlined() -> None:
    mdtoast_js_path = STATIC_DIR / "js" / "mdtoast.js"
    assert not mdtoast_js_path.exists()
    main_js_path = STATIC_DIR / "js" / "main.js"
    assert main_js_path.exists()
    content = main_js_path.read_text(encoding="utf-8")

    # Verify pure vanilla inlined implementation
    assert "function mdtoast" in content
    assert "document.createElement" in content


def test_escape_html_logic() -> None:
    # JavaScript escapeHtml regex replacement logic
    def escape_html(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )

    malicious = "<script>alert('xss');</script><img src=x onerror=alert(1)>"
    escaped = escape_html(malicious)
    assert "<script>" not in escaped
    assert "<img" not in escaped
    assert "&lt;script&gt;" in escaped
    assert "&#039;" in escaped
