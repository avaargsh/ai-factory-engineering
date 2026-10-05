#!/usr/bin/env bash
set -euo pipefail

MANIFEST="${MANIFEST:-}"
ATTESTATION_KEY_ID="${ATTESTATION_KEY_ID:-}"
LAB_ARTIFACTS="${LAB_ARTIFACTS:-.artifacts/real-gpu-lab/$(date -u +%Y%m%dT%H%M%SZ)}"

if [[ -z "$MANIFEST" ]]; then
  echo "MANIFEST=/path/to/site-controlled-lab.json is required" >&2
  exit 2
fi
if [[ -z "$ATTESTATION_KEY_ID" ]]; then
  echo "ATTESTATION_KEY_ID is required" >&2
  exit 2
fi
if [[ -z "${AI_FACTORY_ATTESTATION_SECRET:-}" ]]; then
  echo "AI_FACTORY_ATTESTATION_SECRET is required" >&2
  exit 2
fi
if [[ ! -f "$MANIFEST" ]]; then
  echo "controlled-lab manifest not found: $MANIFEST" >&2
  exit 2
fi
if [[ -e "$LAB_ARTIFACTS" ]]; then
  echo "LAB_ARTIFACTS already exists: $LAB_ARTIFACTS" >&2
  exit 2
fi

python - "$MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
doc = json.loads(path.read_text(encoding="utf-8"))
if doc.get("evidenceMode") != "real-hardware":
    raise SystemExit(
        "real GPU controlled-lab requires evidenceMode=real-hardware"
    )

collectors = {
    str(item.get("collector"))
    for item in doc.get("tests", [])
    if isinstance(item, dict)
}
if not collectors.intersection({"gpu_csv", "dcgm"}):
    raise SystemExit("real GPU lab requires a GPU telemetry collector")
if "inference" not in collectors:
    raise SystemExit("real GPU lab requires an inference collector")

for value in [
    str(doc.get("runId", "")),
    str(doc.get("topologyRef", "")),
    *(str(v) for v in doc.get("assetRefs", [])),
    *(str(v) for v in (doc.get("versionMatrix") or {}).values()),
]:
    lowered = value.lower()
    if any(marker in lowered for marker in (
        "change-me", "synthetic", "fixture", "example-only"
    )):
        raise SystemExit(f"real GPU lab contains non-real marker: {value}")
PY

python -m ai_factory_engineering.cli validate-lab-manifest "$MANIFEST"

mkdir -p "$LAB_ARTIFACTS"
SOURCE_COMMIT="$(git rev-parse HEAD)"
MANIFEST_SHA256="$(sha256sum "$MANIFEST" | awk '{print $1}')"

python - "$MANIFEST" "$LAB_ARTIFACTS/host-provenance.json" "$SOURCE_COMMIT" "$MANIFEST_SHA256" <<'PY'
import json
import os
import platform
import shutil
import socket
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
commands = []
for item in manifest.get("tests", []):
    command = item.get("command") or []
    executable = str(command[0]) if command else ""
    commands.append({
        "bundleId": item.get("bundleId"),
        "collector": item.get("collector"),
        "executable": executable,
        "resolvedExecutable": shutil.which(executable) if executable else None,
    })

payload = {
    "schemaVersion": 1,
    "kind": "RealHardwareControlledLabProvenance",
    "sourceCommit": sys.argv[3],
    "manifestSha256": "sha256:" + sys.argv[4],
    "hostname": socket.gethostname(),
    "platform": platform.platform(),
    "machine": platform.machine(),
    "python": platform.python_version(),
    "commands": commands,
}
Path(sys.argv[2]).write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

make lab-smoke   MANIFEST="$MANIFEST"   ATTESTATION_KEY_ID="$ATTESTATION_KEY_ID"   LAB_ARTIFACTS="$LAB_ARTIFACTS"

python - "$LAB_ARTIFACTS" "$SOURCE_COMMIT" "$MANIFEST_SHA256" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
artifact = json.loads(
    (root / "acceptance-artifact.json").read_text(encoding="utf-8")
)
run = json.loads(
    (root / "commissioning-run.json").read_text(encoding="utf-8")
)
provenance_path = root / "host-provenance.json"
provenance_sha = hashlib.sha256(provenance_path.read_bytes()).hexdigest()

if run.get("annotations", {}).get("evidenceMode") != "real-hardware":
    raise SystemExit("commissioning run lost real-hardware evidence mode")
if not artifact.get("accepted"):
    raise SystemExit("real GPU acceptance artifact is not accepted")

summary = {
    "schemaVersion": 1,
    "kind": "RealHardwareControlledLabReceipt",
    "sourceCommit": sys.argv[2],
    "manifestSha256": "sha256:" + sys.argv[3],
    "hostProvenanceSha256": "sha256:" + provenance_sha,
    "acceptanceArtifactDigest": artifact.get("digest"),
    "runId": run.get("runId"),
    "topologyRef": run.get("topologyRef"),
    "status": run.get("status"),
}
(root / "real-hardware-receipt.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, sort_keys=True))
PY

echo "real GPU controlled-lab evidence: $LAB_ARTIFACTS"
