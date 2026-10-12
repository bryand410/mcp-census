# mcp-census

A census of the official MCP Registry: what it actually contains, measured from
the registry's own public API, with the rules written down so anyone can redo it.

The question behind it is narrow and practical. If you are about to point an
agent at an MCP server, what can the registry tell you about it **before** you
call it? This repository answers that with numbers instead of impressions.

**Read the write-up:** [REPORT.md](REPORT.md) (English) ·
[REPORT.fr.md](REPORT.fr.md) (français)

## What it found, in three lines

1. **The registry is two populations, and the average hides it.** Opaque servers —
   callable, publishing neither source nor package — run from **4.7 %** in
   `guide.*` to **91.3 %** in `live.*`. `io.github.*` is 8.7 % opaque; `com.*` is
   60 %. Freezing the dataset three times proves the point: the aggregate went
   **41.0 % → 24.6 % → 26.0 %** while every completed namespace stayed identical
   to one decimal. A partial pass is a prefix of the alphabet, not a sample.
2. **Descriptions are not a security signal.** A prompt-injection detector over
   the description field returned 9 hits in 42 399 servers, and **all nine were
   false positives** — including two tools that audit against the **EU AI Act
   Article 50** and **California SB 243**. The detector flags the compliance
   tooling. The rejected patterns are kept in the code.
3. **Namespace qualification is not a signal either** — 0 servers out of 42 399
   lack a reverse-DNS namespace. The registry enforces it, so the column has no
   variance and discriminates nothing.

## The registry is not one population

| Namespace | servers | source | package | endpoint | opaque |
|---|---:|---:|---:|---:|---:|
| `io.*` (mostly `io.github.*`) | 28,029 | 89.2 % | 53.4 % | 50.0 % | **8.7 %** |
| `com.*` | 6,856 | 37.2 % | 14.3 % | 90.4 % | **60.3 %** |
| `ai.*` | 1,878 | 46.2 % | 14.7 % | 89.9 % | **51.6 %** |
| `dev.*` | 821 | 43.7 % | 21.6 % | 85.9 % | **52.0 %** |
| `uk.*` | 319 | 10.7 % | 3.1 % | 97.2 % | **89.3 %** |
| `live.*` | 92 | 7.6 % | 1.1 % | 100.0 % | **91.3 %** |
| `guide.*` | 43 | 95.3 % | 0.0 % | 100.0 % | **4.7 %** |

Complete pass on 12 October 2026: the cursor ran to empty, so this is the whole
registry, not a sample. Across the 36 namespaces with at least 30 servers the
opaque rate spans a factor of 19.

## A bug that will cost you 90 minutes

Both crawls died on `http.client.RemoteDisconnected`. The retry loop caught
`urllib.error.URLError`, but `RemoteDisconnected` inherits from
`ConnectionResetError`, which is a **sibling** of `URLError`, not a subclass — so
the most likely failure on a long crawl was the one exception it did not catch.
Catch `OSError` plus `http.client.HTTPException`. See `RETRYABLE` in `crawl.py`.

## What the registry is

`https://registry.modelcontextprotocol.io/v0/servers` is the official index of
MCP servers. Two properties of it shape everything below.

**It lists every published version as its own record.** A server that has cut
40 releases appears 40 times. So a count of records is not a count of servers.
Each record carries `_meta["io.modelcontextprotocol.registry/official"].isLatest`,
and that flag is what separates the two.

**`limit` is capped at 100.** 500 and 1 000 return HTTP 422. A full pass is a
few hundred round trips.

## The two passes

`crawl.py` runs against the registry and writes one JSON record per line,
checkpointing the cursor so an interrupted run resumes.

```bash
# Pass 1 - every published version, one record per version.
# Slow: once the cursor is deep, a single page took 60s to answer.
python crawl.py --out data/registry.jsonl --state data/cursor.txt

# Pass 2 - latest version only, filtered by the registry itself.
# ~1.6s per page, and 100/100 records come back with isLatest=true.
python crawl.py --out data/registry-latest.jsonl --state data/cursor-latest.txt \
    --version latest
```

Pass 2 exists because of a measured difference, not a guess. `version=latest` is
evaluated **server-side**: the same question that takes 60 s against the
unfiltered list is answered in 1.6 s when the filter is applied. The first page
of each pass also starts at a different cursor, so the two orderings are
independent and the passes can run side by side.

The per-server statistics are computed from **pass 2**, because that stream
already contains exactly one row per server. Pass 1 is used only for the
version-churn figures, and those are reported as a subset of the registry, since
the full pass is the slower one.

## The signals

`analyze.py` turns the JSONL into `data/servers.csv` (one row per server, one
column per signal) and `data/summary.json` (the aggregates).

```bash
python analyze.py --raw data/registry-latest.jsonl \
    --csv data/servers-latest.csv --json data/summary-latest.json
```

Nothing here executes a server, contacts an endpoint, or installs a package.
Every column is read straight out of what the registry publishes.

| Column | Meaning |
|---|---|
| `has_repository` | the record names a source repository |
| `has_packages` | the record names an installable artefact |
| `has_remotes` | the record names a URL to send requests to |
| `namespace_qualified` | the name contains a `/`, i.e. a reverse-DNS namespace |
| `unpinned_packages` | a package whose version is absent, `latest`, `*`, or `@latest` |
| `transports` | `streamable-http`, `sse`, or both |
| `registries` | `npm`, `pypi`, `oci`, `mcpb`, `nuget`, `cargo` |

### The derived number that matters

```
opaque = not has_repository and not has_packages and has_remotes
```

A server in this set is one you can **call but not read**. The registry tells you
it exists and where to send requests, and nothing about what runs behind the
URL. It is the only figure here that I would put in a headline, because it is a
statement about what is *absent* from the registry rather than about anyone's
intentions.

## The detector that failed, kept in the code

An earlier version of `analyze.py` looked for prompt-injection wording in server
descriptions, with `system prompt` and `you are now` among the patterns. It
found nine servers. **All nine were false positives**, and reading them one by
one is what makes the point:

- `app.web.mindset-502113/mindset` — *"Semantic search over MINDSET's brand
  strategy topic database, plus its system prompt."* A product description.
- `com.runningunattended/agent-lint` — *"Checks CLAUDE.md, AGENTS.md or a system
  prompt for 12 safeguards unattended agents need."* A security tool.
- `io.github.jmshinhwa/ai-act-article-50-audit` — *"Finds the AI call sites,
  generation code and system prompts that trigger EU AI Act Article 50
  disclosure…"*
- `io.github.jmshinhwa/ai-companion-safety-lint` — *"Reads your companion
  chatbot's system prompt against California SB 243, New York GBL Article 47…"*

In this domain those phrases are ordinary vocabulary, because operating on a
system prompt is what half these servers are *for*. **And the failure is worse
than noise:** the detector flags the compliance tooling — the EU AI Act and
California SB 243 auditors. A security detector that points at the people
writing the safety checks has the worst possible failure mode. The patterns were
removed, `REJECTED_PATTERNS` keeps them visible, and `summary.json` reports
`rejected_pattern_raw_hits` so the false-positive rate stays auditable instead
of being quietly deleted.

This is the honest conclusion, and it is more useful than a scare number:
**the registry's description field does not separate a malicious server from a
legitimate one.** It is written by the publisher, it is unverified, and in a
corpus of this size the only keyword hits are innocent. Anyone claiming to
detect dangerous MCP servers by reading their descriptions is describing a
detector that returns noise here.

## Limits

- **A registry listing is not a population.** It records what has been
  published to one index, not what exists. Servers that were never registered,
  or were removed, are invisible here.
- **`isLatest` is the registry's own claim.** It is taken at face value.
- **It is not an instantaneous snapshot.** The complete pass took about two hours
  across two runs; a server published inside that window may be missed or counted
  twice at the boundary.
- **The counts are of the registry as it stood on 12 October 2026.** The pass is
  complete — the cursor ran to empty — but the registry keeps growing, so rerun
  the two commands rather than quoting these numbers as current.
- **Version churn comes from the other pass** (every version, not just the
  latest), which was still running when this was written.
- **No runtime claim is made anywhere.** A server with a repository is not
  thereby safe, and an opaque one is not thereby malicious. The census measures
  what is *inspectable*, which is a different question from what is *safe*.

## Reproduce it

```bash
python crawl.py --out data/registry-latest.jsonl --state data/cursor-latest.txt --version latest
python analyze.py --raw data/registry-latest.jsonl \
    --csv data/servers-latest.csv --json data/summary-latest.json
```

Two files, no dependencies outside the standard library, no credentials.
