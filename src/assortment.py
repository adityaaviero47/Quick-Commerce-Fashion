"""Step 2: which SKU-sizes should a 60-minute Bengaluru hub stock?

Backtest: rank SKU-sizes on Apr-May demand only, then measure what share of June
Bengaluru order lines the hub could have served (exact style AND size in stock).
"""
import json
import numpy as np
from data import load, demand, SPLIT, RES

VAL_SPLIT = "2022-05-01"  # tune on Apr -> May, then refit on Apr-May and test on June
ALPHAS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
SLOTS = [500, 1000, 1500, 2000, 3000]


def style_first(train_blr, sizes_of_style, k):
    """Common default: take the best-selling styles and stock every size."""
    hub = []
    for style in train_blr.groupby("Style").size().sort_values(ascending=False).index:
        sz = sizes_of_style[style]
        if len(hub) + len(sz) > k:
            break
        hub += sz
    return hub


def size_level(train_blr, train_all, k, alpha):
    """Rank each SKU-size: local Bengaluru demand plus a national prior; last 4 weeks count x2."""
    recent = train_all.date.max() - np.timedelta64(27, "D")
    w_loc = np.where(train_blr.date >= recent, 2.0, 1.0)
    w_nat = np.where(train_all.date >= recent, 2.0, 1.0)
    loc = train_blr.assign(w=w_loc).groupby("SKU").w.sum()
    nat = train_all.assign(w=w_nat).groupby("SKU").w.sum()
    score = loc.reindex(nat.index).fillna(0) + alpha * nat / nat.sum() * w_loc.sum()
    return list(score.sort_values(ascending=False).index[:k])


def coverage(hub, test):
    return float(test.SKU.isin(set(hub)).mean())


def main():
    df = load()
    dm = demand(df)
    sizes_of_style = df.groupby("Style").SKU.apply(lambda x: sorted(set(x)))
    tr_all = dm[dm.date < SPLIT]
    blr = dm[dm.is_blr]
    tr, te = blr[blr.date < SPLIT], blr[blr.date >= SPLIT]
    # choose alpha on a validation month that never touches June
    v_tr_all = dm[dm.date < VAL_SPLIT]
    v_tr = blr[blr.date < VAL_SPLIT]
    v_te = blr[(blr.date >= VAL_SPLIT) & (blr.date < SPLIT)]
    val = {a: round(np.mean([coverage(size_level(v_tr, v_tr_all, k, a), v_te) for k in SLOTS]), 4) for a in ALPHAS}
    alpha = max(val, key=val.get)
    rows = []
    for k in SLOTS:
        a = style_first(tr, sizes_of_style, k)
        b = size_level(tr, tr_all, k, alpha)
        local_only = list(tr.groupby("SKU").size().sort_values(ascending=False).index[:k])
        oracle = list(te.groupby("SKU").size().sort_values(ascending=False).index[:k])
        rows.append({"slots": k, "style_first": round(coverage(a, te), 4),
                     "local_only": round(coverage(local_only, te), 4),
                     "size_level": round(coverage(b, te), 4),
                     "oracle_ceiling": round(coverage(oracle, te), 4)})
    # slots the style-first rule needs to match size-level at 1,000 slots
    target = next(r["size_level"] for r in rows if r["slots"] == 1000)
    need = next(k for k in range(1000, 4000, 10) if coverage(style_first(tr, sizes_of_style, k), te) >= target)
    # mis-promise if the 60-min badge were set per style instead of per size
    hub = set(size_level(tr, tr_all, 1000, alpha))
    hub_styles = set(dm[dm.SKU.isin(hub)].Style)
    on_style = te[te.Style.isin(hub_styles)]
    mispromise = float((~on_style.SKU.isin(hub)).mean())
    out = {"validation_mean_coverage_by_alpha": val, "chosen_alpha": alpha,
           "train_lines": len(tr), "test_lines": len(te), "backtest": rows,
           "style_first_slots_to_match_size_level_1000": need,
           "slot_saving_pct": round(1 - 1000 / need, 4),
           "style_level_badge_mispromise_rate": round(mispromise, 4),
           "share_of_june_lines_on_hub_styles": round(len(on_style) / len(te), 4)}
    json.dump(out, open(RES / "assortment.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
