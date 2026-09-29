PYTHON ?= python3
ARTIFACTS ?= .artifacts

.PHONY: setup test demo smoke clean

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

clean:
	rm -rf $(ARTIFACTS)
