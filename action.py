import logging
import shutil
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
log = logging.getLogger(__name__)


def _unique_name(src: Path, existing: set) -> str:
    """Return a name that doesn't clash with `existing` (name_1.ext, name_2.ext...)."""
    name = src.name
    counter = 1
    while name in existing:
        name = f"{src.stem}_{counter}{src.suffix}"
        counter += 1
    return name


# archive_action() adds a file/directory to a shared dated archive in the
# destination, then deletes the original.
def archive_action(source, destination, format: str = "zip") -> bool:
    if format not in ("zip", "tar"):
        return False
    try:
        src = Path(source)
        if not src.exists():
            return False

        dest_dir = Path(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)
        archive_path = dest_dir / f"Archive_{datetime.now():%d-%b-%Y}.{format}"

        if format == "zip":
            # mode="a" creates the zip if missing, or appends if it exists
            with zipfile.ZipFile(archive_path, "a", zipfile.ZIP_DEFLATED) as zf:
                existing = {n.split("/")[0] for n in zf.namelist()}
                arc = _unique_name(src, existing)
                if src.is_dir():
                    zf.write(src, arc)  # keep empty dir entry
                    for f in src.rglob("*"):
                        zf.write(f, Path(arc) / f.relative_to(src))
                else:
                    zf.write(src, arc)
        else:
            mode = "a" if archive_path.exists() else "w"
            with tarfile.open(archive_path, mode) as tf:
                existing = {n.split("/")[0] for n in tf.getnames()}
                tf.add(src, arcname=_unique_name(src, existing))

        # Delete the original only after it is safely inside the archive
        if src.is_dir():
            shutil.rmtree(src)
        else:
            src.unlink()
        return True
    except (OSError, zipfile.BadZipFile, tarfile.TarError):
        log.exception("archive failed: %s", source)
        return False


# move_action() moves a file; if the name exists in destination it adds _1, _2...
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
        log.exception("move failed: %s", path)
        return False


# remove_action() deletes the file
def remove_action(path) -> bool:
    try:
        Path(path).unlink()
        return True
    except OSError:
        log.exception("remove failed: %s", path)
        return False


# rename_action() renames a file using a format with {name}, {extension}, {date}.
# If destination is given the file is also moved there, otherwise it stays put.
def rename_action(path, destination, format: str) -> bool:
    try:
        src = Path(path)
        if not src.exists() or not src.is_file():
            return False

        dest_dir = Path(destination) if destination else src.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        name = src.stem
        extension = src.suffix.lstrip(".")

        # .replace() avoids KeyError crashes from unknown tokens
        if format:
            new_name = (
                format.replace("{name}", name)
                .replace("{extension}", extension)
                .replace("{date}", today)
            )
        else:
            new_name = src.name

        target = dest_dir / new_name

        # Nothing to do: same name in the same folder
        if target == src:
            return True

        # Collision handling (_1, _2) matching the rest of the app
        counter = 1
        target_stem = target.stem
        target_suffix = target.suffix
        while target.exists():
            target = dest_dir / f"{target_stem}_{counter}{target_suffix}"
            counter += 1

        shutil.move(src, target)  # works across drives too
        return True
    except OSError:
        log.exception("rename failed: %s", path)
        return False


def _resolve_dest(raw):
    """Expand ~ and make relative paths relative to the home folder."""
    if not raw:
        return ""
    dest = Path(raw).expanduser()
    return dest if dest.is_absolute() else Path.home() / dest


# run_action() decides which action to run based on `rules`
def run_action(path, rules, dry_run=False) -> bool:
    action = rules.get("action")
    if action not in ("move", "archive", "rename", "remove"):
        return False

    destination = _resolve_dest(rules.get("dest"))
    if action in ("move", "archive") and not destination:
        return False  # these two require a destination

    if dry_run:
        extra = f" (format={rules.get('format')})" if action == "rename" else ""
        print(f"[dry-run] {action} {path} -> {destination or '-'}{extra}")
        return True

    if action == "rename":
        return rename_action(path, destination, rules.get("format", ""))
    if action == "archive":
        return archive_action(path, destination, rules.get("format", "zip"))
    if action == "move":
        return move_action(path, destination)
    return remove_action(path)

