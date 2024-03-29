import boto3
import datetime
import dateutil.tz
import json
import os
import random
from botocore.exceptions import ClientError

RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                    'ThrottlingException')

MAX_RETRIES = 5


def __get_plus_ones(dynamodb, foreign_ids):
    table_name = os.environ['ANKIENTITIES_TABLE']
    index_name = 'foreign_id-index'

    plus_ones = {}
    for foreign_id in foreign_ids:
        retries = 0
        while True:
            try:
                response = dynamodb.query(
                    TableName=table_name,
                    IndexName=index_name,
                    KeyConditionExpression='foreign_id = :id',
                    ExpressionAttributeValues={':id': {'S': foreign_id}},
                    ProjectionExpression='foreign_id, plus_one'
                )
                break
            except ClientError as err:
                if retries >= MAX_RETRIES:
                    raise Exception("Max retries exceeded.")
                if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                    raise
                sleep(2 ** retries)
                retries += 1

        for item in response['Items']:
            foreign_id = item['foreign_id']['S']
            plus_ones_value = item.get('plus_one', {'N': '0'})['N']
            plus_ones[foreign_id] = int(plus_ones_value)

    print("foreign_ids.size: " + str(len(foreign_ids)) + " result size: " + str(len(plus_ones)))
    return plus_ones


def __get_entities(dynamodb, source, title):
    if source == 'KINDLE':
        table = os.environ['KINDLE_HIGHLIGHTS_TABLE']
    elif source == 'NOTION':
        table = os.environ['NOTION_BOOK_QUOTES_TABLE']
    else:
        raise ValueError("Illegal source " + source)

    return_highlights = []
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
        response = dynamodb.query(**query_params)
    except ClientError as e:
        print("ERROR while getting latest quote. Error: " +
              e.response['Error']['Message'])
        raise e
    else:
        if 'Items' in response:
            items = response['Items']

            foreign_ids = []
            for item in items:
                foreign_ids.append(item['id']['S'])

            foreign_ids_to_plus_ones = __get_plus_ones(dynamodb, foreign_ids)

            for item in items:
                plus_ones = 0
                if item['id']['S'] in foreign_ids_to_plus_ones:
                    plus_ones = foreign_ids_to_plus_ones[item['id']['S']]
                if source == 'KINDLE':
                    return_highlights.append((item['highlight']['S'], plus_ones))
                elif source == 'NOTION':
                    return_highlights.append((item['quote']['S'], plus_ones))
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
    print(str(entities))
    print("Returning " + str(len(entities)) + " for " + title)

    return {
        'statusCode': 200,
        'body': json.dumps(list(entities)),
        'headers': {
            "Content-Type": "application/json",
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }
