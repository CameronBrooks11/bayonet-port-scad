# Changelog

## Unreleased

- The `.scad` files are formatted with topiary 0.8.0 at a 4-space indent; `just check` checks it.
- `just test` also renders the pin and lock halves of every interface and checks each one.
- CI moves onto the dev-toolbox templates, adding a docs site; `just images` renders the README picture.

## v0.1.0

- The port system of open-source-bioreactor at f3c35f0, unchanged: `bayonet_port()` and its probe,
  thermocouple and baffle variants, the interface records, the flex collet, the o-ring and Atlas
  probe registries, the o-ring gland, NPT threads and their helpers.
- `scadman.toml` pins bayonet-lock-scad v0.12.0 and threads-scad 4ae9aeb.
- `examples/ports.scad`, and `just check` and `just test` in CI on OpenSCAD 2026.10.15.
