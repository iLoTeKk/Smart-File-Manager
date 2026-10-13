import shutil
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime
import os


#archive() will archive directory containing files,and move it to the destination
# TODO: Make handle if the file avialabe in destination then change the name.
def archive_action(source, destination, format: str = "zip") -> bool:
    try:
        src = Path(source)
        dest_dir = Path(destination)
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        # 1. One shared archive name based on the date
        counter = ""
        archive_name = f"Archive_{datetime.now().strftime('%d-%b-%Y')}.{format}"
        archive_path = dest_dir / archive_name

        # 2. Append into the archive
        if format == "zip":
            # mode="a" creates the zip if it doesn't exist, or appends if it does!
            with zipfile.ZipFile(archive_path, "a", zipfile.ZIP_DEFLATED) as zf:
                existing_files = zf.namelist()
                arch_name = src.name
                counter = 1
                while arch_name in existing_files:
                    arch_name = f"{src.stem}_{counter}{src.suffix}"
                    counter += 1
                zf.write(src, arcname=arch_name)

        elif format == "tar":
            # mode="a" appends into existing tar, or mode="w" if new
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

        # 3. Delete the original file now that it is inside the archive
        os.remove(src)
        return True

    except OSError:
        return False


#move() will move a file from it's orignial palce
# TODO: Try improve this to handle if the file in the destination directory
def move_action(path, destination) -> bool:
    #basic just try to move
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


#remove() will remove the file
def remove_action(path) -> bool:
    #basic just remove the file
    try:
        os.remove(path)
        return True
    except OSError:
        return False


#rename() will rename a file
def rename_action(path, destination, format: str) -> bool:
    try:
        src = Path(path)

        if not src.exists() or not src.is_file():
            return False

        # If destination is provided, use it; otherwise stay in the same folder
        dest_dir = Path(destination) if destination else src.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        name = src.stem
        extension = src.suffix.lstrip(".")

        # Replace supported tokens; regular names work as-is
        if format:
            new_name = (
                format.replace("{name}", name)
                .replace("{extension}", extension)
                .replace("{date}", today)
            )
        else:
            new_name = src.name

        target = dest_dir / new_name

        # Handle name collisions by adding _1, _2, etc.
        counter = 1
        target_stem = target.stem
        target_suffix = target.suffix

        while target.exists():
            target = dest_dir / f"{target_stem}_{counter}{target_suffix}"
            counter += 1

        # Perform rename
        src.rename(target)
        return True

    except OSError:
        return False


# this function is responsible for running the action
# TODO: Fix rename to make it work with the resulted format, probably make a function for that
def run_action(path, rules):
    action = rules.get("action")

    if action in ["move", "archive", "rename"]:
        dest = Path(rules.get("dest", Path(path).parent)).expanduser()
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