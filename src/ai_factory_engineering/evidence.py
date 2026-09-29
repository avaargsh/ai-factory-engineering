from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping


def build_evidence_bundle(*, bundle_id:str,test_ref:str,topology_ref:str,collector:str,collector_version:str,measurements:Mapping[str,float],artifacts:list[dict]|None=None,version_matrix:Mapping[str,str]|None=None,asset_refs:list[str]|None=None)->dict:
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    return {"apiVersion":"aifactory.engineering/v1alpha1","kind":"EvidenceBundle","metadata":{"bundleId":bundle_id,"startedAt":now,"endedAt":now},"testRef":test_ref,"environment":{"topologyRef":topology_ref,"versionMatrix":dict(version_matrix or {})},"measurements":dict(measurements),"artifacts":artifacts or [],"provenance":{"collector":collector,"collectorVersion":collector_version,"collectedAt":now,"assetRefs":asset_refs or []}}
