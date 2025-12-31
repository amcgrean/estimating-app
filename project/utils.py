# project/utils.py
import hmac

def safe_str_cmp(a, b):
    return hmac.compare_digest(a, b)

import boto3
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )

def upload_file_to_s3(file_obj, folder='bids'):
    """
    Uploads a file to S3 and returns the object key.
    """
    if not file_obj or not file_obj.filename:
        return None
    
    s3 = get_s3_client()
    bucket_name = os.environ.get('AWS_BUCKET_NAME')
    
    if not bucket_name:
        print("Error: AWS_BUCKET_NAME not set.")
        return None

    filename = secure_filename(file_obj.filename)
    # Create unique key: folder/uuid_filename
    key = f"{folder}/{uuid.uuid4().hex}_{filename}"
        
    try:
        current_app.logger.info(f"Attempting S3 upload to bucket: {bucket_name}, Key: {key}")
        s3.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs={'ContentType': file_obj.content_type}
        )
        current_app.logger.info("S3 Upload Successful.")
        return key
    except Exception as e:
        current_app.logger.error(f"S3 Upload Error: {e}")
        return None

def get_s3_url(key, expiration=3600):
    """
    Generates a presigned URL for an S3 object.
    """
    if not key:
        return None
        
    s3 = get_s3_client()
    bucket_name = os.environ.get('AWS_BUCKET_NAME')
    
    try:
        response = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': key},
                                            ExpiresIn=expiration)
        return response
    except Exception as e:
        print(f"S3 Presign Error: {e}")
        return None
