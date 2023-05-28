import boto3
import datetime
import dateutil.tz
import json
import os
import random
from botocore.exceptions import ClientError


def __get_plus_ones(dynamodb, foreign_ids):
    table_name = os.environ['ANKIENTITIES_TABLE']
    index_name = 'foreign_id-index'

    plus_ones = {}
    for foreign_id in foreign_ids:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression='foreign_id = :id',
            ExpressionAttributeValues={':id': {'S': foreign_id}},
            ProjectionExpression='foreign_id, plus_one'
        )

        for item in response['Items']:
            foreign_id = item['foreign_id']['S']
            plus_ones_value = item.get('plus_one', {'N': '0'})['N']
            plus_ones[foreign_id] = int(plus_ones_value)

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
                if source == 'KINDLE':
                    return_highlights.append((item['highlight']['S'], foreign_ids_to_plus_ones[item['id']['S']]))
                elif source == 'NOTION':
                    return_highlights.append((item['quote']['S'], foreign_ids_to_plus_ones[item['id']['S']]))
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
