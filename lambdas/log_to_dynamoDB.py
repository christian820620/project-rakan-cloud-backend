import json
import boto3
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo


def lambda_handler(event, context):
    client = boto3.client('dynamodb')
    #Create timezone key in EST
    eastern_timezone = ZoneInfo('America/New_York')
    now = datetime.now(eastern_timezone)
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    #Convert int data to bool
    heat_bool = bool(event['heat'])
    ac_bool = bool(event['ac'])
    #Put data into DynamoDB
    try:
        response = client.put_item(
            TableName = 'iot_log',
            Item = {
                'timestamp': {'S': formatted_datetime},
                'temperature': {'N': str(event['temperature'])},
                'humidity' : {'N': str(event['humidity'])},
                'fan_speed_per' : {'N': str(event['fan_speed_percent'])},
                'heat' : {'BOOL': heat_bool},
                'ac' : {'BOOL': ac_bool}
            }
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error on first insert': str(e)})
        }
    try: 
        response = client.put_item(
            TableName = 'latest_data',
            Item = {
                'timestamp': {'S': "1"},
                'temperature': {'N': str(event['temperature'])},
                'humidity' : {'N': str(event['humidity'])},
                'fan_speed_per' : {'N': str(event['fan_speed_percent'])},
                'heat' : {'BOOL': heat_bool},
                'ac' : {'BOOL': ac_bool}
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data inserted successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error on second insert': str(e)})
        }

