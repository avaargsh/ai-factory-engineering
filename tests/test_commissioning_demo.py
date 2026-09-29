import runpy
from pathlib import Path


def test_576_gpu_demo_executes(capsys):
    path = Path(__file__).resolve().parents[1] / "examples/576_gpu_commissioning_demo.py"
    runpy.run_path(str(path), run_name="__main__")
    output = capsys.readouterr().out
    assert '"decision": "ACCEPT"' in output
    assert '"artifactVerified": true' in output
    assert '"attestationVerified": true' in output
