import boto3
import boto3
import json
import os
import time
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pprint import pprint


def lambda_handler(event, context):
    print(type(event))
    print(event)
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

    if 'entityid' not in event['queryStringParameters']:
        print("No id in event[queryStringParameters]")
        return {
            'statusCode': 400,
            'body': "No id in event[queryStringParameters]",
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }

    entity_id = event["queryStringParameters"]["entityid"]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['ANKIENTITIES_TABLE'])

    try:
        response = table.get_item(Key={
            'entityid': entity_id,
        })

    except ClientError as e:
        print("ERROR while getting quotes: " +
              e.response['Error']['Message'])
        return {
            'statusCode': 401,
            'body': e.response['Error']['Message'],
            'headers': {
                'Access-Control-Allow-Origin': '*',
            }
        }
    else:
        if 'Item' in response:
            item = response['Item']
            try:
                plus_one = 1
                if 'plus_one' in item:
                    plus_one = item['plus_one'] + 1
                response = table.update_item(
                    Key={
                        'entityid': item['entityid']
                    },
                    UpdateExpression="set plus_one=:r",
                    ExpressionAttributeValues={
                        ':r': plus_one,
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print("Successfully updated plus_one")
            except ClientError as e:
                print("Failed to update plus_one ERROR: " +
                      e.response['Error']['Message'])
                return {
                    'statusCode': 401,
                    'body': e.response['Error']['Message'],
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                    }
                }
            return {
                'statusCode': 200,
                'body': 'Successfully PlusOned the entity',
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': entity_id + ' Not found',
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                }
            }
