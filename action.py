import shutil
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime
import os


# Archive a file and move it into the destination archive.
# TODO: Handle files that already exist in the destination.
def archive_action(source, destination, format: str = "zip") -> bool:
    try:
        src = Path(source)
        dest_dir = Path(destination)

        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        archive_name = f"Archive_{datetime.now().strftime('%d-%b-%Y')}.{format}"
        archive_path = dest_dir / archive_name

        if format == "zip":
            with zipfile.ZipFile(
                archive_path, "a", zipfile.ZIP_DEFLATED
            ) as zf:
                existing_files = zf.namelist()
                arch_name = src.name
                counter = 1

                while arch_name in existing_files:
                    arch_name = f"{src.stem}_{counter}{src.suffix}"
                    counter += 1

                zf.write(src, arcname=arch_name)

        elif format == "tar":
            mode = "a" if archive_path.exists() else "w"

            with tarfile.open(archive_path, mode) as tf:
                existing_files = tf.getnames()
                arch_name = src.name
                counter = 1

                while arch_name in existing_files:
                    arch_name = f"{src.stem}_{counter}{src.suffix}"
                    counter += 1

                tf.add(src, arcname=arch_name)

        else:
            return False

        os.remove(src)
        return True

    except OSError:
        return False


# Move a file to the destination directory.
def move_action(path, destination) -> bool:
    try:
        src = Path(path)
        dest_dir = Path(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)

        target = dest_dir / src.name
        counter = 1

        while target.exists():
            target = dest_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        shutil.move(src, target)
        return True

    except OSError:
        return False


# Remove a file.
def remove_action(path) -> bool:
    try:
        os.remove(path)
        return True
    except OSError:
        return False


# Rename a file using a custom name or format tokens.
def rename_action(path, destination, format: str) -> bool:
    try:
        src = Path(path)

        if not src.exists() or not src.is_file():
            return False

        # If destination is empty, keep the file in its original folder.
        dest_dir = Path(destination) if destination else src.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        name = src.stem
        extension = src.suffix.lstrip(".")

        # Replace supported tokens. A regular filename works as-is.
        if format:
            new_name = (
                format.replace("{name}", name)
                .replace("{extension}", extension)
                .replace("{date}", today)
            )
        else:
            new_name = src.name

        # Avoid creating a path from an empty name or a folder path.
        if not new_name or Path(new_name).name != new_name:
            return False

        target = dest_dir / new_name

        # If the target already exists, append _1, _2, etc.
        counter = 1
        target_stem = target.stem
        target_suffix = target.suffix

        while target.exists():
            target = dest_dir / f"{target_stem}_{counter}{target_suffix}"
            counter += 1

        src.rename(target)
        return True

    except (OSError, ValueError):
        return False


# Run the action defined in the rules.
def run_action(path, rules):
    action = rules.get("action")

    if action in ["move", "archive", "rename"]:
        dest = Path(rules.get("dest") or Path(path).parent).expanduser()
        destination = dest

        if action == "rename":
            return rename_action(
                path,
                destination,
                rules.get("format", "{name}.{extension}")
            )

        elif action == "archive":
            return archive_action(
                path,
                destination,
                rules.get("format", "zip")
            )

        elif action == "move":
            return move_action(path, destination)

    elif action == "remove":
        return remove_action(path)

    return False