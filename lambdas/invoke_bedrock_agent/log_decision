import boto3
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from typing import Dict, Any
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#log decision into DynamoDB table
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        action_group = event['actionGroup']
        function = event['function']
        message_version = event.get('messageVersion',1)
        parameters = event.get('parameters', [])

        def log_to_dynamodb(decision):
            client = boto3.client('dynamodb')
            #get current time
            eastern_timezone = ZoneInfo('America/New_York')
            now = datetime.now(eastern_timezone)
            formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            #put into table
            try:
                response = client.put_item(
                    TableName='AI_Decision_logs',
                    Item={
                        'Log': {'S': formatted_datetime},
                        'decision': {'S': decision}
                    }
                )
                return 'Successfully log decision into DynamoDB'
            except Exception as e:
                return f'Error logging decision: {str(e)}'
        #let agent use and invoke
        if function == 'log_decision':
            decision = parameters[0]['value']
            message = log_to_dynamodb(decision)
            response_body = {
                'TEXT': {
                    'body': message
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
