import csv
import json
import os

from scraper import scrape_website
from llm_extractor import extract_company_data


DOMAINS = [
    "postman.com",
    "supabase.com",
    "vapi.ai"
]


def process_company(domain: str) -> dict:
    """Scrape and enrich one company safely."""

    url = f"https://{domain}"

    print("\n" + "=" * 60)
    print(f"PROCESSING: {domain}")
    print("=" * 60)

    try:

        # Step 1: Scrape website
        scraped_data = scrape_website(url)

        # Step 2: Extract structured information
        company_data = extract_company_data(
            domain,
            scraped_data
        )

        return company_data.model_dump()

    except Exception as e:

        print(
            f"Error processing {domain}: {e}"
        )

        # Continue with remaining companies
        return {
            "domain": domain,
            "company_overview": "",
            "target_audience": "",
            "contact_points": [],
            "leadership": [],
            "confidence_score": 0.0,
            "error": str(e)
        }


def save_json(results: list[dict], filename: str):
    """Save results as JSON."""

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )


def save_csv(results: list[dict], filename: str):
    """Save results as CSV."""

    fieldnames = [
        "domain",
        "company_overview",
        "target_audience",
        "contact_points",
        "leadership",
        "confidence_score",
        "error"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:

            row = result.copy()

            # Convert lists to readable strings
            row["contact_points"] = ", ".join(
                row.get(
                    "contact_points",
                    []
                )
            )

            leadership = row.get(
                "leadership",
                []
            )

            row["leadership"] = "; ".join(
                [
                    f"{member.get('name', '')} - "
                    f"{member.get('role', '')}"
                    for member in leadership
                ]
            )

            writer.writerow(row)


def main():
    """Process all domains and save results."""

    results = []

    for domain in DOMAINS:

        result = process_company(
            domain
        )

        results.append(result)

    # Create output folder
    os.makedirs(
        "output",
        exist_ok=True
    )

    json_file = "output/output.json"
    csv_file = "output/output.csv"

    # Save JSON
    save_json(
        results,
        json_file
    )

    # Save CSV
    save_csv(
        results,
        csv_file
    )

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(
        f"\nJSON saved to: {json_file}"
    )

    print(
        f"CSV saved to: {csv_file}"
    )


if __name__ == "__main__":

    main()