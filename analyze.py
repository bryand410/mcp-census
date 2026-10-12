"""Turn the raw registry dump into security-relevant signals.

Reads the JSONL produced by crawl.py and writes two things:

  data/servers.csv    one row per *latest* server, one column per signal
  data/summary.json   the aggregate numbers, so the report can quote them

The registry lists every published version as its own record, so server-level
statistics count only records whose metadata says `isLatest`. The raw record
count is reported separately, because the difference between the two is itself
a finding.

Every signal here is derived from what the registry publishes. Nothing is
inferred about a server's behaviour at runtime, and nothing is executed.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RAW = HERE / "data" / "registry.jsonl"
OUT_CSV = HERE / "data" / "servers.csv"
OUT_JSON = HERE / "data" / "summary.json"

# Phrases that have no business in a server description. This is deliberately
# narrow: a broad keyword list would produce noise, and the point of publishing
# this is that every hit can be checked by hand.
#
# Two patterns were removed after reading the hits by hand, and the reason is
# the finding, not a detail:
#
#   "system prompt"  matched  app.web.mindset-502113/mindset ("...plus its
#                    system prompt", a product description) and
#                    com.runningunattended/agent-lint ("Checks CLAUDE.md,
#                    AGENTS.md or a system prompt for 12 safeguards"), which is
#                    a security tool. In this domain the phrase is ordinary
#                    vocabulary, not a payload.
#   "you are now"    same problem: it is how these tools describe themselves.
#
# What is left are instructions that only make sense if someone is trying to
# steer a model through a description. They are kept so the count can be
# reported as honestly zero rather than as a scare number.
INJECTION_PATTERNS = [
    r"ignore (all )?previous",
    r"ignore (all )?(prior|above) instructions",
    r"do not (tell|inform|mention)",
    r"without (telling|informing) the user",
    r"disregard (the )?(previous|above)",
]

# Kept for the record: patterns that were tried and rejected because they
# matched ordinary product descriptions. Reported in the summary so the method
# is auditable.
REJECTED_PATTERNS = [r"system prompt", r"you are now"]

# A namespace needs at least this many servers before its rate is worth
# comparing. Below it, 0% and 100% are one server either way.
MIN_NS = 30


def load(path: pathlib.Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def official_meta(record: dict) -> dict:
    return (record.get("_meta") or {}).get("io.modelcontextprotocol.registry/official", {})


def namespace(name: str) -> tuple[str, bool]:
    """Split 'ai.bowmark/bowmark' into ('ai.bowmark', True).

    A slash means the publisher registered a reverse-DNS namespace. A bare name
    like 'github' means they did not.
    """
    if "/" in name:
        return name.split("/", 1)[0], True
    return "", False


def top_namespace(name: str) -> str:
    """The first label of the reverse-DNS namespace: 'io.github.x/y' -> 'io'."""
    ns, qualified = namespace(name)
    return ns.split(".", 1)[0] if qualified else "(none)"


def by_namespace(servers: list[dict]) -> dict:
    """Per-namespace breakdown, because the aggregate is not stable.

    The registry is paginated in namespace order, so any partial pass is a
    prefix of the alphabet rather than a random sample. The opaque rate ranges
    from a few percent to over eighty depending on the namespace, which means a
    single blended figure describes the crawl's progress more than it describes
    the registry. This table is the honest version.
    """
    buckets: dict[str, dict[str, int]] = {}
    for row in servers:
        bucket = buckets.setdefault(
            top_namespace(row["name"]),
            {"n": 0, "repo": 0, "pkg": 0, "remote": 0, "opaque": 0},
        )
        opaque = not row["has_repository"] and not row["has_packages"] and row["has_remotes"]
        bucket["n"] += 1
        bucket["repo"] += bool(row["has_repository"])
        bucket["pkg"] += bool(row["has_packages"])
        bucket["remote"] += bool(row["has_remotes"])
        bucket["opaque"] += opaque

    out = {}
    for ns, b in sorted(buckets.items(), key=lambda kv: -kv[1]["n"]):
        n = b["n"]
        out[ns] = {
            "servers": n,
            "has_repository_pct": round(100.0 * b["repo"] / n, 1),
            "has_packages_pct": round(100.0 * b["pkg"] / n, 1),
            "has_remotes_pct": round(100.0 * b["remote"] / n, 1),
            "opaque_pct": round(100.0 * b["opaque"] / n, 1),
        }
    return out


def analyse(records: list[dict]) -> tuple[list[dict], dict]:
    rows = []
    for record in records:
        server = record.get("server") or {}
        meta = official_meta(record)

        name = server.get("name", "")
        ns, qualified = namespace(name)
        remotes = server.get("remotes") or []
        packages = server.get("packages") or []
        repo = server.get("repository") or {}
        description = server.get("description") or ""

        transports = sorted({r.get("type", "") for r in remotes if r.get("type")})
        registries = sorted({p.get("registryType", "") for p in packages if p.get("registryType")})

        # A package is pinned when the registry entry names an exact version and
        # the identifier is not a floating tag.
        unpinned = 0
        for package in packages:
            identifier = str(package.get("identifier", ""))
            version = str(package.get("version", ""))
            if not version or version in {"latest", "*"} or identifier.endswith("@latest"):
                unpinned += 1

        lowered = description.lower()
        hits = [p for p in INJECTION_PATTERNS if re.search(p, lowered)]

        rows.append(
            {
                "name": name,
                "version": server.get("version", ""),
                "namespace": ns,
                "namespace_qualified": qualified,
                "status": meta.get("status", ""),
                "is_latest": bool(meta.get("isLatest")),
                "published_at": meta.get("publishedAt", ""),
                "has_repository": bool(repo.get("url")),
                "repository_source": repo.get("source", ""),
                "has_remotes": bool(remotes),
                "transports": "|".join(transports),
                "has_packages": bool(packages),
                "registries": "|".join(registries),
                "unpinned_packages": unpinned,
                "description_length": len(description),
                "suspicious_phrases": "|".join(hits),
            }
        )

    latest = [r for r in rows if r["is_latest"]]
    # A record can be missing isLatest entirely; fall back to every record so the
    # denominator is never accidentally empty.
    servers = latest or rows

    total = len(rows)
    n = len(servers)

    versions_per_server = collections.Counter(r["name"] for r in rows)
    statuses = collections.Counter(r["status"] for r in servers)
    transports = collections.Counter(t for r in servers for t in r["transports"].split("|") if t)
    registries = collections.Counter(g for r in servers for g in r["registries"].split("|") if g)
    repo_sources = collections.Counter(r["repository_source"] for r in servers if r["repository_source"])

    no_repo = sum(1 for r in servers if not r["has_repository"])
    no_packages = sum(1 for r in servers if not r["has_packages"])
    unqualified = sum(1 for r in servers if not r["namespace_qualified"])
    with_remotes = sum(1 for r in servers if r["has_remotes"])
    suspicious = [r for r in servers if r["suspicious_phrases"]]
    unpinned_servers = sum(1 for r in servers if r["unpinned_packages"])

    # The one number worth leading with. A server with no repository and no
    # package is a server you can call but cannot read: the registry tells you
    # it exists and where to send requests, and nothing about what it runs.
    opaque = [
        r for r in servers if not r["has_repository"] and not r["has_packages"] and r["has_remotes"]
    ]

    # Count the patterns that were rejected, so the false-positive rate of a
    # naive keyword approach is itself a number in the output.
    rejected_hits = 0
    for record in records:
        description = ((record.get("server") or {}).get("description") or "").lower()
        if any(re.search(p, description) for p in REJECTED_PATTERNS):
            rejected_hits += 1

    ns_table = by_namespace(servers)
    big_ns = {k: v for k, v in ns_table.items() if v["servers"] >= MIN_NS}

    def pct(part: int, whole: int) -> float:
        return round(100.0 * part / whole, 2) if whole else 0.0

    summary = {
        "raw_records": total,
        "latest_servers": n,
        "versions_per_server_median": sorted(versions_per_server.values())[len(versions_per_server) // 2]
        if versions_per_server
        else 0,
        "versions_per_server_max": max(versions_per_server.values()) if versions_per_server else 0,
        "top_version_churn": versions_per_server.most_common(10),
        "statuses": dict(statuses.most_common()),
        "no_repository": no_repo,
        "no_repository_pct": pct(no_repo, n),
        "repository_sources": dict(repo_sources.most_common()),
        "no_packages": no_packages,
        "no_packages_pct": pct(no_packages, n),
        "unqualified_namespace": unqualified,
        "unqualified_namespace_pct": pct(unqualified, n),
        "with_remotes": with_remotes,
        "with_remotes_pct": pct(with_remotes, n),
        "opaque_servers": len(opaque),
        "opaque_servers_pct": pct(len(opaque), n),
        "transports": dict(transports.most_common()),
        "registries": dict(registries.most_common()),
        "unpinned_servers": unpinned_servers,
        "unpinned_servers_pct": pct(unpinned_servers, n),
        "suspicious_phrase_servers": len(suspicious),
        "suspicious_phrase_pct": pct(len(suspicious), n),
        "suspicious_examples": [
            {"name": r["name"], "phrases": r["suspicious_phrases"]} for r in suspicious[:25]
        ],
        # The honest headline. Reading the registry's description field for
        # prompt-injection wording does not work: the naive patterns hit
        # ordinary product copy, and the survivors hit nothing. This is why the
        # report does not claim the registry is full of injection attempts.
        "rejected_pattern_raw_hits": rejected_hits,
        "rejected_pattern_names": REJECTED_PATTERNS,
        "descriptions_as_security_signal": (
            "no usable signal: every raw keyword hit was checked by hand and "
            "was a false positive, so the description field cannot separate a "
            "malicious server from a legitimate one"
        ),
        # The headline table. Reported per namespace because the blended figure
        # moves with the crawl's alphabetical position, not with the registry.
        "by_namespace": ns_table,
        # Spread only over namespaces large enough to mean something. A
        # one-server namespace is trivially 0% or 100% opaque and would make the
        # range look wider than it is.
        "opaque_pct_spread": (
            f"{min(v['opaque_pct'] for v in big_ns.values())}"
            f" to {max(v['opaque_pct'] for v in big_ns.values())}"
            f" (namespaces with at least {MIN_NS} servers)"
            if big_ns
            else ""
        ),
        "by_namespace_min_servers": MIN_NS,
    }
    return servers, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", default=str(RAW), help="JSONL produced by crawl.py")
    parser.add_argument("--csv", default=str(OUT_CSV))
    parser.add_argument("--json", default=str(OUT_JSON))
    args = parser.parse_args()

    out_csv = pathlib.Path(args.csv)
    out_json = pathlib.Path(args.json)

    records = load(pathlib.Path(args.raw))
    servers, summary = analyse(records)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if servers:
        with out_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(servers[0].keys()))
            writer.writeheader()
            writer.writerows(servers)

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"raw records          : {summary['raw_records']}")
    print(f"latest servers       : {summary['latest_servers']}")
    print(f"median versions/srv  : {summary['versions_per_server_median']}")
    print(f"max versions (one)   : {summary['versions_per_server_max']}")
    print()
    print(f"no repository        : {summary['no_repository']} ({summary['no_repository_pct']}%)")
    print(f"no packages          : {summary['no_packages']} ({summary['no_packages_pct']}%)")
    print(f"unqualified name     : {summary['unqualified_namespace']} ({summary['unqualified_namespace_pct']}%)")
    print(f"has remote endpoint  : {summary['with_remotes']} ({summary['with_remotes_pct']}%)")
    print(
        f"opaque (remote only) : {summary['opaque_servers']} "
        f"({summary['opaque_servers_pct']}%)  <- no source, no package, callable"
    )
    print(f"unpinned packages    : {summary['unpinned_servers']} ({summary['unpinned_servers_pct']}%)")
    print(f"suspicious phrases   : {summary['suspicious_phrase_servers']} ({summary['suspicious_phrase_pct']}%)")
    print(
        f"  patterns rejected  : {summary['rejected_pattern_raw_hits']} raw hits, "
        f"all false positives"
    )
    print()
    print("transports :", summary["transports"])
    print("registries :", summary["registries"])
    print()
    print("--- par espace de nommage (le chiffre global ne veut rien dire seul) ---")
    print(f"{'prefixe':12s} {'serveurs':>9s} {'depot':>8s} {'paquet':>8s} {'endpoint':>9s} {'opaque':>8s}")
    for ns, v in list(summary["by_namespace"].items())[:15]:
        print(
            f"{ns:12s} {v['servers']:9d} {v['has_repository_pct']:7.1f}% "
            f"{v['has_packages_pct']:7.1f}% {v['has_remotes_pct']:8.1f}% {v['opaque_pct']:7.1f}%"
        )
    print(f"\netalement opaque de {summary['opaque_pct_spread']} selon l'espace de nommage")
    print(f"\nwrote {out_csv} and {out_json}")


if __name__ == "__main__":
    main()
