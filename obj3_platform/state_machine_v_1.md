# State Machine Specification v1 (MVP)

## Purpose
This document defines the deterministic state machine that controls all system behavior. It ensures that every action follows a valid workflow and prevents unsafe or invalid operations.

---

## States Overview

The system operates under the following states:

- Idle  
- Request Intake  
- Protocol Recommendation  
- Approval Pending  
- Readiness Check  
- Run Active  
- Alarm  
- Completed  

Only the backend can modify the system state.

---

## State Definitions

### 1. Idle

**Description**  
System is inactive and waiting for user input.

**Entry Conditions**
- System startup completed
- Previous run finished
- Alarm resolved and reset

**Exit Conditions**
- User initiates a request

**Transitions**
- → Request Intake

---

### 2. Request Intake

**Description**  
System receives user intent (protocol selection or query).

**Entry Conditions**
- User submits a request

**Exit Conditions**
- Request is sufficiently defined

**Transitions**
- → Protocol Recommendation
- → Idle (if canceled)

---

### 3. Protocol Recommendation

**Description**  
System suggests approved protocols based on user request.

**Entry Conditions**
- Request defined
- Protocol library available

**Exit Conditions**
- Protocol selected or refined

**Transitions**
- → Approval Pending
- → Request Intake (if refinement needed)
- → Idle (if canceled)

---

### 4. Approval Pending

**Description**  
System waits for explicit user approval before execution.

**Entry Conditions**
- Proposed run configuration created

**Exit Conditions**
- User approves or rejects

**Transitions**
- → Readiness Check (if approved)
- → Request Intake (if modified)
- → Idle (if canceled)

---

### 5. Readiness Check

**Description**  
System verifies hardware, sensors, and safety conditions.

**Entry Conditions**
- Approved protocol exists

**Checks Performed**
- MCU connectivity
- Telemetry freshness
- Sensor availability
- Sensor values within safe range
- No active alarms

**Exit Conditions**
- All checks pass OR failure detected

**Transitions**
- → Run Active (if pass)
- → Alarm (if critical failure)
- → Approval Pending (if adjustment needed)
- → Idle (if canceled)

---

### 6. Run Active

**Description**  
System executes protocol and monitors telemetry.

**Entry Conditions**
- Readiness checks passed
- Run started

**Exit Conditions**
- Run completed
- User stops run
- Safety violation occurs

**Transitions**
- → Completed (normal finish)
- → Completed (manual stop)
- → Alarm (if violation)

---

### 7. Alarm

**Description**  
System detects unsafe condition and restricts operations.

**Entry Conditions**
- Sensor out of range
- Telemetry timeout
- Invalid command or fault

**Behavior**
- Block most commands
- Maintain or move to safe state
- Notify UI

**Exit Conditions**
- Operator acknowledges
- Issue resolved
- System reset

**Transitions**
- → Idle only

---

### 8. Completed

**Description**  
Run has finished normally or stopped safely.

**Entry Conditions**
- Protocol completed
- Manual stop executed

**Exit Conditions**
- System reset for next run

**Transitions**
- → Idle

---

## Allowed Transitions Summary

| From State           | To State                |
|---------------------|------------------------|
| Idle                | Request Intake         |
| Request Intake      | Protocol Recommendation |
| Protocol Recommendation | Approval Pending   |
| Approval Pending    | Readiness Check        |
| Readiness Check     | Run Active             |
| Run Active          | Completed              |
| Run Active          | Alarm                  |
| Alarm               | Idle                   |
| Completed           | Idle                   |

---

## Forbidden Transitions (Critical)

The following transitions are NOT allowed:

- Idle → Run Active
- Request Intake → Run Active
- Protocol Recommendation → Run Active
- Approval Pending → Run Active (without readiness check)
- Alarm → Run Active

---

## Control Rules

- Every action must check the current state before execution
- Only valid transitions are allowed
- Rule engine can override transitions by triggering Alarm
- No command execution is allowed in Alarm except safe actions

---

## Reset Logic

After Alarm:
- Operator must acknowledge alarm
- System must return to safe conditions
- State resets to Idle
- New run must restart from beginning

---

## Implementation Notes

- Represent states as enum in backend
- Store current state in memory (and optionally persistent store)
- All API endpoints must validate state before execution

---

## Summary

This state machine ensures:
- Deterministic behavior
- Safety enforcement
- Clear workflow
- Human-in-the-loop control

It is the backbone of the system logic and must be strictly followed during implementation.

