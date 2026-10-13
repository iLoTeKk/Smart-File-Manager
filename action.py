import shutil
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime
import os


#archive() will archive directory containing files,and move it to the destination
# TODO: Make handle if the file avialabe in destination then change the name.
def archive_action(source, destination,format: str = "zip") -> bool:
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
            # mode="a" creates the zip if it doesn't exist, or appends if it    does!
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
 
#rename() will rename a file inside its current directory
def rename_action(path, new_name) -> bool:
    try:
        src = Path(path)
        new_name = Path(new_name).name  # name only, never moves the file elsewhere
        if not new_name:
            return False

        target = src.with_name(new_name)
        if target == src:
            return True  # nothing to change

        # if the name is already taken, add a counter (same logic as move_action)
        new_path = Path(new_name)
        counter = 1
        while target.exists():
            target = src.with_name(f"{new_path.stem}_{counter}{new_path.suffix}")
            counter += 1

        src.rename(target)
        return True
    except OSError:
        return False

# this function is responsible for running the action
def run_action (path, rules, dry_run = False) -> bool:
    destination = ""
    action = rules.get("action")
    if action in ["move", "archive"]:
        # resolve to the destination file
        dest = Path(rules.get("dest")).expanduser()
        destination = dest if dest.is_absolute() else Path.home() / dest
    if dry_run:
        #TODO: Make dry run
        pass
    if action == "rename":
        return rename_action(path, rules.get("new_name", ""))
    elif action == "archive":
        return archive_action(path, destination, rules.get("format", "zip"))
    elif action == "move":
        return move_action(path, destination)
    elif action == "remove":
        return remove_action(path)
    else:
     return False
