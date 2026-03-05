# Hybrid Marketplace Architecture Overview

## Concept
A hybrid marketplace for specialized services that leverages automated web scraping to bootstrap both the supply (service providers) and demand (service requests) sides of the platform.

## Technology Stack
- **Frontend**: Flutter (Dart) - For multi-platform support (Web, iOS, Android, Desktop).
- **Backend / Scraper**: Python - Python is ideal for writing high-performance web scrapers (using libraries like Scrapy, BeautifulSoup, or Playwright/Selenium) and handling data processing/enrichment.
- **Database / Auth / Backend-as-a-Service**: Supabase - PostgreSQL database to store supply and demand data, handle user authentication, storage, and real-time features.

## High-Level Architecture

### 1. Data Ingestion (Python Scraper Layer)
- **Target Niche**: Rope access services (height-related work) and common civil construction services.
- **Target Platforms**: OLX, Mercado Livre, Facebook, Twitter, LinkedIn, and WhatsApp Groups.
- **Scraper Bots**: Scheduled Python scripts running on a server (using Playwright for dynamic content) targeting the platforms above to extract supply (contractors/freelancers) and demand (service requests/job posts).
- **Data Enrichment**: Cleaning and standardizing the scraped data (e.g., categorizing as "Rope Access" or "Civil Construction", normalizing locations).
- **Supabase Integration**: Python scripts use the `supabase-py` client library to insert/update the processed supply and demand data directly into the Supabase PostgreSQL database.

### 2. Core Infrastructure (Supabase Layer)
- **Database**: PostgreSQL with PostgREST for instant APIs.
  - `Providers` (Supply side data)
  - `Requests` (Demand side data)
  - `Users` (Platform users)
  - `Transactions/Matches`
- **Authentication**: Managing user logins for specialized service providers who claim their automatically generated profiles or users who make requests.
- **Edge Functions**: (Optional) Deno based edge functions for any complex webhook handling or intermediate logic that doesn't require a full Python backend.

### 3. User Interface (Flutter Frontend Layer)
- **Client App**: 
  - Allows end-users to browse available providers (the scraped supply).
  - Allows providers to browse user requests (the scraped demand).
  - Facilitates the matching, communication, and management of the service marketplace.
- **Admin Dashboard**: (Optional but recommended) A separate Flutter Web interface or hidden route to manage the scraped data, verify users, and monitor platform health.

## Proposed Directory Structure
```
c:\Users\Admin\DEV\CLEAN_WORK\
├── scraper_backend/          # Python environment for web scrapers
│   ├── scrapers/             # Individual scraper scripts
│   ├── requirements.txt      # Python dependencies
│   └── main.py               # Entry point / Scheduler
├── marketplace_app/          # Flutter frontend
│   ├── lib/                  # Dart source code
│   ├── pubspec.yaml          # Flutter dependencies
│   └── ...
└── architecture_overview.md  # This document
```
