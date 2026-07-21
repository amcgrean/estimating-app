# project/utils/s3.py
import hmac

def safe_str_cmp(a, b):
    return hmac.compare_digest(a, b)

import boto3
import os
import uuid
from botocore.client import Config
from werkzeug.utils import secure_filename
from flask import current_app

# ---------------------------------------------------------------------------
# Object storage: AWS S3 (legacy) or Cloudflare R2 (LiveEdge, unified).
#
# R2 is S3-API compatible, so the same boto3 code drives both — the only
# difference is the endpoint, credentials, bucket, and that R2 has no object
# ACLs. Selection is env-driven so the storage cutover is a config flip that
# can be rolled back instantly, exactly like DATABASE_URL:
#
#   Set R2_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY  -> R2
#   Leave them unset                                             -> AWS S3
#
# Both apps use the same key scheme (folder/uuid_filename), so keys written by
# either app resolve from the other once both point at R2.
# ---------------------------------------------------------------------------

def use_r2():
    """True when R2 credentials are configured (post-cutover)."""
    return bool(
        os.environ.get('R2_ACCOUNT_ID')
        and os.environ.get('R2_ACCESS_KEY_ID')
        and os.environ.get('R2_SECRET_ACCESS_KEY')
    )


def get_bucket_name():
    if use_r2():
        return os.environ.get('R2_BUCKET_NAME', 'bids')
    return os.environ.get('AWS_BUCKET_NAME')


def get_s3_client():
    if use_r2():
        return boto3.client(
            's3',
            endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY'),
            region_name='auto',
            config=Config(signature_version='s3v4'),
        )
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )


def upload_file_to_s3(file_obj, folder='bids'):
    """
    Uploads a file to object storage and returns the object key.
    """
    if not file_obj or not file_obj.filename:
        return None

    s3 = get_s3_client()
    bucket_name = get_bucket_name()

    if not bucket_name:
        print("Error: storage bucket not set (AWS_BUCKET_NAME / R2_BUCKET_NAME).")
        return None

    filename = secure_filename(file_obj.filename)
    # Create unique key: folder/uuid_filename
    key = f"{folder}/{uuid.uuid4().hex}_{filename}"

    try:
        current_app.logger.info(f"Attempting upload to bucket: {bucket_name}, Key: {key}")
        s3.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs={'ContentType': file_obj.content_type}
        )
        current_app.logger.info("Upload Successful.")
        return key
    except Exception as e:
        current_app.logger.error(f"Upload Error: {e}")
        return None


def get_s3_url(key, expiration=3600):
    """
    Generates a presigned GET URL for an object.
    """
    if not key:
        return None

    s3 = get_s3_client()
    bucket_name = get_bucket_name()

    try:
        response = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': key},
                                            ExpiresIn=expiration)
        return response
    except Exception as e:
        print(f"Presign Error: {e}")
        return None


def create_presigned_post(object_name, file_type, folder='bids', expiration=3600):
    """
    Generate a presigned direct-browser upload.

    Returns a uniform contract for both backends:
        { 'method': 'POST'|'PUT', 'url': <str>, 'fields': { 'key': <str>, ... } }

    `fields.key` is always present so the caller can save the object key to the
    DB regardless of backend.

    IMPORTANT — R2 does NOT implement presigned POST (returns
    501 NotImplemented: "Presigned post requests are not yet implemented"), so
    R2 uses a presigned PUT instead, which is verified working. AWS S3 keeps
    using presigned POST exactly as before, so this is safe to roll back by
    unsetting the R2_* env vars.
    """
    s3 = get_s3_client()
    bucket_name = get_bucket_name()

    # Ensure unique key
    filename = secure_filename(object_name)
    key = f"{folder}/{uuid.uuid4().hex}_{filename}"

    try:
        if use_r2():
            # R2: presigned PUT. Client must send a matching Content-Type header.
            url = s3.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket_name, 'Key': key, 'ContentType': file_type},
                ExpiresIn=expiration,
            )
            return {'method': 'PUT', 'url': url, 'fields': {'key': key}}

        # AWS S3: presigned POST (unchanged legacy behaviour, incl. private ACL)
        response = s3.generate_presigned_post(
            Bucket=bucket_name,
            Key=key,
            Fields={'acl': 'private', 'Content-Type': file_type},
            Conditions=[
                {'acl': 'private'},
                {'Content-Type': file_type},
                ["content-length-range", 0, 524288000],  # 500 MB limit
            ],
            ExpiresIn=expiration
        )
        response['method'] = 'POST'
        return response
    except Exception as e:
        current_app.logger.error(f"Presign Error: {e}")
        return None
