import os
import boto3
import logging
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

state_table = os.environ.get('table_name', 'deviceState')
history_table = os.environ.get('history_table_name', 'deviceHistory')

state_table = dynamodb.Table(state_table)
history_table = dynamodb.Table(history_table)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()

def generate_ttl(hours = 24):
    return int((datetime.now(timezone.utc) + timedelta(hours=hours)).timestamp())

def put_reported_state(device_id, reported):
    timestamp = reported.get("timestamp", utc_timestamp())

    #store current state in main table
    try:
        item = {
            "deviceId": device_id,
            "reported": reported,
            "lastUpdated": timestamp,
            "ttl": generate_ttl()
        }
        state_table.put_item(Item=item)
        logger.info(f"Reported state for device {device_id} updated successfully.")

        log_history(device_id, reported)
        return item

    except ClientError as e:
        logger.error(f"DynamoDB PutItem error: {e}")
        raise

def get_device_state(device_id):
    try:
        response = state_table.get_item(Key={"deviceId": device_id})
        item = response.get("Item")
        if not item: 
            logger.warning(f"No device state found for {device_id}")
            return item
    except ClientError as e:
        logger.error(f"DynamoDB GetItem error: {e}")
        raise

def update_desired_state(device_id, desired):
    try: 
        response = state_table.update_item(
            Key={"deviceId": device_id},
            UpdateExpression="SET desired = :d, lastUpdated = :t",
            ExpressionAttributeValues = {
                ":d": desired,
                ":t": utc_timestamp()
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Updated desired state for {device_id}: {desired}")
        return response.get("Attributes")
    except ClientError as e:
        logger.error(f"DynamoDB UpdateItem error: {e}")
        raise

def log_history(device_id, reported):
    try: 
        timestamp = reported.get("timestamp", utc_timestamp())

        history_item = {
            "deviceId": device_id,
            "timestamp": timestamp,
            "temperatureF": reported.get("temperatureF"),
            "humidity": reported.get("humidity"),
            "occupancy": reported.get("occupancy"),
            "ttl": generate_ttl(168) #keeps logs for a week
        }

        history_table.put_item(Item=history_item)
        logger.info(f"Logged history for device {device_id} at {timestamp}.")
    except ClientError as e:
        logger.error(f"History logging error: {e}")