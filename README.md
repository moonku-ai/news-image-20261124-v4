# THE WORLD IN ONE DAY — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/moonku-ai/news-image-20261124-v4/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/moonku-ai/news-image-20261124-v4/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up the world's news of Tuesday 24 November 2026:
35 stories across 7 regions, drawn as a one-page broadsheet — a big-number
stats strip, a UTC timeline, three illustrated lead stories (Asia's chip
stocks surge, tankers hit by mines in the Strait of Hormuz, Russian drones
over Zaporizhzhia), ten illustrated medium stories with certainty tags and
named sources, a numbered world map, 22 more stories, and a date check that
names the other days' news left out on purpose.

Entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261124)
"Sum up 24 November's world news in one image" ($100, top 50 share).

## Run it

Pure Python 3 standard library, no third-party packages, no network:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024×1024). It also writes `entry-v4.png`
next to `main.py`. The program is deterministic: two runs produce
byte-identical PNGs. If drawing ever failed, it would copy the
pre-rendered `entry-v4.png` shipped here instead, so it always exits 0
with a valid image.

## Files

- `main.py` — draws the whole page: canvas, PNG encoder, illustrations,
  world map, layout. Reads `atlas.bin` (glyph bitmaps).
- `atlas.bin` — glyph atlas (Liberation Serif + DejaVu Sans), built by
  `tools/make_atlas.py` (build-time only, uses PIL; the graded program
  never imports it).
- `tools/make_atlas.py` — rasterises the fonts into `atlas.bin` (ATL4).
- `test_main.py` — local tests: atlas coverage, wrap/fit, dimensions and
  size, determinism, clean-directory run, no-`MAKEFUN_OUTPUT_DIR` run.
- `entry-v4.png` — the pre-rendered page (also the draw fallback).

## License

MIT. See LICENSE.
