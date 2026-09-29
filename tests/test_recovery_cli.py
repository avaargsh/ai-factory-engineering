import sys

import pytest

from ai_factory_engineering.cli import main


def test_recovery_cli_help_exposes_execute_as_opt_in(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["ai-factory", "recovery", "run", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--execute" in output
    assert "--slo-profile" in output
    assert "--output-dir" in output


def test_other_cli_commands_do_not_require_kubernetes(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ai-factory",
            "capacity",
            "--contract-mw", "8",
            "--pue", "1.2",
            "--rack-kw", "100",
            "--gpus-per-rack", "8",
        ],
    )
    main()
    assert "productive_gpu_hours" in capsys.readouterr().out
