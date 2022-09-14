#!/usr/bin/env python

import argparse
import time

import boto3
import os

from s3zero import S3ZeroRaw
from pathlib import Path

BUCKET = "hackathon-2022-jkemsley"
AWS_PROFILE = "dev"


# TODO move this logic into the s3zero module.  Gotta remove existing objects before writing
def delete_all_at_prefix(prefix):
    session = boto3.Session(profile_name='dev')
    s3 = session.resource('s3')
    bucket = s3.Bucket(BUCKET)
    bucket.objects.filter(Prefix=prefix).delete()


def write_to_s3(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    s3_key = f"{Path(filename).stem}/"
    delete_all_at_prefix(s3_key)

    session = boto3.Session(profile_name='dev')
    s3 = session.client('s3')

    start_time = time.time()
    size = os.path.getsize(filename)
    o = S3ZeroRaw(bucket=BUCKET, key_prefix=s3_key, client=s3, mode="w")
    o.write(data)
    o.close()
    time_elapsed = time.time() - start_time
    bytes_per_second = size / time_elapsed
    print(f"--- {size} bytes written to s3 in {str(round(time_elapsed, 2))} seconds ({str(round(bytes_per_second, 2))} bytes per second) ---")


def read_from_s3(filename):
    s3_key = f"{Path(filename).stem}/"
    session = boto3.Session(profile_name='dev')
    s3 = session.client('s3')

    start_time = time.time()

    o = S3ZeroRaw(bucket=BUCKET, key_prefix=s3_key, client=s3, mode="r")
    data = o.read_all()
    with open(filename, 'wb') as f:
        f.write(data)
    size = os.path.getsize(filename)

    time_elapsed = time.time() - start_time
    bytes_per_second = size / time_elapsed
    print(f"--- {size} bytes read from s3 in {str(round(time_elapsed, 2))} seconds ({str(round(bytes_per_second, 2))} bytes per second) ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write file to S3 bucket')
    parser.add_argument('mode', type=str, help='The file to write')
    parser.add_argument('filename', type=str, help='The file to write')
    args = parser.parse_args()

    if args.mode == "write":
        write_to_s3(args.filename)
    elif args.mode == "read":
        read_from_s3(args.filename)
    else:
        raise ValueError("dunno what you're trying to do")
