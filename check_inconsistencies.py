import pandas as pd
import numpy as np

df = pd.read_csv("data/portfolio_raw.csv")

print(f"loaded {len(df)} rows")
print(f"assets: {df['asset_id'].nunique()}")
print(f"periods: {df['period'].nunique()}")
print()

notes = []

def log(msg):
    print(msg)
    notes.append(msg)


log("=== inconsistency check ===")
log("")


log("--- check 1: reported return vs calculated return ---")

df["calc_return"] = ((df["end_value"] - df["start_value"]) / df["start_value"] * 100).round(2)
df["return_diff"] = (df["reported_return_pct"] - df["calc_return"]).round(4)

wrong_returns = df[abs(df["return_diff"]) > 0.1].copy()

if len(wrong_returns) == 0:
    log("all reported returns match calculated returns")
else:
    log(f"rows where reported return doesn't match start/end values: {len(wrong_returns)}")
    log("")
    for _, row in wrong_returns.iterrows():
        log(f"  {row['asset_id']} ({row['name']}) — {row['period']}")
        log(f"    start: {row['start_value']}  end: {row['end_value']}")
        log(f"    reported return: {row['reported_return_pct']}%")
        log(f"    calculated return: {row['calc_return']}%")
        log(f"    difference: {row['return_diff']} percentage points")
        log("")

log("")


log("--- check 2: value chain continuity ---")

periods_ordered = ["Q1-2022","Q2-2022","Q3-2022","Q4-2022",
                   "Q1-2023","Q2-2023","Q3-2023","Q4-2023"]

chain_issues = []
for asset_id in df["asset_id"].unique():
    asset_df = df[df["asset_id"] == asset_id].set_index("period")
    for i in range(len(periods_ordered) - 1):
        p1 = periods_ordered[i]
        p2 = periods_ordered[i + 1]
        if p1 in asset_df.index and p2 in asset_df.index:
            end_p1   = asset_df.loc[p1, "end_value"]
            start_p2 = asset_df.loc[p2, "start_value"]
            diff = abs(end_p1 - start_p2)
            if diff > 0.01:
                chain_issues.append({
                    "asset": asset_id,
                    "name": asset_df.loc[p1, "name"],
                    "transition": f"{p1} -> {p2}",
                    "end_prev": end_p1,
                    "start_next": start_p2,
                    "gap": round(diff, 2)
                })

if len(chain_issues) == 0:
    log("value chain is continuous across all assets and periods")
else:
    log(f"chain breaks found: {len(chain_issues)}")
    log("")
    for issue in chain_issues:
        p1, p2 = issue["transition"].split(" -> ")
        log(f"  {issue['asset']} ({issue['name']}) — {issue['transition']}")
        log(f"    end of {p1}: {issue['end_prev']}")
        log(f"    start of {p2}: {issue['start_next']}")
        log(f"    gap: {issue['gap']}")
        log("")

log("")


log("--- check 3: category consistency per asset ---")

cat_changes = []
for asset_id in df["asset_id"].unique():
    cats = df[df["asset_id"] == asset_id]["category"].unique()
    if len(cats) > 1:
        cat_changes.append({
            "asset": asset_id,
            "name": df[df["asset_id"] == asset_id]["name"].iloc[0],
            "categories_found": list(cats)
        })

if len(cat_changes) == 0:
    log("all assets have consistent categories across periods")
else:
    log(f"assets with more than one category: {len(cat_changes)}")
    log("")
    for c in cat_changes:
        log(f"  {c['asset']} ({c['name']})")
        log(f"    categories found: {c['categories_found']}")
        asset_cats = df[df["asset_id"] == c["asset"]][["period","category"]]
        for _, row in asset_cats.iterrows():
            log(f"    {row['period']}: {row['category']}")
        log("")

log("")


log("--- check 4: unusually large single-period changes ---")

df["value_ratio"] = df["end_value"] / df["start_value"]
outliers = df[df["value_ratio"] > 3.0]

if len(outliers) == 0:
    log("no unusually large single-period value changes found")
else:
    log(f"rows where end value is more than 3x start value: {len(outliers)}")
    log("")
    for _, row in outliers.iterrows():
        log(f"  {row['asset_id']} ({row['name']}) — {row['period']}")
        log(f"    start: {row['start_value']}  end: {row['end_value']}")
        log(f"    ratio: {round(row['value_ratio'], 1)}x")
        log("")

log("")

log("=== summary ===")
total_issues = len(wrong_returns) + len(chain_issues) + len(cat_changes) + len(outliers)
log(f"total issues flagged: {total_issues}")
log("")
log("what the data can be used for after reviewing these issues:")
log("  - trend analysis for assets with no chain breaks is fine")
log("  - category-level aggregations should not include A03 until")
log("    the category change is resolved")
log("  - rows with wrong reported returns should not be used for")
log("    return calculations until the source is checked")
log("  - A08 Q4-2022 end value looks wrong — needs source review")

with open("outputs/inconsistency_report.txt", "w") as f:
    f.write("\n".join(notes))

df.drop(columns=["calc_return","return_diff","value_ratio"]).to_csv(
    "outputs/portfolio_flagged.csv", index=False
)
print()
print("saved: outputs/inconsistency_report.txt")
print("saved: outputs/portfolio_flagged.csv")
