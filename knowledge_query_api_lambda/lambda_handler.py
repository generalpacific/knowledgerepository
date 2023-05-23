import boto3
import datetime
import dateutil.tz
import json
import os
import random
from botocore.exceptions import ClientError


def __get_entities(dynamodb, source, title):
    if source == 'KINDLE':
        table = os.environ['KINDLE_HIGHLIGHTS_TABLE']
    elif source == 'NOTION':
        table = os.environ['NOTION_BOOK_QUOTES_TABLE']
    else:
        raise ClientError("Illegal source", source)

    return_highlights = set()
    try:
        # Set up the Query parameters
        query_params = {
            'TableName': table,
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


def lambda_handler(event, context):
    if 'queryStringParameters' not in event:
        print("No queryStringParameters in event")
        return {
            'statusCode': 400,
            'body': "No queryStringParameters in event",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }

    if event['queryStringParameters'] is None:
        print("queryStringParameters in event is none")
        return {
            'statusCode': 400,
            'body': "queryStringParameters in event is none",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }

    query_string_parameters = event['queryStringParameters']

    if 'source' not in query_string_parameters:
        print("No source in event[queryStringParameters]")
        return {
            'statusCode': 400,
            'body': "No source in event[queryStringParameters]. Provide source for which you need entities for.",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }
    source = query_string_parameters['source']

    if 'title' not in query_string_parameters:
        print("No title in event[queryStringParameters]")
        return {
            'statusCode': 400,
            'body': "No title in event[queryStringParameters]. Provide title for which you need entities for.",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }
    title = query_string_parameters['title']

    dynamodb = boto3.client('dynamodb')

    entities = __get_entities(dynamodb, source, title)

    return {
        'statusCode': 200,
        'body': json.dumps(entities),
        'headers': {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }
