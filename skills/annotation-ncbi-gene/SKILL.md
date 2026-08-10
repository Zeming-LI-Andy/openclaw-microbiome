---
name: annotation-ncbi-gene
description: >
  Query NCBI Gene via Entrez E-utilities (esearch, esummary, efetch, elink).
runtime: host
conda_env: mcp_server
tools:
  - python
  - curl
---

# NCBI Gene (E-utilities)

## Base

`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

Always consider `tool=` and `email=` (and `api_key=` via `NCBI_API_KEY` when available).
Without a key, stay around ≤3 requests/second.

## Common calls

```bash
# Search
curl -sL "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=BRCA1[GENE]+AND+human[ORGN]&retmode=json"

# Summaries
curl -sL "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=672&retmode=json"

# Full record
curl -sL "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=672&retmode=xml"
```

Useful fields: `[GENE]`, `[ORGN]`, `[CHR]`. Chain with `usehistory=y` + `WebEnv` /
`query_key` for large results.

## Agent procedure

1. Build a precise `term`; URL-encode special characters.
2. esearch → esummary/efetch as needed.
3. Save under `analysis/annotation-ncbi-gene/`.
4. Metadata/lookup only unless the user asks for sequence download (separate step).
