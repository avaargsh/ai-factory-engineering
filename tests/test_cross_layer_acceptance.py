from ai_factory_engineering.cross_layer_acceptance import (
    AcceptanceDisposition,
    decide_cross_layer_acceptance,
)
from ai_factory_engineering.commissioning import (
    GateSpec,
    GateStatus,
    TestOutcome,
)


GATES = (
    GateSpec(id="gpu", layer="gpu", tests=("dcgm",)),
    GateSpec(
        id="fabric",
        layer="fabric",
        tests=("nccl",),
        depends_on=("gpu",),
    ),
    GateSpec(
        id="runtime",
        layer="runtime",
        tests=("slo",),
        depends_on=("fabric",),
    ),
)


def test_accepts_only_when_every_cross_layer_gate_passes():
    decision = decide_cross_layer_acceptance(
        GATES,
        {
            "gpu": (TestOutcome("dcgm", GateStatus.PASS),),
            "fabric": (TestOutcome("nccl", GateStatus.PASS),),
            "runtime": (TestOutcome("slo", GateStatus.PASS),),
        },
    )

    assert decision.accepted is True
    assert decision.disposition == AcceptanceDisposition.ACCEPT
    assert [gate.status for gate in decision.gates] == [
        GateStatus.PASS,
        GateStatus.PASS,
        GateStatus.PASS,
    ]


def test_missing_evidence_rejects_and_blocks_downstream_gate():
    decision = decide_cross_layer_acceptance(
        GATES,
        {
            "gpu": (TestOutcome("dcgm", GateStatus.PASS),),
            "fabric": (
                TestOutcome(
                    "nccl",
                    GateStatus.PASS,
                    evidence_complete=False,
                ),
            ),
            "runtime": (TestOutcome("slo", GateStatus.PASS),),
        },
    )

    assert decision.accepted is False
    assert decision.disposition == AcceptanceDisposition.REJECT
    assert [gate.status for gate in decision.gates] == [
        GateStatus.PASS,
        GateStatus.FAIL,
        GateStatus.BLOCKED,
    ]


def test_pending_test_never_becomes_false_green():
    decision = decide_cross_layer_acceptance(
        (GateSpec(id="gpu", layer="gpu", tests=("dcgm",)),),
        {"gpu": (TestOutcome("dcgm", GateStatus.PENDING),)},
    )

    assert decision.accepted is False
    assert decision.disposition == AcceptanceDisposition.REJECT
    assert decision.gates[0].status == GateStatus.BLOCKED
