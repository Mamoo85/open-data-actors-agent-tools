"""ONE real run (costs a few cents). NOT part of CI.

    set APIFY_TOKEN=...   (or this script falls back to C:\\gng\\dwa\\.env.apify_token if present)
    python tests/live_default_run.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

if not os.environ.get("APIFY_TOKEN"):
    f = Path(r"C:\gng\dwa\.env.apify_token")
    if f.exists():
        tok = f.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        os.environ["APIFY_TOKEN"] = tok.split("=", 1)[1].strip() if tok.upper().startswith("APIFY_TOKEN=") else tok

from open_data_actors import get_tool, run_actor  # noqa: E402

slug = "sanctions-screening"
inputs = get_tool(slug).sample_input
rows = run_actor(slug, max_items=10, **inputs)
print(f"{slug}: {len(rows)} rows")
if rows:
    print("first row keys:", sorted(rows[0])[:10])
sys.exit(0 if rows else 1)
