#!/usr/bin/env python3
"""Extract JS data from we1co.me HTML files into JSON."""
import json, re, os

SK_VARS = ["FACILITIES", "PLAYROOMS", "LIBRARIES", "RVM_FACILITIES", "HK_HOLIDAYS"]
SK_KEY_MAP = {"FACILITIES": "pools", "RVM_FACILITIES": "rvm", "HK_HOLIDAYS": "holidays"}

KT_VARS = ["POOLS", "PLAYROOMS", "SPORTS_CENTRES", "TENNIS_COURTS",
           "CYCLING_TRACKS", "FOOTBALL_PITCHES", "OTHER_FACILITIES", "HK_HOLIDAYS"]
KT_KEY_MAP = {"HK_HOLIDAYS": "holidays"}


def extract_js_block(html, var_name):
    """Find const VARNAME=<value>; and return the raw value text."""
    # Match: const VARNAME= then capture everything until };\n or ];\n or "];\n
    pattern = rf"const {var_name}\s*=\s*"
    m = re.search(pattern, html)
    if not m:
        return None
    start = m.end()
    # Value is either [...] or "...";  Find matching bracket/quote
    if html[start] == '"':
        end = html.index('";', start) + 1
        return html[start:end]
    elif html[start] == '[':
        depth = 0
        i = start
        while i < len(html):
            if html[i] == '[':
                depth += 1
            elif html[i] == ']':
                depth -= 1
                if depth == 0:
                    return html[start:i+1]
            i += 1
    return None


def js_to_json(raw):
    """Convert JS object notation to valid JSON."""
    s = raw
    # Replace undefined → null
    s = re.sub(r'\bundefined\b', 'null', s)
    # Quote unquoted object keys: word-start chars before :
    # Match: {key: or ,key:  where key is a JS identifier
    s = re.sub(r'([{,])\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', s)
    # Remove trailing commas before ] or }
    s = re.sub(r',\s*([}\]])', r'\1', s)
    return s


def extract_var(html, var_name):
    raw = extract_js_block(html, var_name)
    if raw is None:
        return None
    if raw.startswith('['):
        converted = js_to_json(raw)
        return json.loads(converted)
    elif raw.startswith('"'):
        return json.loads(js_to_json(raw))
    return raw


def extract_last_update(html):
    m = re.search(r"const LAST_UPDATE\s*=\s*'([^']+)'", html)
    return m.group(1) if m else ""


def normalize_pool_sessions(pools):
    """For SK pools: convert schedule.summer to sessions array of time strings."""
    for p in pools:
        if "sessions" not in p and "schedule" in p:
            sched = p["schedule"]
            if isinstance(sched, dict) and "summer" in sched:
                p["sessions"] = [s["time"] for s in sched["summer"]]
                del p["schedule"]  # remove after extracting
            elif "sessions" not in p:
                p["sessions"] = []
    return pools


def process_html(path, var_names, key_map=None, pool_var=None, output_path=None, data_sources=None):
    key_map = key_map or {}
    with open(path, encoding="utf-8") as f:
        html = f.read()

    data = {}
    for v in var_names:
        out_key = key_map.get(v, v.lower())
        data[out_key] = extract_var(html, v)

    if pool_var:
        pool_key = key_map.get(pool_var, pool_var.lower())
        if pool_key in data:
            data[pool_key] = normalize_pool_sessions(data[pool_key])

    data["last_update"] = extract_last_update(html)
    data["data_sources"] = data_sources or []

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_path}: {len(json.dumps(data))} bytes")
    return data


# SK (西貢區)
sk = process_html(
    "/home/ubuntu/we1co.me/index.html",
    SK_VARS,
    key_map=SK_KEY_MAP,
    pool_var="FACILITIES",
    output_path="/home/ubuntu/hk-recreation-status/data/facilities/sk.json",
    data_sources=["康文署", "環保署"],
)

# KT (觀塘區)
kt = process_html(
    "/home/ubuntu/we1co.me/kt.html",
    KT_VARS,
    key_map=KT_KEY_MAP,
    pool_var="POOLS",
    output_path="/home/ubuntu/hk-recreation-status/data/facilities/kt.json",
    data_sources=["康文署", "觀塘區議會"],
)

# Quick validation
for name, d in [("sk", sk), ("kt", kt)]:
    print(f"\n=== {name.upper()} ===")
    for k, v in d.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
        else:
            print(f"  {k}: {v}")
