import json, os
import tweepy
import random
import string
from decimal import Decimal
import boto3
import time
from boto3.dynamodb.conditions import Key
from pprint import pprint
from botocore.exceptions import ClientError
from datetime import date
import dateutil.tz
import datetime

NOTION_TABLE = os.environ['NOTION_BOOK_QUOTES_TABLE']
DAILY_DIGEST_TABLE = os.environ['DAILY_DIGEST_TABLE']
ANKIENTITIES_TABLE = os.environ['ANKIENTITIES_TABLE']
KINDLE_HIGHLIGHTS_TABLE = os.environ['KINDLE_HIGHLIGHTS_TABLE']


# Get the notion quotes stored for the given entities
def get_quote_json(highlight_entities):
    quote_json = []
    for highlight_entity in highlight_entities:
        quote = {}
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(NOTION_TABLE)

            try:
                response = table.get_item(Key={
                    'id': highlight_entity['foreign_id'],
                })

            except ClientError as e:
                print("ERROR while getting quotes: " +
                      e.response['Error']['Message'])
                continue
            else:
                item = response['Item']
                quote['entityid'] = highlight_entity['entityid']
                quote['title'] = item['tite']
                quote['author'] = item['author']
                quote['quote'] = item['quote']
                plus_one = 0
                if 'plus_one' in highlight_entity:
                    plus_one = highlight_entity['plus_one']
                quote['plusones'] = str(plus_one)
                quote_json.append(quote)
        except Exception as e:
            print("Got error while processing quote: " + highlight_entity['foreign_id'] + " Error: ")
            raise e

    return quote_json


def get_highlights_json(highlight_entities):
    quote_json = []
    for highlight_entity in highlight_entities:
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(KINDLE_HIGHLIGHTS_TABLE)

            try:
                response = table.get_item(Key={
                    'id': highlight_entity['foreign_id'],
                })

            except ClientError as e:
                print("ERROR while getting quotes: " +
                      e.response['Error']['Message'])
                continue
            else:
                item = response['Item']
                quote = {}
                quote['entityid'] = highlight_entity['entityid']
                quote['title'] = item['tite']
                quote['author'] = item['author']
                quote['highlight'] = item['highlight']
                plus_one = 0
                if 'plus_one' in highlight_entity:
                    plus_one = highlight_entity['plus_one']
                quote['plusones'] = str(plus_one)
                quote_json.append(quote)
        except Exception as e:
            print("Got error while processing quote: " + highlight_entity['foreign_id'] + " Error: ")
            raise e
    return quote_json


def get_digest():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DAILY_DIGEST_TABLE)

        pacific_tz = dateutil.tz.gettz('US/Pacific')
        date_str = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")

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


def get_entities(entities):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(ANKIENTITIES_TABLE)

    foreign_ids = []
    for entity_id in entities:
        try:
            try:
                response = table.get_item(Key={
                    'entityid': entity_id,
                })

            except ClientError as e:
                print("ERROR while getting entity: " + entity_id + " Error:" +
                      e.response['Error']['Message'])
            else:
                foreign_ids.append(response['Item'])
        except Exception as e:
            print("Got error while getting entity: " + entity_id + " Error: ")
            raise e

    return foreign_ids


def get_tweet_json(tweet_entities):
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
    digest = get_digest()

    print('Got digest: ' + str(digest))

    digest_json = json.loads(digest)

    response_json = {}

    tweet_entities = get_entities(digest_json['TWITTER'])
    response_json['TWITTER'] = get_tweet_json(tweet_entities)

    notion_entities = get_entities(digest_json['NOTION'])
    response_json['NOTION'] = get_quote_json(notion_entities)

    kindle_entities = get_entities(digest_json['KINDLE'])
    response_json['KINDLE'] = get_highlights_json(kindle_entities)

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
