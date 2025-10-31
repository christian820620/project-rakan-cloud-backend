# Project Rakan - AWS Serverless IoT Automation System

## Overview
Project Rakan is a serverless IoT automation backend using AWS IoT Core, Lambda, DynamoDB, and (future) Bedrock LAM. Arduino R4 WiFi devices publish telemetry to AWS IoT, triggering Lambda-based automation and device state management.

### AWS Services Used
- **IoT Core**: Device messaging and rules
- **Lambda**: Ingest, decision, and command functions
- **DynamoDB**: Device state storage
- **Bedrock**: (Planned) Large Action Model for advanced automation

## Folder Structure
```
README.md
api-docs/
  smart_home_api.yaml
infra/
  template.yaml
lambdas/
  ingestLambda/app.py
  decisionLambda/app.py
  commandLambda/app.py
```

## Environment Variables
All Lambdas:
- `TABLE_NAME` (default: rakan-devicestate)
- `IOT_ENDPOINT` (IoT Data endpoint)
Ingest Lambda only:
- `DECISION_FUNCTION_NAME` (default: rakan-decision)

## Local Setup
1. Create and activate virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install boto3:
   ```powershell
   pip install boto3
   ```
3. Zip and upload Lambda folders manually **OR** deploy with AWS SAM:
   ```powershell
   sam build && sam deploy --guided
   ```

## AWS Setup Checklist
- Create DynamoDB table `rakan-devicestate` (PK: deviceId)
- Create IoT Thing and note endpoint
- Create IoT Rule: `SELECT * FROM 'devices/+/telemetry'` → target `rakan-ingest`
- Set Lambda environment variables

## End-to-End Test Steps
1. Arduino publishes telemetry to MQTT topic `devices/{deviceId}/telemetry`
2. AWS IoT Core triggers `rakan-ingest` Lambda
3. Lambda stores state in DynamoDB
4. `rakan-decision` Lambda is invoked and publishes command if needed
5. `rakan-command` Lambda updates desired state and publishes to device

## TODO
- Integrate Bedrock-based Large Action Model for advanced decision logic
