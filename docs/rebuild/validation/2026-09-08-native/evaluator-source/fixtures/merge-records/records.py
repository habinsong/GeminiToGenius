def merge_records(records):
    by_id = {}
    for record in records:
        by_id[record["id"]] = record
    return list(by_id.values())
