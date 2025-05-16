import boto3
from botocore.exceptions import ProfileNotFound
import logging


def init_boto3_session(profile_name, region):
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        return session
    except ProfileNotFound as e:
        logging.error(f"❌ AWS profile '{profile_name}' not found. Make sure it's configured.")
        exit(1)
