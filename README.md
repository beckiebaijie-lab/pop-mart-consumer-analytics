# POP MART Product / Consumer Analytics

An independent portfolio case study on POP MART’s FY2024–FY2025 growth and Chinese mainland member repeat purchasing.

| Evidence | Finding | Scope |
| --- | --- | --- |
| POP MART annual report | FY2025 consolidated revenue was RMB 37.12bn, up 184.7% YoY | Reported company financials |
| POP MART annual report | The PRC contributed RMB 11.97bn, or 49.7% of group revenue growth. The Americas grew fastest (+748.4% YoY) | FY2024–FY2025 reporting regions |
| POP MART annual report | Online channels supplied 66.4% of the Americas’ revenue increase | FY2024–FY2025 Americas channels |
| POP MART annual reports | Chinese mainland member repeat purchase rose from 49.4% to 55.7% (+6.3 pp) | Members who purchased at least twice in the reporting year |
| POP MART annual reports | Chinese mainland registered membership reached 72.58m, up from 46.08m | Year-end registered member count |

## Explore the project

- **[View live dashboard](https://beckiebaijie-lab.github.io/pop-mart-consumer-analytics/dashboard.html)** · Explore regional and channel growth and member repeat purchase in your browser.
- **[Download dashboard (HTML)](https://github.com/beckiebaijie-lab/pop-mart-consumer-analytics/raw/refs/heads/main/docs/dashboard.html?download=1)** · Open the downloaded file in a browser. It works offline.
- **[Business brief](docs/business-brief.md)** · Findings and a proposed retention experiment.

## Data and methods

POP MART’s annual reports provide brand revenue and annual member repeat purchase. Session conversion, monthly cohort retention, and 30-day repeat require more granular brand data. The optional SQL appendix demonstrates cohort analysis with historical UCI retail orders (2010–2011).

- **[Data dictionary](docs/data-dictionary.md)** · Sources, licenses, fields, and metric definitions.
- **[SQL](sql/metrics.sql)** · Order grain, monthly growth, cohorts, and 30-day repeat.
- **[Results](docs/results/)** · Reproducible aggregate CSV and JSON outputs.
- **[Demo notes](docs/demo-notes.md)** · A three-minute walkthrough.

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

The invoice model preserves anonymous sales in revenue and order totals, excludes those invoices from customer metrics, and keeps unobserved cohort cells blank. The test suite exercises those boundaries using a small independent fixture.
