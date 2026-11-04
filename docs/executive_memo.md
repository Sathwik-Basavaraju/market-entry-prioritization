# Executive memo — Market-entry prioritization (illustrative model)

**To:** Decision-makers considering US metro entry
**Subject:** Shortlist from a weighted scoring model + Monte Carlo stability check
**Data warning:** All metro values are **illustrative, author-set values —
not official FRED/BLS/Census statistics** (see DATA_SOURCES.md). Treat this
memo as a method demonstration and a shortlist for further diligence, not
as an entry recommendation on real market data.

## Recommendation

Shortlist **Raleigh, NC; Austin, TX; and Nashville, TN** for deeper diligence
— in that order — and keep **Phoenix, AZ and Denver, CO** as the first
reserves. Do not treat the #3 slot as settled.

## Ranking (base weights: Demand 0.45, Labor cost 0.30, Competition 0.25)

| Rank | Metro | Score |
|---:|---|---:|
| 1 | Raleigh, NC | 0.8026 |
| 2 | Austin, TX | 0.6677 |
| 3 | Nashville, TN | 0.6264 |
| 4 | Phoenix, AZ | 0.6103 |
| 5 | Denver, CO | 0.6075 |
| 6 | Seattle, WA | 0.5643 |
| 7 | Atlanta, GA | 0.5219 |
| 8 | Dallas, TX | 0.4654 |
| 9 | Boston, MA | 0.4445 |
| 10 | Chicago, IL | 0.2962 |

## Stability finding (2,000 Monte Carlo runs, seed 42, weights perturbed)

- **Raleigh is the only uncontested pick: in the top 3 in 100.0% of runs,
  ranked #1 in every run (mean rank 1.0, range 1–1).**
- Austin is near-solid: top 3 in 89.2% of runs (mean rank 2.286).
- Nashville, the base #3, holds the top 3 in only **56.3%** of runs
  (mean rank 3.516, range 2–6) — Phoenix (25.75%), Denver (19.7%), and
  Seattle (9.05%) all displace it in a material share of runs.
- Consequently, **the base top-3 set is unchanged in only 45.9% of runs**.
  Read the shortlist as "Raleigh + Austin, plus one of Nashville / Phoenix /
  Denver depending on how the weights are ultimately set" — not as a fixed
  trio.

## Risks and assumptions

1. **Illustrative data is the dominant risk.** Real ACS/BLS values could
   reorder the middle of the table entirely; replace the dataset before
   any commitment.
2. **Weights are an author exercise, not a stakeholder vote.** If
   leadership weights labor cost or competition more heavily, the #3 slot
   (and the Phoenix/Denver order) changes first — that is exactly what the
   45.9% figure is warning about.
3. **Scores are relative within these 10 metros only** (min-max
   normalisation); they are not absolute attractiveness or profit forecasts.
4. **No revenue, margin, regulatory, or timing analysis** is included.
   Next step: validate Raleigh and Austin on real data, then run a
   commercial case (pricing, hiring, occupancy) for the surviving metros.
