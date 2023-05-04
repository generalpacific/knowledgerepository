import datetime
import json
import os
import unittest
from unittest.mock import patch, MagicMock

import boto3
import dateutil.tz
import lambda_handler
import mock
import moto
import pytest

DAILY_DIGEST_TABLE = "daily-digest-table"
ANKIENTITIES_TABLE = "ankientities-table"

DAILY_DIGEST_ID_TEST_DATA = {"TWITTER": ["1", "2"],
                             "KINDLE": ["3", "4"], "NOTION": ["5", "6"]
                             }


@pytest.fixture
def lambda_environment():
    print("Setting lambda environment variables")
    os.environ['DAILY_DIGEST_TABLE'] = DAILY_DIGEST_TABLE
    os.environ['ANKIENTITIES_TABLE'] = ANKIENTITIES_TABLE


@pytest.fixture
def create_dynamodb_tables():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "date", "AttributeType": "S"}
            ],
            TableName=DAILY_DIGEST_TABLE,
            KeySchema=[
                {"AttributeName": "date", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "entityid", "AttributeType": "S"},
                {"AttributeName": "source", "AttributeType": "S"},
                {"AttributeName": "recallweight", "AttributeType": "N"}
            ],
            TableName=ANKIENTITIES_TABLE,
            KeySchema=[
                {"AttributeName": "entityid", "KeyType": "HASH"}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'source-recallweight-index',
                    'KeySchema': [
                        {'AttributeName': 'source', 'KeyType': 'HASH'},
                        {'AttributeName': 'recallweight', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield DAILY_DIGEST_TABLE, ANKIENTITIES_TABLE


@pytest.fixture
def populate_dynamodb_table_with_data(create_dynamodb_tables):
    """Creates data for daily digest"""

    table = boto3.resource("dynamodb").Table(ANKIENTITIES_TABLE)
    print("Adding data to anki entities table")
    txs = [
        {"entityid": "1", "foreign_id": "tweetid1", "source": "TWITTER", "plus_one": "12", "recallweight": "45"},
        {"entityid": "2", "foreign_id": "tweetid2", "source": "TWITTER", "plus_one": "12", "recallweight": "45"},
        {"entityid": "3", "foreign_id": "kindle3", "source": "KINDLE", "plus_one": "12", "recallweight": "45"},
        {"entityid": "4", "foreign_id": "kindle4", "source": "KINDLE", "plus_one": "12", "recallweight": "45"},
        {"entityid": "5", "foreign_id": "notion5", "source": "NOTION", "plus_one": "12", "recallweight": "45"},
        {"entityid": "6", "foreign_id": "notion6", "source": "NOTION", "plus_one": "12", "recallweight": "45"},
    ]
    for tx in txs:
        table.put_item(Item=tx)


## Tests start here.
def test_lambda_create_daily_digest(lambda_environment, populate_dynamodb_table_with_data):
    """Tests the lambda function for creating the daily digest."""

    response = lambda_handler.lambda_handler({}, {})

    print("response: ", response)
    assert response["statusCode"] == 200

    table = boto3.resource("dynamodb").Table(DAILY_DIGEST_TABLE)
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    today_date = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
    response = table.get_item(Key={
        'date': today_date,
    })
    expected_digest = DAILY_DIGEST_ID_TEST_DATA
    digest = json.loads(response['Item']['digest'])
    assert len(digest) == len(expected_digest)
    assert digest == expected_digest
