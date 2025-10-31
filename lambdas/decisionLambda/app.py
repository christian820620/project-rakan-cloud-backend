import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
iot_client = boto3.client('iot-data', endpoint_url=os.environ.get('IOT_ENDPOINT', ''))
logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ.get('TABLE_NAME', 'rakan-devicestate')

def decide_action_with_bedrock(context):
    """
    Placeholder for future Bedrock LAM integration.
    Returns None for now.
    """
    return None

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    device_id = event.get('deviceId')
    if not device_id:
        logger.error("Missing deviceId in event")
        return {'statusCode': 400, 'body': 'Missing deviceId'}
    try:
        table = dynamodb.Table(table_name)
        resp = table.get_item(Key={'deviceId': device_id})
        item = resp.get('Item')
        if not item:
            logger.error(f"No state found for deviceId {device_id}")
            return {'statusCode': 404, 'body': 'Device not found'}
        reported = item.get('reported', {})
        temperature = reported.get('temperatureF')
        occupancy = reported.get('occupancy')
        action = None
        # Simple rules
        if temperature is not None and occupancy is not None:
            if temperature >= 80 and occupancy:
                action = {'action': 'set_mode', 'value': 'cool'}
            elif temperature <= 68 and occupancy:
                action = {'action': 'set_mode', 'value': 'heat'}
        # Bedrock placeholder
        bedrock_action = decide_action_with_bedrock({'deviceId': device_id, 'reported': reported})
        if bedrock_action:
            action = bedrock_action
        if action:
            topic = f"devices/{device_id}/commands"
            try:
                iot_client.publish(
                    topic=topic,
                    qos=0,
                    payload=json.dumps(action)
                )
                logger.info(f"Published action to {topic}: {action}")
            except ClientError as e:
                logger.error(f"IoT publish error: {e}")
        else:
            logger.info("No action required.")
        return {'statusCode': 200, 'body': 'Decision processed'}
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return {'statusCode': 500, 'body': 'DynamoDB error'}
