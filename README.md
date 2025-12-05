
# Project Rakan - AWS Serverless IoT Automation System

## Overview
Project Rakan is a smart home system utilizing AWS Cloud Infrastructure to control IoT devices, strongly focus on the backend. We are using the Arduino ESP32 Nano as our simulated physical IoT device to give us full control of our test case with how it can interact with AWS using MQTT protocol.

### AWS Services Used
- **IoT Core**: Gateway between IoT devices and AWS.
- **IAM**: Managed roles for all our infrastructures.
- **Lambda**: Serverless code execution, invoked via event JSON or other services.
- **DynamoDB**: NoSQL storage for device states, logs, etc.
- **Bedrock**: We use Nova Lite model to let it makes smart decisions and for users to interact with.
- **API Gateway**: Using REST API for frontend's connection to our service.
![How our system work](https://i.imgur.com/EYBxSux.png)

## Folder Structure
```
README.md
.gitignore
api-docs/
  smart_home_api.yaml
arduino_code/
  project_rankan.ino
  secrets.h
events/
	sample_iot_publish_msg.json
	sample_rule.sql
extras/
	agentInstruction.txt
	LaTeX_report.tex
lambdas/
  invoke_bedrock_agent/
	  example_output.json
	  get_latest_data.py
	  log_decision.py
	  set_thermostat.py
	manual_control/
		set_ac_or_heat.py
		set_fan.py
	log_to_dynamoDB.py
```
## About Our Arduino
We are using the ESP32 Nano connected with a 16x2 LCD Display and DHT11 sensor to recreate a smart thermostat device in common household. We use 3 different LEDs to simulate:
 - Fan speed: By adjusting its brightness value to simulate how fast a fan spin (0->100%)
 - Heating: Is the heating system on or not (Boolean)
 - AC: Is the cooling system on or not (Boolean)
![example schema of the Arduino device](https://i.imgur.com/I7CQH4X.png)
## Set Up
 1. Create a simulated Arduino device setup like above
 2. Log into **AWS IoT Core** to create a Thing, then download its certificate. We need: AWS_CERT_CA, AWS_CERT_CRT, and AWS_CERT_PRIVATE for the next step
 3. Using Arduino IDE, upload `project_rankan.ino` into your Arduino device after modifying `secrets.h` with your appropriate settings and certificates. Change the settings in `.ino` file as needed for your own use or your Arduino setup.
 4. Within your **AWS IAM** console, create appropriate roles for Lambda to use DynamoDB, and to use IoT Core.
 5. Create different **Lambda** functions in our `lambdas/` folder (if you want to have manual control instead of relying on the Bedrock Agent, use the functions in `manual_control/`) and give it the role above for its appropriate function. Only `set_thermostat.py` require publish to IoT permission.
 6. Create NoSQL tables to log data in **DynamoDB**. We use 3 tables in this project: `iot_log`, `latest_data`, and `AI_Decision_logs` all using a String partition key.
 7. Go to **IoT Core**, and create a Rule to invoke the Lambda function `log_do_dynamoDB.py` to log device's state. In the folder `events/` we have `sample_rule.sql` as example for the rule we have, and `sample_iot_publish_msg.json` as how IoT publish its JSON for our Lambda to grab.
 8. In **Amazon Bedrock**, create an agent, then give it instructions like `extras/agentInstruction.txt` with 3 action groups: `decision_logs` which will invoke `lambdas/invoke_bedrock_agent/log_decision.py`, `get_latest_data` which will invoke `lambdas/invoke_bedrock_agent/get_latest_data.py`, and `thermostat_set` which will invoke `lambdas/invoke_bedrock_agent/set_thermostat.py`.
 9. Give the agent appropriate permission to invoke our Lambda functions (each function needs to give agent access to resource via `lambda:InvokeFunction` permission)
 10. Bedrock agent understands Lambda output differently via JSON event, check out `lambdas/invoke_bedrock_agent/example_output.json` to see how we can simulate this within AWS Lambda's test event JSON. (Read more about this: [AWS Document on how to configure Lambda functions for Bedrock Agent](lambdas/invoke_bedrock_agent/example_output.json))
 11. To test each Lambda functions, you can use AWS's built in Event JSON testing
 12. To test Agent's respond, use its appropriate chat box.

## Extras
- `api-docs/smart_home_api.yaml` is our API Document using *Swagger* formatting, we haven't fully setup our **API Gateway** and have to chance to test with the frontend team yet, so consider this as a blueprint for future improvement.
- `extras/LaTeX_report.tex` contains our full report of this project in *LaTeX* format.
