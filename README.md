# AI Lead Enrichment Agent

An autonomous AI-powered lead enrichment agent that crawls public company websites, extracts useful company intelligence, and generates structured lead information using an LLM.

## Features

- Automated website crawling using Playwright
- Discovers relevant internal pages such as:
  - About
  - Company
  - Team
  - Careers
  - Contact
  - Pricing
  - Sales
- Extracts and cleans visible website text
- Extracts public email addresses
- Extracts publicly available LinkedIn URLs
- Uses Groq LLM for company intelligence extraction
- Structured output validated using Pydantic
- Confidence score between 0 and 1
- Handles HTTP errors and timeouts
- Retry mechanism for failed page requests
- Retry mechanism for failed LLM requests
- Continues processing when one company fails
- Generates JSON and CSV output

## Architecture

```text
Company Domains
       |
       v
   Playwright
       |
       v
Homepage + Relevant Pages
       |
       v
Text Cleaning
       |
       +------> Email Extraction
       |
       +------> LinkedIn Extraction
       |
       v
       
    Groq LLM
       |
       v
Pydantic Validation
       |
       v
Structured Company Data
       |
       +------> output.json
       |
       +------> output.csv