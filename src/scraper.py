import re
import time

from playwright.sync_api import sync_playwright
from urllib.parse import urlparse


RELEVANT_KEYWORDS = [
    "about",
    "team",
    "company",
    "contact",
    "pricing",
    "leadership",
    "people",
    "careers",
    "sales"
]


def is_internal_link(href: str, base_url: str) -> bool:
    """Check whether a link belongs to the same website."""

    base_domain = urlparse(base_url).netloc.replace("www.", "")
    link_domain = urlparse(href).netloc.replace("www.", "")

    return link_domain == base_domain


def discover_relevant_pages(page, base_url: str) -> list[str]:
    """Find useful internal pages from the homepage."""

    try:
        links = page.locator("a").evaluate_all(
            """
            elements => elements.map(a => ({
                text: (a.innerText || "").trim(),
                href: a.href
            }))
            """
        )

    except Exception as e:
        print(f"Could not discover links: {e}")
        return []

    relevant_pages = []

    for link in links:

        href = link.get("href", "")
        text = link.get("text", "").lower()

        if not href:
            continue

        if href.startswith(
            ("mailto:", "tel:", "javascript:", "#")
        ):
            continue

        if not is_internal_link(href, base_url):
            continue

        href_lower = href.lower()

        if any(
            keyword in href_lower or keyword in text
            for keyword in RELEVANT_KEYWORDS
        ):
            relevant_pages.append(href)

    return list(dict.fromkeys(relevant_pages))


def extract_page_text(
    page,
    url: str,
    max_retries: int = 2
) -> str:
    """Extract visible page text with retry logic."""

    for attempt in range(1, max_retries + 1):

        try:

            print(
                f"Visiting: {url} "
                f"(attempt {attempt}/{max_retries})"
            )

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Handle HTTP errors
            if response:

                status = response.status

                if status >= 400:

                    print(
                        f"HTTP {status} for {url}"
                    )

                    return ""

            page.wait_for_timeout(1500)

            # Remove unnecessary HTML elements
            try:

                page.locator(
                    "script, style, noscript, svg"
                ).evaluate_all(
                    "elements => elements.forEach(e => e.remove())"
                )

            except Exception:
                pass

            # Extract visible text
            try:

                text = page.locator(
                    "body"
                ).inner_text()

            except Exception as e:

                print(
                    f"Could not extract body text: {e}"
                )

                return ""

            return text.strip()

        except Exception as e:

            print(
                f"Attempt {attempt} failed for {url}: {e}"
            )

            if attempt < max_retries:

                print("Retrying...")

                time.sleep(2)

            else:

                print(
                    f"Giving up on: {url}"
                )

    return ""


def extract_emails(text: str) -> list[str]:
    """Extract public email addresses."""

    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    emails = re.findall(
        pattern,
        text
    )

    return list(
        dict.fromkeys(emails)
    )


def extract_linkedin_urls(text: str) -> list[str]:
    """Extract LinkedIn URLs."""

    pattern = (
        r"https?://(?:www\.)?"
        r"linkedin\.com/[^\s\"<>]+"
    )

    urls = re.findall(
        pattern,
        text
    )

    cleaned_urls = []

    for url in urls:

        url = url.rstrip(
            ".,);]"
        )

        if url not in cleaned_urls:

            cleaned_urls.append(url)

    return cleaned_urls


def scrape_website(url: str) -> dict:
    """Scrape a website with error handling and retries."""

    domain = urlparse(url).netloc

    result = {
        "domain": domain,
        "homepage": "",
        "pages": {},
        "emails": [],
        "linkedin_urls": []
    }

    with sync_playwright() as p:

        browser = None

        try:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            print(
                f"\nOpening homepage: {url}"
            )

            # Scrape homepage
            homepage_text = extract_page_text(
                page,
                url
            )

            result["homepage"] = homepage_text

            # If homepage fails, safely return
            if not homepage_text:

                print(
                    f"Homepage could not be scraped: "
                    f"{domain}"
                )

                return result

            # Discover relevant pages
            relevant_pages = (
                discover_relevant_pages(
                    page,
                    url
                )
            )

            print(
                "\nRelevant pages found:"
            )

            for link in relevant_pages:

                print(
                    f"- {link}"
                )

            # Scrape maximum 5 relevant pages
            for link in relevant_pages[:5]:

                text = extract_page_text(
                    page,
                    link
                )

                if text:

                    result["pages"][link] = text

            # Combine website text
            all_text = (
                result["homepage"]
                + "\n"
                + "\n".join(
                    result["pages"].values()
                )
            )

            # Extract emails
            result["emails"] = extract_emails(
                all_text
            )

            # Extract LinkedIn URLs
            result["linkedin_urls"] = (
                extract_linkedin_urls(
                    all_text
                )
            )

            print(
                "\nEmails found:"
            )

            for email in result["emails"]:

                print(
                    f"- {email}"
                )

            print(
                "\nLinkedIn URLs found:"
            )

            for linkedin in result["linkedin_urls"]:

                print(
                    f"- {linkedin}"
                )

            return result

        except Exception as e:

            print(
                f"Website failed: {domain}"
            )

            print(
                f"Error: {e}"
            )

            return result

        finally:

            if browser:

                browser.close()


if __name__ == "__main__":

    result = scrape_website(
        "https://postman.com"
    )

    print(
        "\n========== RESULT ==========\n"
    )

    print(
        "Domain:",
        result["domain"]
    )

    print(
        "Homepage characters:",
        len(result["homepage"])
    )

    print(
        "\nPages scraped:"
    )

    for url, text in result["pages"].items():

        print(
            f"{url} → {len(text)} characters"
        )

    print(
        "\nEmails:"
    )

    print(
        result["emails"]
    )

    print(
        "\nLinkedIn URLs:"
    )

    print(
        result["linkedin_urls"]
    )