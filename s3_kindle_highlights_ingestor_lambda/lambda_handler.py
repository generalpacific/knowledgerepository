import datetime
import json
import os
import random
import string
import uuid
from pprint import pprint

import boto3
import dateutil.tz
from botocore.exceptions import ClientError

RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                    'ThrottlingException')


# Reads the S3 file for the latest highlights, parses it and stores the
# highlights in DB.
def lambda_handler(event, context):
    # Read file from s3.
    # Get the S3 bucket and key from the event
    s3_bucket = os.environ['KINDLE_HIGHLIGHTS_S3_BUCKET']
    s3_key = os.environ['KINDLE_HIGHLIGHTS_S3_FILE_NAME']

    # Create an S3 client
    s3 = boto3.client('s3')

    # Read the file from S3
    response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    file_contents = response['Body'].read().decode('utf-8')

    # Parse the file contents in title, author and highlight
    highlight_data = __parse_highlights(file_contents)

    print('Done parsing highlight data. Ingesting highlights in db.')
    num_highlights_ingested = __put_highlights_in_db(highlight_data)

    return {
        'statusCode': 200,
        'body': 'Ingested ' + str(num_highlights_ingested) + ' highlights.'
    }


def __put_highlights_in_db(highlight_data):
    num_highlights_ingested = 0
    current_title_to_highlight_map = {}
    for highlight in highlight_data:
        title = highlight['title']
        if title not in current_title_to_highlight_map:
            current_title_to_highlight_map[title] = __get_highlights(title)
    for highlight in highlight_data:
        if highlight['highlight'] in current_title_to_highlight_map[highlight['title']]:
            continue
        num_highlights_ingested += 1
        __put_highlight_in_db(highlight['title'], highlight['author'], highlight['highlight'], highlight['metadata'])
    return num_highlights_ingested


def __put_highlight_in_db(title, author, highlight, metadata):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table(os.environ['KINDLE_HIGHLIGHTS_TABLE'])
    highlight_entity_id = str(uuid.uuid1())
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    date_str = datetime.datetime.now(tz=pacific_tz)

    retries = 0
    while True:
        try:
            table.put_item(
                Item={
                    'id': highlight_entity_id,
                    'tite': title,
                    'author': author,
                    'highlight': highlight,
                    'metadata': metadata,
                    'create_time': str(date_str)
                }
            )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(2 ** retries)
            retries += 1

    table = dyndb.Table(os.environ['ANKIENTITIES_TABLE'])
    entity_id = str(uuid.uuid1())
    retries = 0
    while True:
        try:
            table.put_item(
                Item={
                    'entityid': entity_id,
                    'foreign_id': highlight_entity_id,
                    'source': 'KINDLE',
                    'recallweight': "0",
                    'create_time': str(date_str)
                }
            )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(1. ** retries)
            retries += 1
    print("Added highlight id: " + highlight_entity_id + " new entity_id: " + entity_id)


def __parse_highlights(content):
    content = content.replace('\ufeff', '')
    lines = content.split('\n')
    data = []
    print('Number of lines read: ', len(lines))
    for i in range(0, len(lines), 5):
        if i == len(lines) - 1:
            break
        title_author = lines[i].strip()
        metadata = lines[i + 1].strip().lstrip('- ')
        highlight = lines[i + 3].strip()

        title = ""
        author = ""
        if " (" in title_author:
            title, author = title_author.split(' (')
            author = author[:-1]
        else:
            title = title_author
            author = ""

        data.append({'title': title, 'author': author,
                     'metadata': metadata,
                     'highlight': highlight})
    return data


def __get_highlights(title):
    dyndb = boto3.client('dynamodb')
    return_highlights = set()
    try:
        # Set up the Query parameters
        query_params = {
            'TableName': os.environ['KINDLE_HIGHLIGHTS_TABLE'],
            'IndexName': 'tite-index',
            'KeyConditionExpression': 'tite = :title',
            'ExpressionAttributeValues': {
                ':title': {'S': title}
            }
        }

        # Query the table using the GSI on the title column
        response = dyndb.query(**query_params)
    except ClientError as e:
        print("ERROR while getting latest quote. Returning empty. Error: " +
              e.response['Error']['Message'])
        return return_highlights
    else:
        if 'Items' in response:
            items = response['Items']
            for item in items:
                return_highlights.add(item['highlight']['S'])
        return return_highlights
