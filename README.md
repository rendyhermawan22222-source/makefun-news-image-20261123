# The World on Monday — 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/rendyhermawan22222-source/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/rendyhermawan22222-source/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-page newspaper front page summing up the world's news of Monday,
23 November 2026. The lead is NATO's emergency North Atlantic Council
session in Brussels after three Russian Kh-101 cruise missiles were
confirmed in Polish fields, with Poland summoning Russia's ambassador and
asking allies for stronger air defences. Below it, three picture stories:
Ukrainian strikes hitting the Kerch Bridge again, the AI sell-off that
dragged the Kospi down 3.3%, and rescuers digging through the collapsed
block of flats in Dymer, where the toll reached 15. Eight briefs round out
the day — the COP31 aftermath, Iran and the US naval blockade, four-way
Ukraine talks, Lebanon, Bangladesh, the death of Ian "Molly" Meldrum, the
Delta outage and the arrest of "El Chapo Isidro" — plus the numbers of the
day, a sport strip and a date check that keeps Sunday's news off the page.
The four illustrations are original painted artwork, not photographs.

## Files

- `entry.png` — the finished front page (1024×1024, PNG).
- `main.py` — verifies `entry.png` against its SHA-256 and copies it to
  the output directory.
- `build/compose.py` — draws the page from scratch with Pillow over the
  illustrations in `../art/`; re-running it reproduces `entry.png`
  byte for byte.
- `LICENSE` — MIT.

## Run it

```sh
# Re-draw the page (needs Pillow):
python3 build/compose.py

# Publish it the way the grader does:
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` refuses to copy the image if its hash does not match the value
recorded inside it, so a stale or altered `entry.png` can never slip
through. The entry is for the make.fun competition
[news-image-20261123](https://make.fun/c/news-image-20261123).
