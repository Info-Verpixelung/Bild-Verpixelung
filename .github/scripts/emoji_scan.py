import sys
import re
import tokenize
from io import BytesIO
import pathlib

# Broad emoji range
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]')

# Explicit allowlist
ALLOWED_EMOJIS = {"✓"}  # U+2713

found = False


def contains_disallowed_emoji(text):
    for char in text:
        if EMOJI_PATTERN.match(char) and char not in ALLOWED_EMOJIS:
            return char
    return None


def scan_python(path):
    """Scan Python files including strings, ignoring comments."""
    global found
    content = path.read_bytes()
    tokens = tokenize.tokenize(BytesIO(content).readline)

    for token in tokens:
        if token.type == tokenize.COMMENT:
            continue  # Ignore comments

        bad = contains_disallowed_emoji(token.string)
        if bad:
            print(
                f"Disallowed emoji '{bad}' found in Python file: "
                f"{path} (line {token.start[0]})"
            )
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
    """Scan JS files including strings, ignoring comments."""
    global found
    code = path.read_text(encoding="utf-8", errors="ignore")
    stripped = strip_js_comments(code)

    for lineno, line in enumerate(stripped.splitlines(), 1):
        bad = contains_disallowed_emoji(line)
        if bad:
            print(
                f"Disallowed emoji '{bad}' found in JavaScript file: "
                f"{path} (line {lineno})"
            )
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
        print("Emojis are not allowed in code (except ✓).")
        sys.exit(1)
    else:
        print("No disallowed emojis found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emoji_scan.py <file_list.txt>")
        sys.exit(1)

    main(sys.argv[1])
