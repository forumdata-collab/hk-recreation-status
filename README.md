# 🏊 香港18區康體設施狀態

**Hong Kong 18 District Leisure Facilities Status**

A data-driven, static single-page application that shows real-time operational status of leisure and sports facilities across all 18 districts of Hong Kong.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/hk-recreation-status.git
cd hk-recreation-status

# Build district pages
python3 scripts/build.py

# Validate data
python3 scripts/validate.py

# Serve locally
python3 -m http.server 8080 -d dist
# Open http://localhost:8080
```

## Architecture

```
template.html          ← Single HTML template (all rendering logic)
data/
  districts.json       ← 18 district configs
  facilities/
    sk.json            ← Sai Kung facility data
    kt.json            ← Kwun Tong facility data
scripts/
  build.py             ← Combines template + data → dist/
  validate.py          ← Validates all JSON files
dist/                  ← Generated output (GitHub Pages root)
  index.html           ← 18-district dashboard
  sk/index.html        ← Sai Kung page
  kt/index.html        ← Kwun Tong page
  ...
```

**One template → 18 districts → unlimited facilities → data-driven.**

## How to Add a New District

1. Create `data/facilities/{district_id}.json` (see Data Schema below)
2. Update `data/districts.json` — add the district entry with categories
3. Run `python3 scripts/build.py`
4. Push to GitHub → auto-deploys

Example for Shatin:
```json
{
  "pools": [...],
  "playrooms": [...],
  "holidays": [...],
  "last_update": "2026-08-31 20:00",
  "data_sources": ["康文署"]
}
```

## How to Add a New Facility

1. Edit the district's JSON file (e.g., `data/facilities/kt.json`)
2. Add a new entry to the appropriate category array
3. Run `python3 scripts/build.py`

## How to Add a New Category

1. Add the category to `template.html` — create a new `<section>` and render function
2. Add the category key to `CATEGORY_MAP` in the init code
3. Add category to the district's `categories` array in `districts.json`
4. Run `python3 scripts/build.py`

## How to Change Data Source

The system is designed for data-source independence. The JSON schema is normalized — any source that can populate the fields works:

- **Static JSON**: Current approach — manual/scraper writes JSON
- **Government API**: Build a scraper that outputs the same JSON format
- **Manual update**: Edit JSON files directly

The UI never directly calls any government API.

## Deployment (GitHub Pages)

The repo includes a GitHub Actions workflow (`.github/workflows/deploy.yml`):

1. Push to `main` branch
2. GitHub Actions runs `python3 scripts/build.py`
3. Deploys `dist/` to GitHub Pages

### Backward Compatibility

The existing `we1co.me` URLs continue to work:
- `https://we1co.me/` → Sai Kung (root)
- `https://we1co.me/kt` → Kwun Tong

New architecture: `/sk/`, `/kt/`, etc.

## Data Schema

### District Config (`data/districts.json`)

```json
{
  "id": "kt",
  "name_zh_hant": "觀塘區",
  "name_zh_cn": "观塘区",
  "name_en": "Kwun Tong District",
  "data_sources": ["康文署", "觀塘區議會"],
  "categories": ["swimming", "playroom", "sports_centre", "tennis", "cycling", "football", "other"]
}
```

### Facility Data (`data/facilities/{id}.json`)

```json
{
  "pools": [
    {
      "id": "ktswim",
      "name": "觀塘游泳池",
      "address": "九龍觀塘翠屏道2號",
      "addrEn": "2 Tsui Ping Road, Kwun Tong",
      "addrCn": "九龙观塘翠屏道 2 号",
      "phone": "2717 9022",
      "officialUrl": "https://www.lcsd.gov.hk/...",
      "sessions": ["06:30 - 12:00", "13:00 - 18:00", "19:00 - 22:00"],
      "closures": [...],
      "maintenance": [...],
      "cleaning": {"day": "三", "fallback": "五"},
      "facilities": [
        {"name": "主池", "spec": "50米 x 25米", "status": "open"}
      ]
    }
  ],
  "playrooms": [...],
  "libraries": [...],
  "rvm": [...],
  "sports_centres": [...],
  "tennis_courts": [...],
  "cycling_tracks": [...],
  "football_pitches": [...],
  "other_facilities": [...],
  "holidays": ["2026/01/01", "..."],
  "last_update": "2026-08-31 20:00",
  "data_sources": "康文署 · 環保署"
}
```

## Status System

| Status | CSS Class | Emoji | Description |
|--------|-----------|-------|-------------|
| Open | `.status-open` | 🟢 | Facility is operating normally |
| Closed | `.status-closed` | 🔴 | Facility is closed |
| Partial | `.status-partial` | 🟡 | Some sub-facilities are open |
| Maintenance | `.status-maint` | 🔧 | Under scheduled maintenance |
| Suspended | `.status-suspended` | ⚠️ | Temporarily suspended |
| Unknown | `.status-unknown` | ⚪ | Status unknown |

Status is **semantic** (CSS class + text), not color-only — accessible to screen readers and colorblind users.

## i18n

Three languages supported: 繁體中文, English, 简体中文. Language preference saved in `localStorage`. Also supports `?lang=en` query parameter.

## License

MIT
