import boto3
import json
import os
import urllib3

from botocore.exceptions import ClientError


API_KEY = os.environ['CRYPTOCOMPARE_API_KEY']
FROM_EMAIL = os.environ['FROM_EMAIL']
TO_EMAIL = os.environ['TO_EMAIL']

def send_email(client, message):
    SUBJECT = 'Crypto Price Alert'
    response = None
    
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    TO_EMAIL
                    ]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': message,
                    }
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': SUBJECT,
                },
            },
            Source=FROM_EMAIL,
        )
        
        return response
    except ClientError as e:
        print(e.response['Error']['Message'] + 'ganesh')
        return response

def get_coin_price(coin):
    http = urllib3.PoolManager()
    api_url = 'https://min-api.cryptocompare.com/data/price?fsym=' + coin + '&tsyms=INR&api_key=' + API_KEY
    r = http.request('GET', api_url)
    data = json.loads(r.data.decode("utf-8"))
    return data['INR']
    
def lambda_handler(event, context):
    coins = event['coins']
    client = boto3.client('ses',region_name='ap-south-1')
    
    message = ''
    
    for coin in coins:
        price = get_coin_price(coin)
        message = message + coin + ': ' + str(price) + '\n'
    
    
    response = send_email(client, message)
    
    if(response == None):
        return {
            'status': 500,
            'message': 'Error sending alert'
        }
    else:
        return {
            'status': 200,
            'message': 'Alert sent successfully'
            
        }
