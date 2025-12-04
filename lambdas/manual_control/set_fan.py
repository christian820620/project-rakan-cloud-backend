import json
import boto3
import os

client = boto3.client('iot-data', endpoint_url = os.environ.get('ajf3ues13gfrd-ats.iot.us-east-2.amazonaws.com'))

def lambda_handler(event, context):
    thing_name = os.environ.get('Smart-Thermostat')
    #try to get fan_speed_percent then convert to 1-255 (Value larger or smaller handled in Arduino code)
    try:
        fan_speed_percent = event['fan_speed_percent']
        if not isinstance(fan_speed_percent, (int, float)):
            raise ValueError("fan_speed_percent must be a number")
        fan_speed_raw = int(fan_speed_percent * 255 / 100)
    #error handling
    except KeyError:
        print("Error: fan_speed_percent not found in event JSON payload")
        return {
            'statusCode': 400,
            'body': json.dumps('Error: fan_speed_percent not found in event JSON payload')
        }
    except Exeception as e:
        print("Error: " + str(e))
        return {
            'statusCode': 400,
            'body': json.dumps('Error: ' + str(e))
        }
    #------------------
    #Define publish
    topic = 'thermostat/fan'
    payload = {
        "message" : f"fan speed {fan_speed_raw}",
        "fan speed" : fan_speed_raw
    }
    #Publish payload
    try:
        response = client.publish(
            topic = topic,
            qos = 0,
            payload = json.dumps(payload)
        )
        print("Publish successful")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Publish successful {fan_speed_raw}')
        }
    except Exception as e:
        print("Error publishing to IoT topic: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error publishing to IoT topic: ' + str(e))
        }
        
