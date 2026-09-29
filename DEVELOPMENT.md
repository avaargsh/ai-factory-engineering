# Developer workflow

```bash
make setup
make test
make demo
```

The demo is deterministic and does not require GPU hardware. Its output is written to `.artifacts/demo/acceptance.json`.

For a real site smoke run, copy and edit `acceptance/examples/real-command-commissioning.template.json`, then:

```bash
make smoke MANIFEST=acceptance/examples/my-site-commissioning.json
```

`make smoke` executes the native commands declared in that manifest. Review every command and acceptance baseline before running it on a production or shared GPU environment.
