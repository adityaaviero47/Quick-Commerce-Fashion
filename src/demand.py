"""Step 1: how concentrated is Bengaluru demand (pin codes, styles, sizes)?"""
import json
from data import load, demand, SPLIT, RES


def cum_share_rank(counts, share):
    c = counts.sort_values(ascending=False).cumsum() / counts.sum()
    return int((c < share).sum() + 1)


def main():
    df = load()
    blr_all = df[df.is_blr]
    dm = demand(df)
    blr = dm[dm.is_blr]
    city = df["ship-city"].str.upper().str.strip().value_counts()
    pins = blr.groupby("pin").size()
    skus = blr.groupby("SKU").size()
    tr, te = blr[blr.date < SPLIT], blr[blr.date >= SPLIT]
    out = {
        "order_lines": len(df),
        "date_range": [str(df.date.min().date()), str(df.date.max().date())],
        "top_city": city.index[0],
        "blr_order_lines": len(blr_all),
        "blr_styles": int(blr_all.Style.nunique()),
        "blr_skus": int(blr_all.SKU.nunique()),
        "blr_pin_codes": int(blr_all.pin.nunique()),
        "blr_pins_for_80pct_demand": cum_share_rank(pins, 0.8),
        "blr_skus_for_50pct_demand": cum_share_rank(skus, 0.5),
        "blr_skus_for_80pct_demand": cum_share_rank(skus, 0.8),
        "june_blr_lines_on_sku_unsold_in_blr_before": round(float((~te.SKU.isin(set(tr.SKU))).mean()), 4),
        "june_blr_lines_on_style_unsold_in_blr_before": round(float((~te.Style.isin(set(tr.Style))).mean()), 4),
        "size_mix_blr": blr.Size.value_counts(normalize=True).round(3).to_dict(),
        "cancel_rate_by_fulfilment": df.groupby("Fulfilment").cancelled.mean().round(4).to_dict(),
        "cancel_rate_by_fulfilment_blr": blr_all.groupby("Fulfilment").cancelled.mean().round(4).to_dict(),
        "cancel_rate_overall": round(float(df.cancelled.mean()), 4),
    }
    json.dump(out, open(RES / "demand.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
