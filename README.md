# Smart File Manager

A Python project that organizes files automatically. Instead of sorting only by extension, it lets you create rules based on other file properties, such as the name, download URL, size, and modification date.

## How It Works

Each rule has two parts: the conditions that select files, and the action performed on them.

### Matching

- **Extension:** `.pdf`, `.jpg`, `.docx`, etc.
- **URL:** the address the file was downloaded from.
- **File name:** an exact name or a wildcard pattern, like `report_*.docx`.
- **Size:** smaller or larger than a given size, in MB.
- **Age:** based on the last modification date.

### Actions

| Action | Description | Options |
|---|---|---|
| `archive` | Adds the file or folder to a ZIP/TAR archive, then deletes the original | `dest`, `format` |
| `move` | Moves the file to a folder | `dest` |
| `remove` | Deletes the file permanently | none |
| `rename` | Renames the file, and can also move it | `format`, `dest` |

Rename placeholders: `{name}`, `{date}` (today's date), `{size}`, and `{extension}` (without the dot).

## Example

```python
from action import run_action

rules = {"action": "rename", "format": "{date}_{name}.{extension}"}
run_action("invoice.pdf", rules)  # -> 2026-10-13_invoice.pdf
```

## Notes

- **Dry run:** use `dry_run=True` to see what would happen without changing anything.
- **Duplicates:** if the name already exists, `_1`, `_2`, etc. is added instead of overwriting.
- **Archives:** files archived on the same day go into one archive, like `Archive_13-Oct-2026.zip`.
- **Paths:** `dest` can be absolute, relative to your home folder, or start with `~`.
- **Return value:** each action returns `True` on success and `False` on failure. Errors are logged with Python's `logging` module.
- **`remove` is permanent.** Files don't go to the recycle bin, so test new rules with `dry_run=True` first.