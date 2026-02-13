import sys
import re
import tokenize
from io import BytesIO
import pathlib

# Emoji regex (covers most emoji blocks)
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]')
found = False

def scan_python(path):
    """Scan Python files including strings for emojis, ignoring comments only."""
    global found
    content = path.read_bytes()
    tokens = tokenize.tokenize(BytesIO(content).readline)

    for token in tokens:
        if token.type == tokenize.COMMENT:
            continue  # skip comments
        if EMOJI_PATTERN.search(token.string):
            print(f"Emoji found in Python code: {path} (line {token.start[0]})")
            found = True

def strip_js_comments(code):
    """Strip JavaScript comments but keep strings intact."""
    result = []
    i = 0
    length = len(code)
    while i < length:
        if code[i:i+2] == "//":
            i += 2
            while i < length and code[i] != "\n":
                i += 1
        elif code[i:i+2] == "/*":
            i += 2
            while i < length - 1 and code[i:i+2] != "*/":
                i += 1
            i += 2
        else:
            result.append(code[i])
            i += 1
    return "".join(result)

def scan_js(path):
    """Scan JS files including strings for emojis, ignoring comments."""
    global found
    code = path.read_text(encoding="utf-8", errors="ignore")
    stripped = strip_js_comments(code)
    for lineno, line in enumerate(stripped.splitlines(), 1):
        if EMOJI_PATTERN.search(line):
            print(f"Emoji found in JavaScript code: {path} (line {lineno})")
            found = True

def main(file_list_path):
    with open(file_list_path) as f:
        files = [line.strip() for line in f if line.strip()]

    for file_path in files:
        path = pathlib.Path(file_path)
        try:
            if path.suffix == ".py":
                scan_python(path)
            elif path.suffix == ".js":
                scan_js(path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if found:
        print("Emojis are not allowed in code (including strings).")
        sys.exit(1)
    else:
        print("No emojis found in code.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emoji_scan.py <file_list.txt>")
        sys.exit(1)
    main(sys.argv[1])
