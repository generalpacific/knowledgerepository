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

NOTION_TABLE_NAME = "notion-book-quotes"
KINDLE_HIGHLIGHTS_TABLE = "KINDLE_HIGHLIGHTS_TABLE"
DAILY_DIGEST_TABLE = "daily-digest-table"
ANKIENTITIES_TABLE = "ankientities-table"

DAILY_DIGEST_TEST_DATA = {"TWITTER": ["1", "2"],
                          "KINDLE": ["3", "4"], "NOTION": ["5", "6"]
                          }


@pytest.fixture
def lambda_environment():
    print("Setting lambda environment variables")
    os.environ['NOTION_BOOK_QUOTES_TABLE'] = NOTION_TABLE_NAME
    os.environ['KINDLE_HIGHLIGHTS_TABLE'] = KINDLE_HIGHLIGHTS_TABLE
    os.environ['DAILY_DIGEST_TABLE'] = DAILY_DIGEST_TABLE
    os.environ['ANKIENTITIES_TABLE'] = ANKIENTITIES_TABLE


@pytest.fixture
def kindle_data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"}
            ],
            TableName=KINDLE_HIGHLIGHTS_TABLE,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield KINDLE_HIGHLIGHTS_TABLE


@pytest.fixture
def daily_digest_data_table():
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

        yield DAILY_DIGEST_TABLE


@pytest.fixture
def ankientities_data_table():
    with moto.mock_dynamodb():
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

        yield ANKIENTITIES_TABLE


@pytest.fixture
def notion_data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"}
            ],
            TableName=NOTION_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        yield NOTION_TABLE_NAME


@pytest.fixture
def ankientities_table_with_data(ankientities_data_table):
    """Creates data for anki entities"""

    table = boto3.resource("dynamodb").Table(ankientities_data_table)
    print("Adding data to anki entities table")
    txs = [
        {"entityid": "1", "foreign_id": "tweetid1", "source": "TWITTER"},
        {"entityid": "2", "foreign_id": "tweetid2", "source": "TWITTER"},
        {"entityid": "3", "foreign_id": "kindle3", "source": "KINDLE"},
        {"entityid": "4", "foreign_id": "kindle4", "source": "KINDLE"},
        {"entityid": "5", "foreign_id": "notion5", "source": "NOTION"},
        {"entityid": "6", "foreign_id": "notion6", "source": "NOTION"},
    ]
    for tx in txs:
        table.put_item(Item=tx)


@pytest.fixture
def daily_digest_table_with_data(daily_digest_data_table):
    """Creates data for daily digest"""

    table = boto3.resource("dynamodb").Table(daily_digest_data_table)
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    today_date = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
    print("Adding digest for date: ", today_date)
    txs = [
        {"date": today_date,
         "digest": json.dumps(DAILY_DIGEST_TEST_DATA)},
    ]
    for tx in txs:
        table.put_item(Item=tx)


## Tests start here.

def test_lambda_daily_digest(lambda_environment, daily_digest_table_with_data):
    """Tests the lambda function for getting the daily digest."""

    response = lambda_handler.lambda_handler({}, {})

    print("response: ", response)
    assert response["statusCode"] == 200
