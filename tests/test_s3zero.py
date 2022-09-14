import pytest
from s3zero import S3ZeroRaw
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path

from moto import mock_s3


@pytest.fixture()
def data():
    return {
        "bucket_name": "my-test-bucket",
        "long_string": "a" * 1048
    }


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def s3(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        yield conn


@pytest.fixture
def valid_object_prefixes():
    return [
        "froglegs",
        "froglegs:",
        "froglegs/",
        "froglegs:/",
        "蛙脚/",
        "𓆏𓃀/",
        "ourneighborusedtogofroggiggingandhewouldoffertocookthelegsupforusbuthewasweirdandsowealwayssaidno",
    ]


@pytest.fixture
def bucket(s3, data):
    s3.create_bucket(Bucket=data["bucket_name"])
    yield boto3.resource('s3').Bucket(data["bucket_name"])


# def test_chunk_length(s3, bucket):
#     o = s3zero.S3ZeroBlob(bucket=bucket.name, prefix="doot", client=s3)
#     # Try writing something barely too long
#     with pytest.raises(ValueError):
#         o._S3ZeroBlob__write_value("doot" * 256)
#
#     # Try writing something of max length
#     try:
#         o._S3ZeroBlob__write_value("d" * 1020)
#     except ValueError:
#         pytest.fail("Chunk length of 1020 should be allowed with prefix of length 4")


# def test_write_value(s3, bucket):
#     o = s3zero.S3ZeroBlob(bucket=bucket.name, key_prefix="doot", client=s3)
#     o._S3ZeroBlob__write_value("doot")
#     # Just try to check if object is there
#     s3.head_object(Bucket=bucket.name, Key="dootdoot")

def test_open_closed(s3, bucket):
    o = S3ZeroRaw(bucket=bucket.name, client=s3)
    assert not o.closed
    o.close()
    assert o.closed


def test_modes(s3, bucket):
    o = S3ZeroRaw(bucket=bucket.name, client=s3, mode="r")
    assert o.readable()
    assert not o.writable()
    o = S3ZeroRaw(bucket=bucket.name, client=s3, mode="w")
    assert o.writable()
    assert not o.readable()
    with pytest.raises(ValueError):
        o.close()
        o.writable()
    with pytest.raises(ValueError):
        o = S3ZeroRaw(bucket=bucket.name, client=s3, mode="bzzt")

def test_write_read(s3, bucket):
    o = S3ZeroRaw(bucket=bucket.name, key_prefix="doot/", client=s3, mode="w")

    txt = Path('/Users/jkemsley/ws/s3zero/s3zero/data/lorem_ipsum.txt').read_text()
    o.write(txt.encode())
    o.close()

    o = S3ZeroRaw(bucket=bucket.name, key_prefix="doot/", client=s3, mode="r")
    txt_out = o.read_all().decode()
    # # print(txt_out)
    assert txt == txt_out
    print(txt_out)
    assert False

    # print(s3.list_objects_v2(Bucket=bucket.name, Prefix="doot/"))
    # assert False


