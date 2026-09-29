from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class KubernetesPodFaultDriver:
    core_api: Any
    monotonic: Callable[[], float] = time.monotonic
    sleep: Callable[[float], None] = time.sleep
    poll_interval_s: float = 1.0

    def delete_pod(self, *, namespace: str, pod: str, dry_run: bool = True) -> None:
        kwargs = {"name": pod, "namespace": namespace}
        if dry_run:
            kwargs["dry_run"] = "All"
        self.core_api.delete_namespaced_pod(**kwargs)

    def wait_replacement_ready(
        self, *, namespace: str, workload: str, timeout_s: float
    ) -> float:
        started = self.monotonic()
        while self.monotonic() - started <= timeout_s:
            pods = self.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={workload}",
            )
            for pod in pods.items:
                conditions = getattr(pod.status, "conditions", None) or []
                ready = any(
                    getattr(item, "type", None) == "Ready"
                    and getattr(item, "status", None) == "True"
                    for item in conditions
                )
                if ready:
                    return self.monotonic()
            self.sleep(self.poll_interval_s)
        raise TimeoutError(
            f"replacement workload {namespace}/{workload} not Ready within {timeout_s}s"
        )


@dataclass(frozen=True)
class HttpMetricsSource:
    metrics_url: str
    timeout_s: float = 5.0

    def scrape(self) -> str:
        with urllib.request.urlopen(self.metrics_url, timeout=self.timeout_s) as response:
            if response.status != 200:
                raise RuntimeError(f"metrics scrape returned HTTP {response.status}")
            return response.read().decode("utf-8")
