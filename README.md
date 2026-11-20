# POP MART Product / Consumer Analytics

An independent portfolio case study connecting publicly reported brand growth to a reproducible example of how an ecommerce team can measure repeat purchase.

| Evidence | Finding | Scope |
| --- | --- | --- |
| POP MART annual report | FY2025 consolidated revenue was RMB 37.12bn, up 184.7% YoY | Reported company financials |
| UCI Online Retail | £10.03m in gross positive sales across 19,141 invoices | UK retailer, Dec 2010–Nov 2011 |
| UCI Online Retail | 872 of 3,974 eligible buyers purchased again within 30 days (21.9%) | Identified buyers with a full follow-up window |

Purchase conversion and POP MART customer retention are unavailable from these sources. The UK retailer results illustrate the method and should be interpreted in that retailer’s context.

- **[Dashboard](docs/dashboard.html)** · Download and open the HTML file in a browser. It runs offline with embedded aggregate data.
- **[Business brief](docs/business-brief.md)** · Findings, decisions, and a proposed experiment.
- **[Data dictionary](docs/data-dictionary.md)** · Sources, licenses, fields, and metric definitions.
- **[SQL](sql/metrics.sql)** · Order grain, monthly growth, cohorts, and 30-day repeat.
- **[Results](docs/results/)** · Reproducible aggregate CSV and JSON outputs.

## Reproduce

Use Python 3.9+ with SQLite 3.25+ (Python’s bundled SQLite on current installations). From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py
python -m unittest discover -s tests -v
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Open `build/dashboard.html` in a browser. The first run downloads the official 23 MB archive and validates its SHA-256. For an offline rerun, supply a downloaded copy with `python analyze.py --archive /path/to/online_retail.zip`. The checked-in demo uses the same generated HTML and aggregates. No login or API key is required.

## Three-minute interview walkthrough

1. **Business context (30s).** Show the audited FY2021–FY2025 revenue chart. Explain that consolidated revenue growth tells us how much the company grew, while diagnosing conversion or retention requires customer-level events.
2. **Analytics choices (60s).** Switch the retail chart from gross sales to orders, then average order value. Compare October and November 2011. Show that November sales rose with invoice volume even as AOV declined.
3. **Retention (60s).** Filter the heatmap to October 2011. Show 86 of 358 customers in M1 (24.0%). Explain that M1 is a calendar period, while the dashboard’s 21.9% uses an individual 30-day clock and a separate eligible denominator.
4. **Product decision (30s).** Describe what session instrumentation and a randomized post-purchase test would let a brand team measure. See the [experiment proposal](docs/business-brief.md#proposed-experiment).

The invoice model preserves anonymous sales in revenue and order totals, excludes those invoices from customer metrics, and keeps unobserved cohort cells blank. The test suite exercises those boundaries using a small independent fixture.
