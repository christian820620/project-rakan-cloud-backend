import os
import json
import time
import logging
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ.get('TABLE_NAME', 'rakan-devicestate')
history_table_name = os.environ.get('HISTORY_TABLE', 'rakan-history')
decision_function_name = os.environ.get('DECISION_FUNCTION_NAME', 'rakan-decision')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    device_id = event.get('deviceId') or event.get('device_id')
    if not device_id:
        logger.error("Missing deviceId in event")
        return {'statusCode': 400, 'body': 'Missing deviceId'}

    try:
        table = dynamodb.Table(table_name)
        item = {
            'deviceId': device_id,
            'reported': event.get('reported', event),
            'lastUpdate': datetime.now(timezone.utc).isoformat()
        }
        table.put_item(Item=item)
        logger.info(f"Stored item for deviceId {device_id}")
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return {'statusCode': 500, 'body': 'DynamoDB error'}

    # Log historical data
    try:
        history_table = dynamodb.Table(history_table_name)
        history_table.put_item(Item={
            'deviceId': device_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'temperatureF': event.get('temperatureF'),
            'humidity': event.get('humidity'),
            'occupancy': event.get('occupancy'),
            'ttl': int(time.time()) + 60 * 60 * 24 * 90
        })
        logger.info(f"Logged historical data for {device_id}")
    except ClientError as e:
        logger.error(f"History logging error: {e}")

    # Async invoke decision Lambda
    try:
        payload = json.dumps({'deviceId': device_id})
        lambda_client.invoke(
            FunctionName=decision_function_name,
            InvocationType='Event',
            Payload=payload
        )
        logger.info(f"Invoked decision Lambda for deviceId {device_id}")
    except ClientError as e:
        logger.error(f"Lambda invoke error: {e}")

    return {'statusCode': 200, 'body': 'Success'}
