import json
import os
import re
import subprocess
import urllib.request
from urllib.error import HTTPError
from pathlib import Path

HOST = os.environ["INDEXNOW_HOST"]
KEY = os.environ["INDEXNOW_KEY"]
KEY_FILE = os.environ["INDEXNOW_KEY_FILE"]
BASE = f"https://{HOST}"

sitemap_text = Path("sitemap.xml").read_text(encoding="utf-8")
sitemap_urls = set(re.findall(r"<loc>(.*?)</loc>", sitemap_text))

try:
    diff = subprocess.check_output(["git", "diff", "--name-status", "HEAD^", "HEAD"], text=True).splitlines()
except Exception:
    diff = []

changes = []
for line in diff:
    parts = line.split("\t")
    if len(parts) >= 2:
        changes.append((parts[0], parts[-1]))

full_refresh_files = {"sitemap.xml", KEY_FILE, ".github/workflows/indexnow.yml", "scripts/indexnow.py"}
urls = set()

for status, path in changes:
    if path in full_refresh_files:
        urls.update(sitemap_urls)
        continue

    candidate = None
    parts = path.split("/")
    if path == "index.html" or "/" not in path:
        candidate = BASE + "/"
    elif parts[0] == "articles" and len(parts) > 1:
        candidate = f"{BASE}/articles/{parts[1]}/"
    elif parts[0] == "reader" and len(parts) > 1:
        candidate = f"{BASE}/reader/{parts[1]}/"
    else:
        candidate = BASE + "/"

    if candidate and (status.startswith("D") or candidate in sitemap_urls):
        urls.add(candidate)

if not urls:
    print("No public sitemap URLs changed; IndexNow submission skipped.")
    raise SystemExit(0)

payload = {
    "host": HOST,
    "key": KEY,
    "keyLocation": f"{BASE}/{KEY_FILE}",
    "urlList": sorted(urls),
}

request = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)

print("Submitting to IndexNow:")
for url in payload["urlList"]:
    print(" -", url)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        status = response.status
        print("IndexNow response:", status)
        if status not in (200, 202):
            raise SystemExit(f"Unexpected IndexNow response: {status}")
except HTTPError as error:
    body = error.read().decode("utf-8", errors="replace")
    print("IndexNow HTTP error:", error.code, body)
    raise
