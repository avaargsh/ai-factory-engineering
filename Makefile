PYTHON ?= python3
ARTIFACTS ?= .artifacts
LAB_ARTIFACTS ?= $(ARTIFACTS)/lab

.PHONY: setup test demo smoke lab-smoke verify-release audit-history clean

setup:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

demo:
	mkdir -p $(ARTIFACTS)/demo
	$(PYTHON) examples/576_gpu_commissioning_demo.py | tee $(ARTIFACTS)/demo/acceptance.json

smoke:
	@test -n "$(MANIFEST)" || (echo "MANIFEST=path/to/site.json is required" && exit 2)
	mkdir -p $(ARTIFACTS)/smoke
	$(PYTHON) -m ai_factory_engineering.cli commission "$(MANIFEST)" --output-dir $(ARTIFACTS)/smoke

lab-smoke:
	@test -n "$(MANIFEST)" || (echo "MANIFEST=path/to/site.json is required" && exit 2)
	@test -n "$(ATTESTATION_KEY_ID)" || (echo "ATTESTATION_KEY_ID is required" && exit 2)
	@test -n "${AI_FACTORY_ATTESTATION_SECRET:-}" || (echo "AI_FACTORY_ATTESTATION_SECRET is required" && exit 2)
	@test ! -e "$(LAB_ARTIFACTS)" || (echo "LAB_ARTIFACTS=$(LAB_ARTIFACTS) already exists; choose a new output path to preserve prior evidence" && exit 2)
	$(PYTHON) -m ai_factory_engineering.cli validate-lab-manifest "$(MANIFEST)"
	mkdir -p "$(LAB_ARTIFACTS)"
	$(PYTHON) -m ai_factory_engineering.cli commission "$(MANIFEST)" --output-dir "$(LAB_ARTIFACTS)"
	$(PYTHON) -m ai_factory_engineering.cli attest "$(LAB_ARTIFACTS)/acceptance-artifact.json" --key-id "$(ATTESTATION_KEY_ID)" --output "$(LAB_ARTIFACTS)/acceptance-attestation.json"
	$(PYTHON) -m ai_factory_engineering.cli verify-attestation "$(LAB_ARTIFACTS)/acceptance-artifact.json" "$(LAB_ARTIFACTS)/acceptance-attestation.json" --expected-key-id "$(ATTESTATION_KEY_ID)"

verify-release:
	$(PYTHON) scripts/verify_release.py

audit-history:
	sh scripts/audit_git_history.sh

clean:
	rm -rf $(ARTIFACTS)
