# A census of the official MCP Registry — first pass

**12 October 2026** — dataset frozen at **19,500 servers** (each server's latest version), read from
the official registry at `registry.modelcontextprotocol.io` (v1.8.1).
Reproducible in two commands, no dependencies outside the standard library.

The registry is public, the API is public, and **nobody had published what is actually in it**. This
measures it. Nothing is executed, no endpoint is contacted: everything below is read from what the
registry declares about itself.

---

## 1. The main result: this is not one population, it is two

I computed a single blended figure first, and **it means nothing**. The reason is mechanical: the
registry is paginated in alphabetical order of namespace. A partial pass is therefore a **prefix of
the alphabet**, not a random sample. The share of "opaque" servers — callable, but publishing neither
source nor package — then depends on where the crawler stopped.

Split by namespace, the gap is enormous:

| Namespace | servers | publishes source | publishes a package | exposes an endpoint | **opaque** |
|---|---:|---:|---:|---:|---:|
| `io.*` (mostly `io.github.*`) | 7,570 | 83.3 % | 63.2 % | 41.1 % | **14.1 %** |
| `com.*` | 6,856 | 37.2 % | 14.3 % | 90.4 % | **60.3 %** |
| `ai.*` | 1,878 | 46.2 % | 14.7 % | 89.9 % | **51.6 %** |
| `dev.*` | 821 | 43.7 % | 21.6 % | 85.9 % | **52.0 %** |
| `app.*` | 781 | 42.8 % | 8.1 % | 94.9 % | **55.4 %** |
| `co.*` | 226 | 29.2 % | 12.8 % | 94.2 % | **67.7 %** |
| `eu.*` | 179 | 75.4 % | 57.5 % | 45.3 % | **24.0 %** |
| `de.*` | 111 | 13.5 % | 4.5 % | 97.3 % | **85.6 %** |
| `fr.*` | 86 | 17.4 % | 2.3 % | 98.8 % | **81.4 %** |
| `guide.*` | 43 | 95.3 % | 0.0 % | 100.0 % | **4.7 %** |

Across the 18 namespaces with at least 30 servers, the opaque rate runs from **4.7 % to 85.6 %** — a
factor of 18.

**How to read it.** The registry hosts two different things behind one API:

- **`io.github.*` servers** — code hosted on GitHub, published as a package, versioned. 83 % name a
  repository, 63 % ship an installable artefact. These are libraries.
- **`com.*`, `ai.*`, `app.*` and country-code servers** — commercial services. 90 % expose a URL and
  nothing else. These are endpoints.

They are not the same kind of object and they do not raise the same question. A library can be read,
pinned, and diffed against its source. A commercial endpoint can only be called.

**The practical consequence:** "41 % of MCP servers are opaque" is a figure that describes the
progress of my crawl, not the registry. The usable statement is **"in commercial and country-code
namespaces, 60–86 % of servers are opaque; in `io.github.*`, 14 %"**. Any write-up that quotes a
single average over this registry is wrong — including mine, had I published it as it first stood.

---

## 2. The detector that does not work

I wrote a prompt-injection detector that read server descriptions, with `system prompt` and
`you are now` among its patterns. It found **6 servers**. I read all six.

**All six are false positives.** False-positive rate: **100 %**.

| Server | Description |
|---|---|
| `app.web.mindset-502113/mindset` | "Semantic search over MINDSET's brand strategy topic database, plus its system prompt." |
| `com.runningunattended/agent-lint` | "Checks CLAUDE.md, AGENTS.md or a system prompt for 12 safeguards unattended agents need." |
| `io.gildara/mcp-server` | "Operating contracts for AI agents. Structured instructions compiled into system prompts." |
| `io.github.Evozim/rules-gen` | "Automated .cursorrules and system prompt generator." |
| `io.github.Gildaraio/mcp-server` | (same publisher as the previous entry) |
| `io.github.a-church-ai/magnifica-family` | "Catholic AI compass: system prompts from Pope Leo XIV's encyclical Magnifica Humanitas." |

The reason is simple and it is final: **in this domain, "system prompt" is ordinary vocabulary.** Half
of these servers exist precisely to *generate*, *compile* or *audit* a system prompt. The phrase is in
the product description because it is the product.

With the offending patterns removed, the detector returns **0 out of 19,500**.

**This is not a failure to hide; it is the result.** The registry's `description` field is written by
the publisher, is unverified, and does not separate a malicious server from a legitimate one. Anyone
claiming to detect dangerous MCP servers by reading their descriptions is describing a detector that
returns noise here. The rejected patterns remain **visible in the code** (`REJECTED_PATTERNS`) and are
counted in `summary-latest.json` (`rejected_pattern_raw_hits`), so the false-positive rate stays
checkable instead of being quietly deleted.

---

## 3. The signal that does not exist

I expected to find servers registered under a bare name, with no reverse-DNS namespace — a sign of
improvisation, and therefore of risk. **Result: 0 out of 19,500. No exceptions.**

The registry enforces the prefix. A signal with no variance is not a signal: the column is computed,
published, and discriminates nothing. It stays in the output so the claim is checkable, not so a
conclusion can be drawn from it.

---

## 4. The remaining figures

| Measure | Value |
|---|---|
| servers (latest version each) | 19,500 |
| no public repository | 8,500 (43.6 %) |
| no published package | 12,984 (66.6 %) |
| exposes a remote endpoint | 13,866 (71.1 %) |
| **opaque** (endpoint, no source, no package) | **8,003 (41.0 %)** |
| unpinned packages | 611 (3.1 %) |
| descriptions with injection wording | **0** |
| names without a namespace | **0** |

**Transports:** `streamable-http` 13,280 · `sse` 758. The legacy SSE transport is on its way out —
under 6 % of the fleet.

**Package registries:** npm 3,991 · pypi 1,923 · oci 439 · mcpb 422 · nuget 65 · cargo 22. The
ecosystem is overwhelmingly JavaScript and Python; MCPB (native bundles) exist but remain marginal.

**Version churn** (full pass, still partial): one server, `ai.bowmark/bowmark`, appears **exactly 1,000
times**. The figure is round, so I am not asserting it — either automated publication on every commit,
or a cap on the registry side. Worth checking before quoting. The next highest are 516
(`com.linkbreakers/mcp`), 350, 258, 242, 214.

---

## 5. What not to conclude

- **This is not exhaustive.** The pass stopped at 19,500 servers, inside `io.github.*`. The count is a
  **lower bound**.
- **An opaque server is not malicious, and a server with a repository is not safe.** This census
  measures what is **inspectable**, which is a different question from what is **safe**.
- **`isLatest` is the registry's own claim**, taken at face value.
- **The registry is not the population.** It contains what was published to this index, not what
  exists. A server never registered, or withdrawn, is invisible here.
- **No execution, no intrusive scanning, no calls to any server.** API reads only.

---

## 6. Reproduce it

```bash
python crawl.py --out data/registry-latest.jsonl --state data/cursor-latest.txt --version latest
python analyze.py --raw data/registry-latest.jsonl \
    --csv data/servers-latest.csv --json data/summary-latest.json
```

`servers-latest.csv`: one row per server, one column per signal. `summary-latest.json`: the
aggregates, including the per-namespace table and the rejected patterns.

**The method detail that unblocked the crawl:** `?version=latest` is evaluated **server-side**. The
unfiltered list takes **60 s** per page once the cursor is deep; the same question with the filter
takes **1.6 s**. The registry already knows how to filter — do not redo it client-side.

Repository: https://github.com/bryand410/mcp-census
