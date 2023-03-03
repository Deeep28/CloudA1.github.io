import json
import boto3
import logging
import math
import dateutil.parser
import datetime
import time
import random
import urllib3
import os


def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='Chatbot',
        botAlias='$LATEST',
        userId='user1',
        inputText=event['messages'][0]['unstructured']['text'])

    return {
        'statusCode': 200,
        'messages': [{
            'type': 'unstructured',
            'unstructured': {
                'text': response['message']
            }
        }]
    }