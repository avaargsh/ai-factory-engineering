import hashlib
import sys
from pathlib import Path

import pytest

from ai_factory_engineering.runner import (
    CollectorExecutionError,
    LocalCommandRunner,
    persist_raw_artifact,
)


def test_local_runner_captures_stdout() -> None:
    result = LocalCommandRunner().run(
        [sys.executable, "-c", "print('ok')"]
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_local_runner_fails_closed_on_nonzero_exit() -> None:
    with pytest.raises(CollectorExecutionError):
        LocalCommandRunner().run(
            [sys.executable, "-c", "raise SystemExit(7)"]
        )


def test_local_runner_rejects_empty_command() -> None:
    with pytest.raises(CollectorExecutionError):
        LocalCommandRunner().run([])


def test_raw_artifact_has_replayable_sha256(tmp_path: Path) -> None:
    artifact = persist_raw_artifact(
        output_dir=tmp_path,
        name="rdma.txt",
        content="port_xmit_discards: 0\n",
    )
    expected = hashlib.sha256(
        b"port_xmit_discards: 0\n"
    ).hexdigest()
    assert artifact["checksum"] == f"sha256:{expected}"
    assert Path(artifact["uri"]).read_text() == (
        "port_xmit_discards: 0\n"
    )
