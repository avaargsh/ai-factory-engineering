# Real-command commissioning quick start

Copy `real-command-commissioning.template.json` to a site-specific manifest and replace every `CHANGE-ME` value.

Then run:

```bash
ai-factory commission acceptance/examples/my-site-commissioning.json \
  --output-dir .artifacts/site-commissioning
```

The manifest deliberately keeps commands explicit. Verify them against the installed NVIDIA, RDMA and NCCL tool versions before use. Do not copy benchmark thresholds from another topology.

Expected outputs:

- `commissioning-run.json` — machine-readable gate/result document
- `commissioning-report.md` — operator-facing report
- per-test raw stdout/stderr and EvidenceBundle artifacts under the output directory

A failed command, missing evidence or failed acceptance test must remain fail-closed.
