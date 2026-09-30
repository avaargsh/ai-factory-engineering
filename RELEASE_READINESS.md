# v0.1 Release Readiness

## Release gate

A public v0.1 candidate should satisfy all of the following:

- [x] deterministic zero-hardware demo
- [x] real-command smoke entrypoint
- [x] raw artifacts preserved beside normalized evidence
- [x] fail-closed cross-layer acceptance
- [x] replay-verifiable AcceptanceArtifact
- [x] standard nccl-tests out-of-place / in-place parser coverage
- [x] explicit known limitations
- [x] repository license selected and added (Apache-2.0)
- [x] CONTRIBUTING.md added
- [x] public README internal links checked against repository tree
- [x] current-tree secret/token pattern scan clean
- [x] current-tree private/customer identifier spot-check clean
- [x] full git-history credential scan complete (gitleaks, redacted)
- [ ] full git-history private/customer-data review complete
- [x] direct dependency/license review complete
- [x] GitHub Actions runner issue documented
- [x] fresh-clone install, tests, deterministic demo and release verification complete
- [ ] controlled lab smoke run complete
- [x] v0.1.0 release notes prepared
- [x] stale pre-RC pull requests reconciled; no open pull requests remain at final RC audit
- [ ] v0.1.0 tag/release created

## Verified software baseline

- Exact main commit: `82104ee6bab450dbd54dbdf7f2450a116d287e1f`.
- [Push test](https://github.com/avaargsh/ai-factory-engineering/actions/runs/36685731973): passed.
- [Push release gate](https://github.com/avaargsh/ai-factory-engineering/actions/runs/36685731948): passed, including fresh installation, 128 tests, deterministic demo, release contract and full-history credential scan.
- Native command smoke retains the raw stdout bytes and verifies their SHA-256 checksum.
- Controlled hardware/lab smoke and the historical private-data review remain pending. Do not create the final v0.1.0 tag or describe synthetic results as real GPU/RDMA acceptance.

## Dependency/license review

Declared direct/build/dev dependencies are intentionally small:

- `jsonschema>=4.23` — MIT
- `pytest>=8.0` — MIT (development only)
- `hatchling>=1.25` — MIT (build backend)

No direct copyleft dependency was identified in the declared project metadata. Transitive dependencies should still be checked from a resolved lock/environment before a formal distribution review.

The package metadata explicitly declares `Apache-2.0` and includes `LICENSE`.

## Open-source audit

Before changing repository visibility:

1. Search history and current tree for credentials, tokens, private endpoints, customer names, internal hostnames, proprietary configs and copied vendor material.
2. Confirm all sample topology IDs, S3 URIs, node names and benchmark numbers are synthetic or safe to publish.
3. Verify no production evidence bundles or logs are committed.
4. Review third-party fixture provenance and licenses.
5. Run the deterministic demo from a fresh clone.
6. Run at least one site smoke test on a controlled lab environment and retain its artifacts outside git.
7. Confirm README claims match what has actually been exercised.

### Audit performed

Current default-branch code search returned no matches for representative credential patterns:
`BEGIN PRIVATE KEY`, `AKIA`, `ghp_`, `sk-`, `api_key`, `Bearer`, `ssh-rsa`, `password`.

Spot checks also returned no matches for generic customer markers or known prior-employer naming. Repository-tree review confirmed README-linked `DEVELOPMENT.md` and `RELEASE_READINESS.md` exist.

Full-history gitleaks scanning passed from a fresh clone with `fetch-depth: 0` and a pinned, checksum-verified scanner. This verifies the scanner's credential rules; it does not establish that every historical blob is free of private/customer information. That separate review remains open.

The final RC audit also reconciled stale pre-RC pull requests. Standard-format NCCL parser coverage was preserved on main rather than discarded with the old branch.

## Known limitations

- Reference adapters normalize a deliberately narrow evidence contract. Standard nccl-tests out-of-place and in-place rows are covered, but additional vendor/version output variants still require fixture-backed validation.
- HMAC attestation is a reference mechanism, not a production signing design.
- The 576-GPU case is a deterministic reference case, not proof of a live 576-GPU acceptance run.
- Site operators own command safety, maintenance windows and benchmark thresholds.
- Runtime SLO coverage currently centers on inference; training/model-progress acceptance is not yet first-class.
- Earlier Actions jobs failed before runner execution. Public main now executes the complete release gate successfully; new failures must be diagnosed from their actual job logs.

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for the v0.1.0 candidate notes.
