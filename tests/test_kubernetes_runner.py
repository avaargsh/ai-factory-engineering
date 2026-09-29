from ai_factory_engineering.runner import CommandResult, KubernetesExecRunner


class RecordingRunner:
    def __init__(self):
        self.command = None
        self.timeout = None

    def run(self, command, *, timeout_seconds=60.0):
        self.command = tuple(command)
        self.timeout = timeout_seconds
        return CommandResult(tuple(command), 0, "ok\n", "")


def test_kubernetes_runner_builds_explicit_exec_boundary():
    local = RecordingRunner()
    runner = KubernetesExecRunner(namespace="ai", pod="gpu-debug-0", container="tools", kubeconfig="/cfg/kube", context="prod", local_runner=local)
    result = runner.run(["nvidia-smi", "-L"], timeout_seconds=15)
    assert local.command == ("kubectl", "--kubeconfig", "/cfg/kube", "--context", "prod", "exec", "-n", "ai", "gpu-debug-0", "-c", "tools", "--", "nvidia-smi", "-L")
    assert local.timeout == 15
    assert result.stdout == "ok\n"


def test_kubernetes_runner_minimal_target():
    local = RecordingRunner()
    KubernetesExecRunner(namespace="commissioning", pod="nccl-0", local_runner=local).run(["all_reduce_perf", "-b", "8M"])
    assert local.command == ("kubectl", "exec", "-n", "commissioning", "nccl-0", "--", "all_reduce_perf", "-b", "8M")
