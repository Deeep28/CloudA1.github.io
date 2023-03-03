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
import requests

QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/*****'

ES_USER = 'u***'
ES_PASS = 'Un******'
host = 'https://*****************.us-east-1.es.amazonaws.com'

DYNAMO_DB_TABLE_NAME = 'yelp-restau********'

def lambda_handler(event, context):
    message = event['Records'][0]
    message_atributes = message['messageAttributes']
    cuisine = message_atributes['cuisine']
    cuisine_type = cuisine['stringValue']
    loc = message_atributes['location']
    location = loc['stringValue']
    nop = message_atributes['numberpeople']
    number_of_people = nop['stringValue']
    eml = message_atributes['email']
    email = eml['stringValue']
    t1 = message_atributes['time']
    time = t1['stringValue']
    dt = message_atributes['date']
    Date = dt['stringValue']
    restaurant_info = ""
    print("Message: ", restaurant_info)
    #for i in range(1, 4):
    restaurantId = get_random_business_id(cuisine_type)
    restaurant_info += get_restaurant_info(restaurantId,cuisine_type) + '\n'
    print('Hello! Here are my ' + cuisine_type + ' restaurant suggestions for ' + number_of_people + ' people in '+ location + ' on ' + Date + ' at '+ time + '\n' + restaurant_info)
    sendMessage = 'Hello! Here are my ' + cuisine_type + ' restaurant suggestions for ' + number_of_people + ' people in '+ location + ' on ' + Date + ' at '+ time + '\n' + restaurant_info
    temp_email(sendMessage, email)
def get_random_business_id(cuisine_type):
    index = 'restaurants_search'
    es_query = host + '/' + index + '/_search?q=' + str(cuisine_type)
    esResponse = requests.get(es_query, auth=('user', 'Universal@123'))
    data = json.loads(esResponse.content.decode('utf-8'))
    businessId = []
    random_num_list = list(range(5))
    #random.shuffle(random_num_list)
    cnt = 0
    for random_number in random_num_list:
        if data['hits']['hits'][random_number]['_source']['id'] != None:
            business = data['hits']['hits'][random_number]['_source']['id']
            if business not in businessId and cnt < 3:
                businessId.append(business)
                cnt+=1
    print(businessId)
    return businessId


def get_restaurant_info(businessId,cuisine_type):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMO_DB_TABLE_NAME)
    print(table)
    formatted_restaurant_info = ''
    for i in businessId:

        response = table.get_item(
            Key={
                'id': str(i)
            }
        )
        response_item = response.get("Item")
        restaurant_name = response_item['restaurent']
        restaurant_category = cuisine_type
        restaurant_address = response_item['address'][0]
        restaurant_city = response_item['address'][1]
        #restaurant_zipcode = str(response_item['zip_code'])
        restaurant_review_count = str(response_item['review_count'])
        restaurant_rating = str(response_item['rating'])
        #restaurant_url = response_item['coordinates']
        restaurant_phone = str(response_item['phone'])
        formatted_restaurant_info+=(restaurant_name + ' located at ' + restaurant_address + restaurant_city + ' with the average rating of ' + restaurant_rating + ' among ' + restaurant_review_count + ' reviews. Here is the restaurant phone number ' + restaurant_phone + '\n')
    return formatted_restaurant_info


def temp_email(sendMessage, email):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    ses_client.send_email(
        Destination={
            "ToAddresses": [
                email,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": sendMessage,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Dining Suggestions Chatbot",
            },
        },
        Source="******@gmail.com",
    )