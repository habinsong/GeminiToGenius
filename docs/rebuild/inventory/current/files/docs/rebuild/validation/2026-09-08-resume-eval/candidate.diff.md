# `docs/rebuild/validation/2026-09-08-resume-eval/candidate.diff`

- 형식: `100644`
- 바이트: 942
- SHA-256: `6c071cc78a338a2e4c427d01201f23d070c54b5e9ebd36dea1109b1d2e1f1ecf`
- 인코딩: `utf-8`

```
diff --git a/app.py b/app.py
index 89225b6..bab6c49 100644
--- a/app.py
+++ b/app.py
@@ -1,11 +1,20 @@
-from exports import to_json
+from exports import to_csv, to_json
 
 
-DOWNLOAD_STEM = "records"
+DOWNLOAD_STEM = "현장 기록"
 
 
 def download(records, format="json"):
-    if format != "json":
-        raise ValueError("unsupported format")
-    return {"filename": DOWNLOAD_STEM + ".json",
-            "media_type": "application/json; charset=utf-8", "content": to_json(records)}
+    if format == "json":
+        return {
+            "filename": DOWNLOAD_STEM + ".json",
+            "media_type": "application/json; charset=utf-8",
+            "content": to_json(records),
+        }
+    if format == "csv":
+        return {
+            "filename": DOWNLOAD_STEM + ".csv",
+            "media_type": "text/csv; charset=utf-8",
+            "content": to_csv(records),
+        }
+    raise ValueError("unsupported format")
```
