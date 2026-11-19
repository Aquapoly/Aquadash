# AquaDash v3 — Conceptual model (diagrams)

| Version | Date       | Based on                                 |
| ------- | ---------- | ---------------------------------------- |
| _v0.1_  | 2026-11-18 | [Vision v1.1](aquadash-v3.0.0-vision.md) |

These are **conceptual** diagrams: domain concepts, their main attributes and their associations. They are not database tables or code classes. The glossary, design decisions, triage of the original candidates and open questions are in the sister document [conceptual-model-notes.md](conceptual-model-notes.md).

The model has four views:

- **A. Topology**: what exists physically and logically, and how the two connect.
- **B. Control and commands**: how readings become decisions, doses and commands.
- **C. People, safety and alerts**: who can do what, and who gets told.
- **D. Controller side**: what runs on a controller. This is a separate model from the brain's.

Concepts marked `post-v3` are modeled so that the architecture leaves room for them. v3.0.0 doesn't implement them.

---

## A. Topology

```mermaid
classDiagram
  direction LR

  class Subject {
    <<abstract>>
    uid
    name
  }
  class Site {
    post-v3
  }
  class HydroponicSystem
  class Reservoir {
    nominalVolume
  }
  Subject <|-- Site
  Subject <|-- HydroponicSystem
  Subject <|-- Reservoir
  Site "0..1" -- "0..*" HydroponicSystem : hosts
  HydroponicSystem "1" *-- "1..*" Reservoir

  class Controller {
    uid
    credentials
  }
  class Device {
    uid
    label
  }
  class Wiring {
    locator
    from
    to
  }
  class DeviceType {
    driverId
    driverVersion
    capabilities
    deviceConfigSchema
  }
  class ChannelSpec {
    index
    direction
    valueType
    range
    rawUnit
    doc
  }
  class Channel {
    label
  }
  class MeasureChannel {
    reportPeriod
  }
  class ActuationChannel

  Controller "1" -- "0..*" Wiring
  Wiring "0..*" -- "1" Device
  Controller "0..*" -- "0..*" DeviceType : firmware supports
  Device "0..*" -- "1" DeviceType
  DeviceType "1" *-- "1..*" ChannelSpec
  Device "1" *-- "1..*" Channel
  Channel "0..*" -- "1" ChannelSpec : realizes
  Channel <|-- MeasureChannel
  Channel <|-- ActuationChannel
  MeasureChannel "0..*" -- "0..1" Subject : measures
  ActuationChannel "0..*" -- "0..1" Subject : acts on
  ActuationChannel "0..*" -- "0..1" Solution : delivers

  class Quantity {
    name
    canonicalUnit
  }
  class Unit {
    symbol
    factor
    offset
  }
  Quantity "1" *-- "1..*" Unit
  Channel "0..*" -- "0..1" Quantity
  Channel "0..*" -- "0..1" Unit : values expressed in

  class Reading {
    rawValue
    value
    status
    timestamp
  }
  class ChannelCalibration {
    version
    model
    params
  }
  class DeviceCalibration {
    version
    kind
    payload
  }
  class ReadingFilter {
    version
    strategy
    params
  }
  class PhysicalLimit {
    kind
    value
  }
  MeasureChannel "1" -- "0..*" Reading : produces
  Reading "0..*" -- "1" Subject : about
  Reading "0..*" -- "0..1" ChannelCalibration : under
  Reading "0..*" -- "0..1" DeviceCalibration : under
  Channel "1" -- "0..*" ChannelCalibration : versions
  Device "1" -- "0..*" DeviceCalibration : versions
  MeasureChannel "1" -- "0..*" ReadingFilter : versions
  ActuationChannel "1" -- "0..*" PhysicalLimit

  class ConnectionEvent {
    kind
    timestamp
    reason
  }
  class Discrepancy {
    kind
    detectedAt
    resolvedAt
  }
  Controller "1" -- "0..*" ConnectionEvent
  Controller "1" -- "0..*" Discrepancy
  Discrepancy "0..*" -- "0..1" Wiring : about
```

**Invariant:** only **Channel ↔ Subject** bindings and **calibrations** connect the physical side (Controller, Wiring, Device, DeviceType) to the logical side (Subject and below). Control logic never refers to a controller, a locator or a pin.

---

## B. Control and commands

```mermaid
classDiagram
  direction LR

  class ControlLoopType {
    name
    portSpecs
  }
  class ControlLoop {
    version
    params
    state
    paused
  }
  class PortBinding {
    portName
  }
  class Arbitrator {
    strategy
  }
  class Target {
    strategy
    params
  }
  class PolicyLimit {
    kind
    value
    window
  }

  HydroponicSystem "1" -- "0..*" ControlLoop
  HydroponicSystem "1" -- "1" Arbitrator
  Arbitrator "1" -- "0..*" ControlLoop : arbitrates
  ControlLoop "0..*" -- "1" ControlLoopType
  ControlLoop "1" *-- "1..*" PortBinding
  PortBinding "0..*" -- "1" Channel
  ControlLoop "0..*" -- "0..*" Target : pursues
  Target "0..*" -- "1" Subject
  Target "0..*" -- "0..1" Quantity
  PolicyLimit "0..*" -- "1" Subject
  PolicyLimit "0..*" -- "0..1" ActuationChannel

  class Recipe {
    name
    post-v3
  }
  class GrowthStage {
    name
    transitionRule
  }
  class RecipeApplication {
    startedAt
    currentStage
  }
  Recipe "1" *-- "1..*" GrowthStage
  GrowthStage "1" -- "0..*" Target : defines
  GrowthStage "1" -- "0..*" ControlLoop : configures
  HydroponicSystem "1" -- "0..*" RecipeApplication
  RecipeApplication "0..*" -- "1" Recipe

  class Originator {
    <<abstract>>
  }
  class Decision {
    timestamp
    rationale
    outcome
  }
  class Dose {
    volume
  }
  class Command {
    id
    kind
    params
    deadline
    status
  }
  class CommandReport {
    phase
    executed
    reason
    receivedAt
  }
  Originator <|-- User
  Originator <|-- Decision
  ControlLoop "1" -- "0..*" Decision : makes
  Decision "0..*" -- "0..*" Reading : based on
  Dose "0..*" -- "1" Originator : issued by
  Dose "0..*" -- "1" Solution
  Dose "1" -- "1..*" Command : realized by
  Command "0..*" -- "1" Originator : issued by
  Command "0..*" -- "1" Channel : targets
  Command "1" -- "0..*" CommandReport
```

- `Command.kind` is one of: `actuate`, `readNow`, `configure` (replayable) or `procedure` (one-shot, never replayed). A `configure` or `procedure` command addresses the whole Device rather than a single channel.
- `CommandReport.phase` is `received`, `refused`, `completed` or `partial`. Reports may arrive late (after a reconnect).
- **v3 scope:** one ControlLoop per system (EC → A/B, or EC + pH → A/B/pH±), a trivial Arbitrator, and static Targets.

---

## C. People, safety and alerts

```mermaid
classDiagram
  direction LR

  class Principal {
    <<abstract>>
  }
  class User {
    username
    email
  }
  class Group {
    name
  }
  class Membership {
    role
  }
  Principal <|-- User
  Principal <|-- Group
  User "0..*" -- "0..*" Group
  Membership "0..*" -- "1" Principal
  Membership "0..*" -- "1" HydroponicSystem

  class MaintenanceSession {
    start
    plannedEnd
    end
    endedBy
  }
  HydroponicSystem "1" -- "0..*" MaintenanceSession
  MaintenanceSession "0..*" -- "1" User : held by

  class Alertable {
    <<abstract>>
    uid
  }
  class AlertRule {
    version
    strategy
    params
  }
  class Alert {
    severity
    status
    raisedAt
  }
  class Subscription {
    deliveryChannels
  }
  Alertable <|-- Subject
  Alertable <|-- Controller
  Alertable <|-- Device
  Alertable <|-- Command
  Alertable <|-- ControlLoop
  Subject "1" -- "0..*" AlertRule
  Alert "0..*" -- "1" Alertable : concerns
  Alert "0..*" -- "0..1" AlertRule : raised by
  User "1" -- "0..*" Subscription
  Subscription "0..*" -- "1" HydroponicSystem
```

---

## D. Controller side

```mermaid
classDiagram
  direction LR

  class BrainLink {
    state
    clockOffset
  }
  class ConfigStore {
    <<volatile>>
  }
  class DriverCatalog
  class Driver {
    descriptor
  }
  class DriverInstance {
    deviceUid
    locator
    health
  }
  class LocalChannel {
    index
  }
  class Reporter {
    period
  }
  class CommandInbox {
    seenIds
  }
  class SafetyGovernor {
    limits
    dutyWindow
  }
  class Executor {
    hardwareStopTimer
  }
  class OutboundQueue

  BrainLink "1" -- "1" ConfigStore : refills on connect
  BrainLink "1" -- "1" DriverCatalog : announces
  DriverCatalog "1" *-- "1..*" Driver
  ConfigStore "1" -- "0..*" DriverInstance : wiring creates
  DriverInstance "0..*" -- "1" Driver
  DriverInstance "1" *-- "1..*" LocalChannel
  LocalChannel "1" -- "0..1" Reporter
  BrainLink "1" -- "1" CommandInbox
  CommandInbox "1" -- "1" SafetyGovernor : validates via
  SafetyGovernor "1" -- "1" Executor
  Executor "1" -- "0..*" LocalChannel : drives
  Reporter "1" -- "1" OutboundQueue
  Executor "1" -- "1" OutboundQueue
  OutboundQueue "1" -- "1" BrainLink
```
