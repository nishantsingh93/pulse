import re
from fastapi import HTTPException

TOKEN = re.compile(r'"([^"\n]+)"|(#?[\w][\w-]*)', re.UNICODE)


def parse_query(value: str) -> dict:
    value = value.strip()
    if not 1 <= len(value) <= 256 or value.count('"') % 2:
        raise HTTPException(400, "Query must be 1–256 characters with balanced quotes")
    tokens = []
    cursor = 0
    for match in TOKEN.finditer(value):
        if value[cursor:match.start()].strip():
            raise HTTPException(400, "Unsupported query operator or punctuation")
        phrase, term = match.groups()
        tokens.append({"kind": "phrase" if phrase else "hashtag" if term.startswith("#") else "term", "value": phrase or term})
        cursor = match.end()
    if not tokens or value[cursor:].strip() or any(t["value"].upper() in {"OR", "NOT", "AND"} for t in tokens):
        raise HTTPException(400, "Only terms, quoted phrases and hashtags are supported")
    return {"version": 1, "operator": "and", "tokens": tokens}


def matches_text(ast: dict, text: str) -> bool:
    text = text.casefold()
    return all(token["value"].casefold() in text for token in ast["tokens"])
