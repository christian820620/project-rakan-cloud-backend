import json
import boto3
import os
from decimal import Decimal
import logging
from typing import Dict, Any
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        action_group = event['actionGroup']
        function = event['function']
        message_version = event.get('messageVersion',1)
        parameters = event.get('parameters', [])
        
        def get_table_data():
            #Set table data
            dynamodb = boto3.resource('dynamodb')
            PARTITION_KEY_VALUE = '1'
            PARTITION_KEY_NAME = 'timestamp'
            try:
                table = dynamodb.Table('latest_data')
                response = table.get_item(
                    Key={
                        PARTITION_KEY_NAME: PARTITION_KEY_VALUE
                    }
                )
                item = response.get('Item')
                if not item:
                    return 'Table items not found'
                temperature_dec = item.get('temperature', Decimal(0))
                humidity_dec = item.get('humidity', Decimal(0))
                temperature =float(temperature_dec)
                humidity = float(humidity_dec)
                heat = item.get('heat', False)
                ac = item.get('ac', False)
                fan_speed_percentage = item.get('fan_speed_per')
                message = f'Temperature: {temperature}, Humidity: {humidity}, Heat: {heat}, AC: {ac}, Fan Speed Percent: {fan_speed_percentage}'
            except Exception as e:
                logger.error('Error: %s', str(e))
                message = f'Error: {str(e)}'
            return message
        
        response_body = {}

        if function == 'get_latest_data':
            message = get_table_data()
            response_body = {
                'TEXT': {
                    'body': message
                }
            }
        else:
            response_body = {
                'TEXT': {
                    'body': 'Did not invoke get table data'
                }
            }

        action_response = {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': response_body
            }
        }
        response = {
            'response': action_response,
            'messageVersion': message_version
        }

        logger.info('Response: %s', response)
        return response

    except KeyError as e:
        logger.error('Missing required field: %s', str(e))
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'body': f'Error: {str(e)}'
        }
    except Exception as e:
        logger.error('Unexpected error: %s', str(e))
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': 'Internal server error'
        }
