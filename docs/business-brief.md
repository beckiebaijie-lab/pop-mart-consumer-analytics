# Business brief · POP MART growth and measuring repeat purchase

**Audience** · Ecommerce and product analytics leads  
**Decision** · Establish session and order measurement before attributing growth to conversion or retention. Use the reported member repeat rate to frame the question, then use the proposed test to evaluate one retention lever.

## Company results

POP MART FY2025 consolidated revenue reached **RMB 37.12bn**, versus **RMB 13.04bn** in FY2024, up **184.7%**. The observed result establishes the scale of growth across the group. The company revenue series cannot quantify the share attributable to increased traffic, checkout conversion, or repeat purchase. [HKEX audited annual results](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0325/2026032500285.pdf)

## Chinese mainland membership · company disclosures

Annual member repeat purchase rose from **49.4% in FY2024 to 55.7% in FY2025**, a **6.3 percentage-point increase**. Registered membership rose from **46.08m to 72.58m**. The reported rate measures members purchasing at least twice within each reporting year. The filings do not provide an order-level panel or disclose an exact denominator count for reconstructing the repeat rate. Growth in aggregate repeat purchase does not identify whether individual acquisition cohorts improved. [FY2024 annual report](https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0423/2025042300687.pdf) · [FY2025 annual report, p. 17](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0421/2026042100395_c.pdf#page=18)

## SQL appendix · historical UK retail proxy

| Signal | Result | Interpretation |
| --- | --- | --- |
| Gross sales and orders | £10.03m and 19,141 orders across 12 full months | Gross positive transaction value before deductions |
| November vs October 2011 | Gross sales +30.7%, orders +35.7%, AOV £566.17 → £545.14 | Higher invoice volume drove the increase despite lower basket value. The sales data cannot distinguish traffic from conversion |
| 30-day repeat | 872 / 3,974 = **21.9%** | Rate for identified buyers with full follow-up |
| October cohort M1 | 86 / 358 = **24.0%** | Exact November activity among first-observed October buyers |
| Customer ID coverage | 17,754 / 19,141 = **92.8%** of orders | Identity coverage should be tracked alongside repeat rates |

December 2010 M1 was 36.6%. Customers with purchase history before the workbook begins can be assigned to that opening cohort, so it is weak evidence of stronger acquisition quality. UK gift-retailer behavior and wholesale exposure also limit generalization. These metrics do not estimate POP MART retention. [Monthly results](results/monthly.csv) · [Cohort results](results/retention.csv) · [30-day results](results/repeat_30d.csv)

## Measurement plan

Track eligible sessions, product views, cart additions, checkout starts, and paid purchase events. Capture stable session IDs, privacy-appropriate customer IDs, order IDs, timestamps, channel, region, and stock availability. Link paid purchase to the originating session and deduplicate order events by order ID. Monitor purchasing sessions / eligible sessions, checkout completion, order ID coverage, refund rate, and 30-day repeat. Reconcile paid orders to commerce records and segment by channel, new versus returning customer, and product availability.

## Proposed experiment

Test whether an opt-in reminder for an in-stock collection increases 30-day second purchase among consented, identified first-time ecommerce buyers. Randomize 1:1 at the customer level at first paid order, keeping assignment stable. Control receives the existing post-purchase experience. Treatment also receives the reminder when the collection is available. Record assignment, delivery, and stock eligibility.

Analyze by original assignment. Primary metric is the share of assigned eligible buyers placing a second paid order within 30 days. Monitor unsubscribes, refund rate, and contribution margin per assigned buyer. Predefine guardrail thresholds, check assignment balance, and wait until every enrolled customer has 30 days of follow-up before a fixed-horizon readout.

For planning only, a 20% control rate and +2 percentage point minimum detectable lift imply approximately **6,510 buyers per arm** at 80% power and two-sided 5% significance (normal approximation, before adjustments). Size the actual test against the brand’s measured baseline and volume. Report absolute lift and its 95% confidence interval. The experiment is a proposal with no measured treatment effect.
