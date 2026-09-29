# Contributing

Thanks for your interest in improving this project.

## Before opening a change

- Keep changes small and focused.
- Preserve the current architecture boundaries; do not add a new framework/runtime abstraction unless an existing seam cannot express the requirement.
- Do not commit credentials, production logs, customer identifiers, private endpoints, proprietary configs, or copied vendor material.
- Add or update tests for behavior changes.
- Keep demo data synthetic and clearly labelled.

## Development

```bash
make setup
make test
make demo
```

For environment-dependent validation, use the documented smoke path rather than weakening deterministic unit tests.

## Pull requests

A pull request should explain:

1. what changed,
2. why the existing design was insufficient,
3. which contract or invariant is affected,
4. how the change was tested,
5. any new operational or security assumptions.

## Compatibility

v0.x interfaces may evolve. Prefer additive changes and explicit migration notes, but backward compatibility is not guaranteed before v1.0.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
