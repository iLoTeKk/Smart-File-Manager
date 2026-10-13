import os
import time
from pathlib import Path
import fnmatch
import platform
import subprocess
import plistlib



def extension_filter(path: str, extensions: list[str]) -> bool:
    """True if the file's extension is in the list (case-insensitive, no dot)."""
    if isinstance(extensions, str):
        extensions = [extensions]
    file_ext = Path(path).suffix.lstrip(".").lower()
    for ext in extensions:
        if file_ext == ext.lstrip(".").lower():
            return True
    return False

# this function will get the origin url supporting Windows, Linux, MacOS
def get_origin_url(path: str) :
    os_type = platform.system()
    # Windows
    if os_type == "Windows":
        try:
            with open(path + ":Zone.Identifier", 'r', encoding='utf-8') as file:
                content = file.read().splitlines()
            for key in ["HostUrl=", "ReferrerUrl="]:
                for line in content:
                    if line.startswith(key):
                        return line.strip().removeprefix(key)
        except OSError:
            pass
        return None
    #Mac OS
    elif os_type == "Darwin":
        try:
            hex_text = subprocess.run(
                ["xattr", "-px", "com.apple.metadata:kMDItemWhereFroms", path],
                capture_output=True, text=True, check=True,
            ).stdout
            return plistlib.loads(bytes.fromhex(hex_text))[0]
        except Exception:
            return None
    #linux
    else:
        try:
            return os.getxattr(path,"user.xdg.origin.url").decode("utf-8")
        except OSError:
            return None
    return None


# check if that file contains the URL
def url_filter(path, url) -> bool:
    file_url = get_origin_url(path)
    if file_url is None:
        return False
    if url in file_url:
        return True
    else:
        return False


def _parse_size_in_mb(val):
    """Parses numeric values or strings like '500KB', '2MB', '1GB' into MB."""
    if isinstance(val, (int, float)):
        return float(val) if val >= 0 else None
    if isinstance(val, str):
        val = val.strip().upper()
        multipliers = [("GB", 1024), ("MB", 1), ("KB", 1 / 1024), ("B", 1 / (1024 * 1024))]
        for unit, mult in multipliers:
            if val.endswith(unit):
                try:
                    num = float(val[:-len(unit)].strip())
                    return num * mult if num >= 0 else None
                except ValueError:
                    return None
        try:
            return float(val)
        except ValueError:
            return None
    return None


def size_filter(path, size) -> bool:
    """
    Filters by size in MB.
    Supports numbers, strings ('10MB'), or range dict: {'greater_than': X, 'less_than': Y}
    """
    try:
        if not os.path.isfile(path):
            return False
        size_mb = os.path.getsize(path) / (1024 * 1024)
        
        if isinstance(size, dict):
            if "greater_than" in size:
                gt = _parse_size_in_mb(size["greater_than"])
                if gt is not None and not (size_mb > gt):
                    return False
            if "less_than" in size:
                lt = _parse_size_in_mb(size["less_than"])
                if lt is not None and not (size_mb < lt):
                    return False
            return True
            
        target = _parse_size_in_mb(size)
        return size_mb >= target if target is not None else False
    except OSError:
        return False


def age_days_filter(path, age) -> bool:
    """
    Filters by file age in days since last modification.
    Supports numbers or range dict: {'greater_than': X, 'less_than': Y}
    """
    try:
        if not os.path.exists(path):
            return False
        mtime = os.path.getmtime(path)
        age_in_days = (time.time() - mtime) / 86400.0
        
        if isinstance(age, dict):
            if "greater_than" in age:
                try:
                    gt = float(age["greater_than"])
                    if not (age_in_days > gt):
                        return False
                except (ValueError, TypeError):
                    pass
            if "less_than" in age:
                try:
                    lt = float(age["less_than"])
                    if not (age_in_days < lt):
                        return False
                except (ValueError, TypeError):
                    pass
            return True
            
        return age_in_days >= float(age)
    except (OSError, ValueError, TypeError):
        return False


def name_filter(path, name) -> bool:
    """Filters by filename matching exact name, pattern, or wildcard (e.g. Screenshot*, *2026*)."""
    if not name or not isinstance(name, str):
        return False
    filename = Path(path).name
    return fnmatch.fnmatch(filename, name)

def contains_text_filter(path, text) -> bool:
    """Checks if a file contains the given text."""
    if not text or not isinstance(text, str):
        return False

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            return text in file.read()
    except OSError:
        return False

MATCHERS = {
    "extension": extension_filter,
    "size_mb": size_filter,
    "age_days": age_days_filter,
    "name": name_filter,
    "contains_text": contains_text_filter,
    "url": url_filter,
}


# this function will run the filter functions on the path.
def matches(path, when):
    for key, value in when.items():
        # find the right function
        check = MATCHERS[key]
        # run it on the file
        if not check(path, value):
            return False
    return True

# this function will be used to pass the whole rule.
def first_matching_rule(path, rules):
    for rule in rules:
        if matches(path, rule["when"]):
            return rule
    return None

