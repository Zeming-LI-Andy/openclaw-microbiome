---
name: annotation-metacyc
description: >
  Query MetaCyc pathways, reactions, compounds, and genes via MetaCyc web services.
runtime: host
conda_env: mgx-base
tools:
  - python
  - curl
---

# MetaCyc web services

## Docs

https://metacyc.org/web-services.shtml  

Read that page for current XML/JSON endpoints and organism databases before calling.

## Agent procedure

1. Confirm which MetaCyc DB / organism the user needs.
2. Follow the official web-services docs for request shape.
3. Save responses under `analysis/annotation-metacyc/`.
4. Do not invent pathway membership.
