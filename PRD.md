# PRD: Size-level "60-min" delivery badge for a Bengaluru quick-commerce hub

**Status:** draft for review · **Owner:** Product · **Partners:** Design, Engineering, Supply Chain, Store Ops, CX

## 1. Problem statement
Shoppers in a 60-minute delivery zone see a product they like, but a promise set **per style** can't tell them whether **their size** can actually arrive in 60 minutes. In the backtest (README, step 2), with the hub stocked by the size-level ranking, **23.2%** of June Bengaluru order lines for a style the hub carries were for a size the hub did **not** carry. A style-level badge would have broken the promise on roughly 1 in 4 of those orders, which means cancellations, CX tickets and lost trust in the 60-min promise.

A hub can only hold a few thousand SKU-sizes, and demand is long-tail (552 SKU-sizes make up 50% of Bengaluru demand and 1,748 make up 80%). So the product has to be honest about what is fast and what isn't.

## 2. Goals and non-goals
**Goals**
- The 60-min promise is shown only where it can be kept: per size, per pin code, before the cutoff.
- Grow the share of hub-zone orders delivered in 60 minutes without raising cancellations.

**Non-goals (v1)**
- Changing store replenishment or the hub assortment itself. The assortment ranking in `src/assortment.py` is an input to Planning, not part of this feature.
- Showing exact delivery-time estimates.

## 3. Users and user stories
| # | As a… | I want… | So that… |
|---|-------|---------|----------|
| US-1 | shopper in a hub pin code | to see on the product page whether my selected size arrives in 60 min | I can order for tonight with confidence |
| US-2 | shopper whose size isn't at the hub | to still see a clear standard delivery date | I can decide without being misled |
| US-3 | shopper browsing listings | to see whether a product is fast in all sizes or only some | I don't open products that can't arrive in time in my size |
| US-4 | shopper ordering late at night | to know the order will arrive the next morning | my expectations match reality |
| US-5 | store/hub ops lead | reserved and damaged units excluded from the promise | the hub isn't asked to ship stock it can't pick |
| US-6 | category manager | a weekly list of sizes most often searched but not 60-min | I can bring the right sizes into the hub |

## 4. Requirements and acceptance criteria
Each criterion has a matching automated test in `tests/test_availability.py`.

| ID | Requirement | Acceptance criterion |
|----|-------------|----------------------|
| AC-1 | 60-min shows per size | **Given** a hub pin code before 21:00, **when** the selected size has ≥1 sellable unit at the hub, **then** the page shows "60-min" |
| AC-2 | Fallback when the size isn't at the hub | **Given** the size has no hub record, **then** the page shows the standard delivery date, never "60-min" |
| AC-3 | Stock-accuracy buffer | **Given** on-hand = 1, **then** the size is not promised (1 unit is held back) |
| AC-4 | Only sellable stock counts | **Given** reserved or damaged units, **then** sellable = on-hand − reserved − damaged − buffer |
| AC-5 | Service area | **Given** a pin code outside the hub zone, **then** the page shows standard delivery |
| AC-6 | Cutoff | **Given** an order after 21:00, **then** the page shows "tomorrow morning" |
| AC-7 | Honest listing tile | **Given** some sizes qualify and some don't, **then** the tile says "60-min in some sizes" |
| AC-8 | "All sizes" claim | **Given** every listed size qualifies, **then** the tile says "60-min in all sizes"; if none qualify, no badge |

## 5. Test plan
- **Unit:** `pytest` runs AC-1 to AC-8 on every push (GitHub Actions).
- **Pre-launch QA:** test each AC on staging with seeded hub stock across 3 pin codes (in zone, edge of zone, out of zone) and 2 times (before and after cutoff), on Android, iOS and web. Log each failure in the bug tracker with steps, expected vs actual, and severity.
- **Data check:** for one day, compare badge impressions to hub stock snapshots. Every "60-min" impression must map to a sellable unit.

## 6. Launch plan
1. Internal dogfood in 2 hub pin codes for 1 week.
2. **A/B test** in the hub zone, split by user: control keeps the current style-level message, treatment gets the size-level badge.
3. Roll out to all hub pin codes if the guardrails hold, then repeat for each new hub.

## 7. Metrics
- **Primary:** share of hub-zone orders delivered within 60 minutes.
- **Guardrails:**
  - **Promise-break rate:** orders shown "60-min" but delivered late or cancelled.
  - Cancellation rate. For context in this dataset: 17.5% for seller-fulfilled vs 12.8% for marketplace-fulfilled lines, an association, not a cause.
  - Product-page conversion.
  - CX tickets about delivery time.
- **Post-launch feedback:** weekly review of promise breaks by root cause (stock mismatch, rider delay, picking delay), the US-6 size-gap list for Planning, and a short in-app survey on delivery-time clarity.

## 8. Risks and open questions
- **Stock accuracy at stores used as hubs:** is the 1-unit buffer enough? Tune it after 2 weeks using the promise-break rate.
- **Peak hours:** should the cutoff move earlier at peak times when rider supply is short?
- **Assortment changes:** how often can the hub assortment change without causing ops churn (weekly vs fortnightly)?
