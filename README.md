# open-data-actors-agent-tools

Agent tools (LangChain, LlamaIndex, CrewAI) for 29 public open-data actors on Apify: sanctions screening, SEC Form D funding leads, FMCSA new carriers, building permits, new business filings, ATS and Workday jobs, domain intelligence, technical SEO audits and more. Each tool runs one actor and returns JSON rows.

## Disclosure

- These actors and this package are **maintained by the same author** (Apify user `transparent_meteorite`). This is not an independent integration.
- The actors are **pay-per-result** on **your** Apify account. New Apify accounts get free monthly platform credit, which is enough to try the tools at small caps; nothing here is free beyond that. Check each actor page for its current price.
- Every tool has a small default cap (about 3 to 10 results) and a `max_items` argument, so an agent cannot accidentally run a large job.
- Output comes from public sources (government registries, public APIs, public web pages). Verify anything that matters, especially sanctions or compliance matches.

## Install

Not on PyPI yet. Install from GitHub:

```bash
pip install git+https://github.com/Mamoo85/open-data-actors-agent-tools
pip install "open-data-actors-tools[langchain] @ git+https://github.com/Mamoo85/open-data-actors-agent-tools"   # or [llamaindex] / [crewai]
```

Set your token (never commit it):

```bash
export APIFY_TOKEN=...   # https://console.apify.com/account/integrations
```

The core package only needs `apify-client` and `pydantic`. Framework imports are lazy, so it works without any of them.

## Use

Plain Python:

```python
from open_data_actors import run_actor
rows = run_actor("sanctions-screening", names=["Acme Plumbing Supplies LLC"], lists=["ofac_sdn", "un"], max_items=10)
```

LangChain:

```python
from open_data_actors.langchain import get_langchain_tools
tools = get_langchain_tools()          # list of StructuredTool
```

LlamaIndex:

```python
from open_data_actors.llamaindex import get_llamaindex_tools
tools = get_llamaindex_tools()         # list of FunctionTool
```

CrewAI:

```python
from open_data_actors.crewai import get_crewai_tools
tools = get_crewai_tools()             # list of crewai.tools.BaseTool
```

See `examples/` for runnable scripts. Inputs are validated with pydantic against each actor's input schema (unknown keys are rejected). Secret-like actor options (API keys, webhooks, proxy settings) are deliberately not exposed to agents.

## Tools

| Tool | Actor | Link |
|---|---|---|
| `fmcsa_new_carrier_leads` | FMCSA New Motor Carrier Leads: New Authority, Email & Phone | [actor](https://apify.com/transparent_meteorite/fmcsa-new-carrier-leads?fpr=rnmakg) |
| `warn_layoff_alerts` | WARN Layoff Notices API: 7 States (TX CA WA OR MD VA NC) $3/1k | [actor](https://apify.com/transparent_meteorite/warn-layoff-alerts?fpr=rnmakg) |
| `website_tech_stack_detector` | Website Tech Stack Lookup: CMS, Frameworks, Hosting $0.002/site | [actor](https://apify.com/transparent_meteorite/website-tech-stack-detector?fpr=rnmakg) |
| `ats_open_roles` | Career Site Jobs API: Greenhouse, Lever, Ashby & more | $2/1k | [actor](https://apify.com/transparent_meteorite/ats-open-roles?fpr=rnmakg) |
| `city_council_agendas` | City Council Meetings & Agendas: Legistar Votes, PDFs | $1/1k | [actor](https://apify.com/transparent_meteorite/city-council-agendas?fpr=rnmakg) |
| `company_enrichment_by_domain` | Company Enrichment by Domain: Socials, Emails, Tech Stack $5/1k | [actor](https://apify.com/transparent_meteorite/company-enrichment-by-domain?fpr=rnmakg) |
| `sec_form_d_funding_leads` | SEC Form D Startup Funding Leads: Recently Funded, $2.50/1k | [actor](https://apify.com/transparent_meteorite/sec-form-d-funding-leads?fpr=rnmakg) |
| `technical_seo_page_audit` | Technical SEO Page Audit: Broken Links, Hreflang, $3/1k | [actor](https://apify.com/transparent_meteorite/technical-seo-page-audit?fpr=rnmakg) |
| `domain_intelligence_lookup` | Domain Intelligence: WHOIS/RDAP, DNS, Subdomains, SSL, $2/1k | [actor](https://apify.com/transparent_meteorite/domain-intelligence-lookup?fpr=rnmakg) |
| `new_business_filings` | New Business Filings: New LLCs and Corporations, $4/1k | [actor](https://apify.com/transparent_meteorite/new-business-filings?fpr=rnmakg) |
| `app_store_reviews` | App Store Reviews Scraper: Ratings, 150+ Countries, $0.50/1k | [actor](https://apify.com/transparent_meteorite/app-store-reviews?fpr=rnmakg) |
| `website_contact_extractor` | Website Contact Details Scraper: Emails, Phones & Socials $2/1k | [actor](https://apify.com/transparent_meteorite/website-contact-extractor?fpr=rnmakg) |
| `shopify_store_leads` | Shopify Leads: Store Apps, Products & Contacts | $4/1k | [actor](https://apify.com/transparent_meteorite/shopify-store-leads?fpr=rnmakg) |
| `local_business_leads` | Local Business Leads: No-Website Finder (OpenStreetMap) $3/1k | [actor](https://apify.com/transparent_meteorite/local-business-leads?fpr=rnmakg) |
| `workday_jobs_scraper` | Workday Jobs Scraper: Any Career Site, 165+ Companies $1/1k | [actor](https://apify.com/transparent_meteorite/workday-jobs-scraper?fpr=rnmakg) |
| `company_news_monitor` | Company News Monitor: Brand & Keyword News Alerts, $2/1k | [actor](https://apify.com/transparent_meteorite/company-news-monitor?fpr=rnmakg) |
| `building_permits_leads` | Building Permits Leads: US City Permits and Violations, $1.5/1k | [actor](https://apify.com/transparent_meteorite/building-permits-leads?fpr=rnmakg) |
| `sitemap_link_inventory` | Sitemap Link Inventory: All URLs + Broken-Link Check, $1/1k | [actor](https://apify.com/transparent_meteorite/sitemap-link-inventory?fpr=rnmakg) |
| `developer_signals` | Hacker News, npm & PyPI Developer Signals | [actor](https://apify.com/transparent_meteorite/developer-signals?fpr=rnmakg) |
| `sanctions_screening` | Sanctions Screening: OFAC SDN, EU, UN & UK Lists, Fuzzy Match | [actor](https://apify.com/transparent_meteorite/sanctions-screening?fpr=rnmakg) |
| `federal_grants_contracts` | Federal Grants & Contracts Finder: Grants.gov + USAspending | [actor](https://apify.com/transparent_meteorite/federal-grants-contracts?fpr=rnmakg) |
| `amazon_product_search` | Amazon Product Search: prices, ratings, ASINs | [actor](https://apify.com/transparent_meteorite/amazon-product-search?fpr=rnmakg) |
| `linkedin_public_jobs` | LinkedIn Public Jobs Scraper (no login) | Salary & Level | [actor](https://apify.com/transparent_meteorite/linkedin-public-jobs?fpr=rnmakg) |
| `meta_ad_library` | Meta Ad Library Scraper: Facebook & Instagram Ads | [actor](https://apify.com/transparent_meteorite/meta-ad-library?fpr=rnmakg) |
| `google_maps_places_scraper` | Google Maps Scraper: Places, Phones, Emails, Reviews | [actor](https://apify.com/transparent_meteorite/google-maps-places-scraper?fpr=rnmakg) |
| `tiktok_public_profile_scraper` | TikTok Profile Scraper: Followers, Posts, Bio Email, $2.5/1K | [actor](https://apify.com/transparent_meteorite/tiktok-public-profile-scraper?fpr=rnmakg) |
| `youtube_comments_scraper` | YouTube Comments Scraper: Comments + Replies, $1/1K | [actor](https://apify.com/transparent_meteorite/youtube-comments-scraper?fpr=rnmakg) |
| `amazon_bestsellers` | Amazon Best Sellers Scraper: Ranks, 21 Countries, $1.9/1K | [actor](https://apify.com/transparent_meteorite/amazon-bestsellers?fpr=rnmakg) |
| `sam_gov_opportunities` | SAM.gov Contract Opportunities: Federal Bids & RFPs | [actor](https://apify.com/transparent_meteorite/sam-gov-opportunities?fpr=rnmakg) |

## Testing, honestly

- `pytest` runs 100% mocked (no network, no spend) and is what CI runs. It checks the registry, input validation, `run_actor` against a fake Apify client for all 24 tools, and adapter construction.
- `tests/live_default_run.py` makes ONE real run of `sanctions-screening` and is not run in CI.
- CrewAI: see the status note at the bottom of this README.

## Regenerate the registry

`src/open_data_actors/registry.json` is generated from the actor catalog in `catalog_src/`:

```bash
python tools/generate_registry.py
```

## License

MIT. Homepage: https://mamoo85.github.io/open-data-actors/

## Status notes

- CrewAI: the adapter was tested against the real `crewai` package (installed on Python 3.12, Windows) with a mocked Apify client. If a future crewai release changes `BaseTool`, the stub-based test in `tests/test_tools.py` still covers the adapter's own logic.
- Tested with apify-client 3.3 (and written to also accept the 1.x/2.x `timeout_secs` call style, not tested there).
- One real default run (`sanctions-screening`, sample input) returned 3 rows on 2026-10-13.

_Some links are affiliate links._
