from ai_factory_engineering.runner import CommandResult, SshCommandRunner


class RecordingRunner:
    def __init__(self):
        self.command = None
        self.timeout = None

    def run(self, command, *, timeout_seconds=60.0):
        self.command = tuple(command)
        self.timeout = timeout_seconds
        return CommandResult(tuple(command), 0, "ok\n", "")


def test_ssh_runner_builds_argv_without_shell_string():
    local = RecordingRunner()
    runner = SshCommandRunner(host="gpu-01", user="ubuntu", port=2222, identity_file="/keys/gpu", local_runner=local)
    result = runner.run(["ethtool", "-S", "mlx5_0"], timeout_seconds=12)
    assert local.command == ("ssh", "-o", "BatchMode=yes", "-p", "2222", "-i", "/keys/gpu", "ubuntu@gpu-01", "ethtool", "-S", "mlx5_0")
    assert local.timeout == 12
    assert result.stdout == "ok\n"


def test_ssh_runner_supports_host_only_target():
    local = RecordingRunner()
    SshCommandRunner(host="gpu-02", local_runner=local).run(["nvidia-smi", "-L"])
    assert local.command == ("ssh", "-o", "BatchMode=yes", "gpu-02", "nvidia-smi", "-L")
