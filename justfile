# OpenSCAD is whichever is first on PATH unless OPENSCAD names one.
openscad := env("OPENSCAD", "openscad")

# List the recipes.
default:
    @just --list

# Install the pinned libraries into .scadman/env.
setup:
    scadman sync

# Render every library file and fail on any error or warning; the files emit no geometry, the example does.
check: fmt-check
    #!/usr/bin/env bash
    set -uo pipefail
    export OPENSCADPATH="$PWD/.scadman/env"  # the pinned libraries only, whatever the shell sets
    "{{openscad}}" --version
    tmp=$(mktemp -d) && trap 'rm -rf "$tmp"' EXIT
    failed=0
    for f in custom/*.scad purchased/*.scad utils/*.scad examples/*.scad; do
        "{{openscad}}" -o "$tmp/out.csg" "$f" 2>"$tmp/err" >/dev/null
        if grep -qE '^(ERROR|WARNING)|Assertion' "$tmp/err"; then
            echo "FAIL  $f  $(grep -m1 -E '^(ERROR|WARNING)|Assertion' "$tmp/err")"
            failed=1
        else
            echo "ok    $f"
        fi
    done
    exit $failed

# Render the example to a mesh on CGAL, which reports a solid that is not 2-manifold.
test:
    #!/usr/bin/env bash
    set -uo pipefail
    export OPENSCADPATH="$PWD/.scadman/env"  # the pinned libraries only, whatever the shell sets
    tmp=$(mktemp -d) && trap 'rm -rf "$tmp"' EXIT
    backend=""
    case "$("{{openscad}}" --help 2>&1)" in *--backend*) backend="--backend=CGAL" ;; esac
    "{{openscad}}" $backend -o "$tmp/ports.stl" examples/ports.scad 2>"$tmp/err" >/dev/null
    if grep -qE '^(ERROR|WARNING)|Assertion' "$tmp/err" || [ ! -s "$tmp/ports.stl" ]; then
        echo "FAIL  examples/ports.scad"; grep -m3 -E '^(ERROR|WARNING)|Assertion' "$tmp/err"; exit 1
    fi
    echo "ok    examples/ports.scad renders to a 2-manifold mesh"

# Format the .scad sources with topiary (.topiary/languages.ncl)
fmt:
    git ls-files -z '*.scad' | xargs -0 -r topiary format

# Check the .scad sources are formatted, without changing them
fmt-check:
    git ls-files -z '*.scad' | xargs -0 -r -n1 topiary format --check
