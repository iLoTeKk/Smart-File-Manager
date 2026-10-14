# Individual Contribution Report

## Student Information

- **Name:** MOHAMAD W. M. ALHADDAD
- **Student ID:** 2509115109
- **GitHub Username:** ilotekk
- **Project:** Smart File Manager

---

## Contributions

As part of the Smart File Manager project, I was responsible for the core architecture design, JSON configuration validation, cross-platform origin metadata extraction, and key filesystem execution operations.

### 1. System Pipeline Architecture & CLI Integration

- Designed the high-level automated processing pipeline: **Ingestion & Validation $\to$ File Discovery $\to$ Strategy Rule Matching $\to$ Action Execution**.
- Co-designed the CLI interface in [`cli.py`](../cli.py) using `argparse`, supporting `--base-dir`, `--config`, `--recursive`, and the `--dry-run` safety preview flag.
- Ensured fail-fast execution: if the configuration validation fails, the program halts before performing any filesystem mutations.

### 2. Configuration Validation Engine (`config.py`)

- Implemented and refined [`validate_json()`](../config.py) to guard against malformed configuration files and malicious or invalid inputs.
- Validated root schema keys (`rules`), mandatory rule items (`when`, `action`), allowed action types (`move`, `archive`, `rename`, `remove`), and filter conditions.
- Enforced required sub-keys (e.g. ensuring `dest` is specified for `move` and `archive`, and `format` is specified for `rename`).
- Handled operator checking for numeric criteria (`greater_than` and `less_than` for `size_mb` and `age_days`).

### 3. Cross-Platform Origin URL Extraction & Content Matching (`matchers.py`)

- Researched and implemented cross-platform browser download origin URL extraction via [`get_origin_url()`](../matchers.py):
  - **Windows:** Parses the NTFS Alternate Data Stream (`:Zone.Identifier`) to extract `HostUrl` and `ReferrerUrl`.
  - **macOS:** Invokes `xattr` to read the binary plist attribute `com.apple.metadata:kMDItemWhereFroms` and decodes it via `plistlib`.
  - **Linux:** Reads extended attributes (`xattr`) using the standard `user.xdg.origin.url` namespace.
- Integrated [`url_filter()`](../matchers.py) to enable organizing files based on which website or domain they were downloaded from.
- Implemented [`contains_text_filter()`](../matchers.py) to inspect the body of text files for keyword matching, opening up document-content-based workflows.

### 4. Filesystem Execution Engine & Safety Guarantees (`action.py`)

- Implemented [`move_action()`](../action.py) with automatic collision handling: if a destination file exists, the system automatically resolves conflicts using a numeric suffix (`_1`, `_2`) to guarantee zero data loss.
- Implemented [`archive_action()`](../action.py) supporting both `zip` and `tar` formats:
  - Generates date-stamped archive bundles (`Archive_<DATE>.zip`).
  - Utilizes append mode (`mode="a"`) to stream files directly into existing archives without creating intermediate temp directories.
  - Safely deletes source files only after successful archive inclusion.
- Implemented [`remove_action()`](../action.py) for targeted disk space reclamation.
- Added destination resolution logic in [`run_action()`](../action.py) ensuring relative destination paths expand safely against `Path.home()`.
- Added `--dry-run` simulation reporting in [`action.py`](../action.py) allowing users to audit planned actions safely without mutating storage.

---

## Summary

My contributions provided the foundational architecture and safety guarantees of the Smart File Manager: from schema validation and cross-platform operating system metadata integration to robust, collision-proof action execution.
