import json
import re


def find_matching_codes(obj, codes=None):
    if codes is None:
        codes = set()
    pattern = re.compile(r"\b[A-Z]{6}\d{4}\b")
    if isinstance(obj, dict):
        for v in obj.values():
            find_matching_codes(v, codes)
    elif isinstance(obj, list):
        for item in obj:
            find_matching_codes(item, codes)
    elif isinstance(obj, str):
        matches = pattern.findall(obj)
        codes.update(matches)
    return codes


with open("details.json") as f:
    data = json.load(f)


codes = find_matching_codes(data)
with open("all_codes.txt", "w") as f:
    for code in sorted(codes):
        f.write(code + "\n")
