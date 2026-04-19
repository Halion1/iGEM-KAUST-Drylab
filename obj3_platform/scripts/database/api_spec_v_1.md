# API Specification v1 (FastAPI)

## Purpose
This document defines all backend endpoints, request/response formats, and validation rules for the MVP system. It serves as the contract between the UI, backend, and hardware (Arduino).

---

## General Rules
- All requests and responses use JSON
- All timestamps use ISO-8601 format
- Backend is the only authority for state transitions and command validation
- All actuator commands must pass whitelist + rule engine validation

---

## 1. Chat Endpoint

### POST /chat

**Purpose**
Operator interaction with the assistant (LLM + retrieval)

**Request**
```json
{
  "session_id": "string",
  "message": "string",
  "context": {
    "current_state": "string",
    "selected_protocol_id": "string|null"
  }
}
```

**Response**
```json
{
  "answer": "string",
  "citations": ["string"],
  "suggested_action": {
    "type": "string",
    "protocol_id": "string"
  }
}
```

---

## 2. Protocol Endpoints

### GET /protocols

**Purpose**
Retrieve all approved protocols

**Response**
```json
{
  "protocols": [
    {
      "protocol_id": "string",
      "name": "string",
      "target_compound": "string",
      "version": "string"
    }
  ]
}
```

---

## 3. Run Management

### POST /run/request

**Purpose**
Create a proposed run configuration

**Request**
```json
{
  "operator_id": "string",
  "protocol_id": "string",
  "notes": "string"
}
```

**Response**
```json
{
  "run_id": "string",
  "state": "Approval Pending",
  "proposed_config": {
    "temperature_target_c": "float",
    "ph_range": ["float", "float"],
    "duration_min": "int"
  }
}
```

---

### POST /run/approve

**Purpose**
Approve or reject a proposed run

**Request**
```json
{
  "run_id": "string",
  "operator_id": "string",
  "approved": true
}
```

**Response**
```json
{
  "run_id": "string",
  "state": "Readiness Check"
}
```

---

### POST /run/start

**Purpose**
Start an approved run

**Request**
```json
{
  "run_id": "string"
}
```

**Response**
```json
{
  "run_id": "string",
  "state": "Run Active",
  "started_at": "timestamp"
}
```

---

### POST /run/stop

**Purpose**
Stop an active run

**Request**
```json
{
  "run_id": "string",
  "reason": "string"
}
```

**Response**
```json
{
  "run_id": "string",
  "state": "Completed"
}
```

---

## 4. System Status

### GET /status

**Response**
```json
{
  "system_state": "string",
  "active_run_id": "string|null",
  "mcu_online": true,
  "last_telemetry_ts": "timestamp",
  "active_alarms": []
}
```

---

### GET /sensor/latest

**Response**
```json
{
  "timestamp": "timestamp",
  "temperature_c": {
    "sensor_1": "float",
    "sensor_2": "float"
  },
  "ph": {
    "sensor_1": "float",
    "sensor_2": "float"
  },
  "pressure_kpa": "float",
  "co2_ppm": "float"
}
```

---

## 5. Hardware (MCU) Endpoints

### POST /telemetry

**Purpose**
Receive sensor data from Arduino

**Request**
```json
{
  "device_id": "string",
  "timestamp": "timestamp",
  "sensors": {
    "temperature_c": {"sensor_1": "float", "sensor_2": "float"},
    "ph": {"sensor_1": "float", "sensor_2": "float"},
    "pressure_kpa": "float",
    "co2_ppm": "float"
  },
  "actuator_status": {
    "pump_1": "on|off",
    "pump_2": "on|off",
    "motor_1": "on|off",
    "motor_2": "on|off",
    "heater_1": "on|off"
  }
}
```

**Response**
```json
{
  "accepted": true
}
```

---

### GET /mcu/commands

**Purpose**
MCU polls for pending commands

**Response**
```json
{
  "commands": [
    {
      "command_id": "string",
      "action": "string",
      "target": "string",
      "parameters": {}
    }
  ]
}
```

---

### POST /mcu/command_ack

**Purpose**
MCU confirms command execution

**Request**
```json
{
  "device_id": "string",
  "command_id": "string",
  "timestamp": "timestamp",
  "status": "executed|failed"
}
```

---

## 6. Alarm Handling

### POST /alarm/acknowledge

**Request**
```json
{
  "alarm_id": "string",
  "operator_id": "string",
  "notes": "string"
}
```

---

## Validation Rules (Critical)

All requests must satisfy:
- Valid system state transition
- Protocol must exist and be approved
- Commands must be in whitelist
- Parameters must be within bounds
- No execution allowed during Alarm state (except safe actions)

---

## Error Handling

Standard response:
```json
{
  "error": "string",
  "code": "string"
}
```

Examples:
- INVALID_STATE
- COMMAND_NOT_ALLOWED
- SENSOR_TIMEOUT
- PROTOCOL_NOT_FOUND

---

## Summary

This API ensures:
- Clear separation between UI, backend, and hardware
- Deterministic and safe control flow
- Human-in-the-loop enforcement
- Extensibility for future phases

