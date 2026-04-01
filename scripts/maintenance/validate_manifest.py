"""
scripts/validate_manifest.py — Manifest Integrity Validator (v1.0)

Validates that a format's manifest is consistent with the actual engine classes.
Catches configuration drift before it reaches the frontend.

Checks:
  1. Every `engine_method` exists on the declared `engine_class`
  2. Every `engine_class` is loadable from the format registry
  3. Every `output_type` is in the approved list
  4. Every `required_context` field exists in `context_fields`
  5. No duplicate `key` values (across all functions)
  6. All required manifest fields are present

Usage:
    python scripts/validate_manifest.py              # Validates all formats with manifests
    python scripts/validate_manifest.py --format odi  # Validates ODI only
"""
import sys
import os
import argparse

# Windows console needs UTF-8 for emoji output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)  # noqa: E402

from config.format_registry import FORMATS, get_format_manifest, get_format_engines  # noqa: E402


# ── Required fields per level ────────────────────────────────────────────
REQUIRED_MANIFEST_FIELDS = ["format_key", "format_label", "format_icon", "context_fields", "categories"]
REQUIRED_CATEGORY_FIELDS = ["key", "label", "icon", "group", "functions"]
REQUIRED_FUNCTION_FIELDS = ["key", "label", "engine_class", "engine_method", "required_context", "output_type"]
VALID_GROUPS = ["intelligence", "players", "operations", "system"]


def validate_manifest(format_type: str) -> list:
    """
    Validates a single format's manifest against its actual engine classes.

    Returns:
        list: List of error strings. Empty = all good.
    """
    errors = []

    # ── 1. Load Manifest ─────────────────────────────────────────────────
    try:
        manifest = get_format_manifest(format_type)
    except (KeyError, ValueError, ImportError) as e:
        return [f"❌ Cannot load manifest for '{format_type}': {e}"]

    # ── 2. Check Top-Level Fields ────────────────────────────────────────
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"❌ Missing top-level field: '{field}'")

    if errors:
        return errors  # Can't continue without basic structure

    # ── 3. Load Engines ──────────────────────────────────────────────────
    try:
        engine_classes = get_format_engines(format_type)
    except KeyError as e:
        return [f"❌ Cannot load engines for '{format_type}': {e}"]

    # ── 4. Collect Valid Context Fields ───────────────────────────────────
    valid_context_fields = set(manifest.get("context_fields", {}).keys())

    # ── 5. Collect Approved Output Types ─────────────────────────────────
    approved_output_types = set(manifest.get("output_types", []))
    if not approved_output_types:
        errors.append("⚠️  No 'output_types' list declared in manifest. Skipping output_type validation.")

    # ── 6. Walk Categories and Functions ─────────────────────────────────
    all_function_keys = []
    all_category_keys = []

    categories = manifest.get("categories", [])
    if not categories:
        errors.append("❌ Manifest has no categories.")
        return errors

    for cat_idx, category in enumerate(categories):
        cat_key = category.get("key", f"<unnamed_category_{cat_idx}>")

        # Check required category fields
        for field in REQUIRED_CATEGORY_FIELDS:
            if field not in category:
                errors.append(f"❌ Category '{cat_key}': Missing field '{field}'")

        # Check group value
        group = category.get("group", "")
        if group and group not in VALID_GROUPS:
            errors.append(f"⚠️  Category '{cat_key}': Invalid group '{group}'. Expected: {VALID_GROUPS}")

        # Check for duplicate category key
        if cat_key in all_category_keys:
            errors.append(f"❌ Duplicate category key: '{cat_key}'")
        all_category_keys.append(cat_key)

        # Walk functions
        functions = category.get("functions", [])
        if not functions:
            errors.append(f"⚠️  Category '{cat_key}' has no functions.")

        for fn_idx, fn in enumerate(functions):
            fn_key = fn.get("key", f"<unnamed_fn_{fn_idx}>")
            fn_label = f"{cat_key}/{fn_key}"

            # Check required function fields
            for field in REQUIRED_FUNCTION_FIELDS:
                if field not in fn:
                    errors.append(f"❌ Function '{fn_label}': Missing field '{field}'")

            # Check for duplicate function key
            if fn_key in all_function_keys:
                errors.append(f"❌ Duplicate function key: '{fn_key}'")
            all_function_keys.append(fn_key)

            # ── Validate engine_class exists ─────────────────────────────
            engine_class_name = fn.get("engine_class", "")
            if engine_class_name and engine_class_name not in engine_classes:
                errors.append(
                    f"❌ Function '{fn_label}': engine_class '{engine_class_name}' "
                    f"not found. Available: {list(engine_classes.keys())}"
                )
                continue  # Can't validate method if class doesn't exist

            # ── Validate engine_method exists on engine class ────────────
            engine_method = fn.get("engine_method", "")
            if engine_class_name and engine_method:
                cls = engine_classes.get(engine_class_name)
                if cls and not hasattr(cls, engine_method):
                    # Get all public methods for helpful error message
                    public_methods = [
                        m for m in dir(cls)
                        if not m.startswith("_") and callable(getattr(cls, m, None))
                    ]
                    errors.append(
                        f"❌ Function '{fn_label}': method '{engine_method}' "
                        f"NOT FOUND on {engine_class_name}. "
                        f"Available methods: {public_methods}"
                    )

            # ── Validate output_type ─────────────────────────────────────
            output_type = fn.get("output_type", "")
            if approved_output_types and output_type and output_type not in approved_output_types:
                errors.append(
                    f"❌ Function '{fn_label}': output_type '{output_type}' "
                    f"not in approved list: {sorted(approved_output_types)}"
                )

            # ── Validate required_context fields ─────────────────────────
            required_context = fn.get("required_context", [])
            for ctx_field in required_context:
                if ctx_field not in valid_context_fields:
                    errors.append(
                        f"❌ Function '{fn_label}': required_context '{ctx_field}' "
                        f"not declared in context_fields. "
                        f"Available: {sorted(valid_context_fields)}"
                    )

    return errors


def run_validation(target_format: str = None):
    """
    Runs validation for one or all formats.

    Args:
        target_format: If specified, validate only this format. Otherwise, validate all.
    """
    formats_to_check = [target_format] if target_format else list(FORMATS.keys())
    total_errors = 0
    total_passed = 0
    total_skipped = 0

    print("=" * 70)
    print("🔍 MANIFEST VALIDATOR — Checking manifest ↔ engine integrity")
    print("=" * 70)

    for fmt in formats_to_check:
        print(f"\n📋 Validating: {fmt.upper()} ({FORMATS[fmt]['label']})")
        print("-" * 50)

        # Check if manifest exists
        try:
            get_format_manifest(fmt)
        except (ValueError, ImportError):
            print("   ⏭️  No manifest found — SKIPPED")
            total_skipped += 1
            continue

        errors = validate_manifest(fmt)

        if not errors:
            # Get stats for the passing report
            manifest = get_format_manifest(fmt)
            num_cats = len(manifest.get("categories", []))
            num_fns = sum(len(c.get("functions", [])) for c in manifest.get("categories", []))
            print(f"   ✅ PASSED — {num_cats} categories, {num_fns} functions validated")
            total_passed += 1
        else:
            for err in errors:
                print(f"   {err}")
            total_errors += len(errors)

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    if total_errors == 0:
        print(f"✅ ALL CLEAR — {total_passed} format(s) passed, {total_skipped} skipped, 0 errors")
    else:
        print(f"❌ FAILED — {total_errors} error(s) found across {len(formats_to_check)} format(s)")
    print("=" * 70)

    return total_errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate format manifests against engine classes.")
    parser.add_argument("--format", "-f", type=str, default=None,
                        help="Format to validate (e.g., 'odi'). Validates all if not specified.")
    args = parser.parse_args()

    error_count = run_validation(args.format)
    sys.exit(1 if error_count > 0 else 0)
