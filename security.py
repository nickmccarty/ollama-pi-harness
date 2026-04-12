"""
security.py — pre-execution safety checks for agent tool calls.

Three layers:
  1. check_python_code(code)  — AST scan before run_python executes
  2. check_file_path(path)    — allowlist + blocklist before read_file reads
  3. scan_for_injection(text) — heuristic scan of web results before synthesis

All checks return (ok: bool, reason: str). Callers decide whether to block or warn.
"""

import ast
import os
import re

# ---------------------------------------------------------------------------
# 1. Python code scanner
# ---------------------------------------------------------------------------

# Imports that grant filesystem, network, or process access
BLOCKED_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "socket", "requests", "urllib",
    "httpx", "aiohttp", "ftplib", "smtplib", "telnetlib", "paramiko",
    "fabric", "pathlib", "glob", "tempfile", "pty", "tty", "signal",
    "ctypes", "cffi", "winreg", "win32api", "win32con",
    # Dynamic import / code execution — bypass the blocklist entirely
    "importlib", "runpy", "zipimport",
    # Serialisation-based code execution
    "pickle", "shelve", "marshal",
    # Process / thread spawning
    "multiprocessing", "concurrent",
    # Interactive interpreters
    "code", "codeop", "readline",
    # Low-level I/O that bypasses open() block
    "io", "_io",
    # Direct access to builtins namespace
    "builtins",
    # Platform-specific command execution
    "webbrowser", "antigravity",
}

# Builtins that can execute arbitrary code or bypass restrictions
BLOCKED_CALLS = {
    "exec", "eval", "compile", "__import__", "open", "breakpoint",
    "vars", "globals", "locals", "getattr", "setattr", "delattr",
    # Process control / resource exhaustion
    "input", "exit", "quit",
    # Low-level memory access
    "memoryview",
    # Class hierarchy traversal (sandbox escape)
    "__subclasses__",
}

# Attribute access patterns that indicate dangerous stdlib use
BLOCKED_ATTR_PATTERNS = [
    re.compile(r'\bos\s*\.\s*(system|popen|remove|unlink|rmdir|rename|makedirs|execv|execve|fork|kill|getenv|putenv|environ)'),
    re.compile(r'\bsubprocess\s*\.\s*(run|call|Popen|check_output|getoutput)'),
    re.compile(r'\bshutil\s*\.\s*(rmtree|move|copy|copytree)'),
    re.compile(r'\bsocket\s*\.\s*socket'),
    re.compile(r'\bopen\s*\('),
    re.compile(r'__builtins__'),
    re.compile(r'__class__.*__bases__'),  # class hierarchy traversal
    re.compile(r'\bimportlib\s*\.\s*import_module'),  # dynamic import bypass
    re.compile(r'\bpickle\s*\.\s*(loads|load|Unpickler)'),  # deserialisation exec
    re.compile(r'\.__subclasses__\s*\('),  # sandbox escape via class hierarchy
    re.compile(r'\bcodecs\s*\.\s*(open|decode)'),  # file I/O via codecs
]


def check_python_code(code: str) -> tuple[bool, str]:
    """
    AST-scan Python code for dangerous imports and calls.
    Returns (True, "ok") if safe, (False, reason) if blocked.
    """
    # First pass: raw pattern matching (catches obfuscation attempts like getattr tricks)
    for pattern in BLOCKED_ATTR_PATTERNS:
        if pattern.search(code):
            return False, f"blocked pattern: {pattern.pattern!r}"

    # Second pass: AST analysis
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"syntax error: {e}"

    for node in ast.walk(tree):
        # import foo / import foo as bar
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in BLOCKED_IMPORTS:
                    return False, f"blocked import: {alias.name!r}"

        # from foo import bar
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in BLOCKED_IMPORTS:
                return False, f"blocked import: from {node.module!r}"

        # direct calls: exec(...), eval(...), open(...), etc.
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in BLOCKED_CALLS:
                return False, f"blocked call: {name!r}"

    return True, "ok"


# ---------------------------------------------------------------------------
# 2. File path sandbox
# ---------------------------------------------------------------------------

# Only allow reading from these directory prefixes (expanded at check time)
ALLOWED_READ_DIRS = [
    "~/Desktop",
    "~/Documents",
]

# Never read files matching these patterns regardless of directory
BLOCKED_FILE_PATTERNS = [
    re.compile(r'\.env(\.|$)', re.IGNORECASE),
    re.compile(r'\.(key|pem|p12|pfx|crt|cer|pub)$', re.IGNORECASE),
    re.compile(r'id_(rsa|dsa|ecdsa|ed25519)(\.pub)?$', re.IGNORECASE),
    re.compile(r'(credentials|secrets|api.?key|token|password|passwd)(\.\w+)?$', re.IGNORECASE),
    re.compile(r'\.ssh[/\\]', re.IGNORECASE),
    re.compile(r'(known_hosts|authorized_keys)$', re.IGNORECASE),
    re.compile(r'\.(htpasswd|netrc|gnupg)$', re.IGNORECASE),
]


def check_file_path(path: str) -> tuple[bool, str]:
    """
    Validate a file path before read_file reads it.
    Returns (True, "ok") if permitted, (False, reason) if blocked.
    """
    # realpath resolves symlinks so a symlink inside ~/Desktop pointing
    # outside the sandbox cannot bypass the directory allowlist.
    expanded = os.path.realpath(os.path.expanduser(path))
    filename = os.path.basename(expanded)

    # Check blocklisted filename patterns
    for pattern in BLOCKED_FILE_PATTERNS:
        if pattern.search(filename) or pattern.search(expanded):
            return False, f"blocked sensitive file: {filename!r}"

    # Check allowed directory prefixes
    allowed_expanded = [os.path.realpath(os.path.expanduser(d)) for d in ALLOWED_READ_DIRS]
    if not any(expanded.startswith(d) for d in allowed_expanded):
        return False, f"path outside allowed dirs: {expanded!r}"

    return True, "ok"


# ---------------------------------------------------------------------------
# 2b. Output path sandbox
# ---------------------------------------------------------------------------

# Directories where the agent is allowed to write output files
ALLOWED_WRITE_DIRS = [
    "~/Desktop",
    "~/Documents",
]


def check_output_path(path: str) -> tuple[bool, str]:
    """
    Validate an output file path before writing.
    Returns (True, "ok") if permitted, (False, reason) if blocked.
    """
    expanded = os.path.realpath(os.path.expanduser(path))
    filename = os.path.basename(expanded)

    # Block writing to sensitive file patterns
    for pattern in BLOCKED_FILE_PATTERNS:
        if pattern.search(filename) or pattern.search(expanded):
            return False, f"blocked sensitive file: {filename!r}"

    # Check allowed directory prefixes
    allowed_expanded = [os.path.realpath(os.path.expanduser(d)) for d in ALLOWED_WRITE_DIRS]
    if not any(expanded.startswith(d) for d in allowed_expanded):
        return False, f"output path outside allowed dirs: {expanded!r}"

    return True, "ok"


# ---------------------------------------------------------------------------
# 3. Prompt injection scanner
# ---------------------------------------------------------------------------

# Patterns that suggest injected instructions in external content
INJECTION_PATTERNS = [
    re.compile(r'ignore (all |previous |prior |above |your )(instructions?|directives?|system prompt)', re.IGNORECASE),
    re.compile(r'(disregard|forget|override) (your |all |previous )?(instructions?|rules?|guidelines?)', re.IGNORECASE),
    re.compile(r'you are now (a|an|acting as)', re.IGNORECASE),
    re.compile(r'new (instructions?|directives?|task|objective):', re.IGNORECASE),
    re.compile(r'(system|developer|admin)\s*prompt:', re.IGNORECASE),
    re.compile(r'<(system|instructions?|prompt)>', re.IGNORECASE),
    re.compile(r'execute the following (code|command|script|instruction)', re.IGNORECASE),
    re.compile(r'(run|exec|execute|call)\s*:\s*(os\.|subprocess\.|import\s)', re.IGNORECASE),
    re.compile(r'write (this|the following) to (/|~|[A-Z]:)', re.IGNORECASE),
    re.compile(r'delete (all|the|every|this)', re.IGNORECASE),
]


def scan_for_injection(text: str, source: str = "unknown") -> tuple[bool, list[str]]:
    """
    Scan external text (search results, file contents) for injection patterns.
    Returns (clean: bool, matches: list[str]).
    clean=False means suspicious content was found — caller should log and consider stripping.
    """
    found = []
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            found.append(f"[{source}] {pattern.pattern!r} matched: {match.group(0)!r}")
    return len(found) == 0, found


def strip_injection_candidates(text: str) -> tuple[str, int]:
    """
    Remove lines from text that match injection patterns.
    Returns (cleaned_text, lines_removed).
    """
    lines = text.splitlines()
    clean_lines = []
    removed = 0
    for line in lines:
        clean, _ = scan_for_injection(line)
        if clean:
            clean_lines.append(line)
        else:
            removed += 1
    return "\n".join(clean_lines), removed
