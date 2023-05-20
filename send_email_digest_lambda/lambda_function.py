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

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
SENDER_EMAIL = os.environ['SENDER_EMAIL']
TO_EMAIL = os.environ['TO_EMAIL']


def send_email(subject, text, to):
    client = boto3.client('ses')
    print("Sending email with text: " + text)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    to,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': text,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=SENDER_EMAIL
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        raise ValueError(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def get_image_url(tweet_obj):
    if len(tweet_obj.entities) == 0:
        print("No entities in tweet")
        return ""
    else:
        print("Entities are: " + str(tweet_obj.entities))
        if "media" in tweet_obj.entities:
            media = tweet_obj.entities['media']
            if len(media) == 0:
                print("0 length media found in entities. Return empty image_url")
                return ""
            image_url = tweet_obj.entities['media'][0]['media_url']
            print("Got media url :" + str(image_url))
            return str(image_url)
        else:
            print("No media in entities")
            return ""


def get_embed_tweet(tweetids):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    tweet_string = "<h1> Liked Tweets </h1>"
    for tweet_id in tweetids:
        try:
            tweet = api.get_status(tweet_id)
            url_str = "https://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id_str
            embeded_str = api.get_oembed(url=url_str)
            print("Got embedded str: " + str(embeded_str))
            tweet_string = tweet_string + "<br>" + embeded_str['html']
            tweet_media_url = get_image_url(tweet)
            if tweet_media_url != "":
                tweet_string = tweet_string + "<br><img src='" + tweet_media_url + "' width='50%'>"
            tweet_string = tweet_string + "<hr>"
        except Exception as e:
            print("Got error while processing tweetid: " + tweet_id + " Error: ")
            print(e)
    return tweet_string


def get_quote_string(quote_ids):
    quote_string = "<h1> Book quotes </h1>"
    for quote_id in quote_ids:
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('notion-book-quotes')

            try:
                response = table.get_item(Key={
                    'id': quote_id,
                })

            except ClientError as e:
                print("ERROR while getting quotes: " +
                      e.response['Error']['Message'])
                continue
            else:
                item = response['Item']
                quote_string += "<br>" + item['tite'] + "<br>" + item['author']
                quote_string += "<br><br><blockquote>" + item['quote'] + "</blockquote>"
                quote_string += "<hr>"
        except Exception as e:
            print("Got error while processing quote: " + quote_id + " Error: ")
            print(e)
    return quote_string


def get_highlights_string(highlight_ids):
    quote_string = "<h1> Latest Highlights </h1>"
    for quote_id in highlight_ids:
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('kindle-highlights')

            try:
                response = table.get_item(Key={
                    'id': quote_id,
                })

            except ClientError as e:
                print("ERROR while getting quotes: " +
                      e.response['Error']['Message'])
                continue
            else:
                item = response['Item']
                quote_string += "<br>" + item['tite'] + "<br>" + item['author']
                quote_string += "<br><br><blockquote>" + item['highlight'] + "</blockquote>"
                quote_string += "<hr>"
        except Exception as e:
            print("Got error while processing quote: " + quote_id + " Error: ")
            print(e)
    return quote_string


def get_digest():
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('daily-digest')

        date_str = date.today().strftime("%Y-%m-%d")

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
        print("Got error while getting digest: " + date_str + " Error: ")
        print(e)


def get_foreign_ids(entities):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('ankientities')

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
                foreign_ids.append(response['Item']['foreign_id'])
        except Exception as e:
            print("Got error while getting entity: " + entity_id + " Error: ")
            raise e

    return foreign_ids


def lambda_handler(event, context):
    digest = get_digest()

    print('Got digest: ' + str(digest))

    digest_json = json.loads(digest)

    tweet_ids = get_foreign_ids(digest_json['TWITTER'])
    tweet_string = get_embed_tweet(tweet_ids)

    notion_ids = get_foreign_ids(digest_json['NOTION'])
    quote_string = get_quote_string(notion_ids)

    kindle_ids = get_foreign_ids(digest_json['KINDLE'])
    highlights_string = get_highlights_string(kindle_ids)

    digest_link = "<a href='generalpacific.link'>Link to digest</a><br><a href='https://master.dcz6fmdennwso.amplifyapp.com	'>alternate link</a><br><br><b>"
    send_email('KnowledgeAnki: Todays Summary.', digest_link + highlights_string + tweet_string + quote_string,
               TO_EMAIL)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully sent liked daily digest email!')
    }
