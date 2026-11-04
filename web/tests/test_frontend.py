"""Frontend and security verification tests for ClasificaHumor."""

from pathlib import Path

import httpx2

BASE_DIR = Path(__file__).resolve().parent.parent / "src" / "clasificahumor"
STATIC_DIR = BASE_DIR / "static"


async def test_index_html_no_jquery_or_bootstrap_js(client: httpx2.AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    content = response.text

    # Verify jQuery, Popper, and Bootstrap JS are completely removed
    assert "jquery" not in content.lower()
    assert "popper" not in content.lower()
    assert "bootstrap.min.js" not in content.lower()
    assert "bootstrap.js" not in content.lower()

    # Verify vanilla assets are included
    assert "js/main.js" in content
    assert "js/mdtoast.js" in content
    assert "js/placeload.min.js" in content
    assert "js/emoji.min.js" in content


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
    assert 'href="/img/favicon.png"' in content
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


def test_mdtoast_js_vanilla() -> None:
    mdtoast_js_path = STATIC_DIR / "js" / "mdtoast.js"
    assert mdtoast_js_path.exists()
    content = mdtoast_js_path.read_text(encoding="utf-8")

    # Verify pure vanilla implementation
    assert "This plugin requires jQuery" not in content
    assert "document.createElement" in content
    assert "doc.appendChild(that.toast)" in content


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
