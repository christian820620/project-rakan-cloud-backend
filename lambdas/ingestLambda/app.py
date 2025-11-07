import os
import json
import logging
from datetime import datetime, timezone
from dynamoLambda import put_reported_state
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ.get('TABLE_NAME', 'rakan-devicestate')
iot_endpoint = os.environ.get('IOT_ENDPOINT', '')
decision_function_name = os.environ.get('DECISION_FUNCTION_NAME', 'rakan-decision')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    #parse MQTT message 
    if "message" in event:
        try:
            event = json.loads(event["message"])
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            return {'statusCode' : 400, 'body': 'Invalid JSON payload'}

        device_id = event.get('deviceId') or event.get('device_id')
        if not device_id:
            return {'statusCode': 400, 'body': 'Missing deviceId'}
        
        #build + update device state
        reported = event.get('reported', event)
        if 'timestamp' not in reported:
            reported['timestamp'] = datetime.now(timezone.utc).isoformat()
        put_reported_state(device_id, reported)

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
