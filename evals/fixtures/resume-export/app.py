from exports import to_json


DOWNLOAD_STEM = "records"


def download(records, format="json"):
    if format != "json":
        raise ValueError("unsupported format")
    return {"filename": DOWNLOAD_STEM + ".json",
            "media_type": "application/json; charset=utf-8", "content": to_json(records)}
