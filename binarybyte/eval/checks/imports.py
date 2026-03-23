from __future__ import annotations

import importlib.util
import re

from binarybyte.eval.schema import CheckResult

_IMPORT_RE = re.compile(
    r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import\s+)"
)


def _parse_added_imports(diff_text: str) -> list[str]:
    """Extract top-level module names from added import lines."""
    modules: list[str] = []
    for line in diff_text.splitlines():
        if not (line.startswith("+") and not line.startswith("+++")):
            continue
        code_line = line[1:]
        match = _IMPORT_RE.match(code_line)
        if match:
            module = (match.group(1) or match.group(2)).split(".")[0]
            if module not in modules:
                modules.append(module)
    return modules


def _is_module_available(module_name: str) -> bool:
    """Check if a module is importable in the current environment."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


_STDLIB_MODULES = {
    "abc", "aifc", "argparse", "array", "ast", "asyncio", "atexit",
    "base64", "binascii", "bisect", "builtins", "calendar", "cgi",
    "cgitb", "cmath", "cmd", "code", "codecs", "collections",
    "colorsys", "compileall", "concurrent", "configparser", "contextlib",
    "contextvars", "copy", "copyreg", "cProfile", "csv", "ctypes",
    "curses", "dataclasses", "datetime", "dbm", "decimal", "difflib",
    "dis", "distutils", "doctest", "email", "encodings", "enum",
    "errno", "faulthandler", "filecmp", "fileinput", "fnmatch",
    "fractions", "ftplib", "functools", "gc", "getopt", "getpass",
    "gettext", "glob", "gzip", "hashlib", "heapq", "hmac", "html",
    "http", "idlelib", "imaplib", "importlib", "inspect", "io",
    "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache",
    "locale", "logging", "lzma", "mailbox", "mailcap", "marshal",
    "math", "mimetypes", "mmap", "modulefinder", "multiprocessing",
    "netrc", "numbers", "operator", "optparse", "os", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posixpath", "pprint", "profile", "pstats",
    "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random",
    "re", "readline", "reprlib", "resource", "rlcompleter", "runpy",
    "sched", "secrets", "select", "selectors", "shelve", "shlex",
    "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr",
    "socket", "socketserver", "sqlite3", "ssl", "stat", "statistics",
    "string", "stringprep", "struct", "subprocess", "sunau", "symtable",
    "sys", "sysconfig", "syslog", "tabnanny", "tarfile", "tempfile",
    "test", "textwrap", "threading", "time", "timeit", "tkinter",
    "token", "tokenize", "tomllib", "trace", "traceback", "tracemalloc",
    "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
    "unittest", "urllib", "uuid", "venv", "warnings", "wave",
    "weakref", "webbrowser", "winreg", "winsound", "wsgiref",
    "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
}


def check_imports(diff_text: str) -> CheckResult:
    modules = _parse_added_imports(diff_text)
    if not modules:
        return CheckResult(
            name="hallucinated_imports",
            passed=True,
            details=["No new imports detected in diff."],
        )

    warnings: list[str] = []
    for mod in modules:
        if mod in _STDLIB_MODULES:
            continue
        if not _is_module_available(mod):
            warnings.append(
                f"Import '{mod}' not found in current environment (may be hallucinated or missing from requirements)."
            )

    return CheckResult(
        name="hallucinated_imports",
        passed=len(warnings) == 0,
        details=warnings if warnings else [f"All {len(modules)} imported module(s) verified."],
    )
