import boto3
import datetime
import dateutil.tz
import json
import lambda_function
import mock
import moto
import os
import pytest
import unittest
from unittest.mock import patch, MagicMock

NOTION_TABLE_NAME = "notion-book-quotes"
KINDLE_HIGHLIGHTS_TABLE = "kindle-highlights-table"
DAILY_DIGEST_TABLE = "daily-digest-table"
ANKIENTITIES_TABLE = "ankientities-table"

DAILY_DIGEST_ID_TEST_DATA = {"TWITTER": ["1", "2"],
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
                {"AttributeName": "foreign_id", "AttributeType": "S"}
            ],
            TableName=ANKIENTITIES_TABLE,
            KeySchema=[
                {"AttributeName": "entityid", "KeyType": "HASH"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "foreign_id-index",
                    "KeySchema": [
                        {"AttributeName": "foreign_id", "KeyType": "HASH"}
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "tite", "AttributeType": "S"}
            ],
            TableName=NOTION_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "tite-index",
                    "KeySchema": [
                        {"AttributeName": "tite", "KeyType": "HASH"}
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "tite", "AttributeType": "S"}
            ],
            TableName=KINDLE_HIGHLIGHTS_TABLE,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "tite-index",
                    "KeySchema": [
                        {"AttributeName": "tite", "KeyType": "HASH"}
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                }
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
        {"entityid": "1", "foreign_id": "tweetid1", "source": "TWITTER", "plus_one": 12},
        {"entityid": "2", "foreign_id": "tweetid2", "source": "TWITTER", "plus_one": 13},
        {"entityid": "3", "foreign_id": "kindle3", "source": "KINDLE", "plus_one": 14},
        {"entityid": "4", "foreign_id": "kindle4", "source": "KINDLE", "plus_one": 15},
        {"entityid": "5", "foreign_id": "notion5", "source": "NOTION", "plus_one": 16},
        {"entityid": "6", "foreign_id": "notion6", "source": "NOTION", "plus_one": 17},
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
def test_plus_one_404(lambda_environment, populate_dynamodb_table_with_data):
    event = {'queryStringParameters': {'entityid': '453425354'}}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 404
    assert response['body'] == "453425354 Not found"


def test_plus_one_success(lambda_environment, populate_dynamodb_table_with_data):
    event = {'queryStringParameters': {'entityid': '6'}}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 200
    assert response['body'] == "Successfully PlusOned the entity"

    #### Verify plus one in db
    dynamodb = boto3.client("dynamodb")
    response = dynamodb.get_item(TableName=ANKIENTITIES_TABLE, Key={
        'entityid': {'S': '6'},
    })
    dynamodb_data = response['Item']
    assert dynamodb_data['plus_one']['N'] == '18'


def test_lambda_handler_no_query_string_parameters():
    event = {}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response['body'] == "No queryStringParameters in event"


def test_lambda_handler_none_query_string_parameters():
    event = {'queryStringParameters': None}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response['body'] == "queryStringParameters in event is none"


def test_lambda_handler_no_entityid():
    event = {'queryStringParameters': {}}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response[
               'body'] == "No id in event[queryStringParameters]"
