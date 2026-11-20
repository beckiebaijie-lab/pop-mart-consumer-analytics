# Data dictionary and provenance

## POP MART company financials

Source is POP MART International Group Limited, **Annual Report 2025**, printed p. 6, Financial Performance Highlights. This project transcribes the five consolidated revenue figures into `data/pop_mart_revenue.csv`. The annual report is publicly accessible, with no open-data reuse license identified in the filing. The repository cites the filing and includes only the selected numeric facts. The filing, text, and brand artwork are excluded. [HKEX annual report](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100395_c.pdf)

| Field | Definition |
| --- | --- |
| year | Fiscal year ended December 31 |
| revenue_rmb_thousands | Consolidated revenue in RMB thousands as reported |
| yoy | Current-year revenue divided by prior-year revenue minus 1. Blank for the first year |

## UCI Online Retail proxy

Daqing Chen (2015), *Online Retail*, UCI Machine Learning Repository, DOI **10.24432/C5BW33**. The data covers a UK gift retailer with many wholesale customers. UCI lists **CC BY 4.0**. Adaptations here include filtering, invoice aggregation, and calculation of summary metrics. Raw invoices and customer IDs are downloaded locally for analysis and excluded from the repository. License applies to the UCI data and adapted UCI results. [Dataset](https://doi.org/10.24432/C5BW33) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

| UCI column | Role |
| --- | --- |
| InvoiceNo | Invoice identifier. Prefix C marks cancellations |
| StockCode | Product code, unused |
| Description | Product description, unused |
| Quantity | Line item quantity |
| InvoiceDate | Invoice timestamp, used as recorded without timezone conversion |
| UnitPrice | Line item price in GBP |
| CustomerID | Customer key. The original worksheet has blank IDs |
| Country | Customer country, unused. Results include every destination |

### Processing and scope

- The pinned workbook covers 2010-12-01 through 2011-12-09 and contains 541,909 rows. Analysis uses December 2010 through November 2011 inclusive, excluding partial December 2011 for comparability.
- Keep rows with positive quantity, positive price, and an invoice without a cancellation prefix. Preserve repeated source lines because there is no line ID to verify duplication. Gross sales include all qualifying invoice line types, including any positively priced charges, and do not deduct returns or adjustments.
- Aggregate by invoice using earliest qualifying timestamp and any non-null customer ID. Reject invoices with conflicting customer IDs. One distinct qualifying invoice is one order.
- First purchase means first observed qualifying invoice by that customer. Earlier purchases may be invisible, especially in the opening cohort. The window also means there is no full-year YoY comparison for the proxy.
- Monthly retention is exact-period activity and can rise after a quiet month. M0 equals 100% by construction. Observed months with no purchases show 0%. Future months outside the window are absent. An anonymous invoice cannot contribute to customer metrics.

### Aggregate output

| File | Field | Definition |
| --- | --- | --- |
| monthly.csv | month | First date of month |
| monthly.csv | gross_gbp | Sum of positive included line amounts, rounded to two decimals |
| monthly.csv | orders | Number of distinct included invoices |
| monthly.csv | buyers | Unique identified purchasing customers in the month |
| monthly.csv | identified_orders | Included invoices linked to a customer ID |
| monthly.csv | identified_gross_gbp | Gross sales linked to identified orders |
| monthly.csv | aov_gbp | Gross sales divided by all orders |
| monthly.csv | mom | Current gross divided by prior month's gross minus 1. Blank if undefined |
| retention.csv | cohort, month, age | First observed purchase month, activity month, and calendar months elapsed |
| retention.csv | size, active_buyers, rate | Cohort size, distinct buyers active in the observation month, and active buyers / size |
| repeat_30d.csv | eligible_buyers | Identified buyers whose first observed order plus 30 days falls strictly before 2011-12-01 |
| repeat_30d.csv | repeat_buyers, rate | Eligible buyers with at least one invoice strictly after first order and within 30 days, and repeat buyers / eligible buyers |
| metrics.json | quality | Unfiltered workbook row count and number of rows with blank customer ID |

Session conversion requires purchasing sessions / eligible sessions, measured over the same time, channel, and eligibility scope. Neither source provides those counts. 30-day repeat and AOV are separate transaction metrics. Order ID coverage = identified orders / all orders.
