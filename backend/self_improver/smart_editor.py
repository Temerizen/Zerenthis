import re

def replace_in_function(code, function_name, new_block):
    pattern = rf"(def {function_name}\(.*?\):)([\s\S]*?)(?=\ndef |\Z)"
    match = re.search(pattern, code)

    if not match:
        return None

    header = match.group(1)
    return code.replace(match.group(0), header + "\n" + new_block)

def append_if_missing(code, marker, content):
    if marker in code:
        return code
    return code + "\n\n" + content
