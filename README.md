# Quick-Commerce Fashion: Hub Assortment, Size Availability & PRD

![ci](https://github.com/adityaaviero47/quick-commerce-size-availability/actions/workflows/ci.yml/badge.svg)

**The question:** if a fashion brand runs a 60-minute delivery hub in Bengaluru, which sizes should the hub stock, and how should the product page promise "60 minutes" without breaking that promise?

**The data:** 128,975 real Amazon.in order lines from one Indian apparel brand (kurtas, sets, western dresses), Mar 31 – Jun 29, 2022, with style, size, SKU, pin code, order status and fulfilment type. It's public: the Kaggle "E-Commerce Sales Dataset", downloaded by `get_data.sh` from a GitHub copy with its checksum verified.

## Findings

### 1. Bengaluru demand is concentrated by place, not by product (`src/demand.py`)
- Bengaluru (pin codes 560xxx) is the brand's **top city**: 13,110 order lines across 1,042 styles and 107 pin codes.
- **44 of 107 pin codes** carry 80% of non-cancelled demand, which is a good fit for a hub serving a limited zone.
- Products are long-tail: **552 SKU-sizes** make up 50% of demand and **1,748** make up 80%.
- **25.7% of June Bengaluru order lines** were for a SKU-size never ordered in Bengaluru in April–May, though only 3.2% were for a new style. Local history alone can't stock a hub, but the size pattern of the national catalogue can.

### 2. Stock the hub by size, using national demand (`src/assortment.py`)
**Backtest setup:**
- Rank SKU-sizes on April–May only, then measure the share of June Bengaluru order lines whose exact style **and** size would have been in the hub.
- The national-prior weight is chosen on a separate validation split (April → May), so June is never used for tuning.

| Hub slots (SKU-sizes) | Top styles, all sizes | Local demand only | **Size-level + national prior** | Perfect foresight |
|---|---|---|---|---|
| 500 | 35.1% | 34.6% | **35.2%** | 54.6% |
| 1,000 | 47.8% | 46.4% | **50.7%** | 74.8% |
| 1,500 | 58.4% | 54.5% | **62.4%** | 88.4% |
| 2,000 | 65.7% | 60.6% | **69.2%** | 100% |
| 3,000 | 77.4% | 73.2% | **81.1%** | 100% |

- To match the size-level hub at 1,000 slots, the "top styles in every size" rule needs **1,140 slots**, so the size-level hub uses **12% fewer slots** for the same coverage.
- Ranking on Bengaluru data alone does worse than both, because local data is too thin per size.
- **The catch:** a size-level hub carries only some sizes of many styles. **23.2%** of June order lines on a style the hub carries were for a size the hub didn't carry. A badge set per style would mislead those shoppers, which is why the PRD sets the badge **per size**.

### 3. The promise logic, tested against acceptance criteria (`src/availability.py`, `tests/`)
- `PRD.md` has the problem statement, 6 user stories, 8 acceptance criteria, a test plan, an A/B launch plan and post-launch metrics.
- Each acceptance criterion is an automated `pytest` test that runs in GitHub Actions on every push:
  - per-size badge
  - fallback to standard delivery
  - 1-unit stock buffer
  - reserved and damaged units excluded
  - pin-code service area
  - 21:00 cutoff
  - "some sizes" vs "all sizes" listing tile

### 4. KPIs rebuilt in SQL (`src/sql_kpis.py`)
- Cancellation rate by fulfilment type, Bengaluru volume and the pin codes behind 80% of demand are rebuilt in SQLite with CTEs and window functions.
- The script asserts they match pandas exactly.
- Seller-fulfilled lines cancel at **17.5%** vs **12.8%** for marketplace-fulfilled ones (Bengaluru: 14.4% vs 10.7%). This is an association: fulfilment type also differs in delivery speed (Standard vs Expedited).

## Run it
```bash
pip install -r requirements.txt
bash get_data.sh
python src/demand.py && python src/assortment.py && python src/sql_kpis.py
python -m pytest -q        # 10 tests
```

## Honest limits
- **Not Snitch's data.** It's one women's ethnic-wear brand on one marketplace, so the method transfers but the numbers won't.
- **Censored demand.** "Demand" means non-cancelled order lines. Sizes that were out of stock show up as low demand, so the real long tail is likely worse.
- **Slots, not depth.** Hub capacity is counted in SKU-size slots. Unit depth per size, store-as-hub stock and replenishment aren't modelled.
- **Pin codes stand in for Bengaluru.** There's no geodata, so service radius and rider time aren't modelled.
- **One snapshot not used.** The dataset's stock snapshot has an unknown date, so I didn't use it for any claim.
- **Short backtest.** It covers one city and one test month (3,691 June lines), so gaps of 1–3 points are directional.
