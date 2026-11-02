"""Reproduce the power-law fit from the Yasso 800 blog post.

    uv run fit.py

Reads the Wikipedia record tables in data/, builds a pace-vs-distance table,
drops points that are slower than some longer event (the red points in the
post's figures), and fits log10(pace) = a + b * log10(distance) by OLS.
Same logic as process_wikipedia_data.ipynb + yasso.ipynb, in one script.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def parse_time(x):
    """'9.58' -> 9.58, '3:26.00' -> 206.0, '2:01:39' -> 7299.0; non-times -> None."""
    try:
        return sum(float(v) * 60**i for i, v in enumerate(reversed(str(x).split(":"))))
    except ValueError:
        return None


# Official IAAF records: the first 23 rows are the running events.
iaaf = pd.read_csv("data/mens-IAAF-records.csv").iloc[:23].copy()
iaaf["distance"] = [
    100, 200, 400, 800, 1000, 1500, 1609, 2000, 3000,
    5000, 5000, 5000, 10000, 10000, 10000, 20000, 21000,
    21285,  # one-hour run: distance covered in 3600 s
    25000, 30000, 42000, 42000, 100000,
]

# "World bests" (not official IAAF records): the first 28 rows are running.
# The 8 km here is Deriba Merga's 21:51 split en route in the 2011 RAK Half.
noniaaf = pd.read_csv("data/mens-nonIAAF-records.csv").iloc[:28].copy()
noniaaf["distance"] = [
    50, 60, 60, 100 * 0.9144, 100 * 0.9144, 100 * 0.9144, 150, 150, 200,
    220 * 0.9144, 220 * 0.9144, 300, 440 * 0.9144, 500, 600, 1609 * 2,
    5000, 8000, 15000, 10 * 1609, 20000, 25000, 30000, 35000, 40000,
    50000, 90000, 100000,
]

for df in (iaaf, noniaaf):
    df["seconds"] = df["Perf."].apply(parse_time)
iaaf["seconds"] = iaaf["seconds"].fillna(3600)  # the one-hour run

records = pd.concat([iaaf, noniaaf])
records["pace"] = records.distance / records.seconds  # m/s

# Keep the fastest performance at each distance.
records = records.sort_values(["distance", "seconds"]).drop_duplicates(["distance"])

# Keep a point only if it is faster than every longer event.
paces = records.pace.values
records["kept"] = [(p > paces[i + 1 :]).all() for i, p in enumerate(paces)]

pd.set_option("display.width", 200)
print(records[["Event", "Perf.", "distance", "seconds", "pace", "kept"]].to_string(index=False))

kept = records[records.kept].assign(
    logpace=lambda d: np.log10(d.pace),
    logdistance=lambda d: np.log10(d.distance),
)
fit = smf.ols("logpace ~ logdistance", data=kept).fit()
a, b = 10 ** fit.params.Intercept, fit.params.logdistance
print(f"\npace = {a:.2f} * distance^({b:.4f})   (pace in m/s, distance in m)")
print(f"R^2 = {fit.rsquared:.4f}, n = {len(kept)} of {len(records)} points")

marathon, five_miles = 42000, 5 * 1609
print(f"marathon pace / 5-mile pace = {(marathon / five_miles) ** b:.3f}  (Yasso implies 52.4/60 = {52.4/60:.3f})")
