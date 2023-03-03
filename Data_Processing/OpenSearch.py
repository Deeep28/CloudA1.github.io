from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import pickle
import random


openSearchEndpoint = 'https://search-search-es-restaurants-ujmv432i6ot4q5n6lsadgcw5kq.us-east-1.es.amazonaws.com'
region = 'us-east-1'
accessID='AKIAWMQVJQOOLMMDVGN2'
secretKey = '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'

service = 'es'
credentials = boto3.Session(region_name=region, aws_access_key_id=accessID, aws_secret_access_key=secretKey).get_credentials()
awsauth = AWS4Auth(accessID, secretKey, region, service, session_token=credentials.token)

search = OpenSearch(
    hosts = openSearchEndpoint,
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

index_body = {
  'settings': {
    'index': {
      'number_of_shards': 4
    }
  }
}

response = search.indices.create('restaurants_search', body=index_body)

print('\nCreating index:')
print(response)

pickle_file = open("odict.pkl", "rb")
oDict = pickle.load(pickle_file)

id = 1

for tmpKey in oDict.keys():
    print(tmpKey)
    print(oDict[tmpKey])
    try:        
        response = search.index(
            index = 'restaurants_search',
            body = {
                'id': tmpKey,
                'cuisine': oDict[tmpKey]['cuisine']
            },
            refresh = True
            )
        id = id + 1

        print('\nAdding document:')
        print(response)
    except:
        print('')