# Project Rakan - AWS Serverless IoT Automation System

## Overview
Project Rakan is a serverless IoT automation backend using AWS IoT Core, Lambda, and DynamoDB. Arduino R4 WiFi devices publish telemetry to AWS IoT, triggering Lambda-based automation and device state management.

### AWS Services Used
- **IoT Core**: Device messaging and rules
- **Lambda**: Ingest, decision, and command functions
- **DynamoDB**: Device state storage

## Folder Structure
```
README.md
api-docs/
  smart_home_api.yaml
  dynamodb_schema.json
infra/
  template.yaml
lambdas/
  ingestLambda/app.py
  decisionLambda/app.py
  commandLambda/app.py
```
## DynamoDB Schema

### Table: `rakan-devicestate`
Stores current state and desired state of IoT devices (Arduino).

**Table Configuration:**
- **Partition Key**: `deviceId` (String)
- **Billing Mode**: PAY_PER_REQUEST
- **TTL**: Enabled on `ttl` attribute (data expiration in seconds)

**Item Structure:**
```json
{
  "deviceId": "thermo-001",
  "currentState": {
    "temperatureF": 72.5,
    "humidity": 45.0,
    "occupancy": true,
    "timestamp": "2024-11-15T10:30:00Z"
  },
  "desiredState": {
    "temperatureF": 70.0,
    "mode": "cool",
    "fan": "auto"
  },
  "status": "online",
  "lastUpdated": 1699999999,
  "ttl": 1700000000
}
```

**Access Patterns:**
- `GetItem(deviceId)` - Decision Lambda retrieves current device state
- `PutItem(Item)` - Ingest Lambda stores new telemetry data
- `UpdateItem(deviceId, desiredState)` - Command Lambda updates desired state

## Environment Variables
All Lambdas:
- `TABLE_NAME` (default: rakan-devicestate)
- `IOT_ENDPOINT` (IoT Data endpoint)

Ingest Lambda only:
- `DECISION_FUNCTION_NAME` (default: rakan-decision)


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
- Add more advanced decision logic if needed
