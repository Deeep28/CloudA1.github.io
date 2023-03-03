import requests
import json
import boto3
from datetime import datetime
import pickle

#globalConfig
cuisineTypes = ['indian','american','italian','japanese','chinese','mexican']
location = ['manhattan']
businessType = 'restaurant'
radius ='30000'

#AWS Config
awsRegion = 'us-east-1'
accessID='AKIAWMQVJQOOLMMDVGN2'
secretKey = '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'
dbObject = boto3.resource('dynamodb',region_name=awsRegion, aws_access_key_id=accessID, aws_secret_access_key=secretKey)
dbtable = dbObject.Table('yelp-restaurants')


#yelpConfig
yelpEndpoint='https://api.yelp.com/v3/businesses/search'
clientID='qmfVRIb1J7JiqUMeYVQUbw'
yelpKey='rqw2hboWgSoScJuaBU9EDXaujOOnSQSD07Vax48SFwYxocenWrDbY60Dr-LExubhHR3qikjPKJUo14Q6qMcKRocNjGbyRL0UEMe7wgsRYQNWlsG___HpyVxi38r7Y3Yx'
yelpConfig={'Authorization':'Bearer ' + yelpKey}

globalDict = {}
opensearchDict = {}

def updateDict(responseObject, cuisineType):
    print(responseObject)

    restaurentList = responseObject['businesses']
    for i in range(len(restaurentList)):
        tmpKey = restaurentList[i]['id']
        if tmpKey in globalDict.keys():
            continue
        else:
            tmpValue = {
                          'id': restaurentList[i]['id'],
                          'restaurent': restaurentList[i]['name'],
                          'address': restaurentList[i]['location']['display_address'],
                          'zip_code' : restaurentList[i]['location']['zip_code'],
                          'timestamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                          'rating': str(restaurentList[i]['rating']), 
                          'coordinates': str(restaurentList[i]['coordinates']['latitude']) +" , " + str(restaurentList[i]['coordinates']['longitude']),
                          'review_count': str( restaurentList[i]['review_count'] ),
                          'phone': restaurentList[i]['display_phone']

                        }
            globalDict[tmpKey] = tmpValue
            opensearchTmpValue = {'id': restaurentList[i]['id'],'cuisine':cuisineType}
            opensearchDict[tmpKey] = opensearchTmpValue


def yelpDataCollecter():
    for cuisine in cuisineTypes:
        for loc in location:
            offsetValue = 1
            for i in range(18):
                urlParameter = {'categories':cuisine,'location':loc, 'limit':50, 'offset':offsetValue,'radius': radius}
                apiResponse = requests.get(yelpEndpoint, headers = yelpConfig, params = urlParameter)
                jsonResponse = json.loads(apiResponse.content.decode("utf-8"))
                updateDict(jsonResponse,cuisine)
                offsetValue = offsetValue + 50

def dbInsert(restaurentDict):
    with dbtable.batch_writer() as writer:
        for tmpKey in restaurentDict:
            writer.put_item(
                Item=restaurentDict[tmpKey]
            )

def saveData(gDict, osDict):
    f = open("gdict.pkl","wb")
    pickle.dump(gDict,f)
    f.close()

    q = open("odict.pkl","wb")
    pickle.dump(osDict,q)
    q.close()

yelpDataCollecter()
print("Items in global dictionary:", len(globalDict))
print("Items in global dictionary:", len(opensearchDict))

saveData(globalDict, opensearchDict)
userInput = 1 #int(input("Do you want to update DynamoDb and Open Search?"))

if(userInput == 1):
    dbInsert(globalDict)
else:
    print("Ending program")