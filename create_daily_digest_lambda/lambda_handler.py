import boto3
import datetime
import dateutil.tz
import json
import os
import random
import string
import time
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import date
from decimal import Decimal
from pprint import pprint


def __get_liked_tweets_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(os.environ['ANKIENTITIES_TABLE'])

    try:
        response = table.query(IndexName="source-recallweight-index",
                               KeyConditionExpression=Key('source').eq('TWITTER'),
                               Limit=int(os.environ['NUM_TWITTER_ENTITIES']))
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


def __get_kindle_highlights_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(os.environ['ANKIENTITIES_TABLE'])

    try:
        response = table.query(IndexName="source-recallweight-index",
                               KeyConditionExpression=Key('source').eq('KINDLE'),
                               Limit=int(os.environ['NUM_KINDLE_ENTITIES']))
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


def __get_notion_quotes_from_db():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(os.environ['ANKIENTITIES_TABLE'])

    try:
        response = table.query(IndexName="source-recallweight-index",
                               KeyConditionExpression=Key('source').eq('NOTION'),
                               Limit=int(os.environ['NUM_NOTION_ENTITIES']))
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


def __UpdateDigest(digest):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table(os.environ['DAILY_DIGEST_TABLE'])
    retries = 0
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    date_str = datetime.datetime.now(tz=pacific_tz).strftime("%Y-%m-%d")
    while True:
        try:
            response = table.put_item(
                Item={
                    'date': date_str,
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
    tweet_ids = __get_liked_tweets_from_db()

    quote_ids = __get_notion_quotes_from_db()

    highlight_ids = __get_kindle_highlights_from_db()

    digest = {}
    digest['TWITTER'] = tweet_ids
    digest['NOTION'] = quote_ids
    digest['KINDLE'] = highlight_ids

    __UpdateDigest(digest)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully created digest!')
    }
