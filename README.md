# Samsung Electronics DART Financial Agent

Automated financial-data collection and analysis for Samsung Electronics using OpenDART. This implementation follows the available `ms_samsung` project documentation; the original source files were not accessible, so this is a functional reproduction rather than a byte-for-byte clone.


## Features
- Collect annual, semiannual and quarterly financial statements from OpenDART (2015 onward)
- Consolidated statements prioritized
- Financial ratios and validation checks
- Markdown report and GitHub Pages dashboard
- Monthly scheduled update on the 1st; manual Actions run supported

## Setup
1. In repository **Settings → Secrets and variables → Actions**, add `DART_API_KEY`.
2. Run **Actions → DART Financial Agent → Run workflow**.
3. Enable GitHub Pages in Settings → Pages, source **GitHub Actions**.

## Reports
- Generated report: `reports/financial_analysis.md`
- Dashboard: GitHub Pages site


## Scope
Samsung Electronics only (corp code `00126380`); data from 2015 onward. Filing codes: annual `11011`, half-year `11012`, Q1 `11013`, Q3 `11014`. Data availability and OpenDART response format may vary. Educational analysis only, not investment advice.
