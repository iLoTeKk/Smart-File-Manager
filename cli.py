# Download Manager CLI Python Script
# Give config + watch folder
import sys
import os
import json
import argparse
from pathlib import Path
import matchers
import action
import config



#this will parse to get all dest folder
def resolve_path(path):
    if path is None:
        return path
    return Path(path).expanduser().resolve()

#this function will scan all the files in the base_dir and will skip the destination files
def scan(base_dir: Path, recursive: bool, skip_dir) -> list[str]:
    files = []
    base = Path(base_dir).resolve()
    skip = Path(skip_dir).resolve() if skip_dir else None
    if not base.is_dir():
        return files
    if recursive:
        paths = base.rglob("*")
    else:
        paths = base.iterdir()
    for path in paths:
        if path.is_file() and not path.is_symlink():
            if skip and (path.resolve() == skip or skip in path.resolve().parents):
                continue
            if path.suffix in [".crdownload", ".part", ".tmp"]:
                continue
            files.append(str(path))
    return files

# here the main logic will be
def main():
    p = argparse.ArgumentParser(description="Organize files using a JSON rules file.")
    p.add_argument("--base-dir", required=True, help="folder to scan")
    p.add_argument("--config", required=True, help="path to the rules JSON")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    #parse args
    config_file = resolve_path(args.config)
    base_dir = resolve_path(args.base_dir)
    recursive = args.recursive
    dry_run = args.dry_run

    #get and parse json
    ok, json_error = config.validate_json(config_file)
    if not ok:
        sys.exit(json_error)

    with open(config_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    all_files = scan(base_dir, recursive, skip_dir=None)
    for file in all_files:
        rule = matchers.first_matching_rule(file, json_data["rules"])
        if rule:
            action.run_action(file, rule, dry_run)



if __name__ == "__main__":
    main()
