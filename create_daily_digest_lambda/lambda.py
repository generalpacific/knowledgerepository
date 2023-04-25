
import json, os
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

DAILY_DIGEST_TABLE = os.environ('DAILY_DIGEST_TABLE')
ANKIENTITIES_TABLE = os.environ('ANIKENTITIES_TABLE')
KINDLE_HIGHLIGHTS_TABLE = os.environ('KINDLE_HIGHLIGHTS_TABLE')
NOTION_BOOK_QUOTES_TABLE = os.environ('NOTION_BOOK_QUOTES_TABLE')

def get_liked_tweets_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(ANKINTITIES_TABLE)

    try:
       response = table.query(IndexName="source-recallweight-index",
            KeyConditionExpression=Key('source').eq('TWITTER'),
            Limit=5)
    except ClientError as e:
        print("ERROR while getting tweets: " +
            e.response['Error']['Message'])
        return ''
    else:
        pprint(response)
        tweet_ids = []
        for item in response['Items']:
            try:
                new_weight = 1
                if 'recallweight' in item:
                    new_weight = int(time.time())
                response = table.update_item(
                   Key={
                        'entityid': item['entityid']
                        },
                    UpdateExpression="set recallweight=:r",
                    ExpressionAttributeValues={
                        ':r': new_weight,
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print("Successfully updated recallweight")
            except ClientError as e:
                print("Failed to update recallweight ERROR: " +
                    e.response['Error']['Message'])
            tweet_ids.append(item['entityid'])
        return tweet_ids

def get_kindle_highlights_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(ANKIENTITIES_TABLE)

    try:
       response = table.query(IndexName="source-recallweight-index",
            KeyConditionExpression=Key('source').eq('KINDLE'),
            Limit=7)
    except ClientError as e:
        print("ERROR while getting tweets: " +
            e.response['Error']['Message'])
        return ''
    else:
        pprint(response)
        quote_ids = []
        for item in response['Items']:
            try:
                new_weight = 1
                if 'recallweight' in item:
                    new_weight = int(time.time())
                response = table.update_item(
                   Key={
                        'entityid': item['entityid']
                        },
                    UpdateExpression="set recallweight=:r",
                    ExpressionAttributeValues={
                        ':r': new_weight,
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print("Successfully updated recallweight")
            except ClientError as e:
                print("Failed to update recallweight ERROR: " +
                    e.response['Error']['Message'])
            quote_ids.append(item['entityid'])
        return quote_ids

def get_notion_quotes_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(ANKIENTITIES_TABLE)

    try:
       response = table.query(IndexName="source-recallweight-index",
            KeyConditionExpression=Key('source').eq('NOTION'),
            Limit=6)
    except ClientError as e:
        print("ERROR while getting tweets: " +
            e.response['Error']['Message'])
        return ''
    else:
        pprint(response)
        quote_ids = []
        for item in response['Items']:
            try:
                new_weight = 1
                if 'recallweight' in item:
                    new_weight = int(time.time())
                response = table.update_item(
                   Key={
                        'entityid': item['entityid']
                        },
                    UpdateExpression="set recallweight=:r",
                    ExpressionAttributeValues={
                        ':r': new_weight,
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print("Successfully updated recallweight")
            except ClientError as e:
                print("Failed to update recallweight ERROR: " +
                    e.response['Error']['Message'])
            quote_ids.append(item['entityid'])
        return quote_ids

def UpdateDigest(digest):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table(DAILY_DIGEST_TABLE)
    retries = 0
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    date_str = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
    while True:
        try:
            response = table.put_item(
                    Item={
                    'date' : date_str,
                    'digest': json.dumps(digest),
                    }
                )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(2 ** retries)
            retries += 1
    print('Created digest for date: ' + date_str)

def lambda_handler(event, context):
    tweet_ids = get_liked_tweets_from_db()

    quote_ids = get_notion_quotes_from_db()

    highlight_ids = get_kindle_highlights_from_db()

    digest = {}
    digest['TWITTER'] = tweet_ids
    digest['NOTION'] = quote_ids
    digest['KINDLE'] = highlight_ids

    UpdateDigest(digest)


    return {
        'statusCode': 200,
        'body': json.dumps('Successfully created digest!')
    }

