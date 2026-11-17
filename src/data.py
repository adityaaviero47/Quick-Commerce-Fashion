"""Load and clean the order report. One row = one order line (one SKU-size)."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "amazon_sale_report.csv"
BLR_PREFIX = 560          # Bengaluru pin codes are 560xxx
SPLIT = "2022-06-01"      # train on Apr-May, test on June (time split, no peeking)
RES = Path(__file__).resolve().parents[1] / "results"


def load(path=DATA) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["Date"], format="%m-%d-%y")
    df["pin"] = df["ship-postal-code"].fillna(0).astype(int)
    df["is_blr"] = df["pin"] // 1000 == BLR_PREFIX
    df["cancelled"] = df["Status"].eq("Cancelled")
    return df


def demand(df: pd.DataFrame) -> pd.DataFrame:
    """Order lines that were not cancelled: the demand a hub has to serve."""
    return df[~df["cancelled"]]
