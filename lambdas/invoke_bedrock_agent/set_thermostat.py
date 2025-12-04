
import json
import boto3
import os
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

        response_body = {}
        message = ''
        #topic to publish to
        def publish_mqtt_fan(fan_speed_per):
            try:
                client = boto3.client('iot-data', endpoint_url = os.environ.get('ajf3ues13gfrd-ats.iot.us-east-2.amazonaws.com'))
                thing_name = os.environ.get('Smart-Thermostat')
                fan_speed_float = float(fan_speed_per)
                fan_speed_raw = int(fan_speed_float * 2.55)
                #Publish to fan speed
                client.publish(
                    topic = 'thermostat/fan',
                    qos = 0,
                    payload = json.dumps(
                        {
                            "message" : f"fan speed set {fan_speed_raw}",
                            "fan speed" : fan_speed_raw
                        }
                    )
                )
                return f'Fan speed successfully set to {fan_speed_float}%'
            except Exception as e:
                logger.error('Unexpected error: %s', str(e))
                return f'Error: {str(e)}'
        
        def publish_mqtt_heat_ac(heat, ac):
            client = boto3.client('iot-data', endpoint_url = os.environ.get('ajf3ues13gfrd-ats.iot.us-east-2.amazonaws.com'))
            thing_name = os.environ.get('Smart-Thermostat')
            #Publish to heat and ac
            try:
                client.publish(
                    topic = 'thermostat/heatAC',
                    qos = 0,
                    payload = json.dumps(
                        {
                            "message" : f"set ac {ac} and set heat {heat}",
                            "heat set" : heat,
                            "ac set" : ac
                        }
                    )
                )
                return f'AC successfully set to {ac},and Heat successfully set to {heat}'
            except Exception as e:
                logger.error('Unexpected error: %s', str(e))
                return f'Error: {str(e)}'

        #let agent set according to topic
        if function == 'set_thermostat_fan':
            fan_speed_per = parameters[0]['value']
            message = publish_mqtt_fan(fan_speed_per)
            response_body = {
                'TEXT': {
                    'body': message
                }
            }
        elif function == 'set_thermostat_heat_ac':
            for param in parameters:
                if param['name'] == 'heat':
                    heat_str = param['value']
                    if heat_str == 'true' or heat_str == 'True':
                        heat = True
                    else: heat = False
                if param['name'] == 'ac':
                    ac_str = param['value']
                    if ac_str == 'true' or ac_str == 'True':
                        ac = True
                    else: ac = False
            message = publish_mqtt_heat_ac(heat, ac)
            response_body = {
                'TEXT': {
                    'body': message
                }
            }
        else:
            response_body = {
                'TEXT': {
                    'body': f'The function {function} was called successfully with parameters: {parameters}!'
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

