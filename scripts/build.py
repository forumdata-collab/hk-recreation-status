#!/usr/bin/env python3
"""Build district pages from template + data JSON files."""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
DATA = os.path.join(ROOT, 'data')
FAC = os.path.join(DATA, 'facilities')
TEMPLATE = os.path.join(ROOT, 'template.html')

def build():
    # Clean dist
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    # Read template
    with open(TEMPLATE, 'r') as f:
        template = f.read()

    # Read districts config
    with open(os.path.join(DATA, 'districts.json'), 'r') as f:
        districts = json.load(f)

    # Build index.html (18-district dashboard)
    dashboard_items = []
    for d in districts:
        did = d['id']
        data_file = os.path.join(FAC, f'{did}.json')
        has_data = os.path.exists(data_file)
        status_icon = '🟢' if has_data else '⚪'
        label = d.get('name_zh_hant', did)
        dashboard_items.append(
            f'<a href="/{did}/" class="district-card">'
            f'<div class="district-name">{status_icon} {label}</div>'
            f'<div class="district-en">{d.get("name_en","")}</div>'
            f'</a>'
        )

    dashboard_html = f'''<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>香港18區康體設施狀態</title>
<style>
:root{{--brand:#1e3a8a;--bg:#F8FAFC;--card:#fff;--border:#E2E8F0;--text:#1E293B;--text2:#64748B}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","Microsoft JhengHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
.header{{text-align:center;padding:40px 16px 20px}}
.header h1{{font-size:1.5rem;color:var(--brand);margin-bottom:8px}}
.header p{{color:var(--text2);font-size:.9rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;max-width:960px;margin:0 auto;padding:0 16px 40px}}
.district-card{{display:block;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-decoration:none;color:var(--text);transition:transform .15s,box-shadow .15s}}
.district-card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.08)}}
.district-name{{font-weight:700;font-size:1rem;margin-bottom:4px}}
.district-en{{font-size:.8rem;color:var(--text2)}}
</style>
</head>
<body>
<div class="header">
<h1>🏊 香港18區康體設施狀態</h1>
<p>Hong Kong District Sports & Recreation Status</p>
</div>
<div class="grid">
{''.join(dashboard_items)}
</div>
</body>
</html>'''
    with open(os.path.join(DIST, 'index.html'), 'w') as f:
        f.write(dashboard_html)
    print(f'  index.html (dashboard)')

    # Build each district page
    for d in districts:
        did = d['id']
        data_file = os.path.join(FAC, f'{did}.json')
        if not os.path.exists(data_file):
            print(f'  {did}/ — skipped (no data)')
            continue

        with open(data_file, 'r') as f:
            facility_data = json.load(f)

        # Inject district metadata
        facility_data['district'] = d
        facility_data['categories'] = d.get('categories', [])

        # Build name lookup
        name_l10n = {}
        for key in ['pools', 'playrooms', 'sports_centres', 'tennis_courts',
                     'cycling_tracks', 'football_pitches', 'other_facilities', 'rvm']:
            for item in facility_data.get(key, []):
                item_id = item.get('id', '')
                if item_id:
                    name_l10n[item_id] = {
                        'zh': item.get('name', ''),
                        'en': item.get('nameEn', item.get('name', '')),
                        'cn': item.get('nameCn', item.get('name', ''))
                    }
        facility_data['_nameL10n'] = name_l10n

        # Inject data_sources text
        sources = d.get('data_sources', ['康文署'])
        facility_data['data_sources'] = ' · '.join(sources)

        # Inject into template
        page = template.replace(
            'var DD=window.DISTRICT_DATA||{pools:[],playrooms:[],libraries:[],rvm:[],sports_centres:[],tennis_courts:[],cycling_tracks:[],football_pitches:[],other_facilities:[],holidays:[],last_update:\'--\',data_sources:\'康文署\'};',
            f'var DD={json.dumps(facility_data, ensure_ascii=False)};'
        )

        out_dir = os.path.join(DIST, did)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            f.write(page)
        print(f'  {did}/index.html ({len(facility_data.get("pools",[]))} pools, {len(facility_data.get("playrooms",[]))} playrooms)')

    # Copy any static files
    static_dir = os.path.join(ROOT, 'static')
    if os.path.exists(static_dir):
        for item in os.listdir(static_dir):
            src = os.path.join(static_dir, item)
            dst = os.path.join(DIST, item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)

    print(f'\nBuild complete: {DIST}/')

if __name__ == '__main__':
    build()
