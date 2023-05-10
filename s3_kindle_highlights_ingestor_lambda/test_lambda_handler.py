import json
import os

import boto3
import lambda_handler
import moto
import pytest

KINDLE_HIGHLIGHTS_S3_BUCKET = 'testdata'
KINDLE_HIGHLIGHTS_S3_FILE_NAME = 'MyClippings.txt'

# corresponds to testdata/testhighlights.txt
EXPECTED_HIGHLIGHTS_FROM_TESTDATA = [{'title': 'Thinking in Systems', 'author': 'Meadows, Donella H.',
                                      'metadata': 'Your Highlight on page 22 | Location 492-493 | Added on Saturday, July 16, 2022 9:50:38 AM',
                                      'highlight': 'Everyone understands that you can prolong the life of an oil-based economy by discovering new oil deposits. It seems to be harder to understand that the same result can be achieved by burning less oil.'},
                                     {'title': 'Egghead', 'author': 'Burnham, Bo',
                                      'metadata': 'Your Highlight on page 140 | Location 707-707 | Added on Sunday, July 17, 2022 7:16:19 AM',
                                      'highlight': 'I wanted something this morning. I may be stuck. But at least I’m three feet closer to it.'},
                                     {'title': 'How to Do Nothing', 'author': 'Odell, Jenny',
                                      'metadata': 'Your Highlight on page ix | Location 46-47 | Added on Sunday, July 17, 2022 7:18:10 AM',
                                      'highlight': 'We submit our free time to numerical evaluation, interact with algorithmic versions of each other, and build and maintain personal brands.'},
                                     {'title': 'Indistractable', 'author': 'Eyal, Nir',
                                      'metadata': 'Your Highlight on page 83 | Location 1189-1191 | Added on Wednesday, August 10, 2022 7:59:22 AM',
                                      'highlight': 'The Fogg Behavior Model states that for a behavior (B) to occur, three things must be present at the same time: motivation (M), ability (A), and a trigger (T). More succinctly, B = MAT.'}]

KINDLE_HIGHLIGHTS_TABLE = "kindle-highlights-table"
ANKIENTITIES_TABLE = "ankientities-table"


@pytest.fixture
def lambda_environment():
    print("Setting lambda environment variables")
    os.environ['KINDLE_HIGHLIGHTS_S3_BUCKET'] = KINDLE_HIGHLIGHTS_S3_BUCKET
    os.environ['KINDLE_HIGHLIGHTS_S3_FILE_NAME'] = KINDLE_HIGHLIGHTS_S3_FILE_NAME
    os.environ['KINDLE_HIGHLIGHTS_TABLE'] = KINDLE_HIGHLIGHTS_TABLE
    os.environ['ANKIENTITIES_TABLE'] = ANKIENTITIES_TABLE


@pytest.fixture
def create_aws_resources():
    with moto.mock_all():
        # the file had 4 test highlights
        with open('testdata/testhighlights.txt', 'r') as file:
            content = file.read()

        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=KINDLE_HIGHLIGHTS_S3_BUCKET)
        s3.put_object(Bucket=KINDLE_HIGHLIGHTS_S3_BUCKET, Key=KINDLE_HIGHLIGHTS_S3_FILE_NAME,
                      Body=content)
        print('Done adding test data in s3 file: ', KINDLE_HIGHLIGHTS_S3_FILE_NAME)

        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "entityid", "AttributeType": "S"}
            ],
            TableName=ANKIENTITIES_TABLE,
            KeySchema=[
                {"AttributeName": "entityid", "KeyType": "HASH"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            TableName=KINDLE_HIGHLIGHTS_TABLE,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        yield s3, KINDLE_HIGHLIGHTS_TABLE, ANKIENTITIES_TABLE


## Tests start here.
def test_lambda_ingest_from_s3(lambda_environment, create_aws_resources):
    """Tests the lambda function that reads highlights from s3 and ingests them."""

    response = lambda_handler.lambda_handler({}, {})

    print("response: ", response)
    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(EXPECTED_HIGHLIGHTS_FROM_TESTDATA)

    #### Verify data in kindle highlights is saved correctly.
    dynamodb = boto3.client("dynamodb")
    response = dynamodb.scan(TableName=KINDLE_HIGHLIGHTS_TABLE)

    dynamodb_data = response['Items']
    assert len(dynamodb_data) == len(EXPECTED_HIGHLIGHTS_FROM_TESTDATA)
    # Extract data from DynamoDB items and create a list of dicts
    foreign_ids = []
    for item in dynamodb_data:
        foreign_ids.append(item['id']['S'])
        item_data = {
            "title": item['tite']['S'],
            "author": item['author']['S'],
            "highlight": item['highlight']['S'],
            "metadata": item['metadata']['S']
        }
        assert item_data in EXPECTED_HIGHLIGHTS_FROM_TESTDATA

    response = dynamodb.scan(TableName=ANKIENTITIES_TABLE)
    dynamodb_data = response['Items']
    assert len(dynamodb_data) == len(EXPECTED_HIGHLIGHTS_FROM_TESTDATA)
    dynamo_foreign_ids_data = set()
    for item in dynamodb_data:
        dynamo_foreign_ids_data.add(item['foreign_id']['S'])

    for foreign_id in foreign_ids:
        assert foreign_id in dynamo_foreign_ids_data

    # TODO: Add support for testing the dedup logic

