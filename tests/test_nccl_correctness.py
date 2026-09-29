from ai_factory_engineering.collectors.nccl import parse_nccl_tests, summarize_nccl


def test_normalized_nccl_error_column_is_preserved():
    raw = "8388608 2097152 float sum -1 75.0 111.0 112.35 2\n"
    samples = parse_nccl_tests(raw)
    assert samples[0].wrong == 2
    assert summarize_nccl(samples)["nccl_wrong_total"] == 2.0


def test_nccl_wrong_total_sums_all_rows():
    raw = ("4194304 1048576 float sum -1 40 90 91 1\n"
           "8388608 2097152 float sum -1 75 111 112.35 2\n")
    assert summarize_nccl(parse_nccl_tests(raw))["nccl_wrong_total"] == 3.0
