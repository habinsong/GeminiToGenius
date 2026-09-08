from records import merge_records


def summarize(records):
    return {"items": merge_records(records)}
