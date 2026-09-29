from types import SimpleNamespace

import pytest

from ai_factory_engineering.providers import KubernetesPodFaultDriver


class FakeCoreApi:
    def __init__(self) -> None:
        self.deletes = []
        self.lists = 0

    def delete_namespaced_pod(self, **kwargs) -> None:
        self.deletes.append(kwargs)

    def list_namespaced_pod(self, **kwargs):
        self.lists += 1
        ready = self.lists >= 2
        condition = SimpleNamespace(type="Ready", status="True" if ready else "False")
        pod = SimpleNamespace(status=SimpleNamespace(conditions=[condition]))
        return SimpleNamespace(items=[pod])


def test_kubernetes_driver_uses_server_dry_run_by_default() -> None:
    api = FakeCoreApi()
    driver = KubernetesPodFaultDriver(core_api=api)

    driver.delete_pod(namespace="ai", pod="vllm-0", dry_run=True)

    assert api.deletes == [
        {"name": "vllm-0", "namespace": "ai", "dry_run": "All"}
    ]


def test_kubernetes_driver_requires_explicit_real_delete() -> None:
    api = FakeCoreApi()
    driver = KubernetesPodFaultDriver(core_api=api)

    driver.delete_pod(namespace="ai", pod="vllm-0", dry_run=False)

    assert api.deletes == [{"name": "vllm-0", "namespace": "ai"}]


def test_wait_replacement_ready_observes_ready_condition() -> None:
    api = FakeCoreApi()
    clock = iter([0.0, 0.0, 1.0, 1.0, 2.0])
    driver = KubernetesPodFaultDriver(
        core_api=api,
        monotonic=lambda: next(clock),
        sleep=lambda _: None,
    )

    ready_at = driver.wait_replacement_ready(
        namespace="ai", workload="vllm", timeout_s=10
    )

    assert ready_at == 1.0
    assert api.lists == 2
