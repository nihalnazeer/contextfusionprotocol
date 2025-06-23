from typing import Dict, List, Any

# Schema-based metadata for each version
SCHEMA_RULES = {
    "1.0.0": {
        "required": ["schema_version", "pipeline_id", "files", "final_query"],
        "optional": ["missing_value_check", "default_fill_value", "description"],
        "repeatable": ["files", "files[].features"],
    },
    "2.0.0": {
        "required": ["schema_version", "pipeline_id", "files", "final_query", "created_by", "created_at", "global_settings"],
        "optional": ["context_settings", "missing_value_check", "default_fill_value", "description" ],
        "repeatable": ["files", "files[].features", "preprocessing_hooks", "postprocessing_hooks"],
    },
    "2.0.0-coc": {
        "required": ["schema_version", "pipeline_id", "files", "final_query", "created_by", "created_at", "global_settings", "context_settings", "chain_of_command"],
        "optional": ["missing_value_check", "default_fill_value", "description"],
        "repeatable": ["files", "files[].features", "preprocessing_hooks", "postprocessing_hooks", "depends_on"],
        "required_per_file": ["execution_order"],
    },
}


def run_post_schema_rules(context_input: Dict[str, Any]) -> None:
    """
    Validates input against version-specific schema rules after JSON schema validation.
    Raises an exception with all errors if validation fails.
    """
    version = context_input.get("schema_version", "1.0.0")
    rules = SCHEMA_RULES.get(version)

    if not rules:
        raise ValueError(f" Unsupported schema version: {version}")

    errors: List[str] = []

    # Check required fields at root level
    for field in rules["required"]:
        if field not in context_input:
            errors.append(f"Missing required field: {field}")

    # Check file-specific rules
    for file in context_input.get("files", []):
        file_id = file.get("file_id", "unknown")

        # Version-specific file checks
        if version == "2.0.0-coc":
            if "required_per_file" in rules:
                for field in rules["required_per_file"]:
                    if field not in file:
                        errors.append(f"Missing '{field}' in file: {file_id}")

            if "depends_on" in file and not isinstance(file["depends_on"], list):
                errors.append(f"'depends_on' must be a list in file: {file_id}")

        # API-specific checks
        if file.get("file_type") == "api" and "headers" not in file:
            errors.append(f"'headers' required for API file: {file_id}")

    # Check repeatable fields (basic validation, can be extended)
    for repeatable in rules.get("repeatable", []):
        if repeatable.startswith("files[]."):
            subfield = repeatable.split(".")[1]
            for file in context_input.get("files", []):
                if subfield in file and not isinstance(file[subfield], list):
                    errors.append(f"'{subfield}' must be a list in file: {file.get('file_id', 'unknown')}")

    if errors:
        raise ValueError(" Schema rules failed:\n" + "\n".join(errors))


def suggest_upgrade(current_version: str, target_version: str) -> None:
    """
    Suggests required fields to add when upgrading from current_version to target_version.
    Prints guidance to stdout (can be adapted for other outputs).
    """
    if current_version not in SCHEMA_RULES:
        raise ValueError(f" Unknown current version: {current_version}")
    if target_version not in SCHEMA_RULES:
        raise ValueError(f" Unknown target version: {target_version}")

    current_required = set(SCHEMA_RULES[current_version]["required"])
    target_required = set(SCHEMA_RULES[target_version]["required"])
    new_required = target_required - current_required

    if not new_required:
        print(f"🆙 No new required fields when upgrading from {current_version} to {target_version}.")
        return

    print(f"🆙 To upgrade from {current_version} → {target_version}, you must add:")
    for field in sorted(new_required):
        print(f"  🔸 {field}")


def print_rule_summary() -> None:
    """
    Prints a table summarizing required/optional fields across schema versions.
    Useful for CLI or documentation generation.
    """
    all_fields = sorted(
        set().union(
            *[
                set(r["required"] + r["optional"])
                for r in SCHEMA_RULES.values()
            ]
        )
    )

    print("| Field Group | " + " | ".join(SCHEMA_RULES.keys()) + " |")
    print("|-------------|" + "---|" * len(SCHEMA_RULES) + "")

    for field in all_fields:
        row = f"| {field} "
        for version in SCHEMA_RULES:
            if field in SCHEMA_RULES[version]["required"]:
                row += "| ✅ "
            elif field in SCHEMA_RULES[version]["optional"]:
                row += "| 🟡 "
            else:
                row += "| ❌ "
        row += "|"
        print(row)