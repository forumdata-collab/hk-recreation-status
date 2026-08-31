#!/usr/bin/env python3
"""Validate all JSON data files and district configs."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAC = os.path.join(ROOT, 'data', 'facilities')
DISTRICTS_FILE = os.path.join(ROOT, 'data', 'districts.json')

VALID_STATUSES = {'open', 'closed', 'partial', 'maintenance', 'temporary_closed', 'holiday', 'unknown'}
errors = []
warnings = []

def check(msg, ok=True, is_error=True):
    if not ok:
        (errors if is_error else warnings).append(msg)
        print(f'  ❌ {msg}')
    return ok

print('=== Validating districts.json ===')
with open(DISTRICTS_FILE) as f:
    districts = json.load(f)
print(f'  {len(districts)} districts found')

seen_ids = set()
for d in districts:
    did = d.get('id', '')
    check(f'District missing id: {d}', did)
    if did in seen_ids:
        check(f'Duplicate district id: {did}')
    seen_ids.add(did)
    check(f'District {did} missing name_zh_hant', 'name_zh_hant' in d)
    check(f'District {did} missing name_en', 'name_en' in d)
    check(f'District {did} missing categories', 'categories' in d)

print(f'\n=== Validating facility data files ===')
for fname in sorted(os.listdir(FAC)):
    if not fname.endswith('.json'):
        continue
    fpath = os.path.join(FAC, fname)
    did = fname.replace('.json', '')
    print(f'\n  --- {fname} ---')
    try:
        with open(fpath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        check(f'{fname}: invalid JSON: {e}')
        continue

    # Check required top-level keys
    for key in ['pools', 'playrooms', 'holidays', 'last_update']:
        check(f'{fname}: missing key "{key}"', key in data)

    # Validate pools
    seen_facility_ids = set()
    for pool in data.get('pools', []):
        fid = pool.get('id', '')
        check(f'{fname}: pool missing id', fid)
        if fid in seen_facility_ids:
            check(f'{fname}: duplicate pool id: {fid}')
        seen_facility_ids.add(fid)
        check(f'{fname}: pool {fid} missing name', 'name' in pool)
        check(f'{fname}: pool {fid} missing address', 'address' in pool)
        check(f'{fname}: pool {fid} missing sessions', 'sessions' in pool)

        # Validate sub-facilities
        for sf in pool.get('facilities', []):
            if 'name' not in sf:
                check(f'{fname}: pool {fid} sub-facility missing name')

    # Validate playrooms
    for pr in data.get('playrooms', []):
        prid = pr.get('id', '')
        check(f'{fname}: playroom missing id', prid)
        if prid in seen_facility_ids:
            check(f'{fname}: duplicate playroom id: {prid}')
        seen_facility_ids.add(prid)
        check(f'{fname}: playroom {prid} missing name', 'name' in pr)
        check(f'{fname}: playroom {prid} missing sessions', 'sessions' in pr)

    # Validate sports centres
    for sc in data.get('sports_centres', []):
        sid = sc.get('id', '')
        check(f'{fname}: sports centre missing id', sid)
        if sid in seen_facility_ids:
            check(f'{fname}: duplicate sports centre id: {sid}')
        seen_facility_ids.add(sid)

    print(f'  ✓ {fname}: {len(data.get("pools",[]))} pools, {len(data.get("playrooms",[]))} playrooms')

print(f'\n=== Summary ===')
if errors:
    print(f'  ❌ {len(errors)} errors')
    for e in errors:
        print(f'    - {e}')
    sys.exit(1)
else:
    print(f'  ✅ All checks passed')
    if warnings:
        print(f'  ⚠️  {len(warnings)} warnings')
