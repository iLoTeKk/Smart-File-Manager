import shutil
from pathlib import Path
from datetime import datetime
import os


#archive() will archive directory containing files,and move it to the destination
# TODO: Make handle if the file avialabe in destination then change the name.
def archive_action(source, destination, format: str = "zip") -> bool:
    #get the date and format it as string
    now = datetime.now()
    archive_name = now.strftime("%d-%b-%Y")

    try:
        #make the archive
        archive_path = shutil.make_archive(archive_name, format, source)
        destination_path = Path(destination)
        #check that the destination file is a directory
        if not destination_path.exists():
            destination_path.mkdir()
        else:
            if not destination_path.is_dir():
                destination_path.mkdir()
        #move it with the new format
        shutil.move(archive_path, destination / f"{archive_name}.{format}")
        return True
    except:
        return False


#move() will move a file from it's orignial palce
# TODO: Try improve this to handle if the file in the destination directory
def move_action(path, destination) -> bool:
    #basic just try to move
    try:
        destination_path = Path(destination)
        if not destination_path.exists():
            destination_path.mkdir()
        else:
            if not destination_path.is_dir():
                destination_path.mkdir()
        shutil.move(path, destination)
        return True
    except:
        return False

#remove() will remove the file
def remove_action(path) -> bool:
    #basic just remove the file
    try:
        os.remove(path)
        return True
    except:
        return False

#rename() will rename a file from
def rename_action(path, new_name) -> bool:
    #it should handle if the file it's trying to renmae is there
    try:
        Path(path).rename(new_name)
        return True
    except:
        return False

# this function is responsible for running the action
# TODO: Fix rename to make it work with the resulted format, probably make a function for that

def run_action(path, rules, dry_run=False):
    destination = ""
    action = rules.get("action")

    if action in ["move", "archive"]:
        destination = rules.get("dest", "")

    if dry_run:
        if action in ["move", "archive"]:
            print(f"[DRY-RUN] Would {action.upper()}: '{path}' -> '{destination}'")
        elif action == "remove":
            print(f"[DRY-RUN] Would REMOVE: '{path}'")
        elif action == "rename":
            print(f"[DRY-RUN] Would RENAME: '{path}' (format: '{rules.get('format')}')")
        return True

    if action == "rename":
        return rename_action(path, rules.get("format"))
    elif action == "archive":
        return archive_action(path, destination)
    elif action == "move":
        return move_action(path, destination)
    elif action == "remove":
        return remove_action(path)
    else:
        return False


