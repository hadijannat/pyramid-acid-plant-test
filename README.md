# Pyramid

A neutral, quantitative test of Geoffrey Drumm's "Land of Chem" hypothesis, which holds that the Great Pyramid operated as a sulfuric-acid plant. Every number and every claim lives in a sourced ledger (`ledger/`), and the Tier 0 screening table, the parametric geometry of the interior and the browser viewer are all computed from it.

## Tests

```
uv run pytest -W error
```

## Regenerating the results

Run the three commands from the repository root, in this order:

```
uv run python -m pyramid.screening          # results/tier0/: the Tier 0 table and the first verdicts
uv run python -m pyramid.geometry.export    # results/geometry/: STEP files of both levels (ignored by git)
uv run python -m pyramid.viewer_data        # viewer/data/: the viewer's models, claims and cycle
```

Generated files are regenerated on a clean tree, after the commit that changes the code or the ledger, and are committed separately. The `manifest.json` beside them then records the commit that produced them. A test fails while `results/tier0` or `viewer/data` was generated from another ledger than the one in the repository.

## Viewer

```
python3 -m http.server 8765 --directory viewer
```

Then open http://localhost:8765/. The viewer animates the cycle as claimed and shows a verdict per step. It is an animation of the claim, not a simulation result.
