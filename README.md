# ProtocolPilot (RUO)

Convert papers/preprints into draft, **research-use-only** lab protocols with a structured schema, auto-generated Bill of Materials (BOM), guardrails, and CI. Designed to pair with async agents (e.g., Open SWE) that open pull requests instead of just chatting.

## Quick start

**Requirements**: Python 3.11+, GitHub repo, (optional) Open SWE + Daytona for async runs.

```bash
# Clone and set up
uv venv -p 3.11  # or python -m venv .venv
source .venv/bin/activate
pip install -U uv || true
uv pip install -e .
pre-commit install
pytest -q
```

## Typical flow
1. Open a GitHub Issue using the "ProtocolPilot task" template and include links to PDFs/DOIs and constraints.
2. Agent (or you) runs the extractor → planner → programmer → reviewer flow.
3. A PR adds `protocols/<slug>.md`, `env/conda.yaml` (optional), `tests/` updates, and a BOM JSON/CSV.
4. You edit, request changes, and merge when satisfied.

## Open SWE integration (labels)
- Add labels from `labels.json` to your repo.
- To run **with plan approval**: label an Issue `open-swe`.
- To run **auto-execute**: label `open-swe-auto` (use sparingly).

## Safety & scope
- RUO only; no patient data; no diagnostic/treatment claims.
- PRs include a RUO disclaimer and the guardrails checker blocks unsafe language.

## Commands
```bash
# Validate a protocol Markdown against the schema
python -m protocol_pilot.extract --validate protocols/examples/qPCR.md

# Generate a BOM stub from a protocol (to JSON)
python -m protocol_pilot.bom protocols/examples/qPCR.md --out bom.json
```

## Contributing
- Keep protocol steps numbered, measurable, and source-cited.
- Prefer SI units and temperatures in °C.
- Use PRs; auto-merge should remain off.
