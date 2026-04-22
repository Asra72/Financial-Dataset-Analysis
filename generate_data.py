import pandas as pd
import random
import numpy as np

random.seed(3)

assets = [
    ("A01", "Solar Energy Fund",       "Renewable"),
    ("A02", "Wind Power Index",         "Renewable"),
    ("A03", "Palm Oil Equity",          "Commodities"),
    ("A04", "Agricultural Bond",        "Fixed Income"),
    ("A05", "Biomass ETF",              "Renewable"),
    ("A06", "Crude Oil Futures",        "Commodities"),
    ("A07", "Green Infrastructure",     "Renewable"),
    ("A08", "Timber REIT",              "Commodities"),
    ("A09", "Carbon Credit Fund",       "Renewable"),
    ("A10", "Emerging Markets Bond",    "Fixed Income"),
]

periods = ["Q1-2022","Q2-2022","Q3-2022","Q4-2022",
           "Q1-2023","Q2-2023","Q3-2023","Q4-2023"]

rows = []
for asset_id, name, category in assets:
    start = round(random.uniform(50000, 200000), 2)
    for period in periods:
        end = round(start * (1 + random.uniform(-0.08, 0.12)), 2)
        true_return = round((end - start) / start * 100, 2)
        rows.append([asset_id, name, category, period, start, end, true_return])
        start = end

df = pd.DataFrame(rows, columns=[
    "asset_id","name","category","period",
    "start_value","end_value","reported_return_pct"
])

bad_return_idx = df.sample(4, random_state=5).index
for i in bad_return_idx:
    df.loc[i, "reported_return_pct"] = round(df.loc[i, "reported_return_pct"] + random.choice([-8.5, 12.3, -3.1, 7.7]), 2)

gap_idx = df[(df["asset_id"] == "A05") & (df["period"] == "Q3-2022")].index[0]
df.loc[gap_idx, "start_value"] = round(df.loc[gap_idx, "start_value"] * 1.15, 2)

mask = (df["asset_id"] == "A03") & (df["period"].isin(["Q1-2023","Q2-2023","Q3-2023","Q4-2023"]))
df.loc[mask, "category"] = "Renewable"

idx2 = df[(df["asset_id"] == "A08") & (df["period"] == "Q4-2022")].index[0]
df.loc[idx2, "end_value"] = round(df.loc[idx2, "end_value"] * 10, 2)

df.to_csv("data/portfolio_raw.csv", index=False)
print(f"saved {len(df)} rows")
