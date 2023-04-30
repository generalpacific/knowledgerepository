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
KINDLE_HIGHLIGHTS_TABLE = "kindle-highlights-table"
DAILY_DIGEST_TABLE = "daily-digest-table"
ANKIENTITIES_TABLE = "ankientities-table"

DAILY_DIGEST_ID_TEST_DATA = {"TWITTER": ["1", "2"],
                             "KINDLE": ["3", "4"], "NOTION": ["5", "6"]
                             }

EXPECTED_DAILY_DIGEST_TEST_DATA = {"digest": [
    {"entityid": "5", "title": "title5", "author": "author5", "quote": "quote5", "plusones": "12"},
    {"entityid": "4", "title": "title4", "author": "author4", "highlight": "highlight4", "plusones": "12"},
    {"entityid": "1", "tweet_id": "tweetid1", "plusones": "12"},
    {"entityid": "6", "title": "title6", "author": "author6", "quote": "quote6", "plusones": "12"},
    {"entityid": "2", "tweet_id": "tweetid2", "plusones": "12"},
    {"entityid": "3", "title": "title3", "author": "author3", "highlight": "highlight3", "plusones": "12"}]}


@pytest.fixture
def lambda_environment():
    print("Setting lambda environment variables")
    os.environ['NOTION_BOOK_QUOTES_TABLE'] = NOTION_TABLE_NAME
    os.environ['KINDLE_HIGHLIGHTS_TABLE'] = KINDLE_HIGHLIGHTS_TABLE
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
            TableName=NOTION_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}
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

        yield DAILY_DIGEST_TABLE, ANKIENTITIES_TABLE


@pytest.fixture
def populate_dynamodb_table_with_data(create_dynamodb_tables):
    """Creates data for daily digest"""

    table = boto3.resource("dynamodb").Table(DAILY_DIGEST_TABLE)
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    today_date = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
    print("Adding digest for date: ", today_date)
    txs = [
        {"date": today_date,
         "digest": json.dumps(DAILY_DIGEST_ID_TEST_DATA)},
    ]
    for tx in txs:
        table.put_item(Item=tx)

    table = boto3.resource("dynamodb").Table(ANKIENTITIES_TABLE)
    print("Adding data to anki entities table")
    txs = [
        {"entityid": "1", "foreign_id": "tweetid1", "source": "TWITTER", "plus_one": "12"},
        {"entityid": "2", "foreign_id": "tweetid2", "source": "TWITTER", "plus_one": "12"},
        {"entityid": "3", "foreign_id": "kindle3", "source": "KINDLE", "plus_one": "12"},
        {"entityid": "4", "foreign_id": "kindle4", "source": "KINDLE", "plus_one": "12"},
        {"entityid": "5", "foreign_id": "notion5", "source": "NOTION", "plus_one": "12"},
        {"entityid": "6", "foreign_id": "notion6", "source": "NOTION", "plus_one": "12"},
    ]
    for tx in txs:
        table.put_item(Item=tx)

    table = boto3.resource("dynamodb").Table(NOTION_TABLE_NAME)
    print("Adding data to notion table")
    txs = [
        {"id": "notion5", "author": "author5", "quote": "quote5", "tite": "title5"},
        {"id": "notion6", "author": "author6", "quote": "quote6", "tite": "title6"},
    ]
    for tx in txs:
        table.put_item(Item=tx)

    table = boto3.resource("dynamodb").Table(KINDLE_HIGHLIGHTS_TABLE)
    print("Adding data to kindle table")
    txs = [
        {"id": "kindle3", "author": "author3", "highlight": "highlight3", "tite": "title3"},
        {"id": "kindle4", "author": "author4", "highlight": "highlight4", "tite": "title4"},
    ]
    for tx in txs:
        table.put_item(Item=tx)


## Tests start here.

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def test_lambda_daily_digest(lambda_environment, populate_dynamodb_table_with_data):
    """Tests the lambda function for getting the daily digest."""

    response = lambda_handler.lambda_handler({}, {})

    print("response: ", response)
    assert response["statusCode"] == 200

    digest = json.loads(response["body"])["digest"]
    expected_digest = EXPECTED_DAILY_DIGEST_TEST_DATA['digest']
    assert len(digest) == len(expected_digest)
    assert ordered(digest) == ordered(expected_digest)