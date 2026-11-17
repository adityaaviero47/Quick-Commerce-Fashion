"""Step 4: rebuild the launch KPIs in SQL (SQLite) and check they match pandas exactly."""
import json, sqlite3
from data import load, RES

SQL = """
WITH lines AS (
  SELECT Fulfilment AS fulfilment, Status = 'Cancelled' AS cancelled,
         CAST("ship-postal-code" AS INTEGER) / 1000 = 560 AS is_blr, pin, SKU AS sku
  FROM orders
),
blr_demand AS (
  SELECT pin, COUNT(*) AS n FROM lines WHERE is_blr AND NOT cancelled GROUP BY pin
),
pin_rank AS (
  SELECT pin, n, SUM(n) OVER (ORDER BY n DESC, pin ROWS UNBOUNDED PRECEDING) * 1.0
                 / SUM(n) OVER () AS cum_share
  FROM blr_demand
)
SELECT
  (SELECT ROUND(AVG(cancelled), 4) FROM lines WHERE fulfilment = 'Amazon')   AS cancel_amazon,
  (SELECT ROUND(AVG(cancelled), 4) FROM lines WHERE fulfilment = 'Merchant') AS cancel_merchant,
  (SELECT COUNT(*) FROM lines WHERE is_blr)                                    AS blr_lines,
  (SELECT COUNT(*) + 1 FROM pin_rank WHERE cum_share < 0.8)                  AS pins_for_80pct
"""


def main():
    df = load()
    con = sqlite3.connect(":memory:")
    df[["Fulfilment", "Status", "ship-postal-code", "pin", "SKU"]].to_sql("orders", con, index=False)
    row = con.execute(SQL).fetchone()
    sql = dict(zip(["cancel_amazon", "cancel_merchant", "blr_lines", "pins_for_80pct"], row))
    d = json.load(open(RES / "demand.json"))
    py = {"cancel_amazon": d["cancel_rate_by_fulfilment"]["Amazon"],
          "cancel_merchant": d["cancel_rate_by_fulfilment"]["Merchant"],
          "blr_lines": d["blr_order_lines"], "pins_for_80pct": d["blr_pins_for_80pct_demand"]}
    out = {"sql": sql, "pandas": py, "match": sql == py}
    json.dump(out, open(RES / "sql_kpis.json", "w"), indent=2)
    print(json.dumps(out, indent=2))
    assert out["match"], "SQL and pandas KPIs differ"


if __name__ == "__main__":
    main()
