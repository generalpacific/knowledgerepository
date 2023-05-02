import datetime
import json
import os
import random

import boto3
import dateutil.tz
from botocore.exceptions import ClientError


# Get notion and kindle entity data from their respective tables.
def __get_entities_json(notion_entities, kindle_entities, dynamodb):
    foreignid_to_originaldata = {}
    for entity in notion_entities:
        plus_one = entity.get('plus_one', 0)
        foreignid_to_originaldata[entity['foreign_id']] = [entity['entityid'], plus_one]
    for entity in kindle_entities:
        plus_one = entity.get('plus_one', 0)
        foreignid_to_originaldata[entity['foreign_id']] = [entity['entityid'], plus_one]

    notion_table = dynamodb.Table(os.environ['NOTION_BOOK_QUOTES_TABLE'])
    kindle_table = dynamodb.Table(os.environ['KINDLE_HIGHLIGHTS_TABLE'])

    batch_keys = {
        notion_table.name: {
            'Keys': [{'id': entity['foreign_id']} for entity in notion_entities]
        },
        kindle_table.name: {
            'Keys': [{'id': entity['foreign_id']} for entity in kindle_entities]
        }
    }
    responses = dynamodb.batch_get_item(RequestItems=batch_keys)

    notion_entity_json = []
    notion_responses = responses['Responses'][notion_table.name]
    for item, entity in zip(notion_responses, notion_entities):
        entity_data = {}
        entity_data['entityid'] = foreignid_to_originaldata[item['id']][0]
        entity_data['title'] = item.get('tite', '')
        entity_data['author'] = item.get('author', '')
        entity_data['quote'] = item.get('quote', '')
        entity_data['plusones'] = str(foreignid_to_originaldata[item['id']][1])
        notion_entity_json.append(entity_data)

    kindle_entity_json = []
    kindle_responses = responses['Responses'][kindle_table.name]
    for item, entity in zip(kindle_responses, kindle_entities):
        entity_data = {}
        entity_data['entityid'] = foreignid_to_originaldata[item['id']][0]
        entity_data['title'] = item.get('tite', '')
        entity_data['author'] = item.get('author', '')
        entity_data['highlight'] = item.get('highlight', '')
        entity_data['plusones'] = str(foreignid_to_originaldata[item['id']][1])
        kindle_entity_json.append(entity_data)

    return notion_entity_json, kindle_entity_json


def __get_digest(dynamodb):
    try:
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


def __get_entities(entities, dynamodb):
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
    dynamodb = boto3.resource('dynamodb')
    digest = __get_digest(dynamodb)

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

    tweet_entities = __get_entities(digest_json['TWITTER'], dynamodb)
    response_json['TWITTER'] = __get_tweet_json(tweet_entities)

    notion_entities = __get_entities(digest_json['NOTION'], dynamodb)
    kindle_entities = __get_entities(digest_json['KINDLE'], dynamodb)
    response_json['NOTION'], response_json['KINDLE'] = __get_entities_json(notion_entities, kindle_entities, dynamodb)

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
