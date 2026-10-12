# A census of the official MCP Registry — first pass

**12 October 2026** — dataset frozen at **36,200 servers** (each server's latest version), read from
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

I can prove this rather than assert it, because I froze the dataset twice:

| Snapshot | servers | aggregate opaque | `com.*` opaque | `io.*` opaque |
|---|---:|---:|---:|---:|
| 19,500 | **41.0 %** | 60.3 % | 14.1 % |
| 36,200 | **24.6 %** | 60.3 % | 8.1 % |

Same registry, same code, same question. The aggregate fell by 16 points because the crawler walked
further into the alphabet and picked up more `io.github.*` servers. The completed namespaces did not
move at all. **The aggregate is a measurement of the crawl's progress, not of the registry.**

Split by namespace, the gap is enormous:

| Namespace | servers | publishes source | publishes a package | exposes an endpoint | **opaque** |
|---|---:|---:|---:|---:|---:|
| `io.*` (mostly `io.github.*`) | 24,270 | 90.0 % | 53.2 % | 49.8 % | **8.1 %** |
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

- **`io.github.*` servers** — code hosted on GitHub, published as a package, versioned. 90 % name a
  repository, 53 % ship an installable artefact. These are libraries.
- **`com.*`, `ai.*`, `app.*` and country-code servers** — commercial services. ~90 % expose a URL and
  nothing else. These are endpoints.

They are not the same kind of object and they do not raise the same question. A library can be read,
pinned, and diffed against its source. A commercial endpoint can only be called.

**The practical consequence:** the usable statement is **"in commercial and country-code namespaces,
50–86 % of servers are opaque; in `io.github.*`, 8 %"**. Any write-up that quotes a single average
over this registry is wrong — including mine, had I published it as it first stood.

---

## 2. The detector that does not work

I wrote a prompt-injection detector that read server descriptions, with `system prompt` and
`you are now` among its patterns. It found **9 servers**. I read all nine.

**All nine are false positives.** False-positive rate: **100 %**.

| Server | Description |
|---|---|
| `app.web.mindset-502113/mindset` | "Semantic search over MINDSET's brand strategy topic database, plus its system prompt." |
| `com.runningunattended/agent-lint` | "Checks CLAUDE.md, AGENTS.md or a system prompt for 12 safeguards unattended agents need." |
| `io.gildara/mcp-server` | "Operating contracts for AI agents. Structured instructions compiled into system prompts." |
| `io.github.Evozim/rules-gen` | "Automated .cursorrules and system prompt generator." |
| `io.github.Gildaraio/mcp-server` | (same publisher as the previous entry) |
| `io.github.a-church-ai/magnifica-family` | "Catholic AI compass: system prompts from Pope Leo XIV's encyclical Magnifica Humanitas." |
| `io.github.izworskic/openclaw-registry` | "Search and retrieve agent instruction files: system prompts, skills, workflows, and safety filters." |
| `io.github.jmshinhwa/ai-act-article-50-audit` | "Finds the AI call sites, generation code and system prompts that trigger EU AI Act Article 50 disclosure…" |
| `io.github.jmshinhwa/ai-companion-safety-lint` | "Reads your companion chatbot's system prompt against California SB 243, New York GBL Article 47…" |

The reason is simple and it is final: **in this domain, "system prompt" is ordinary vocabulary.** Half
of these servers exist precisely to *generate*, *compile* or *audit* a system prompt. The phrase is in
the product description because it is the product.

**And the failure is worse than noise.** Three of the nine are compliance and safety tooling — one
checks a chatbot against the **EU AI Act Article 50**, another against **California SB 243 and New York
GBL Article 47**. A detector that flags the people writing the compliance checks is not merely
useless; it points at exactly the wrong population. That is the worst failure mode a security
detector can have.

With the offending patterns removed, the detector returns **0 out of 36,200**.

**This is not a failure to hide; it is the result.** The registry's `description` field is written by
the publisher, is unverified, and does not separate a malicious server from a legitimate one. Anyone
claiming to detect dangerous MCP servers by reading their descriptions is describing a detector that
returns noise here. The rejected patterns remain **visible in the code** (`REJECTED_PATTERNS`) and are
counted in `summary-latest.json` (`rejected_pattern_raw_hits`), so the false-positive rate stays
checkable instead of being quietly deleted.

---

## 3. The signal that does not exist

I expected to find servers registered under a bare name, with no reverse-DNS namespace — a sign of
improvisation, and therefore of risk. **Result: 0 out of 36,200. No exceptions.**

The registry enforces the prefix. A signal with no variance is not a signal: the column is computed,
published, and discriminates nothing. It stays in the output so the claim is checkable, not so a
conclusion can be drawn from it.

---

## 4. The remaining figures

| Measure | Value |
|---|---|
| servers (latest version each) | 36,200 |
| no public repository | 9,656 (26.7 %) |
| no published package | 21,571 (59.6 %) |
| exposes a remote endpoint | 22,855 (63.1 %) |
| **opaque** (endpoint, no source, no package) | **8,893 (24.6 %)** |
| unpinned packages | 1,317 (3.6 %) |
| descriptions with injection wording | **0** |
| names without a namespace | **0** |

**Transports:** `streamable-http` 22,169 · `sse` 929. The legacy SSE transport is on its way out —
under 4 % of the fleet.

**Package registries:** npm 9,458 · pypi 3,850 · oci 921 · mcpb 818 · nuget 133 · cargo 63. The
ecosystem is overwhelmingly JavaScript and Python; MCPB (native bundles) exist but remain marginal.

**Version churn** (full pass, 58,100 records and still partial): one server, `ai.bowmark/bowmark`,
appears **exactly 1,000 times**. The figure is round, so I am not asserting it — either automated
publication on every commit, or a cap on the registry side. Worth checking before quoting. The next
highest are 516 (`com.linkbreakers/mcp`), 350, 258, 242, 214.

---

## 5. A bug worth reporting: the crawl died twice

Both passes crashed mid-run with `http.client.RemoteDisconnected` — the registry closing the
connection mid-response — after 1 h 16 and 1 h 37 of work. The retry loop caught
`urllib.error.URLError`, but `RemoteDisconnected` inherits from `ConnectionResetError`, which is a
**sibling** of `URLError`, not a subclass. So the single most likely failure on a long crawl was the
one exception the loop did not catch.

The fix is to catch `OSError` (which covers `URLError`, `ConnectionResetError` and plain socket
timeouts) plus `http.client.HTTPException`, and to raise the retry count. A code bug still stops the
crawl; a dropped connection no longer does. If you are paginating this registry, that is the line
that will bite you.

---

## 6. What not to conclude

- **This is not exhaustive.** The pass stopped at 36,200 servers, inside `io.github.*`. The count is a
  **lower bound**.
- **An opaque server is not malicious, and a server with a repository is not safe.** This census
  measures what is **inspectable**, which is a different question from what is **safe**.
- **`isLatest` is the registry's own claim**, taken at face value.
- **The registry is not the population.** It contains what was published to this index, not what
  exists. A server never registered, or withdrawn, is invisible here.
- **No execution, no intrusive scanning, no calls to any server.** API reads only.

---

## 7. Reproduce it

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
