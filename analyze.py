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
