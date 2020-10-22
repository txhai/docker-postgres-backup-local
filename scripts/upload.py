# Sync backup files to S3 Storage
import argparse
import os
from datetime import datetime

import boto3
import pytz


# Get environment variable
def getenv(name, default_value=None):
    return os.environ.get(name, default_value)


ACCESS_KEY = getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = getenv('AWS_SECRET_ACCESS_KEY')
ENDPOINT_URL = getenv('AWS_S3_ENDPOINT_URL')
REGION = str(getenv('AWS_S3_REGION_NAME'))
BUCKET = getenv('AWS_STORAGE_BUCKET_NAME')
ROOT = getenv('AWS_LOCATION')
KEEP_DAYS = int(getenv('BACKUP_KEEP_DAYS', 7))
KEEP_WEEKS = int(getenv('BACKUP_KEEP_WEEKS', 4)) * 7
KEEP_MONTHS = int(getenv('BACKUP_KEEP_MONTHS', 6)) * 30


class BucketSession:
    def __init__(self):
        session = boto3.session.Session()
        self.client = session.client('s3',
                                     region_name=REGION,
                                     endpoint_url=ENDPOINT_URL,
                                     aws_access_key_id=ACCESS_KEY,
                                     aws_secret_access_key=SECRET_KEY)

    def upload(self, path):
        filename = os.path.basename(path)
        backup_type = os.path.basename(os.path.dirname(path))
        object_name = f"{ROOT}/{backup_type}/{filename}"

        try:
            self.client.upload_file(path, BUCKET, object_name)
        except Exception as e:
            print(f"Upload {path} to S3 failed.")
            print(e)
            return False
        return True

    def remove_old_files(self):
        try:
            response = self.client.list_objects(
                Bucket=BUCKET,
                Prefix=f"{ROOT}"
            )
            contents = response['Contents']
        except Exception as e:
            print(f"Retrieve remote backup files failed.")
            print(e)
            return

        time_now = datetime.now(tz=pytz.utc)
        removal_list = []

        for content in contents:
            backup_type = os.path.basename(os.path.dirname(content['Key']))
            last_modified = content['LastModified']

            if (backup_type == "daily" and (time_now - last_modified).days > KEEP_DAYS) or \
                    (backup_type == "weekly" and (time_now - last_modified).days > KEEP_WEEKS) or \
                    (backup_type == "monthly" and (time_now - last_modified).days > KEEP_MONTHS):
                removal_list.append(content['Key'])

        removal_payload = {
            'Objects': [
                {'Key': k} for k in removal_list
            ],
            'Quiet': True
        }

        try:
            self.client.delete_objects(
                Bucket=BUCKET,
                Delete=removal_payload
            )
        except Exception as e:
            print(f"Deletion request to S3 failed.")
            print(e)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, default=None, help="Daily backup file")
    parser.add_argument('-w', type=str, default=None, help="Weekly backup file")
    parser.add_argument('-m', type=str, default=None, help="Monthly backup file")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    bucket = BucketSession()
    d, w, m = args.d, args.w, args.m
    if d and os.path.exists(d):
        bucket.upload(d)
    if w and os.path.exists(w):
        bucket.upload(w)
    if m and os.path.exists(m):
        bucket.upload(m)
    bucket.remove_old_files()
    print("Backups synchronized to S3 successfully.")
