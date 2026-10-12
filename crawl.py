"""Crawl the official MCP Registry into a local JSONL file.

The registry is paginated with an opaque cursor and caps `limit` at 100, so a
full pass is a few hundred round trips. Every record is written as one JSON
line, and the cursor is checkpointed, so an interrupted run resumes instead of
starting over.

Two passes are worth running, into two different files:

    # every published version, one record per version -- slow (a deep cursor
    # page takes ~60s) but it is what the version-churn figures need
    python crawl.py --out data/registry.jsonl --state data/cursor.txt

    # latest version only, filtered server-side -- ~1.6s per page, and this
    # is the stream the per-server statistics are computed from
    python crawl.py --out data/registry-latest.jsonl --state data/cursor-latest.txt \
        --version latest

Nothing here is specific to the analysis that follows: this step only records
what the registry says.
"""

from __future__ import annotations

import argparse
import http.client
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://registry.modelcontextprotocol.io/v0/servers"
LIMIT = 100  # the API rejects anything larger with a 422
TIMEOUT = 180  # a deep cursor page took 60s to answer; 60 would sit on the edge
RETRIES = 8  # a 90-minute crawl should not die on one dropped connection
UA = "mcp-census/0.1 (+https://github.com/bryand410)"

# What counts as a transient failure. This list is the whole point of the
# retry loop, and getting it wrong is expensive:
#
#   http.client.RemoteDisconnected inherits from ConnectionResetError, which is
#   an OSError. urllib.error.URLError is *also* an OSError, but the two are
#   siblings, not parent and child. Catching only URLError therefore misses the
#   single most likely failure on a long crawl -- the server closing the
#   connection mid-response -- and the run dies after 90 minutes of work.
#
# Catching OSError covers URLError, ConnectionResetError, RemoteDisconnected and
# plain socket timeouts; HTTPException covers a malformed status line. Only a
# genuinely unretryable error, or exhausting RETRIES, stops the crawl.
RETRYABLE = (OSError, http.client.HTTPException, json.JSONDecodeError)


def build_url(cursor: str | None, version: str | None, search: str | None) -> str:
    """Assemble one page URL.

    `version=latest` is not a client-side convenience: the registry filters
    server-side and answers in about a second, where the unfiltered list takes
    a minute per page once the cursor is deep. That is the whole reason the
    latest-version pass exists.
    """
    url = f"{BASE}?limit={LIMIT}"
    if version:
        url += "&version=" + urllib.parse.quote(version)
    if search:
        url += "&search=" + urllib.parse.quote(search)
    if cursor:
        url += "&cursor=" + urllib.parse.quote(cursor)
    return url


def fetch(
    cursor: str | None,
    version: str | None = None,
    search: str | None = None,
    retries: int = RETRIES,
) -> dict:
    """Fetch one page, retrying on transient failures."""
    url = build_url(cursor, version, search)

    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except RETRYABLE as err:
            last = err
            # Back off, but do not hammer a service that is already unhappy.
            # Capped at 30s: eight doublings would otherwise reach two minutes.
            delay = min(2 ** attempt, 30)
            print(
                f"    retry {attempt + 1}/{retries} in {delay}s "
                f"({type(err).__name__}: {err})",
                file=sys.stderr,
            )
            time.sleep(delay)
    raise RuntimeError(f"gave up after {retries} attempts: {last}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/registry.jsonl")
    parser.add_argument("--max-pages", type=int, default=0, help="0 means no cap")
    parser.add_argument("--state", default="data/cursor.txt")
    parser.add_argument(
        "--version",
        default=None,
        help="pass 'latest' to let the registry return only latest-version records",
    )
    parser.add_argument("--search", default=None, help="substring match on the server name")
    args = parser.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    state = pathlib.Path(args.state)

    cursor = state.read_text().strip() if state.exists() else None
    if cursor:
        print(f"resuming from checkpoint {cursor[:40]}...", file=sys.stderr)

    total = 0
    page = 0
    started = time.time()

    with out.open("a", encoding="utf-8") as sink:
        while True:
            payload = fetch(cursor, version=args.version, search=args.search)
            records = payload.get("servers", [])
            for record in records:
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()

            total += len(records)
            page += 1
            cursor = (payload.get("metadata") or {}).get("nextCursor")
            state.write_text(cursor or "")

            rate = total / max(time.time() - started, 0.001)
            print(
                f"page {page:4d}  +{len(records):3d}  total {total:6d}  {rate:5.0f}/s",
                file=sys.stderr,
            )

            if not cursor:
                print("registry exhausted", file=sys.stderr)
                break
            if args.max_pages and page >= args.max_pages:
                print(f"stopped at the {args.max_pages}-page cap", file=sys.stderr)
                break

    elapsed = time.time() - started
    print(f"\n{total} records in {page} pages, {elapsed:.0f}s -> {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
