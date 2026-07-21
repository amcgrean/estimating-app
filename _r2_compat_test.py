"""
Verifies the ACTUAL project/utils/s3.py functions work against Cloudflare R2
before the cutover — exercising the real code path Flask will use.

Run:  .venv\Scripts\python.exe _r2_compat_test.py
"""
import os, re, io, sys, uuid, types

# --- load R2 creds from the LiveEdge .env.local, then point s3.py at R2 ---
ENV = r"C:\Users\amcgrean\python\beisser-takeoff\.env.local"
with open(ENV, "r", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"^([^#=]+)=(.+)$", line.strip())
        if m:
            os.environ.setdefault(m.group(1).strip(), m.group(2).strip().strip('"').strip("'"))

# stub flask.current_app so s3.py's logger calls work outside an app context
import flask
class _Log:
    def info(self, *a, **k): pass
    def error(self, *a, **k): print("   logger.error:", *a)
flask.current_app = types.SimpleNamespace(logger=_Log())

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project.utils.s3 import (
    use_r2, get_bucket_name, get_s3_client,
    upload_file_to_s3, get_s3_url, create_presigned_post,
)
import urllib3
http = urllib3.PoolManager()

print(f"\nR2 mode active: {use_r2()}   bucket: {get_bucket_name()}")
assert use_r2(), "R2_* env vars not picked up — aborting"

s3 = get_s3_client()
bucket = get_bucket_name()
made, ok = [], {}

# 1. upload_file_to_s3 (server-side)
try:
    f = io.BytesIO(b"hello-server-upload")
    f.filename = "cutover_test.txt"
    f.content_type = "text/plain"
    key = upload_file_to_s3(f, folder="_cutover_test")
    if key:
        made.append(key); ok["upload_file_to_s3"] = "PASS"
    else:
        ok["upload_file_to_s3"] = "FAIL: returned None"
except Exception as e:
    ok["upload_file_to_s3"] = f"FAIL: {e}"

# 2. get_s3_url (presigned GET) on what we just uploaded
try:
    url = get_s3_url(made[0]) if made else None
    r = http.request("GET", url) if url else None
    ok["get_s3_url"] = "PASS" if r and r.status == 200 and r.data == b"hello-server-upload" else f"FAIL: {getattr(r,'status',None)}"
except Exception as e:
    ok["get_s3_url"] = f"FAIL: {e}"

# 3. create_presigned_post -> should return method=PUT on R2, and upload must work
try:
    data = create_presigned_post("plan.pdf", "application/pdf", folder="_cutover_test")
    if not data:
        ok["create_presigned_post"] = "FAIL: returned None"
    elif data.get("method") != "PUT":
        ok["create_presigned_post"] = f"FAIL: expected method PUT on R2, got {data.get('method')}"
    elif not data.get("fields", {}).get("key"):
        ok["create_presigned_post"] = "FAIL: fields.key missing (JS needs it)"
    else:
        # simulate exactly what the browser JS now does for isPut
        r = http.request("PUT", data["url"], body=b"%PDF-1.4 fake",
                         headers={"Content-Type": "application/pdf"})
        if r.status in (200, 201, 204):
            made.append(data["fields"]["key"])
            ok["create_presigned_post (browser PUT)"] = "PASS"
        else:
            ok["create_presigned_post (browser PUT)"] = f"FAIL: HTTP {r.status} {r.data[:160]}"
        ok["create_presigned_post contract"] = "PASS (method=PUT, fields.key present)"
except Exception as e:
    ok["create_presigned_post"] = f"FAIL: {e}"

print("=" * 66)
for k, v in ok.items():
    print(f"  {'OK  ' if v.startswith('PASS') else 'XX  '}{k:<38} {v}")

for k in made:
    try: s3.delete_object(Bucket=bucket, Key=k)
    except Exception: pass
print(f"\ncleaned up {len(made)} test object(s)")
sys.exit(0 if all(v.startswith("PASS") for v in ok.values()) else 1)
