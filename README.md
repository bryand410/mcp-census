# mcp-census

A census of the official MCP Registry: what it actually contains, measured from
the registry's own public API, with the rules written down so anyone can redo it.

The question behind it is narrow and practical. If you are about to point an
agent at an MCP server, what can the registry tell you about it **before** you
call it? This repository answers that with numbers instead of impressions.

**Read the write-up:** [REPORT.md](REPORT.md) (English) ·
[REPORT.fr.md](REPORT.fr.md) (français)

## What it found, in three lines

1. **The registry is two populations, and the average is meaningless.** Opaque
   servers — callable, publishing neither source nor package — run from **4.7 %**
   in `guide.*` to **85.6 %** in `de.*`. `io.github.*` is 14 % opaque; `com.*` is
   60 %. A single blended figure describes the crawl's alphabetical position, not
   the registry.
2. **Descriptions are not a security signal.** A prompt-injection detector over
   the description field returned 6 hits in 19 500 servers, and **all six were
   false positives** — read individually, they are tools that *generate* or
   *audit* system prompts. The rejected patterns are kept in the code.
3. **Namespace qualification is not a signal either** — 0 servers out of 19 500
   lack a reverse-DNS namespace. The registry enforces it, so the column has no
   variance and discriminates nothing.

## The registry is not one population

| Namespace | servers | source | package | endpoint | opaque |
|---|---:|---:|---:|---:|---:|
| `io.*` (mostly `io.github.*`) | 7,570 | 83.3 % | 63.2 % | 41.1 % | **14.1 %** |
| `com.*` | 6,856 | 37.2 % | 14.3 % | 90.4 % | **60.3 %** |
| `ai.*` | 1,878 | 46.2 % | 14.7 % | 89.9 % | **51.6 %** |
| `dev.*` | 821 | 43.7 % | 21.6 % | 85.9 % | **52.0 %** |
| `de.*` | 111 | 13.5 % | 4.5 % | 97.3 % | **85.6 %** |

Frozen at 19,500 servers on 12 October 2026. The pass is incomplete — it stopped
inside `io.github.*` — so the counts are lower bounds. The percentages per
namespace are stable across completed namespaces.

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
found two servers. Both were false positives:

- `app.web.mindset-502113/mindset` — *"Semantic search over MINDSET's brand
  strategy topic database, plus its system prompt."* A product description.
- `com.runningunattended/agent-lint` — *"Checks CLAUDE.md, AGENTS.md or a system
  prompt for 12 safeguards unattended agents need."* A security tool.

In this domain those phrases are ordinary vocabulary, because operating on a
system prompt is what half these servers are *for*. The patterns were removed,
`REJECTED_PATTERNS` keeps them visible, and `summary.json` reports
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
- **The percentages move while the crawl runs.** Any figure quoted from a
  partial pass is marked as such; the crawl is resumable and the script is the
  method.
- **Version churn comes from the partial pass** and is a lower bound.
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
