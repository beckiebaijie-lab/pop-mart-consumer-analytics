"""Download the attributed UCI snapshot and publish aggregate SQLite results."""
import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
SHA256 = "f5385cbb54bbebf7196389109c6b0621faab0c304e3702548165e71c84aede8b"
METRICS = {"monthly": "month", "retention": "cohort, age", "repeat_30d": "eligible_buyers"}
HEADERS = ("InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate",
           "UnitPrice", "CustomerID", "Country")


def open_database():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE lines(invoice TEXT NOT NULL, at TEXT NOT NULL, customer TEXT,
                           quantity INTEGER NOT NULL, price REAL NOT NULL);
        CREATE INDEX lines_customer_at ON lines(customer, at);
    """)
    db.executescript((ROOT / "sql/metrics.sql").read_text())
    return db


def ensure_archive(path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(URL, timeout=60) as response:
            temporary = path.with_suffix(".download")
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
            temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError("UCI archive checksum mismatch. Supply the original pinned archive.")


def read_lines(path):
    from openpyxl import load_workbook

    with ZipFile(path) as archive, archive.open("Online Retail.xlsx") as sheet:
        workbook = load_workbook(sheet, read_only=True, data_only=True)
        try:
            rows = workbook.active.values
            if tuple(next(rows)) != HEADERS:
                raise ValueError("Unexpected UCI column names")
            for invoice, _, _, quantity, at, price, customer, _ in rows:
                yield (str(invoice), at.isoformat(sep=" ", timespec="seconds"),
                       str(customer) if customer is not None else None, quantity, price)
        finally:
            workbook.close()


def aggregate(db):
    # Materialize one row per order to speed up 30-day follow-up.
    db.executescript("""
        CREATE TABLE order_snapshot AS SELECT * FROM orders;
        DROP VIEW orders;
        CREATE TABLE orders AS SELECT * FROM order_snapshot;
        DROP TABLE order_snapshot;
        CREATE INDEX orders_customer_at ON orders(customer, at);
    """)
    return {table: [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY {sort}")]
            for table, sort in METRICS.items()}


def read_financials():
    history = []
    with (ROOT / "data/pop_mart_revenue.csv").open(newline="") as source:
        for row in csv.DictReader(source):
            revenue = int(row["revenue_rmb_thousands"])
            yoy = revenue / history[-1]["revenue_rmb_thousands"] - 1 if history else None
            history.append(dict(year=int(row["year"]), revenue_rmb_thousands=revenue, yoy=yoy))
    return history


def read_regions(financials):
    totals = {row["year"]: row["revenue_rmb_thousands"] for row in financials}
    group_growth = totals[2025] - totals[2024]
    regions = []
    with (ROOT / "data/pop_mart_regions.csv").open(newline="") as source:
        for row in csv.DictReader(source):
            prior = int(row["revenue_2024_rmb_thousands"])
            current = int(row["revenue_2025_rmb_thousands"])
            growth = current - prior
            regions.append(dict(region=row["region"], prior=prior, current=current,
                                growth=growth, yoy=growth / prior,
                                growth_share=growth / group_growth))
    if (sum(row["prior"] for row in regions) != totals[2024]
            or sum(row["current"] for row in regions) != totals[2025]):
        raise ValueError("Regional revenue does not reconcile to group revenue")
    return regions


def read_americas_channels(regions):
    americas = next(row for row in regions if row["region"] == "Americas")
    breakdowns = {"all": [], "online": []}
    with (ROOT / "data/pop_mart_americas_channels.csv").open(newline="") as source:
        for row in csv.DictReader(source):
            prior = int(row["revenue_2024_rmb_thousands"])
            current = int(row["revenue_2025_rmb_thousands"])
            breakdowns[row["scope"]].append(dict(channel=row["channel"], prior=prior,
                                                 current=current, growth=current - prior))

    online = next(row for row in breakdowns["all"] if row["channel"] == "Online")
    for scope, total in (("all", americas), ("online", online)):
        rows = breakdowns[scope]
        if any(sum(row[period] for row in rows) != total[period]
               for period in ("prior", "current")):
            raise ValueError(f"Americas channel revenue does not reconcile for {scope}")
        for row in rows:
            row["growth_share"] = row["growth"] / total["growth"]
    return breakdowns


def read_ip_revenue(financials):
    totals = {row["year"]: row["revenue_rmb_thousands"] for row in financials}
    prior_total, current_total = totals[2024], totals[2025]
    group_growth = current_total - prior_total
    rows = []
    with (ROOT / "data/pop_mart_ip_revenue.csv").open(newline="") as source:
        for row in csv.DictReader(source):
            prior = int(row["revenue_2024_rmb_thousands"])
            current = int(row["revenue_2025_rmb_thousands"])
            growth = current - prior
            rows.append(dict(ip=row["ip"], prior=prior, current=current, growth=growth,
                             prior_share=prior / prior_total, current_share=current / current_total,
                             growth_share=growth / group_growth))
    if (sum(row["prior"] for row in rows), sum(row["current"] for row in rows)) != (prior_total, current_total):
        raise ValueError("IP revenue does not reconcile to group revenue")

    monsters = next(row for row in rows if row["ip"] == "THE MONSTERS")
    remaining_prior = prior_total - monsters["prior"]
    remaining_current = current_total - monsters["current"]
    return {"rows": rows, "other_business_yoy": (remaining_current - remaining_prior) / remaining_prior}


def read_membership():
    with (ROOT / "data/pop_mart_members.csv").open(newline="") as source:
        return [
            dict(year=int(row["year"]),
                 registered_members_millions=float(row["registered_members_millions"]),
                 annual_member_repeat_rate=float(row["annual_member_repeat_rate"]),
                 source=row["source"])
            for row in csv.DictReader(source)
        ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "data/raw/online_retail.zip")
    parser.add_argument("--output", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    ensure_archive(args.archive)

    db = open_database()
    with db:
        db.executemany("INSERT INTO lines VALUES (?, ?, ?, ?, ?)", read_lines(args.archive))
    count, missing = db.execute("""
        SELECT count(*), count(*) - count(customer) FROM lines
    """).fetchone()
    if count != 541909:
        raise ValueError(f"Expected 541,909 UCI rows, received {count:,}")
    conflicts = db.execute("""
        SELECT invoice FROM sales GROUP BY invoice HAVING count(DISTINCT customer) > 1 LIMIT 1
    """).fetchone()
    if conflicts:
        raise ValueError(f"Multiple customers on invoice {conflicts[0]}")
    data = aggregate(db)
    data["quality"] = {"raw_rows": count, "missing_customer_rows": missing}
    data["financials"] = read_financials()
    data["regions"] = read_regions(data["financials"])
    data["americas_channels"] = read_americas_channels(data["regions"])
    data["ip_revenue"] = read_ip_revenue(data["financials"])
    data["membership"] = read_membership()
    args.output.mkdir(parents=True, exist_ok=True)
    for metric in METRICS:
        rows = data[metric]
        with (args.output / f"{metric}.csv").open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    (args.output / "metrics.json").write_text(json.dumps(data, indent=2) + "\n")
    template = (ROOT / "docs/dashboard.template.html").read_text()
    (args.output / "dashboard.html").write_text(template.replace("__METRICS__", json.dumps(data)))
    print(f"Processed {count:,} rows. Dashboard: {args.output / 'dashboard.html'}")


if __name__ == "__main__":
    main()
