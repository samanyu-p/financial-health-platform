# Corporate Financial Health & Working Capital Analysis

## Overview

This project is an end-to-end financial analytics platform that uses SEC Company Facts data to analyze public companies across revenue growth, profitability, working capital, free cash flow, forecasting, and scenario analysis.

The project started with Walmart and has expanded to compare Walmart, Target, and Costco. It is currently retail-focused because working-capital metrics such as inventory days, payables days, and cash conversion cycle are most meaningful for companies with inventory-heavy business models.

## Goals

The goal of this project is to build something stronger than a basic machine-learning notebook. It is designed to show:

- Python data engineering
- SEC financial statement data collection
- Pandas-based cleaning and transformation
- Financial metric calculation
- Multi-company comparison
- Forecasting and scenario analysis
- SQLite / SQL querying
- Streamlit dashboarding
- Git/GitHub workflow
- Business interpretation and data-quality awareness

## Data Source

The project uses the SEC Company Facts API.

Example:

```text
https://data.sec.gov/api/xbrl/companyfacts/CIK0000104169.json