---
name: manifest-contract-verifier
description: Trigger this skill whenever manifest.py or any engine file in formats/ is updated to verify that implementation matches the UI contract.
---

# Manifest Contract Verifier

Use this skill to enforce the Manifest-Driven UI contract between `formats/*/manifest.py` and engine implementations.

## Scope

- Single responsibility: verify manifest `engine_class`/`engine_method` contracts and required-context parameter compatibility.
- Zero-context assumption: parse manifest and engine files fresh on each run.
- Validate across all categories/functions in the target manifest.

## AST Verification Rules

1. Parse `MANIFEST` from `manifest.py` using Python `ast`.
2. Parse engine files in the same format folder using Python `ast` and build:
- class name -> method name -> parameter names
3. For each function entry in every category:
- Ensure `engine_class` exists.
- Ensure `engine_method` exists on that class.
- Ensure each `required_context` field maps to a compatible method parameter alias.
  `venue` must map to a venue-like parameter (`venue`, `venue_id`, `stadium_name`, etc.).
4. Output:
- `Pass` if no contract violations
- `Fail` with rule ids and function locations when violations are found

## Command

```powershell
python "core/gen_ai/skills/manifest-contract-verifier/scripts/run_verifier.py" --root "." --manifest "formats/odi/manifest.py"
```

## Test (Expected Pass)

```powershell
python "core/gen_ai/skills/manifest-contract-verifier/scripts/run_verifier.py" --root "." --manifest "formats/odi/manifest.py"
```

Expected output:

```text
Pass
```

If `engine_method` in manifest is renamed (for example `analyze_venue_bias`) but the class implementation is not updated, this verifier returns `Fail`.
