# A census of the official MCP Registry

**12 October 2026** — **complete** pass: **42,399 servers**, each server's latest version, read from
the official registry at `registry.modelcontextprotocol.io` (v1.8.1). The pagination cursor ran to
empty, so this is the whole registry, not a sample.
Reproducible in two commands, no dependencies outside the standard library.

The registry is public, the API is public, and **nobody had published what is actually in it**. This
measures it. Nothing is executed, no endpoint is contacted: everything below is read from what the
registry declares about itself.

---

## 1. The main result: this is not one population, it is two

I computed a single blended figure first. It is **not** meaningless now that the pass is complete —
26.0 % of the registry is opaque — but it is the **least** informative number in this document,
because it averages over two populations that have almost nothing in common.

I can show why, because I froze the dataset three times during the crawl:

| Snapshot | servers | aggregate opaque | `com.*` opaque | `io.*` opaque |
|---|---:|---:|---:|---:|
| partial | 19,500 | **41.0 %** | 60.3 % | 14.1 % |
| partial | 36,200 | **24.6 %** | 60.3 % | 8.1 % |
| **complete** | **42,399** | **26.0 %** | 60.3 % | 8.7 % |

Same registry, same code, same question. The aggregate swung **16 points down and then up** because
the crawler walked further into the alphabet and picked up different namespaces. **Every completed
namespace stayed identical to one decimal place** — `com.*` is 60.3 % in all three.

So: had I published after the first snapshot I would have said 41 %. After the second, 24.6 %. Both
would have been wrong, and confidently so. That is the trap of paginated datasets: the ordering key
is not random, so a partial pass is a prefix, not a sample.

Split by namespace, the gap is enormous:

| Namespace | servers | publishes source | publishes a package | exposes an endpoint | **opaque** |
|---|---:|---:|---:|---:|---:|
| `io.*` (mostly `io.github.*`) | 28,029 | 89.2 % | 53.4 % | 50.0 % | **8.7 %** |
| `com.*` | 6,856 | 37.2 % | 14.3 % | 90.4 % | **60.3 %** |
| `ai.*` | 1,878 | 46.2 % | 14.7 % | 89.9 % | **51.6 %** |
| `dev.*` | 821 | 43.7 % | 21.6 % | 85.9 % | **52.0 %** |
| `app.*` | 781 | 42.8 % | 8.1 % | 94.9 % | **55.4 %** |
| `uk.*` | 319 | 10.7 % | 3.1 % | 97.2 % | **89.3 %** |
| `org.*` | 229 | 40.6 % | 14.0 % | 86.9 % | **57.2 %** |
| `co.*` | 226 | 29.2 % | 12.8 % | 94.2 % | **67.7 %** |
| `net.*` | 223 | 27.4 % | 13.9 % | 88.3 % | **65.5 %** |
| `eu.*` | 179 | 75.4 % | 57.5 % | 45.3 % | **24.0 %** |
| `de.*` | 111 | 13.5 % | 4.5 % | 97.3 % | **85.6 %** |
| `live.*` | 92 | 7.6 % | 1.1 % | 100.0 % | **91.3 %** |
| `fr.*` | 86 | 17.4 % | 2.3 % | 98.8 % | **81.4 %** |
| `guide.*` | 43 | 95.3 % | 0.0 % | 100.0 % | **4.7 %** |

Across the 36 namespaces with at least 30 servers, the opaque rate runs from **4.7 % to 91.3 %** — a
factor of **19**.

**How to read it.** The registry hosts two different things behind one API:

- **`io.github.*` servers** — code hosted on GitHub, published as a package, versioned. 89 % name a
  repository, 53 % ship an installable artefact. These are libraries.
- **`com.*`, `ai.*`, `app.*`, `uk.*`, `live.*` and country-code servers** — commercial services.
  ~90 % expose a URL and nothing else. These are endpoints.

They are not the same kind of object and they do not raise the same question. A library can be read,
pinned, and diffed against its source. A commercial endpoint can only be called. `live.*` — 100 % of
them expose an endpoint, 7.6 % name a repository, 91.3 % are opaque — is the purest form of the
second kind.

**The practical consequence:** the usable statement is **"in commercial and country-code namespaces,
50–91 % of servers are opaque; in `io.github.*`, 8.7 %"**. The registry-wide 26.0 % is arithmetically
correct and practically useless, because it depends entirely on how many GitHub libraries happen to
have been registered that month.

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

With the offending patterns removed, the detector returns **0 out of 42,399**.

**This is not a failure to hide; it is the result.** The registry's `description` field is written by
the publisher, is unverified, and does not separate a malicious server from a legitimate one. Anyone
claiming to detect dangerous MCP servers by reading their descriptions is describing a detector that
returns noise here. The rejected patterns remain **visible in the code** (`REJECTED_PATTERNS`) and are
counted in `summary-latest.json` (`rejected_pattern_raw_hits`), so the false-positive rate stays
checkable instead of being quietly deleted.

---

## 3. The signal that does not exist

I expected to find servers registered under a bare name, with no reverse-DNS namespace — a sign of
improvisation, and therefore of risk. **Result: 0 out of 42,399. No exceptions.**

The registry enforces the prefix. A signal with no variance is not a signal: the column is computed,
published, and discriminates nothing. It stays in the output so the claim is checkable, not so a
conclusion can be drawn from it.

---

## 4. The remaining figures

| Measure | Value |
|---|---|
| servers (latest version each) | 42,399 |
| no public repository | 11,951 (28.2 %) |
| no published package | 25,435 (60.0 %) |
| exposes a remote endpoint | 27,008 (63.7 %) |
| **opaque** (endpoint, no source, no package) | **11,013 (26.0 %)** |
| unpinned packages | 1,549 (3.7 %) |
| descriptions with injection wording | **0** |
| names without a namespace | **0** |

**Transports:** `streamable-http` 26,271 · `sse` 1,081. The legacy SSE transport is on its way out —
under 4 % of the fleet.

**Package registries:** npm 10,882 · pypi 4,371 · mcpb 1,101 · oci 1,091 · nuget 146 · cargo 76. The
ecosystem is overwhelmingly JavaScript and Python. MCPB (native bundles) has now passed OCI — worth
watching, because a native bundle is not a sandboxed install.

---

## 5. A bug worth reporting: the crawl died twice

Both passes crashed mid-run with `http.client.RemoteDisconnected` — the registry closing the
connection mid-response — after 1 h 16 and 1 h 37 of work. The retry loop caught
`urllib.error.URLError`, but `RemoteDisconnected` inherits from `ConnectionResetError`, which is a
**sibling** of `URLError`, not a subclass. So the single most likely failure on a long crawl was the
one exception the loop did not catch.

The fix is to catch `OSError` (which covers `URLError`, `ConnectionResetError` and plain socket
timeouts) plus `http.client.HTTPException`. On the resumed run it rode through `502 Bad Gateway` and
`SSL: UNEXPECTED_EOF_WHILE_READING` without losing the pass. A code bug still stops the crawl; a
dropped connection no longer does. If you are paginating this registry, that is the line that will
bite you.

---

## 6. What not to conclude

- **A registry listing is not a population.** This counts what was published to this index on
  12 October 2026, not what exists. Servers never registered, or withdrawn, are invisible here.
- **It is not an instantaneous snapshot.** The complete pass took about two hours across two runs.
  Servers published during that window may be missed or counted twice at the boundary.
- **An opaque server is not malicious, and a server with a repository is not safe.** This census
  measures what is **inspectable**, which is a different question from what is **safe**.
- **`isLatest` is the registry's own claim**, taken at face value.
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
