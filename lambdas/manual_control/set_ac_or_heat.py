import json
import boto3
import os

client = boto3.client('iot-data', endpoint_url = os.environ.get('ajf3ues13gfrd-ats.iot.us-east-2.amazonaws.com'))

def lambda_handler(event, context):
    thing_name = os.environ.get('Smart-Thermostat')
    #Check in JSON event to see if it's heat and ac present
    try:

        if "heat" and "ac" in event:
            heat = event["heat"]
            if not isinstance(heat, bool):
                raise ValueError("heat must be a bool")
            ac = event["ac"]
            if not isinstance(ac, bool):
                raise ValueError("ac must be a bool")
            if heat == ac:
                raise ValueError("Cannot set both heat and ac at the same time")
        elif "heat" not in event or "ac" not in event:
            raise ValueError("Must set heat and ac")
    except ValueError as e:
        print("Error: " + str(e))
        return {
            'statusCode': 400,
            'body': json.dumps('Error: ' + str(e))
        }
    except Exeception as e:
        print("Error: " + str(e))
        return {
            'statusCode': 400,
            'body': json.dumps('Error: ' + str(e))
        }
    #------------------
    #Define publish
    topic = 'thermostat/heatAC'
    payload = {
        "message" : "heat control",
        "heat set" : heat,
        "ac set" : ac
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
            'body': json.dumps(f'Publish successful')
        }
    except Exception as e:
        print("Error publishing to IoT: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error publishing to IoT: ' + str(e))
        }
        
