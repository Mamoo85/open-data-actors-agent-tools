"""Regenerate src/open_data_actors/registry.json from catalog_src/catalog.json + sample_inputs.json.

Usage: python tools/generate_registry.py [catalog.json sample_inputs.json]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "catalog_src" / "catalog.json"
SAMPLES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "catalog_src" / "sample_inputs.json"
OUT = ROOT / "src" / "open_data_actors" / "registry.json"

# Secrets, webhooks, proxies and run-state storage are not exposed to agents.
SKIP = re.compile(r"apikey|token|webhook|proxy|statestore|statekey|deltastore|monitorname", re.I)
CAP = re.compile(r"^max(Results|Items|Stores|Domains|Sites|Pages|Reviews|Jobs|Urls|Matches|Links|Subdomains)", re.I)
TYPES = {"string", "integer", "number", "boolean", "array", "object"}


def field(spec):
    f = {"type": spec.get("type", "string")}
    if f["type"] not in TYPES:
        f["type"] = "string"
    for k in ("enum", "default", "minimum", "maximum"):
        if k in spec:
            f[k] = spec[k]
    items = spec.get("items") or {}
    if f["type"] == "array":
        f["items"] = items.get("type") if items.get("type") in {"string", "integer", "number", "boolean"} else "any"
    f["description"] = " ".join((spec.get("description") or spec.get("title") or "").split())[:400]
    return f


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    samples = json.loads(SAMPLES.read_text(encoding="utf-8"))
    tools = []
    for a in catalog:
        props = a["input"].get("properties", {})
        fields = {k: field(v) for k, v in props.items() if not SKIP.search(k)}
        required = [r for r in (a["input"].get("required") or []) if r in fields]
        sample = {k: v for k, v in samples[a["slug"]].items() if k in fields}
        caps = {k: sample[k] for k in sample if CAP.match(k) and isinstance(sample[k], int)}
        tools.append({
            "slug": a["slug"],
            "tool_name": a["slug"].replace("-", "_"),
            "title": a["title"],
            "description": " ".join(a["description"].split()),
            "url": f"https://apify.com/transparent_meteorite/{a['slug']}",
            "required": required,
            "fields": fields,
            "caps": caps,
            "sample_input": sample,
        })
    OUT.write_text(json.dumps({"actor_owner": "transparent_meteorite", "tools": tools}, indent=1), encoding="utf-8")
    print(f"wrote {len(tools)} tools -> {OUT}")


if __name__ == "__main__":
    main()
