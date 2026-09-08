import csv
import io
import json


def to_json(records):
    return json.dumps(records, ensure_ascii=False, indent=2)


def to_csv(records):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["id", "name", "note"])
    for record in records:
        writer.writerow([record.get(name, "") for name in ("id", "name", "note")])
    return output.getvalue()
