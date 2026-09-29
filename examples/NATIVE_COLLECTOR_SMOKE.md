# Native Collector Smoke Path

The CLI already supports executing a native collector command and persisting its
stdout/stderr as evidence artifacts.

Example shape:

```bash
ai-factory run-collector dcgm \
  --output-dir .artifacts/dcgm \
  --bundle-id dcgm-smoke-001 \
  --test-ref dcgm-health \
  --topology-ref topology://local/smoke \
  -- bash -lc 'printf "gpu,health\n0,pass\n"'
```

For a real environment, replace the command after `--` with the approved DCGM,
NVLink, RDMA or NCCL command. The runner owns process execution and raw artifacts;
collector parsers normalize output; EvidenceBundle remains the contract consumed
by commissioning.

The full commissioning path is:

```text
native command
  -> LocalCommandRunner
  -> raw stdout/stderr artifact
  -> collector parser
  -> EvidenceBundle
  -> AcceptanceTest
  -> Gate DAG
  -> commissioning-run.json
  -> commissioning-report.md
```

Do not treat this smoke example as GPU validation. A production run must use the
actual vendor/system commands declared by the commissioning manifest.
