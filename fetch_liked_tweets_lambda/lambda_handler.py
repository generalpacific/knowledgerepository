import boto3
import datetime
import dateutil.tz
import json
import os
import random
import string
import tweepy
import uuid
from botocore.exceptions import ClientError
from pprint import pprint

# Gets the liked tweets for the user since the max id that is stored in the
# DynamoDb table.

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
SCREEN_NAME = os.environ['SCREEN_NAME']


def __get_liked_tweets(since_tweet_id):
    print("Setting up tweepy api")
    client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_KEY,
                           access_token_secret=ACCESS_KEY)

    username = SCREEN_NAME
    user = client.get_user(username=username)
    user_id = user.data.id

    liked_tweets = client.get_liked_tweets(id=user_id, max_results=5)
    return liked_tweets


def __get_max_tweet_id(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('ankitweetmaxid')

    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
        return ''
    else:
        pprint(response)
        return response['Items'][0]['tweeid']


def __update_dynamodb_with_tweets(favorites, old_max_id):
    dynamodb = boto3.resource('dynamodb')
    new_max_id = -1
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    date_str = datetime.datetime.now(tz=pacific_tz)
    for tweet in favorites:
        tweet_id = tweet.id_str
        if int(tweet.id_str) > new_max_id:
            new_max_id = int(tweet.id_str)
        table = dynamodb.Table('ankientities')
        entity_id = str(uuid.uuid1())
        print("Writing id: ", entity_id, " tweetid: ", tweet_id)
        response = table.put_item(
            Item={
                'entityid': entity_id,
                'foreign_id': tweet_id,
                'source': 'TWITTER',
                'recallweight': 0,
                'create_time': str(date_str)
            }
        )
    print('Put succeeded in ankientities')
    print('Updating max_id: ', new_max_id)

    table = dynamodb.Table('ankitweetmaxid')
    print("Deleting max tweetid: ", old_max_id)
    response = table.delete_item(Key={'tweeid': old_max_id})
    pprint(response)
    print("Writing max tweetid: ", new_max_id)
    response = table.put_item(
        Item={
            'tweeid': str(new_max_id),
        }
    )
    pprint(response)
    print("Done adding max tweetid: ")


def lambda_handler(event, context):
    max_id = __get_max_tweet_id()
    pprint("Got max tweet id: " + max_id)
    favorites = __get_liked_tweets(max_id)

    if len(favorites) == 0:
        print("No new favorites to updates. Returning.")
        return {
            'statusCode': 200,
            'body': json.dumps('No new liked tweets!')
        }

    __update_dynamodb_with_tweets(favorites, max_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated liked tweets!')
    }
