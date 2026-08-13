---
name: annotation-kegg
description: >
  Look up KEGG orthologs, pathways, and links via the KEGG REST API; optional
  local KO↔pathway tables for enrichment prep.
runtime: stats
conda_env: mgx-base
tools:
  - python
  - curl
  - R
  - clusterProfiler
  - KEGGREST
---

# KEGG REST / mapping

## Docs

Official REST overview: https://www.kegg.jp/kegg/rest/keggapi.html  

Operations to know: `info`, `list`, `find`, `get`, `conv`, `link`, `ddi`.

Base pattern:

```text
https://rest.kegg.jp/<operation>/<argument>[/<argument2>…]
```

Examples (fetch with curl/WebFetch; adapt to the question):

```bash
curl -sL "https://rest.kegg.jp/list/pathway/ko"
curl -sL "https://rest.kegg.jp/find/genes/tp53"
curl -sL "https://rest.kegg.jp/get/ko:K00001"
curl -sL "https://rest.kegg.jp/link/pathway/ko:K00001"
curl -sL "https://rest.kegg.jp/conv/uniprot/eco:b0002"
```

## Local tables (optional)

Look up local mapping tables in `registry/references.yaml` when offline /
enrichment needs them. If missing, ask the user — do not invent. Useful for
`stats-enrichment`.

## Agent procedure

1. Prefer REST for ID lookup; local files for bulk mapping when available.
2. Save responses under `analysis/annotation-kegg/`.
3. Do not invent KO/pathway associations.
4. Rate-limit politely; no scraping beyond the documented API.
