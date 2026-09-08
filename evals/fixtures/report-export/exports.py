import json


def to_json(records):
    return json.dumps(records, ensure_ascii=False, indent=2)
