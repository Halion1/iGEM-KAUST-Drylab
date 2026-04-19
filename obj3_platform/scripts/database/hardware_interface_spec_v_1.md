# Hardware Interface Specification v1 (MVP)

## Purpose
This document defines how the Arduino Uno R4 WiFi (MCU) communicates with the backend and how sensors and actuators are handled in the MVP system.

This is the contract between firmware and backend.

---

## Communication Architecture

### Protocol
- Communication: WiFi (local network)
- Protocol: HTTP
- Data format: JSON

### Pattern (MVP)
- MCU → Backend: POST telemetry
- MCU → Backend: GET commands (polling)
- MCU → Backend: POST command acknowledgements

This design keeps the MCU simple and avoids real-time synchronization issues.

---

## Responsibilities

### Arduino (MCU)
- Read sensors
- Send telemetry to backend
- Poll backend for commands
- Execute actuator commands
- Send command acknowledgements
- Maintain safe defaults

### Backend
- Receive and validate telemetry
- Store latest sensor values
- Evaluate safety rules
- Queue validated commands
- Serve commands to MCU
- Track command execution

---

## Sensor Integration (MVP)

### Sensors (Real)
- DS18B20 Temperature Sensor x2
- pH Sensor x2
- Pressure Sensor x1
- CO2 Sensor x1

### Reading Frequency
- Temperature: every 2 seconds
- pH: every 2 seconds
- Pressure: every 2 seconds
- CO2: every 5 seconds

### Telemetry Frequency
- Every 2 seconds

---

## Telemetry Schema

```json
{
  "device_id": "arduino_uno_r4_01",
  "timestamp": "ISO-8601",
  "heartbeat": 1,
  "sensors": {
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

---

## Actuator Integration (MVP)

### Real Actuators
- Peristaltic Pump 1
- Peristaltic Pump 2
- Gear Motor 1 (via L298N)
- Gear Motor 2 (via L298N)
- Heating Pads

### Supported Commands
- start_pump
- stop_pump
- start_motor
- stop_motor
- set_heater
- stop_run

---

## Command Schema

```json
{
  "command_id": "string",
  "action": "string",
  "target": "string",
  "parameters": {}
}
```

### Example
```json
{
  "command_id": "cmd_101",
  "action": "start_pump",
  "target": "pump_1",
  "parameters": {
    "duration_sec": 10
  }
}
```

---

## Command Flow

1. Backend validates command
2. Backend stores command in queue
3. MCU polls `/mcu/commands`
4. MCU receives command
5. MCU validates target + parameters
6. MCU executes command
7. MCU sends acknowledgement

---

## Command Acknowledgement Schema

```json
{
  "device_id": "arduino_uno_r4_01",
  "command_id": "string",
  "timestamp": "ISO-8601",
  "status": "executed|failed",
  "details": "string"
}
```

---

## MCU Loop (Reference)

Recommended loop:

1. Read sensors
2. Validate readings (basic sanity checks)
3. Send telemetry to backend
4. Poll backend for commands
5. Execute command if present
6. Send acknowledgement

---

## Safety Behavior

### Backend-side
- Missing telemetry → Alarm
- Out-of-range values → Alarm
- Invalid commands → Rejected

### MCU-side
- On startup → all actuators OFF
- On communication loss → maintain safe state
- Reject unknown commands

---

## Real vs Simulated (MVP)

### Real
- Sensor readings
- Pump control (on/off)
- Motor control (basic)
- Heater control (on/off)

### Simulated
- Precise dosing feedback
- Advanced actuator timing
- Chromatography control

---

## Constraints

- MCU must never execute unvalidated commands
- Backend must never assume command execution without acknowledgement
- Communication must be robust to temporary disconnections

---

## Summary

This interface ensures:
- Clear separation between hardware and logic
- Safe command execution
- Deterministic behavior
- Easy debugging and testing

It is the foundation for reliable integration between firmware and backend.

