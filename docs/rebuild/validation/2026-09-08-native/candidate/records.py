def merge_records(records):
    by_id = {}
    for record in records:
        if "id" not in record:
            raise ValueError("Record missing 'id'")
        rec_id = record["id"]
        if rec_id in by_id:
            by_id[rec_id] = {**by_id[rec_id], **record}
        else:
            by_id[rec_id] = dict(record)
    return list(by_id.values())

