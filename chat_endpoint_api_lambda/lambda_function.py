import boto3
import boto3
import json
import os
import time
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pprint import pprint


def lambda_handler(event, context):
    print("Event json %s" % json.dumps(event))
    print("Context %s" % context)

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

    if 'chatinput' not in event['queryStringParameters']:
        print("No id in event[queryStringParameters]")
        return {
            'statusCode': 400,
            'body': "No chatinput in event[queryStringParameters]",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }

    chatinput = event["queryStringParameters"]["chatinput"]

    response = {'response': 'User sent request: ' + chatinput}

    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }
