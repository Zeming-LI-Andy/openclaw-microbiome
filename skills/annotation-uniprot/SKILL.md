---
name: annotation-uniprot
description: >
  Query UniProtKB via REST for protein accessions, function text, and ID mapping.
runtime: host
conda_env: mgx-base
tools:
  - python
  - curl
---

# UniProtKB REST

## Docs / base

- Server: `https://rest.uniprot.org/`
- Entry by accession: `GET /uniprotkb/{accession}`
- Field list: https://rest.uniprot.org/configure/uniprotkb/result-fields
- Broader docs: UniProt REST help on uniprot.org

Examples:

```bash
curl -sL "https://rest.uniprot.org/uniprotkb/P05067.json"
curl -sL "https://rest.uniprot.org/uniprotkb/P05067?fields=accession,protein_name,cc_function,ft_binding"
curl -sL "https://rest.uniprot.org/uniprotkb/search?query=gene:TP53+AND+organism_id:9606&format=json&size=5"
```

## Agent procedure

1. Confirm accession or search query with the user.
2. Fetch only needed `fields` when possible.
3. Save JSON/TSV under `analysis/annotation-uniprot/`.
4. Respect rate limits; do not fabricate annotations.
