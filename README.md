# Yasso 800s and the power law of running records

Code and data behind the blog post
[Exploring the science behind the Yasso 800](https://andyreagan.com/2019-08-17-yasso.html)
(August 2019).

The post fits a power law, `pace = a * distance^b`, to men's running world
records from 100 m to 100 km, and uses it to check the Yasso 800 rule
(average time for 10 x 800 m in min:sec = marathon time in h:min).
Result: `pace = 17.85 * distance^(-0.1144)` (pace in m/s, distance in m).

## Quick start

```sh
uv run fit.py
```

This prints every data point, whether it was used in the fit, and the fitted
coefficients. The original exploratory notebooks are also here
(`uv run jupyter lab`), but `fit.py` is the shortest path to the numbers.

## Files

| File | What it is |
|------|------------|
| `fit.py` | Standalone reproduction of the data prep and the fit |
| `process_wikipedia_data.ipynb` | Original data prep: parse the tables, assign distances, dedupe, filter |
| `yasso.ipynb` | Original analysis: plots, log-log OLS fit, Yasso ratio |
| `data/*.csv` | Wikipedia tables, converted with [wikitable2csv](https://wikitable2csv.ggor.de/) |
| `blog-post.markdown` | Original draft of the post |
| `*.png` | Figures from the post |

## Data

Source: [List of world records in athletics](https://en.wikipedia.org/wiki/List_of_world_records_in_athletics),
as it stood in mid-2019. Two tables are combined:

- `mens-IAAF-records.csv`: official IAAF (now World Athletics) records.
- `mens-nonIAAF-records.csv`: "world best performances", for distances with
  no official record (8 km, 15 km, 30 km, 50 m, 150 m, ...). Several of these
  are splits recorded *inside* a longer race. For example, the 8 km (21:51)
  is Deriba Merga's split during the 2011 RAK Half Marathon, and the 30, 35
  and 40 km times are splits from marathons.

The women's and indoor tables were downloaded but are not used.

## Method

1. Assign a distance in metres to each event (yards and miles converted;
   the one-hour run uses the distance covered in 3600 s).
2. Compute pace = distance / time (m/s).
3. Where several marks share a distance, keep the fastest.
4. **Exclude any point that is slower than some longer event.** Pace should
   fall as distance grows. Points that break that are either sprint starts
   (50 m, 60 m, 100 y, 100 m, which include accelerating from a standstill)
   or splits run inside a longer race (8 km, 30 km, 35 km, 40 km). These are
   the red points in the figures; 27 of 35 points are kept.
5. Fit `log10(pace) = log10(a) + b * log10(distance)` by ordinary least
   squares, giving a = 17.85, b = -0.1144 (R^2 = 0.96).

## Quirks, for anyone re-doing this

- The marathon is coded as 42,000 m (not 42,195 m) and the half as 21,000 m
  (not 21,097.5 m).
- Deduplication keeps the fastest mark, so the marathon point is Kipchoge's
  2:00:25 from the Breaking2 exhibition (Monza, 2017), not the official
  2:01:39 record of the time.
- The records are as of 2019; many have since fallen.

Fixing these, or using today's records or the women's tables, makes a good
exercise.

## License

Code: MIT. Data: from Wikipedia, CC BY-SA 4.0.
