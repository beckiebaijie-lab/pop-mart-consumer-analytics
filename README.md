# POP MART Product / Consumer Analytics

An independent portfolio case study on POP MART’s FY2024–FY2025 growth and Chinese mainland member repeat purchasing.

| Evidence | Finding | Scope |
| --- | --- | --- |
| POP MART annual report | FY2025 consolidated revenue was RMB 37.12bn, up 184.7% YoY | Reported company financials |
| POP MART annual reports | Chinese mainland member repeat purchase rose from 49.4% to 55.7% (+6.3 pp) | Members who purchased at least twice in the reporting year |
| POP MART annual reports | Chinese mainland registered membership reached 72.58m, up from 46.08m | Year-end registered member count |

The filings contain annual member repeat purchase, while session conversion, monthly cohort retention, and 30-day repeat require additional granular data. The dashboard’s SQL appendix uses historical UCI orders (2010–2011) to demonstrate those order-based methods independently.

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
2. **Member behavior (60s).** Show the rise from 49.4% to 55.7% in annual repeat purchase. Explain the reporting-year definition and why year-end registered membership is a separate metric.
3. **Retention method (60s).** Open the historical SQL appendix and filter the heatmap to October 2011. Show 86 of 358 customers in M1 (24.0%). Explain that M1 is a calendar period, while the dashboard’s 21.9% uses an individual 30-day clock and a separate eligible denominator.
4. **Product decision (30s).** Describe what session instrumentation and a randomized post-purchase test would let a brand team measure. See the [experiment proposal](docs/business-brief.md#proposed-experiment).

The invoice model preserves anonymous sales in revenue and order totals, excludes those invoices from customer metrics, and keeps unobserved cohort cells blank. The test suite exercises those boundaries using a small independent fixture.
