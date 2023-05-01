import datetime
import json
import os
import random

import boto3
import dateutil.tz
from botocore.exceptions import ClientError


# Get the notion quotes stored for the given entities
def __get_quote_json(highlight_entities):
    quote_json = []

    foreignid_to_originaldata = {}
    for highlight_entity in highlight_entities:
        if 'plus_one' in highlight_entity:
            foreignid_to_originaldata[highlight_entity['foreign_id']] = [highlight_entity['entityid'],
                                                                         highlight_entity['plus_one']]
        else:
            foreignid_to_originaldata[highlight_entity['foreign_id']] = [highlight_entity['entityid'], 0]

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['NOTION_BOOK_QUOTES_TABLE'])

        batch_keys = {
            table.name: {
                'Keys': [{'id': highlight_entity['foreign_id']} for highlight_entity in highlight_entities]
            }
        }
        try:
            responses = dynamodb.batch_get_item(RequestItems=batch_keys)

        except ClientError as e:
            print("ERROR while getting quotes: " +
                  e.response['Error']['Message'])
            raise e
        else:
            for item in responses['Responses'][table.name]:
                quote = {}
                quote['entityid'] = foreignid_to_originaldata[item['id']][0]
                quote['title'] = item['tite']
                quote['author'] = item['author']
                quote['quote'] = item['quote']
                quote['plusones'] = str(foreignid_to_originaldata[item['id']][1])
                quote_json.append(quote)
    except Exception as e:
        print("Got error while get highlights. Error: ")
        raise e
    return quote_json


def __get_highlights_json(highlight_entities):
    quote_json = []

    foreignid_to_originaldata = {}
    for highlight_entity in highlight_entities:
        if 'plus_one' in highlight_entity:
            foreignid_to_originaldata[highlight_entity['foreign_id']] = [highlight_entity['entityid'],
                                                                         highlight_entity['plus_one']]
        else:
            foreignid_to_originaldata[highlight_entity['foreign_id']] = [highlight_entity['entityid'], 0]

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['KINDLE_HIGHLIGHTS_TABLE'])

        batch_keys = {
            table.name: {
                'Keys': [{'id': highlight_entity['foreign_id']} for highlight_entity in highlight_entities]
            }
        }
        try:
            responses = dynamodb.batch_get_item(RequestItems=batch_keys)

        except ClientError as e:
            print("ERROR while getting quotes: " +
                  e.response['Error']['Message'])
            raise e
        else:
            for item in responses['Responses'][table.name]:
                quote = {}
                quote['entityid'] = foreignid_to_originaldata[item['id']][0]
                quote['title'] = item['tite']
                quote['author'] = item['author']
                quote['highlight'] = item['highlight']
                quote['plusones'] = str(foreignid_to_originaldata[item['id']][1])
                quote_json.append(quote)
    except Exception as e:
        print("Got error while get highlights. Error: ")
        raise e
    return quote_json


def __get_digest():
    try:
        dynamodb = boto3.resource('dynamodb')
        print("Opening daily digest table with name: ", os.environ['DAILY_DIGEST_TABLE'])
        table = dynamodb.Table(os.environ['DAILY_DIGEST_TABLE'])

        pacific_tz = dateutil.tz.gettz('US/Pacific')
        date_str = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
        print("Getting digest for: ", date_str)

        try:
            response = table.get_item(Key={
                'date': date_str,
            })

        except ClientError as e:
            print("ERROR while getting digest: " +
                  e.response['Error']['Message'])
        else:
            return response['Item']['digest']
    except Exception as e:
        print("Got error while getting digest: " + " Error: ")
        print(e)
        raise e


def __get_entities(entities):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(os.environ['ANKIENTITIES_TABLE'])

    foreign_ids = []
    batch_keys = {
        table.name: {
            'Keys': [{'entityid': entity_id} for entity_id in entities]
        }
    }
    try:
        responses = dynamodb.batch_get_item(RequestItems=batch_keys)
    except ClientError as e:
        print("ERROR while getting entity: " + entities + " Error:" +
              e.response['Error']['Message'])
        raise e
    else:
        for response in responses['Responses'][table.name]:
            foreign_ids.append(response)

    return foreign_ids


def __get_tweet_json(tweet_entities):
    tweet_json = []
    for entity in tweet_entities:
        quote = {}
        quote['entityid'] = entity['entityid']
        quote['tweet_id'] = entity['foreign_id']
        plus_one = 0
        if 'plus_one' in entity:
            plus_one = entity['plus_one']
        quote['plusones'] = str(plus_one)
        tweet_json.append(quote)
    return tweet_json


def lambda_handler(event, context):
    digest = __get_digest()

    if digest is None:
        return {
            'statusCode': 404,
            'headers': {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }

    print('Got digest: ' + str(digest))

    digest_json = json.loads(digest)

    response_json = {}

    tweet_entities = __get_entities(digest_json['TWITTER'])
    response_json['TWITTER'] = __get_tweet_json(tweet_entities)

    notion_entities = __get_entities(digest_json['NOTION'])
    response_json['NOTION'] = __get_quote_json(notion_entities)

    kindle_entities = __get_entities(digest_json['KINDLE'])
    response_json['KINDLE'] = __get_highlights_json(kindle_entities)

    twiddled_response = {}
    twiddled_response['digest'] = []

    for tweet_response in response_json['TWITTER']:
        twiddled_response['digest'].append(tweet_response)

    for notion_response in response_json['NOTION']:
        twiddled_response['digest'].append(notion_response)

    for kindle_response in response_json['KINDLE']:
        twiddled_response['digest'].append(kindle_response)

    random.shuffle(twiddled_response['digest'])

    return {
        'statusCode': 200,
        'body': json.dumps(twiddled_response),
        'headers': {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }
