# Portfolio data — inconsistency detection

Part of a multi-period portfolio analysis project. Before running any
return calculations or category-level comparisons, I wanted to check
whether the dataset was internally consistent.

It wasn't. Found four types of problems.

---

## Dataset

80 rows covering 10 assets tracked across 8 quarters (2022–2023).
Each row has a start value, end value, and a reported return percentage.
Assets are categorised as Renewable, Commodities, or Fixed Income.

---

## Checks run

**1. Reported return vs calculated return**

The return percentage in each row should match
(end value - start value) / start value * 100.
Flagged any row where the reported figure differed from that by more
than 0.1 percentage points.

Found 5 rows with mismatches. The worst was A08 (Timber REIT) in Q4-2022
where the reported return was 8.7% but the actual change from start to end
was over 1000%. That suggested the end value itself was wrong, not just
the return figure.

**2. Value chain continuity**

The end value of one quarter should equal the start value of the next
quarter for the same asset. If there's a gap, the data was probably
assembled from different versions or sources.

Found 2 breaks — both involving A05 (Biomass ETF) and A08 (Timber REIT),
which also showed up in check 1. The A08 break was clearly related to
the same bad end value.

**3. Category consistency**

Each asset should have the same category across all periods. Found one
asset (A03, Palm Oil Equity) listed as Commodities in 2022 and Renewable
in 2023. That may be a genuine reclassification but it needs to be
confirmed before using category-level aggregations.

**4. Outlier values**

Flagged any row where the end value was more than 3x the start value in
a single quarter. Found one — A08 Q4-2022 again, with an 11x jump.
Looks like a decimal was dropped somewhere.

---

## What can and can't be used

Fine:
- trend analysis for the 8 assets that had no issues
- period-level comparisons that don't depend on A08 or A05

Not until reviewed:
- any return calculation involving the 5 flagged rows
- category-level aggregations that include A03
- anything that depends on the Q4-2022 to Q1-2023 transition for A08

---

## Files

```
data/portfolio_raw.csv              the raw dataset
outputs/inconsistency_report.txt    full findings
outputs/portfolio_flagged.csv       cleaned copy with issues noted
scripts/generate_data.py            generates the raw file
scripts/check_inconsistencies.py    runs all four checks
```

---

## How to run

```bash
pip install pandas numpy

python scripts/generate_data.py
python scripts/check_inconsistencies.py
```

---

## Tools

Python, pandas
