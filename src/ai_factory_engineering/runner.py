from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


class CollectorExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class Runner(Protocol):
    def run(self, command: Sequence[str], *, timeout_seconds: float = 60.0) -> CommandResult:
        ...


class LocalCommandRunner:
    def run(self, command: Sequence[str], *, timeout_seconds: float = 60.0) -> CommandResult:
        try:
            completed = subprocess.run(tuple(command), capture_output=True, text=True, timeout=timeout_seconds, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CollectorExecutionError(str(exc)) from exc
        result = CommandResult(tuple(command), completed.returncode, completed.stdout, completed.stderr)
        if result.returncode != 0:
            raise CollectorExecutionError(f"collector command failed rc={result.returncode}: {result.stderr.strip()}")
        return result


def persist_raw_artifact(*, output_dir: str | Path, name: str, content: str) -> dict[str, str]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    data = content.encode("utf-8")
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    return {"type": "raw-collector-output", "uri": str(path), "checksum": f"sha256:{digest}"}
