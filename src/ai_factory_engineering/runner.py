from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class CollectorExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        result: CommandResult | None = None,
    ) -> None:
        super().__init__(message)
        self.result = result


class Runner(Protocol):
    def run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: float = 60.0,
    ) -> CommandResult: ...


def _stream_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


class LocalCommandRunner:
    def run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: float = 60.0,
    ) -> CommandResult:
        if not command:
            raise CollectorExecutionError("collector command must not be empty")
        try:
            completed = subprocess.run(
                tuple(command),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = _stream_text(exc.stdout)
            stderr = _stream_text(exc.stderr)
            result = CommandResult(
                tuple(command),
                124,
                stdout,
                stderr or str(exc),
            )
            raise CollectorExecutionError(
                f"collector command timed out after {timeout_seconds}s",
                result=result,
            ) from exc
        except OSError as exc:
            result = CommandResult(
                tuple(command),
                -1,
                "",
                str(exc),
            )
            raise CollectorExecutionError(
                str(exc),
                result=result,
            ) from exc

        result = CommandResult(
            tuple(command),
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )
        if result.returncode != 0:
            raise CollectorExecutionError(
                f"collector command failed rc={result.returncode}: "
                f"{result.stderr.strip()}",
                result=result,
            )
        return result


def persist_raw_artifact(
    *,
    output_dir: str | Path,
    name: str,
    content: str,
    artifact_type: str = "raw-collector-output",
) -> dict[str, str]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    data = content.encode("utf-8")
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    return {
        "type": artifact_type,
        "uri": str(path),
        "checksum": f"sha256:{digest}",
    }


@dataclass(frozen=True)
class SshCommandRunner:
    host: str
    user: str | None = None
    port: int | None = None
    identity_file: str | None = None
    local_runner: Runner | None = None

    def run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: float = 60.0,
    ) -> CommandResult:
        if not command:
            raise CollectorExecutionError("collector command must not be empty")
        target = f"{self.user}@{self.host}" if self.user else self.host
        ssh_command: list[str] = ["ssh", "-o", "BatchMode=yes"]
        if self.port is not None:
            ssh_command.extend(["-p", str(self.port)])
        if self.identity_file is not None:
            ssh_command.extend(["-i", self.identity_file])
        ssh_command.append(target)
        ssh_command.extend(command)
        backend = self.local_runner or LocalCommandRunner()
        return backend.run(ssh_command, timeout_seconds=timeout_seconds)


@dataclass(frozen=True)
class KubernetesExecRunner:
    namespace: str
    pod: str
    container: str | None = None
    kubeconfig: str | None = None
    context: str | None = None
    local_runner: Runner | None = None

    def run(
        self,
        command: Sequence[str],
        *,
        timeout_seconds: float = 60.0,
    ) -> CommandResult:
        if not command:
            raise CollectorExecutionError("collector command must not be empty")
        kubectl_command: list[str] = ["kubectl"]
        if self.kubeconfig is not None:
            kubectl_command.extend(["--kubeconfig", self.kubeconfig])
        if self.context is not None:
            kubectl_command.extend(["--context", self.context])
        kubectl_command.extend(["exec", "-n", self.namespace, self.pod])
        if self.container is not None:
            kubectl_command.extend(["-c", self.container])
        kubectl_command.append("--")
        kubectl_command.extend(command)
        backend = self.local_runner or LocalCommandRunner()
        return backend.run(kubectl_command, timeout_seconds=timeout_seconds)
