
# 🧠 CFP Input Parser System (v2.0.0)

> A complete, version-controlled system for validating and loading multimodal context JSONs used in LLM pipelines.

---

## 📌 Overview

The **Context Fusion Protocol (CFP)** requires a structured `context.json` file to drive multimodal data ingestion and fusion. This system:

* Validates input JSON files using versioned schemas
* Logs and manages schema evolution
* Supports rollback to prior schema versions
* Is fully extensible for new modalities, hooks, and formats

---

## 📁 Project File Structure

```bash
cfp_input_parser/
├── schemas/
│   ├── context_schema_v1.0.0.json         # Basic schema
│   ├── context_schema_v2.0.0.json         # Advanced schema with audit/hooks
│   ├── coc_variant_v2.0.0.json            # Chain of Command variant (optional)
│   └── current.json                       # Active schema pointer or copy
├── context_inputs/
│   ├── sample_input_v1.json               # For schema v1
│   ├── sample_input_v2.json               # For schema v2
│   └── invalid_sample.json                # Fails validation (for tests)
├── src/
│   ├── core_parser.py                     # Loads, validates, parses JSON
│   ├── schema_manager.py                  # Handles versioning, updates log
│   ├── rollback_engine.py                 # Handles version rollback
│   ├── type_handlers/
│   │   ├── numerical.py
│   │   ├── text.py
│   │   ├── datetime.py
│   └── utils.py                           # Shared utility functions
├── version_log.json                       # Tracks schema versions & changelogs
├── README.md                              # Docs & usage guide
└── tests/
    ├── test_parser.py
    ├── test_schema_versioning.py
    └── test_rollback.py
```

---

## 📐 Context JSON Architecture (v2.0.0)

```json
{
  "$schema": "https://your-domain.org/schemas/context-schema-v2.0.0.json",
  "version": "2.0.0",
  "pipeline_id": "run_2025_06_18_001",
  "created_by": "analyst_01",
  "created_at": "2025-06-18T22:00:00Z",
  "global_settings": {
    "fusion_method": "attention_based_fusion",
    "output_vector_dimension": 512,
    "logging_level": "INFO",
    "error_handling": "strict"
  },
  "contexts": [
    {
      "context_id": "customer_insight_context",
      "description": "Customer behavioral analysis using transactions and feedback.",
      "context_settings": {
        "override_fusion_method": "weighted_average",
        "preprocessing_steps": ["remove_duplicates", "normalize_amounts"]
      },
      "data_sources": [
        {
          "source_id": "txn_data",
          "source_type": "file",
          "file_path": "./data/transactions.csv",
          "file_type": "csv",
          "file_query": "Summarize monthly transaction trends.",
          "source_version": "2025-06-17",
          "features_mapping": {
            "customer_id": {
              "type": "categorical",
              "alias": "cust_id",
              "nullable": false,
              "description": "Unique customer identifier"
            },
            "transaction_date": {
              "type": "datetime",
              "alias": "txn_time",
              "nullable": false
            },
            "amount": {
              "type": "numerical",
              "alias": "txn_amount",
              "nullable": true,
              "default": 0
            }
          },
          "preprocessing_hooks": ["validate_dates"],
          "postprocessing_hooks": ["aggregate_monthly"]
        },
        {
          "source_id": "customer_notes",
          "source_type": "file",
          "file_path": "./data/feedback.txt",
          "file_type": "text",
          "file_query": "Extract sentiment from customer feedback.",
          "source_version": "2025-06-15",
          "features_mapping": {
            "note_text": {
              "type": "text",
              "alias": "customer_feedback",
              "nullable": false,
              "description": "Raw customer feedback text"
            }
          },
          "preprocessing_hooks": ["clean_text", "remove_stopwords"],
          "postprocessing_hooks": ["sentiment_analysis"]
        }
      ],
      "primary_query": "Combine transaction and feedback insights to profile high-value customers.",
      "audit": {
        "created_by": "analyst_01",
        "created_at": "2025-06-18T22:00:00Z",
        "last_modified_by": "analyst_02",
        "last_modified_at": "2025-06-18T23:00:00Z"
      }
    }
  ],
  "final_llm_prompt_template": "Generate a comprehensive customer profile report."
}
```

---

## ✅ Core Parser Responsibilities

| Feature                            | Status     | File                      |
| ---------------------------------- | ---------- | ------------------------- |
| JSON validation (against schema)   | ✅          | `core_parser.py`          |
| Human-readable error reporting     | ✅          | `core_parser.py`          |
| Schema version detection & loading | ✅          | `schema_manager.py`       |
| Rollback to previous versions      | ✅          | `rollback_engine.py`      |
| Hook support (pre/post processing) | ⚙️ planned | `type_handlers/`          |
| CLI or API interface               | ⚙️ planned | `utils.py` or CLI wrapper |

---

## 🧪 Sample Python: Validate Context JSON

```python
from jsonschema import validate, ValidationError
import json

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def validate_context(input_file, schema_file):
    context = load_json(input_file)
    schema = load_json(schema_file)
    
    try:
        validate(instance=context, schema=schema)
        print("✅ Valid context input.")
    except ValidationError as e:
        print(f"❌ Invalid input: {e.message}")
```

---

## 🧭 Version Control Example (version\_log.json)

```json
[
  {
    "version": "1.0.0",
    "file": "schemas/context_schema_v1.0.0.json",
    "timestamp": "2025-06-18T20:00:00Z",
    "changelog": "Initial schema structure"
  },
  {
    "version": "2.0.0",
    "file": "schemas/context_schema_v2.0.0.json",
    "timestamp": "2025-06-18T22:10:00Z",
    "changelog": "Added audit trail, hooks, nullable, and defaults"
  }
]
```

---

## 🧱 Schema Design Philosophy

* **Immutable Schemas**: Each versioned schema file is frozen.
* **Single Source of Truth**: `version_log.json` holds audit & changelog.
* **Modular Type Handlers**: Each data type can be extended with pre/post processors.
* **Chain of Command**: Optional variant (`coc_variant_v2.0.0.json`) adds task/role hierarchy support.

---

## 🚀 Development Roadmap

| Phase   | Task                                   | Status            |
| ------- | -------------------------------------- | ----------------- |
| Phase 1 | Define schemas v1 + v2                 | ✅ Done            |
| Phase 1 | Sample context inputs                  | ✅ Done            |
| Phase 2 | Core validation script                 | ✅ Prototype ready |
| Phase 2 | Add rollback + version control         | ⚙️ In Progress    |
| Phase 3 | Add CoC variant schema                 | 🔜 Next           |
| Phase 3 | Add preprocessing/postprocessing logic | 🔜 Next           |
| Phase 4 | Add CLI (`cfp-validate`, `cfp-log`)    | 🔜 Planned        |

---

## 🔚 Summary

This system provides the foundation for building robust, schema-controlled multimodal pipelines using context JSON. It ensures:

* High-quality, validated inputs
* Full audit and version rollback
* Extensibility via variants and plugin hooks

---

Would you like me to generate:

* The actual `context_schema_v2.0.0.json` and `sample_input_v2.json` files?
* A working repo template?
* A Chain of Command schema variant?

Let me know and I’ll package them all for download or GitHub drop-in.
