import os

import boto3
import lambda_handler
import moto
import pytest

KINDLE_HIGHLIGHTS_S3_BUCKET = 'testdata'
KINDLE_HIGHLIGHTS_S3_FILE_NAME = 'MyClippings.txt'


@pytest.fixture
def lambda_environment():
    print("Setting lambda environment variables")
    os.environ['KINDLE_HIGHLIGHTS_S3_BUCKET'] = KINDLE_HIGHLIGHTS_S3_BUCKET
    os.environ['KINDLE_HIGHLIGHTS_S3_FILE_NAME'] = KINDLE_HIGHLIGHTS_S3_FILE_NAME


@pytest.fixture
def create_s3_file():
    with moto.mock_s3():
        # the file had 4 test highlights
        with open('testdata/testhighlights.txt', 'r') as file:
            content = file.read()

        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=KINDLE_HIGHLIGHTS_S3_BUCKET)
        s3.put_object(Bucket=KINDLE_HIGHLIGHTS_S3_BUCKET, Key=KINDLE_HIGHLIGHTS_S3_FILE_NAME,
                      Body=content)
        print('Done adding test data in s3 file: ', KINDLE_HIGHLIGHTS_S3_FILE_NAME)
        yield s3


## Tests start here.
def test_lambda_ingest_from_s3(lambda_environment, create_s3_file):
    """Tests the lambda function that reads highlights from s3 and ingests them."""

    response = lambda_handler.lambda_handler({}, {})

    print("response: ", response)
    assert response["statusCode"] == 200
    assert response["body"] == '\"Successfully ingested highlights from S3!. Number of highlights 4\"'
