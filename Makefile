PYTHON ?= python3
ARTIFACTS ?= .artifacts

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
	@test -n "$AI_FACTORY_ATTESTATION_SECRET" || (echo "AI_FACTORY_ATTESTATION_SECRET is required" && exit 2)
	$(PYTHON) -m ai_factory_engineering.cli validate-lab-manifest "$(MANIFEST)"
	rm -rf $(ARTIFACTS)/lab
	mkdir -p $(ARTIFACTS)/lab
	$(PYTHON) -m ai_factory_engineering.cli commission "$(MANIFEST)" --output-dir $(ARTIFACTS)/lab
	$(PYTHON) -m ai_factory_engineering.cli attest $(ARTIFACTS)/lab/acceptance-artifact.json --key-id "$(ATTESTATION_KEY_ID)" --output $(ARTIFACTS)/lab/acceptance-attestation.json
	$(PYTHON) -m ai_factory_engineering.cli verify-attestation $(ARTIFACTS)/lab/acceptance-artifact.json $(ARTIFACTS)/lab/acceptance-attestation.json --expected-key-id "$(ATTESTATION_KEY_ID)"

verify-release:
	$(PYTHON) scripts/verify_release.py

audit-history:
	sh scripts/audit_git_history.sh

clean:
	rm -rf $(ARTIFACTS)
