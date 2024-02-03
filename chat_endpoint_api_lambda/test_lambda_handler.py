import boto3
import datetime
import dateutil.tz
import json
import lambda_function
import mock
import moto
import os
import pytest
import unittest
from unittest.mock import patch, MagicMock


def test_chat_input_success():
    event = {'queryStringParameters': {'chatinput': 'This is chat input!'}}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 200
    assert response['body'] == "User sent request: This is chat input!"


def test_lambda_handler_no_query_string_parameters():
    event = {}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response['body'] == "No queryStringParameters in event"


def test_lambda_handler_none_query_string_parameters():
    event = {'queryStringParameters': None}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response['body'] == "queryStringParameters in event is none"


def test_lambda_handler_no_chatinput():
    event = {'queryStringParameters': {}}

    response = lambda_function.lambda_handler(event, None)

    assert response['statusCode'] == 400
    assert response[
               'body'] == "No chatinput in event[queryStringParameters]"
