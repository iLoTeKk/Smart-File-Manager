# Smart File Manager

A modular, automated command-line file organization and management tool built with Python. Rather than sorting files merely by extension, **Smart File Manager** evaluates rich file attributes—such as filename wildcard globs, browser download origin URLs, file sizes, modification age, and inner text content—and applies customizable actions (`move`, `archive`, `rename`, `remove`) in priority order.

---

## Repository Structure

As required by the project specifications, the repository is organized into distinct, modular components:

| File / Directory | Purpose & Description |
| :--- | :--- |
| **[`cli.py`](cli.py)** | **CLI Entrypoint:** Parses command-line arguments (`--base-dir`, `--config`, `--recursive`, `--dry-run`), triggers JSON schema validation, scans the filesystem, and orchestrates the rule matching and action execution loop. |
| **[`config.py`](config.py)** | **Validation Engine:** Validates user-provided JSON rules against schema constraints (`validate_json()`). Enforces required keys, allowed actions, valid filter operators, and formats in a fail-fast manner. |
| **[`matchers.py`](matchers.py)** | **Strategy Matching Engine:** Contains a dispatch table (`MATCHERS`) mapping filter keys to predicates (`extension_filter`, `size_filter`, `age_days_filter`, `name_filter`, `url_filter`, `contains_text_filter`). Extracts origin URLs across platforms (Linux xattr, Windows NTFS ADS, macOS xattr) and performs short-circuit rule evaluation. |
| **[`action.py`](action.py)** | **Execution & Safety Engine:** Implements filesystem operations (`move_action`, `archive_action`, `remove_action`, `rename_action`). Handles automatic collision avoidance (`_1`, `_2`), archive appending (`mode="a"`), relative destination resolution against `Path.home()`, and non-destructive `--dry-run` simulation. |
| **[`example.json`](example.json)** | **Sample Ruleset:** An example configuration file showcasing practical rules combining multiple filters, thresholds, and actions. |
| **[`contributions/`](contributions/)** | **Team Member Reports:** Contains detailed individual contribution markdown files for each project member following the course naming convention. |

---

## How It Works

Each rule defined in the JSON configuration file consists of:
1. **Conditions (`when`):** One or more criteria that must all match (logical AND conjunction).
2. **Action (`action`):** The operation to execute when a file matches the rule.

The engine uses a **first-match-wins** priority model: rules are evaluated in the order they appear in the JSON file. Once a matching rule is found for a file, its action is scheduled and remaining rules are skipped.

### Supported Matchers (`when`)

- **`extension`:** A single extension or list of extensions (case-insensitive, e.g. `["pdf", "docx"]`).
- **`name`:** File name match supporting wildcard globs via `fnmatch` (e.g. `Screenshot*`, `IMG_*`).
- **`size_mb`:** Checks file size in megabytes using comparison operators (e.g. `{"greater_than": 500}` or `{"less_than": 10}`).
- **`age_days`:** Checks file age in days since last modification (e.g. `{"greater_than": 30}`).
- **`url`:** Checks the download origin URL extracted from operating system metadata (supports Windows Zone.Identifier, macOS `kMDItemWhereFroms`, and Linux `user.xdg.origin.url`).
- **`contains_text`:** Inspects file content for specific keyword or text occurrences (case-insensitive).

### Supported Actions (`action`)

| Action | Description | Required Options |
| :--- | :--- | :--- |
| `move` | Moves the file to the target destination folder. | `dest` |
| `archive` | Appends the file to a shared date-stamped archive (`Archive_<DATE>.zip` or `.tar`), then removes the original. | `dest`, `format` (`"zip"` or `"tar"`) |
| `rename` | In-place file renaming using dynamic format tokens. | `format` |
| `remove` | Permanently deletes the file (useful for cleaning up temporary files). | None |

#### Dynamic Rename Placeholders
When using `"action": "rename"`, the `format` string supports dynamic tokens:
- `{name}`: Original filename stem (without extension).
- `{date}`: Current date in `YYYY-MM-DD` format.
- `{extension}`: Original file extension (without dot).

*Example:* `"{date}_{name}.{extension}"` transforms `invoice.pdf` into `2026-10-14_invoice.pdf`.

---

## Usage

Interact with the Smart File Manager using the CLI (`cli.py`).

### CLI Arguments

| Argument | Type | Required | Description |
| :--- | :---: | :---: | :--- |
| `--base-dir` | Path | **Yes** | Target directory to scan for files to organize. |
| `--config` | Path | **Yes** | Path to the JSON configuration file defining the rules. |
| `--recursive` | Flag | No | Recursively scan subdirectories within `--base-dir`. |
| `--dry-run` | Flag | No | Simulates actions and outputs planned operations without touching the disk. |

### Commands

**1. Dry-Run Simulation (Recommended before executing):**
Preview what actions would occur without making any actual changes:
```bash
python3 cli.py --base-dir ~/Downloads --config example.json --dry-run
```

**2. Standard Execution:**
Process and organize files in the specified directory:
```bash
python3 cli.py --base-dir ~/Downloads --config example.json
```

**3. Recursive Execution:**
Scan the directory and all nested subfolders:
```bash
python3 cli.py --base-dir ~/Downloads --config example.json --recursive
```

---

## Example Configuration (`example.json`)

```json
{
  "rules": [
    {
      "when": { "url": "example.com", "extension": ["pdf"] },
      "action": "move",
      "dest": "Work/Example"
    },
    {
      "when": { "name": "Screenshot*", "age_days": { "greater_than": 30 } },
      "action": "archive",
      "dest": "Archive",
      "format": "zip"
    },
    {
      "when": { "size_mb": { "greater_than": 500 } },
      "action": "move",
      "dest": "Large"
    },
    {
      "when": { "extension": ["tmp", "part"] },
      "action": "remove"
    },
    {
      "when": { "name": "IMG_*" },
      "action": "rename",
      "format": "{date}_{name}.{extension}"
    }
  ]
}
```

---

## Safety & Robustness Features

- **Zero Data Loss on Collision:** When moving or renaming, if a file already exists at the destination, the system automatically appends an incrementing counter (`file_1.ext`, `file_2.ext`) instead of overwriting data.
- **Fail-Fast Schema Guard:** If the JSON configuration file contains syntax errors, missing keys, or unsupported values, execution stops immediately with a descriptive error message before any filesystem scanning occurs.
- **Safe Path Resolution:** Relative destination paths are safely resolved relative to the user's home directory (`Path.home()`), preventing unintended modifications in the current terminal directory.
- **In-Place Archives:** The archive engine streams files directly into existing archives using append mode (`mode="a"`), avoiding unnecessary intermediate temporary directories.