import os
import time

from dotenv import load_dotenv
from groq import Groq

from scraper import scrape_website
from models import CompanyData


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:

    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


client = Groq(
    api_key=api_key
)


def build_website_context(
    scraped_data: dict
) -> str:
    """Prepare clean website text for the LLM."""

    sections = []

    homepage = scraped_data.get(
        "homepage",
        ""
    )

    if homepage:

        sections.append(
            "HOMEPAGE:\n"
            + homepage[:6000]
        )

    pages = scraped_data.get(
        "pages",
        {}
    )

    for url, text in pages.items():

        if text:

            sections.append(
                f"\nPAGE: {url}\n"
                f"{text[:3000]}"
            )

    context = "\n\n".join(
        sections
    )

    # Keep prompt within Groq token limit
    return context[:16000]


def extract_company_data(
    domain: str,
    scraped_data: dict
) -> CompanyData:
    """Extract structured company information using Groq."""

    website_context = build_website_context(
        scraped_data
    )

    emails = scraped_data.get(
        "emails",
        []
    )

    linkedin_urls = scraped_data.get(
        "linkedin_urls",
        []
    )

    prompt = f"""
You are an AI lead enrichment agent.

Analyze the public website information below.

Company domain:
{domain}

Website content:
{website_context}

Information directly extracted from the website:

Public emails:
{emails}

LinkedIn URLs:
{linkedin_urls}

Extract the following:

1. company_overview
- Exactly 2 concise sentences.
- Explain what the company does.

2. target_audience
- Identify the company's ideal customers or users.
- Use evidence from the website.
- Do not guess.

3. contact_points
- Use the public emails provided above.
- Do not invent email addresses.
- If there are no emails, return an empty list.

4. leadership
- Identify important leadership/team members if clearly mentioned.
- Include name and role.
- Include LinkedIn URL only when reliably associated with that person.
- Do not invent names, roles, or URLs.
- If no leadership information is available, return an empty list.

5. confidence_score
- Number between 0 and 1.
- Higher means stronger evidence.
- Lower means information is missing or uncertain.

IMPORTANT:
- Never invent information.
- Use only evidence from the website.
- Return ONLY valid JSON.
- Follow the requested structure exactly.

Return:

{{
    "domain": "{domain}",
    "company_overview": "two sentence overview",
    "target_audience": "target audience",
    "contact_points": [],
    "leadership": [],
    "confidence_score": 0.0
}}
"""

    response = None

    # Retry Groq request
    for attempt in range(1, 3):

        try:

            print(
                f"Groq request "
                f"(attempt {attempt}/2)"
            )

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You extract accurate company "
                            "intelligence from public "
                            "website information."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                response_format={
                    "type": "json_object"
                }
            )

            break

        except Exception as e:

            print(
                f"Groq request failed: {e}"
            )

            if attempt < 2:

                print(
                    "Retrying Groq request..."
                )

                time.sleep(3)

            else:

                raise

    if response is None:

        raise RuntimeError(
            "Groq did not return a response."
        )

    result = response.choices[
        0
    ].message.content

    # Validate LLM output with Pydantic
    company_data = (
        CompanyData.model_validate_json(
            result
        )
    )

    return company_data


if __name__ == "__main__":

    domain = "postman.com"

    url = "https://postman.com"

    print(
        "\n=============================="
    )

    print(
        "SCRAPING WEBSITE"
    )

    print(
        "=============================="
    )

    scraped_data = scrape_website(
        url
    )

    print(
        "\n=============================="
    )

    print(
        "EXTRACTING COMPANY DATA"
    )

    print(
        "=============================="
    )

    company_data = extract_company_data(
        domain,
        scraped_data
    )

    print(
        "\n=============================="
    )

    print(
        "FINAL STRUCTURED OUTPUT"
    )

    print(
        "=============================="
    )

    print(
        company_data.model_dump_json(
            indent=2
        )
    )