# Architecture Freeze v1

## Purpose
This document freezes the MVP system architecture for the iGEM mini project so software and hardware development can proceed in parallel without interface drift.

## Architecture Principles
- Reliability is prioritized over complexity.
- The system must be demo-ready, not feature-complete.
- Human approval is required before any run starts.
- The LLM is advisory only.
- No module can bypass the deterministic rule engine.
- Real, simulated, and future components must remain clearly separated.
- The system must run locally without cloud dependency for core control.

## MVP Architecture Summary
The MVP is built around a single local orchestration layer running on the mini PC. The backend owns the system state machine, enforces safety rules, serves the UI, coordinates the local LLM and retrieval layer, and exchanges telemetry and commands with the Arduino Uno R4 WiFi.

The architecture includes the following modules:
- UI layer
- FastAPI backend
- Deterministic rule engine
- Retrieval layer
- Local LLM layer
- Modeling module
- Hardware interface inside the backend
- Arduino Uno R4 WiFi firmware

## Frozen System Blocks

### 1. UI Layer
**Role**
- Dashboard for live monitoring
- Chat interface for operator assistance
- Protocol selection and approval
- Manual command panel
- Alarm display and acknowledgement

**Responsibilities**
- Display current system state
- Show latest sensor values
- Show active protocol and run metadata
- Let the operator approve or reject proposed runs
- Send only validated user requests to the backend

**Non-responsibilities**
- No direct communication with the MCU
- No direct actuator control
- No business logic or state authority

### 2. FastAPI Backend
**Role**
Central orchestrator of the MVP.

**Responsibilities**
- Own the system state machine
- Serve API endpoints to the UI
- Receive telemetry from the MCU
- Queue and dispatch validated control commands
- Manage run sessions and logs
- Coordinate retrieval, LLM, model, and rule engine
- Enforce all module boundaries

**Non-responsibilities**
- No direct low-level hardware pin control

### 3. Deterministic Rule Engine
**Role**
Single authority for safety and control validation.

**Responsibilities**
- Validate requested actions against current state
- Validate requested actions against protocol limits
- Validate requested actions against whitelist constraints
- Trigger alarms when safety thresholds are exceeded
- Block unsafe transitions and commands

**Non-responsibilities**
- No direct user interaction
- No language generation

### 4. Retrieval Layer
**Role**
Ground the assistant on approved system knowledge.

**Responsibilities**
- Index approved protocol files
- Index operating manual and troubleshooting references
- Return relevant context to the LLM

**Non-responsibilities**
- No actuator control
- No protocol generation

### 5. Local LLM Layer
**Role**
Operator-facing advisory assistant.

**Responsibilities**
- Explain approved protocols
- Answer operator questions
- Summarize current run status
- Recommend from approved protocols only

**Non-responsibilities**
- No direct command execution
- No state transitions
- No hardware authority
- No autonomous decision making

### 6. Modeling Module
**Role**
Advisory model for expected trends and run interpretation.

**Responsibilities**
- Consume current telemetry and selected protocol
- Produce simple advisory outputs such as expected trend or run-health summary
- Support the dashboard and assistant with non-controlling predictions

**Non-responsibilities**
- No actuator control
- No optimization-driven control
- No autonomous run adjustment

### 7. Hardware Interface Layer
**Role**
Backend-side interface to the MCU.

**Responsibilities**
- Receive telemetry packets
- Normalize incoming hardware data
- Maintain latest sensor snapshot
- Track communication health
- Expose pending commands for MCU polling
- Receive command acknowledgements

**Non-responsibilities**
- No direct sensor acquisition

### 8. Arduino Uno R4 WiFi Firmware
**Role**
Low-level hardware execution layer.

**Responsibilities**
- Read connected sensors on a fixed loop
- Report telemetry to backend over WiFi
- Poll backend for pending commands
- Execute validated actuator commands
- Return command acknowledgements
- Hold outputs in safe default states on reset or fault

**Non-responsibilities**
- No protocol logic
- No run orchestration
- No LLM or retrieval logic

## Frozen Deployment Topology
### Mini PC / Local Computer
Runs:
- FastAPI backend
- UI frontend
- Deterministic rule engine
- Retrieval service
- Local LLM runtime
- Modeling module
- Logging layer

### Arduino Uno R4 WiFi
Runs:
- Sensor acquisition loop
- Telemetry sender
- Command polling loop
- Command execution logic
- Local hardware safety defaults

## Frozen Communication Paths
### UI ↔ Backend
- HTTP for standard API requests
- Optional WebSocket for live dashboard updates

### Backend ↔ Arduino
- WiFi-based local network communication
- HTTP + JSON for MVP
- MCU posts telemetry to backend
- MCU polls backend for pending commands
- MCU posts command acknowledgements back to backend

### Backend ↔ Retrieval / LLM / Model
- Local internal calls within the mini PC environment

## Frozen Data Flow
### Telemetry Flow
1. Sensors are read by the Arduino.
2. Arduino packages telemetry into JSON.
3. Arduino sends telemetry to the FastAPI backend.
4. Backend validates and stores the telemetry.
5. Rule engine evaluates safety thresholds.
6. UI displays latest values.
7. Modeling module consumes telemetry for advisory output.
8. LLM may reference telemetry through backend tools.

### Command Flow
1. Operator sends a request from the dashboard or chat-derived workflow.
2. Backend receives the request.
3. State machine checks whether the current state allows the action.
4. Rule engine validates action, target, and parameters.
5. Backend stores a validated pending command.
6. Arduino polls backend for commands.
7. Arduino validates target and parameter range again.
8. Arduino executes the command.
9. Arduino sends command acknowledgement.
10. Backend updates status and logs the result.

### Chat and Recommendation Flow
1. Operator asks a question in chat.
2. Backend queries retrieval for approved context.
3. Relevant protocol and system documents are returned.
4. LLM produces a grounded answer.
5. If a protocol is recommended, backend creates a structured proposal.
6. Proposal waits for human approval before any run action.

## Frozen Control Authority
The following authority order is frozen for MVP:
1. Operator approval is required for run initiation.
2. FastAPI backend owns run orchestration.
3. Deterministic rule engine is the only safety authority.
4. Arduino executes only validated backend-issued commands.
5. LLM has no control authority.

## Human-in-the-Loop Freeze
The following actions require explicit operator approval:
- Selecting a proposed protocol for execution
- Starting a run
- Acknowledging alarms
- Restarting after alarm
- Stopping a run unless emergency rule logic forces safe-state action

## Real vs Simulated vs Future Work
### Real in MVP
- FastAPI backend
- State machine
- Rule engine
- Dashboard
- Chat interface
- Retrieval over approved documents
- Local advisory LLM
- Real telemetry ingestion from Arduino
- Real sensor reads for temperature, pH, pressure, and CO2
- Real actuation for pumps, motors, and heater at basic command level

### Simulated in MVP
- Full bioreactor biological dynamics
- Advanced production yield prediction
- Rich digital twin behavior
- Chromatography automation
- Advanced dosing optimization
- Any unwired actuator confirmation path

### Future Work
- Autonomous optimization
- Multi-reactor orchestration
- Cloud sync and remote control
- Advanced voice interface
- Automated downstream purification integration
- Model-driven closed-loop control

## Frozen Hardware Scope for MVP
### Real Sensors
- DS18B20 temperature sensor 1
- DS18B20 temperature sensor 2
- pH sensor 1
- pH sensor 2
- Pressure sensor
- CO2 sensor

### Real Actuators
- Peristaltic pump 1
- Peristaltic pump 2
- Gear motor 1
- Gear motor 2 via L298N
- Heating pads

### Context Only
- Chromatography components
- Extended tubing/valve choreography not required for MVP

## Frozen Safety Constraints
- No direct LLM-to-hardware communication
- No direct UI-to-MCU communication
- No automatic run start without operator approval
- No command execution outside whitelist
- No unsafe command execution during Alarm state
- No restart from Alarm without explicit reset path
- Loss of telemetry beyond timeout triggers Alarm

## Frozen System Assumptions
- Single reactor instance for MVP
- Single local backend instance
- Single Arduino controller in MVP
- Local network only
- Approved protocols stored locally as JSON files
- Advisory model is not a control source

## What Is Not Allowed to Change Without Explicit Review
The following are frozen at the end of Phase 1 and should not change casually:
- Backend as single orchestration authority
- Human-in-the-loop requirement
- Rule engine as mandatory control gate
- HTTP over WiFi as backend-MCU MVP communication pattern
- Approved-protocol-only assistant behavior
- Whitelist-based command execution
- Single-reactor architecture

## Exit Criteria for Architecture Freeze
Phase 1 architecture freeze is complete when all of the following exist:
- Architecture diagram approved by the team
- Module responsibility table approved
- Data flow agreed by backend and firmware owners
- Backend–MCU communication method fixed
- Human-in-the-loop boundaries documented
- Real vs simulated vs future classification approved
- No unresolved ambiguity on control authority

## Output Files Linked to This Freeze
- `docs/mvp_scope_v1.md`
- `docs/architecture_diagram_v1.png`
- `docs/state_machine_v1.md`
- `docs/api_spec_v1.md`
- `docs/hardware_interface_spec_v1.md`
- `docs/allowed_control_actions_v1.md`
- `protocols/protocol_library_v1/protocol_schema.json`

## Signoff
This version should be reviewed and signed off by:
- Technical lead
- Backend lead
- Firmware / hardware lead
- UI lead
- Safety / systems integration owner
