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



def test_local_runner_preserves_nonzero_process_output() -> None:
    with pytest.raises(CollectorExecutionError) as exc_info:
        LocalCommandRunner().run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "print('stdout-before-fail'); "
                    "print('stderr-before-fail', file=sys.stderr); "
                    "raise SystemExit(7)"
                ),
            ]
        )

    result = exc_info.value.result
    assert result is not None
    assert result.returncode == 7
    assert "stdout-before-fail" in result.stdout
    assert "stderr-before-fail" in result.stderr


def test_local_runner_preserves_partial_output_on_timeout() -> None:
    with pytest.raises(CollectorExecutionError) as exc_info:
        LocalCommandRunner().run(
            [
                sys.executable,
                "-u",
                "-c",
                (
                    "import sys,time; "
                    "print('stdout-before-timeout'); "
                    "print('stderr-before-timeout', file=sys.stderr); "
                    "time.sleep(5)"
                ),
            ],
            timeout_seconds=0.1,
        )

    result = exc_info.value.result
    assert result is not None
    assert result.returncode == -1
    assert "stdout-before-timeout" in result.stdout
    assert "stderr-before-timeout" in result.stderr
