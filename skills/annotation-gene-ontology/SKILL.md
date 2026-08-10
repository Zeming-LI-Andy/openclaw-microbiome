---
name: annotation-gene-ontology
description: >
  Query Gene Ontology (GO) via the Gene Ontology REST API for terms, gene
  products, and annotations.
runtime: host
conda_env: mcp_server
tools:
  - python
  - curl
---

# Gene Ontology REST

## Docs

API overview: https://api.geneontology.org/#/

Use documented endpoints for ontology terms, gene products, and annotations.
Read the OpenAPI/docs page before inventing paths.

Example starting points (verify against current docs):

```bash
curl -sL "https://api.geneontology.org/api/ontology/term/GO:0008150"
```

## Agent procedure

1. Open/fetch the API docs if unsure of the exact route.
2. Query the minimal endpoint for the user’s question.
3. Save results under `analysis/annotation-gene-ontology/`.
4. Do not invent GO term definitions or gene–term links.
