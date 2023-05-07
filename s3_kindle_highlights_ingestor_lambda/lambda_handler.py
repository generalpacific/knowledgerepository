import datetime
import json
import os
import random
import string
import uuid
from pprint import pprint

import boto3
import dateutil.tz
import tweepy
from botocore.exceptions import ClientError


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

    return {
        'statusCode': 200,
        'body': json.dumps(
            'Successfully ingested highlights from S3!. Number of highlights ' + str(len(highlight_data)))
    }


def __parse_highlights(content):
    lines = content.split('\n')
    data = []
    print('Number of lines read: ', len(lines))
    for i in range(0, len(lines), 5):
        if i == len(lines) - 1:
            print("At the end of the file. Returning.")
            break
        title_author = lines[i].strip()
        metadata = lines[i + 1].strip().lstrip('- ')
        highlight = lines[i + 3].strip()

        title, author = title_author.split(' (')
        author = author[:-1]  # Remove the trailing ')'

        data.append({'title': title, 'author': author,
                     'metadata': metadata,
                     'highlight': highlight})
    return data
