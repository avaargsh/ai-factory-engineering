# v0.1 Release Readiness

## Release gate

A public v0.1 candidate should satisfy all of the following:

- [x] deterministic zero-hardware demo
- [x] real-command smoke entrypoint
- [x] raw artifacts preserved beside normalized evidence
- [x] fail-closed cross-layer acceptance
- [x] replay-verifiable AcceptanceArtifact
- [x] explicit known limitations
- [x] repository license selected and added (Apache-2.0)
- [x] CONTRIBUTING.md added
- [ ] public README links/screenshots checked
- [x] current-tree secret/token pattern scan clean
- [x] current-tree private/customer identifier spot-check clean
- [ ] full git-history secret/private-data scan complete
- [ ] dependency/license review complete
- [x] GitHub Actions runner issue documented
- [ ] fresh-clone demo verification complete
- [ ] controlled lab smoke run complete
- [ ] v0.1.0 tag/release notes prepared

## Open-source audit

Before changing repository visibility:

1. Search history and current tree for credentials, tokens, private endpoints, customer names, internal hostnames, proprietary configs and copied vendor material.
2. Confirm all sample topology IDs, S3 URIs, node names and benchmark numbers are synthetic or safe to publish.
3. Verify no production evidence bundles or logs are committed.
4. Review third-party fixture provenance and licenses.
5. Run the deterministic demo from a fresh clone.
6. Run at least one site smoke test on a controlled lab environment and retain its artifacts outside git.
7. Confirm README claims match what has actually been exercised.

### Audit performed in this hardening pass

Current default-branch code search returned no matches for representative credential patterns:

`BEGIN PRIVATE KEY`, `AKIA`, `ghp_`, `sk-`, `api_key`, `Bearer`, `ssh-rsa`, `password`.

Spot checks also returned no matches for generic customer markers or known prior-employer naming.

This is a current-tree search only. It does **not** prove that unreachable/old git history is clean. A local full-history scanner such as gitleaks/trufflehog remains required before repository visibility changes.

## Known limitations

- Reference adapters normalize a narrow evidence contract; vendor output variants still need parser hardening.
- HMAC attestation is a reference mechanism, not a production signing design.
- The 576-GPU case is a deterministic reference case, not proof of a live 576-GPU acceptance run.
- Site operators own command safety, maintenance windows and benchmark thresholds.
- Runtime SLO coverage currently centers on inference; training/model-progress acceptance is not yet first-class.
- GitHub Actions has recently shown jobs failing before execution with no steps/logs; treat that as CI infrastructure state until runner execution is restored.

## Suggested v0.1 release note

**AI Factory Engineering v0.1** establishes an executable cross-layer commissioning contract from native GPU/fabric/runtime evidence through fail-closed gates to a replay-verifiable acceptance artifact. It is intended as a reference engineering toolkit, not a replacement for vendor diagnostics or site-specific commissioning procedures.
