Paper download error (non-critical for computation): HTTPError: HTTP Error 403: Forbidden
Replication Notes
- Used RED dataset version 1.0 from Princeton-linked public Dropbox mirror.
- Parsed sheets: 1-Timing & location and 5-Participants.
- Constructed yearly revolution activity from startyear in [1900, 2014], matching the paper’s stated temporal scope.
- The paper reports n=395 episodes. The RED v1.0 included set contains 343 episodes with start year 1900-2014 and 2 episodes starting in 1899.
  This is the principal reproducibility mismatch that prevents exact replication of that point from public materials.
- Total included rows in workbook: 345; included and excluded totals in data description are 345 and 131 respectively.
- Sunspot source: SILSO monthly total sunspot number, aggregated to annual mean.
- World population proxy: World Bank WLD SP.POP.TOTL.
- Solar-window spec: threshold at local maxima minima, then ±2-year window in a robustness check.
- No inferential models/robust SEs were reported in the paper text extract available; this script focuses on replicating published threshold-style diagnostics only.

Quick interpretation guide:
- Solar threshold year count (annual>=threshold): 50
- Solar window year count (±2 years around local maxima): 50
- High revolution threshold: mean(revolution_index)+sd = 1.000001
- See contingency_analysis.csv for metric sensitivity across solar definitions.

Top sampled 1900-2014 year totals:
[
  {
    "year": 1900,
    "events": 2,
    "tnp": 32000.0,
    "episode": [
      {
        "revid": "352",
        "name": "War of the Golden Stool",
        "participants": 12000
      },
      {
        "revid": "348",
        "name": "Huizhou Uprising",
        "participants": 20000
      }
    ]
  },
  {
    "year": 1901,
    "events": 2,
    "tnp": 25000.0,
    "episode": [
      {
        "revid": "253",
        "name": "Liberating Revolution",
        "participants": 20000
      },
      {
        "revid": "341",
        "name": "Moro Wars",
        "participants": 5000
      }
    ]
  },
  {
    "year": 1903,
    "events": 1,
    "tnp": 25000.0,
    "episode": [
      {
        "revid": "283",
        "name": "Ilinden Revolt",
        "participants": 25000
      }
    ]
  },
  {
    "year": 1904,
    "events": 3,
    "tnp": 11000.0,
    "episode": [
      {
        "revid": "2",
        "name": "Herero Rebellion",
        "participants": 10000
      },
      {
        "revid": "381",
        "name": "Sasun Uprising",
        "participants": 1000
      },
      {
        "revid": "305",
        "name": "Vaccine Revolt",
        "participants": 0
      }
    ]
  },
  {
    "year": 1905,
    "events": 4,
    "tnp": 2040000.0,
    "episode": [
      {
        "revid": "5",
        "name": "1905 Revolution in Russia",
        "participants": 2000000
      },
      {
        "revid": "337",
        "name": "Argentinian Revolution of 1905",
        "participants": 0
      },
      {
        "revid": "3",
        "name": "Maji-Maji Rebellion",
        "participants": 20000
      }
    ]
  }
]