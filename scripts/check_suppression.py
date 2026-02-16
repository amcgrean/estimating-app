
import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_suppression():
    sesv2 = boto3.client(
        'sesv2',
        aws_access_key_id=os.environ.get('MAIL_USERNAME'),
        aws_secret_access_key="fwIpxEEfRECW2R1vl+01j9sJH0ZnSXgW9U+g+bEe",
        region_name="us-east-1"
    )
    email = "amcgrean@beisserlumber.com"
    try:
        response = sesv2.get_suppressed_destination(EmailAddress=email)
        print("Suppression Found:")
        print(json.dumps(response, indent=2, default=str))
    except sesv2.exceptions.NotFoundException:
        print(f"Recipient {email} is NOT on the suppression list.")
    except Exception as e:
        print(f"Error checking suppression list: {e}")

if __name__ == "__main__":
    check_suppression()
