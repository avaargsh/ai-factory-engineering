# Release verification

Run these commands from a fresh, real Git clone before creating `v0.1.0`:

```bash
make setup
make verify-release
make audit-history
```

`make verify-release` checks package release metadata, runs the complete pytest suite and executes the deterministic demo. A successful run writes `.artifacts/release/verification.json`.

`make audit-history` scans the real Git history with gitleaks when available, otherwise trufflehog. It exits with status 2 if neither scanner is installed; absence of a scanner is never treated as success.

The environment-dependent commissioning smoke remains a separate release gate:

```bash
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

Do not create the public release tag merely because the deterministic verifier passed; record the history audit and controlled smoke result separately.
