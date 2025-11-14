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

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    device_id = event.get('deviceId') or event.get('device_id')
    desired = event.get('desired')
    if not device_id or desired is None:
        logger.error("Missing deviceId or desired state in event")
        return {'statusCode': 400, 'body': 'Missing deviceId or desired'}
    try:
        table = dynamodb.Table(table_name)
        # Update desired state in DynamoDB
        resp = table.update_item(
            Key={'deviceId': device_id},
            UpdateExpression="SET desired = :d, lastUpdate = :t",
            ExpressionAttributeValues={
                ':d': desired,
                ':t': int(context.aws_request_id[:8], 16)
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Updated desired state for {device_id}: {desired}")
        # Publish command to device
        topic = f"devices/{device_id}/commands"
        iot_client.publish(
            topic=topic,
            qos=0,
            payload=json.dumps({'desired': desired})
        )
        logger.info(f"Published desired state to {topic}")
        return {'statusCode': 200, 'body': 'Command processed'}
    except ClientError as e:
        logger.error(f"Error: {e}")
        return {'statusCode': 500, 'body': 'Error processing command'}
