# AquaDash v3 — Conceptual model (notes)

| Version | Date       | Diagrams                                     |
| ------- | ---------- | -------------------------------------------- |
| _v0.1_  | 2026-11-18 | [conceptual-model.md](conceptual-model.md)   |

This document explains the diagrams in [conceptual-model.md](conceptual-model.md): what each concept means, why the model has this shape, and what is still open. It follows [vision v1.1](aquadash-v3.0.0-vision.md). The raw brainstorming (candidate list, questions and answers) is in [domain-model.md](domain-model.md).

---

## 1. Structural principles

1. **Physical and logical are separate (vision 7.5).** The physical side is Controller, Wiring, Device, DeviceType and Channel. The logical side is Subject (Site, HydroponicSystem, Reservoir), Target, ControlLoop, Decision and Dose. They meet only where a **Channel is bound to a Subject** (or to a loop port) and through **calibrations**. Rewiring hardware changes Wiring; it never changes logic.
2. **The brain knows values, not sensor types.** A channel produces typed values (bool, int or float in a range, bytes). What a value *means* (EC, pH, temperature) comes from binding it to a Quantity, a Subject and a loop port. Supporting a new sensor never needs new code in the brain.
3. **Derived associations are not stored.** For example, "this controller serves this reservoir" can be computed through Wiring → Device → Channel → Subject. Storing it as well would create a second source of truth that drifts on every rewire.
4. **Logic is "a strategy plus parameters, versioned."** ReadingFilter, AlertRule, Target, ControlLoop and Arbitrator all follow the same pattern: a strategy type chosen from a list, its parameters, a version, and a date it took effect. Changing logic means activating a new version, never editing the old one, so past decisions stay explainable (7.8).
5. **Everything that can raise an alert or be traced has a uid.**

---

## 2. Glossary

### Topology (view A)

| Concept | Meaning |
| --- | --- |
| **Subject** | Anything the brain measures or acts on. It is abstract. Readings, targets, alert rules and policy limits point at a Subject. |
| **Site** | `post-v3`. A physical place (a room, a warehouse) that hosts systems. It lets one ambient sensor serve several systems. In v3, an ambient sensor binds to its HydroponicSystem directly. |
| **HydroponicSystem** | The logical unit users think about and that control logic targets. It is made of one or more reservoirs. |
| **Reservoir** | One body of water. It belongs to **exactly one** system. Its volume drifts (evaporation, leaks), so `nominalVolume` is only an estimate until a level sensor exists. |
| **Controller** | A networked process attached to devices (vision §6). It has an identity and credentials. |
| **Device** | A physical piece of hardware with its own identity in the brain, **independent of where it is plugged in**. Its channels and calibrations stay with it when it is rewired. |
| **Wiring** | Device ↔ Controller ↔ locator (bus, address, pin), with a time range. The brain is the source of truth for it and pushes it as configuration (vision 7.6, v1.1). |
| **DeviceType** | The descriptor of a driver, as announced by the controllers whose firmware contains it. It lists channels, operations, capabilities (e.g. the minimum intensity a pump runs at) and, if needed, the schema of its device-side calibration. The brain stores it as data. |
| **ChannelSpec** | One channel as the driver documents it: index, direction (measure or actuation), value type, range, raw unit, and a text description ("ch0 = temperature"). |
| **Channel** | A device's instance of a ChannelSpec, with a user-given label. It is either a **MeasureChannel** (has a report period) or an **ActuationChannel**. A device can have several channels: the SHTC3 measures temperature and humidity, and a pump board drives 4 pumps. |
| **Quantity / Unit** | A shared vocabulary that makes values comparable across systems (see D6). |
| **Solution** | What an actuation channel delivers (nutrient A, nutrient B, pH−, …). |
| **Reading** | One value from a MeasureChannel. It is **about a Subject**, recorded when the reading is taken, so rebinding a channel later doesn't move old readings. It stores the raw value, the converted and calibrated value, a status (accepted / rejected / corrected) and the calibration versions in effect. |
| **ChannelCalibration** | Brain-side calibration (see D7). |
| **DeviceCalibration** | Device-side calibration (see D7). |
| **ReadingFilter** | The strategy for detecting and handling aberrant data on a channel: thresholds, running statistics, or both (7.7). |
| **PhysicalLimit** | A physical safety limit on an actuation channel: max duration, intensity bounds, duty cap per window. It is modeled in the brain, pushed down, and **enforced by the controller** (see D8). |
| **ConnectionEvent** | A transition in a controller's connection (connected or lost, with a reason). Heartbeats themselves aren't stored. These events answer "why didn't the 3 AM dose happen?" |
| **Discrepancy** | A gap between the wiring the brain configured and what the controller reports: device not responding, driver missing from firmware, and so on (7.6). |

### Control and commands (view B)

| Concept | Meaning |
| --- | --- |
| **ControlLoopType** | A control strategy offered in a dropdown. It declares named **ports**: inputs (e.g. `ec`) and outputs (e.g. `nutrientA`, `nutrientB`). |
| **ControlLoop** | One configured instance on a system: a type, parameters, a state (dosing / mixing / measuring / deciding) and a pause flag. |
| **PortBinding** | Connects a loop port to a channel. This is how a loop finds "its" pumps and sensors without knowing about hardware. |
| **Arbitrator** | Resolves conflicts between a system's loops (e.g. an EC dose making pH drift). v3 uses a trivial arbitrator over a single loop. |
| **Target** | The desired value or range of a Quantity on a Subject. It is a strategy: static in v3, and later it may depend on the growth stage or on other readings. |
| **PolicyLimit** | A brain-only cap on what the brain is willing to issue, e.g. at most X mL of nutrient per system per day (see D8). |
| **Recipe / GrowthStage / RecipeApplication** | `post-v3`. A named bundle of targets and loop configurations per growth stage ("Tomatoes & Strawberries"). Stages change manually or by rule (e.g. elapsed time). A RecipeApplication records when a recipe was applied to a system. |
| **Decision** | One evaluation by a loop: the readings it used, its rationale, and its outcome (dose, wait, or abstain and alert). It is the main object of traceability (7.8). |
| **Dose** | A logical request: "add *V* mL of solution *S*." Calibration turns it into one or more Commands. It is what operators normally issue. |
| **Command** | A uniquely identified, bounded directive from the brain to a controller (vision §6). Kinds: `actuate`, `readNow`, `configure` (replayable), `procedure` (one-shot). Operators can issue raw commands from an "advanced" menu, where they may also set the deadline. |
| **CommandReport** | What the controller reports back for a command: received, refused (with a reason), completed, or partial (what actually ran, and why it stopped). A report may arrive late, after a reconnect, and change an `unknown` command to a known outcome. |
| **Originator** | Who issued a Dose or Command: a **User** (manual) or a **Decision** (automatic). |

### People and alerts (view C)

| Concept | Meaning |
| --- | --- |
| **User / Group / Principal** | Groups carry baseline permissions shared by their members. |
| **Membership** | Gives a role to a principal on a HydroponicSystem. Permissions are per system. |
| **MaintenanceSession** | Suspends automation on a system. Only its holder can send manual commands. It has a mandatory `plannedEnd`, so it expires even if the holder disappears, and an admin can end it early. |
| **AlertRule** | The logic that decides when readings warrant a warning or an emergency stop, attached to a Subject. It belongs to the brain, not to the sensor. |
| **Alert** | Concerns any Alertable (Subject, Controller, Device, Command, ControlLoop). It is raised by a rule, a decision that abstains, a lost connection, a discrepancy, and so on. |
| **Subscription** | A user follows a system, which covers all alerts under it, and chooses delivery (email, in-app, both or neither). Finer-grained subscriptions come later. Because every Alertable has a uid, that is possible without changing the model. |

### Controller side (view D)

| Concept | Meaning |
| --- | --- |
| **BrainLink** | The connection to the brain, whatever the transport (vision §8). It keeps the clock offset learned at connection. |
| **ConfigStore** | Volatile. It holds wiring, limits and report periods, all received again on every connection. |
| **DriverCatalog / Driver** | The drivers compiled into the firmware. Their descriptors are announced to the brain and become DeviceTypes there. |
| **DriverInstance / LocalChannel** | A driver instance created for one device at one locator, as the wiring requires, with its health status. |
| **Reporter** | Sends periodic readings for a measure channel. |
| **CommandInbox** | Removes duplicate commands by id (7.4) and refuses those past their deadline. |
| **SafetyGovernor** | Enforces PhysicalLimits, including the duty window. It refuses; it never modifies a command (see D5). |
| **Executor** | Runs actuations with a stop that **does not depend on the code that started them** (see §5). |
| **OutboundQueue** | Buffers readings and reports while the brain is unreachable. |

---

## 3. Design decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D1 | **Channels, not sensor types.** The brain sees typed value streams. Meaning comes from binding. | New hardware means only a new driver. Two EC channels on the same reservoir are allowed; the UI may warn about duplicate dosing but doesn't forbid it. |
| D2 | **Readings belong to Subjects, not sensors.** | A reading describes the water or the environment. The sensor is just how it was obtained. |
| D3 | **Device identity is separate from Wiring.** | A rewire, even onto another controller, keeps the device's calibration and channel bindings. If a device moves to a different *Subject*, the loops bound to it are flagged for review. |
| D4 | **The brain pushes the wiring; controllers announce driver catalogs.** This replaces vision v1.0 §7.6 (corrected in v1.1). | The controller can't know which physical device is where. Microcontroller firmware becomes "a library of drivers plus configuration." |
| D5 | **Controllers refuse or report partial execution; they never modify commands.** | If the controller clamped a command, the brain's dose accounting would stop being deterministic, and the controller would be making decisions. A refusal with a reason gives the brain everything it needs to replan. |
| D6 | **Units are a shared Quantity vocabulary with affine conversions.** Each Quantity has a canonical unit and a list of Units, each with `factor` and `offset` to the canonical one (an offset is needed for °F). A channel declares the unit its values come in, by default the driver's `rawUnit`. The brain stores values in canonical units and displays them in the user's choice. There is an **"Other"** escape: a custom Quantity and unit, which is only comparable to itself. | This makes EC from system 1 comparable to EC from system 2, whatever each driver reports (mS/cm, µS/cm, mS/m). Unit conversion is exact by definition, which is different from calibration (D7), which corrects device error. |
| D7 | **There are two kinds of calibration, and two ways of pushing configuration.** **ChannelCalibration** is brain-side. The brain uses it in its own arithmetic (pump flow curve, sensor offset), so it supports a small fixed set of *models* (linear, polynomial, piecewise-linear table). That is code written once per model, never per device. **DeviceCalibration** is device-side and opaque to the brain. It is described by the driver's schema, so the UI renders a generic form, and it is pushed with a Command. Device-side calibration comes in two forms: `replayable` (data, resent on every connection) and `procedure` (a one-shot action performed by a human in the right physical context, never replayed). | No code per device type in the brain. Atlas EZO calibration is a procedure: `Cal,mid,7.00` means "the probe is in pH 7 buffer *right now*." Replaying it with the probe in the reservoir would corrupt the calibration. Today's code ([AtlasI2C.py](Sensors/services/AtlasI2C.py)) only knows that `CAL` needs a longer timeout, so calibration was done by hand on the device. |
| D8 | **Limits have two layers.** A **PhysicalLimit** protects hardware. The brain models and pushes it, and the controller is the final barrier. A **PolicyLimit** is a brain-only cap on what the brain issues. | The controller's limits are about physical safety, nothing less and nothing more. Policies (e.g. mL per day) are the brain's business. |
| D9 | **Dose and Command are separate.** | A Dose is logical ("5 mL of A"), a Command is physical ("pump P: 4.2 s at 50%"), and calibration translates between them (7.5). The brain may split one dose into several commands. Manual activation is normally a Dose, with raw Commands behind an "advanced" menu. |
| D10 | **One Originator covers User and Decision.** | Manual and automatic commands follow the same path: bounded, confirmed, traced (7.9). |
| D11 | **`readNow` is a Command.** Periodic reporting stays the baseline. | A loop that has waited 15 min for mixing should decide on a fresh reading, not one from 2 min ago. Users may also request one. |
| D12 | **Store connection transitions, not heartbeats.** | They cost almost nothing and are what traceability needs. Current state is derived from the latest event. |
| D13 | **Loops have ports and an Arbitrator.** In v3: a dropdown with two loop types (EC → A/B; EC + pH → A/B/pH±), one loop per system, and a trivial arbitrator. | This leaves room for multiple loops and arbitration strategies later without changing the model. |
| D14 | **Calibrations are versioned, and readings record the versions in effect.** | Old readings can be recomputed under a new calibration if someone wants that, or kept as they are. Raw values are always kept. |
| D15 | **Maintenance sessions have a mandatory planned end.** | If the holder disappears and no admin is around, maintenance still ends eventually. |
| D16 | **Permissions are per system, with groups for shared baselines.** | Botanists can own their systems. Groups avoid assigning everyone one at a time. |

---

## 4. Modeled but not in v3

- **Site**: needed once one sensor serves several systems (a warehouse thermometer). In v3, ambient sensors bind to their HydroponicSystem.
- **Recipe, GrowthStage, RecipeApplication**: v3 has static Targets and hand-picked loop parameters.
- **Dynamic Targets**: a target as a function of growth stage or of other readings ("if it's cold, …").
- **Multiple loops per system with real arbitration.**
- **Water level management**: an IR level sensor plus a refill valve. These are just a new MeasureChannel and ActuationChannel bound to a Reservoir, with no model change.
- **Lights, fans and heaters**: ActuationChannels bound to a HydroponicSystem or Site rather than a Reservoir.
- **Camera as a device**: a MeasureChannel with a `bytes` value type (vision 9.3).
- **Guided calibration procedures** in the UI. In v3, users run the procedure and enter the results.
- **Finer-grained subscriptions** (per channel, per controller).

---

## 5. Controller-side safety concerns

These come from view D and don't appear in the brain's model.

1. **A reboot erases the controller's memory.** After a restart, `seenIds` and the duty window are gone. A crash loop could then bypass the 60 s/h cap or run a duplicate command. Options: persist them (ESP32 RTC memory survives soft resets but not power loss), or treat the duty window as full at boot. The command **deadline** is the real backstop against duplicates, which is why a trustworthy clock matters (see open question 1).
2. **The stop must not depend on the code that started the actuation.** On the Pi, a killed process leaves GPIO pins as they were. That is exactly Annex A of the vision. Use a hardware timer or watchdog, wiring that fails safe (normally-open relays), and pins that default to off at boot.
3. **OutboundQueue** covers brain restarts (vision 8.3). An MQTT persistent session would provide most of it.

---

## 6. Triage of the original candidate list

| Candidate(s) | Outcome |
| --- | --- |
| HydroponicSystem = Prototype | **HydroponicSystem** |
| Reservoir | **Reservoir** |
| HydroponicParameter, PhysicalQuantity | **Quantity** (+ **Unit**) |
| Temperature, PhLevel, EC, NutrientConcentration, ConcentrationN/K/P | *Instances* of Quantity, not classes |
| HydroponicParameterTarget | **Target** |
| Device, Sensor, Actuator, Pump | **Device** + **MeasureChannel** / **ActuationChannel**. "Pump" is a DeviceType, not a class. |
| DeviceType, DeviceInterface, StandardOperation | Merged into **DeviceType** (driver descriptor) + **ChannelSpec** |
| DeviceDriver, StandardOperationImplementation | **Driver** in the controller-side model (view D) |
| Address, Pin | `Wiring.locator` |
| DeviceIdentifier, CommandIdentifier | `uid` / `id` attributes |
| PhysicalOwnership | **Wiring** |
| LogicalOwnership | Channel → Subject binding + **PortBinding** |
| Hardware = ElectronicMaterial, Microcontroller, ControllerHardware, AquaBrainHost | Dropped: the brain only knows **Controller** |
| Reading = Measure = InboundValue | **Reading** |
| Calibration, CalibrationCommand | **ChannelCalibration**, **DeviceCalibration**; pushed by a Command of kind `configure` or `procedure` |
| Command = OutgoingCommand, Activation | **Command** (Activation = kind `actuate`) |
| CommandStatus (+ Complete / Error / Unknown) | `Command.status` |
| ActivationError | `CommandReport.reason` |
| Dose, Volume | **Dose**, with `volume` as an attribute |
| NutrimentSolution, PhSolution | **Solution** |
| MixingTime | ControlLoop parameter |
| ActivationPeriod, ActivationLimit = ActivationBound, AbsoluteActivationTimeLimit, HardwareOperationalLimit, PumpActivationIntensityBounds | **PhysicalLimit** (enforced by the controller) and DeviceType capabilities (declared by the driver) |
| PumpActivationIntensity | `Command.params` |
| ActuatorConfiguration | Split into PhysicalLimit, calibration, bindings and ControlLoop |
| ControlLoop | **ControlLoop** (+ **ControlLoopType**, **PortBinding**, **Arbitrator**) |
| ControlLoopStatus (+ Dosing / Mixing / Measuring / Deciding) | `ControlLoop.state` |
| Decision | **Decision** |
| ActivationHistory, ReadingsHistory, EventHistory | Dropped: derived (Readings, Commands, Decisions, ConnectionEvents ordered by time) |
| Controller | **Controller** |
| HydroponicSystemStatus | Derived from the active **MaintenanceSession** and loop states |
| Maintainer, MaintenanceSession | **MaintenanceSession** held by a User |
| Alert | **Alert** (+ **AlertRule**, **Subscription**) |
| User, Operator = Grower, SystemAdministrator, HardwareIntegrator, Botanist = Researcher | **User**, **Group**, **Membership.role**. The rest are use-case actors. |
| Plant | `post-v3`, through Recipe |
| Water | Dropped. Its relevant fact is `Reservoir.nominalVolume`. |

New concepts that came out of the questions: Subject, Site, Wiring, ChannelSpec, Channel, Unit, ReadingFilter, PolicyLimit, PortBinding, Arbitrator, Recipe, GrowthStage, Originator, CommandReport, ConnectionEvent, Discrepancy, Group, Membership, Subscription, AlertRule.

---

## 7. Open questions

1. **Clock and deadlines.** Deduplicating commands across a controller reboot relies on deadlines, and deadlines rely on a shared clock. Is "the controller adopts the brain's time at every connection" enough, or does the microcontroller spec need an RTC or NTP?
2. **Command supersession.** When the brain has an `unknown` command and wants to issue a new one on the same channel, does the new one cancel the old one? Should the controller run only one actuation per channel at a time, refusing or queueing the rest?
3. **EZO calibration export.** Does the firmware on our EZO units support `Export`/`Import`? If so, that blob is a safe `replayable` DeviceCalibration; otherwise EZO calibration is `procedure` only.
4. **Corrected readings.** When a ReadingFilter "corrects" a value, is the corrected value stored as `value` (with `rawValue` kept), or as a separate derived reading?
5. **Rebinding a channel to a different Subject.** Should the brain automatically pause loops bound to that channel until someone confirms?
6. **Decision granularity.** Is a Decision recorded for every evaluation (including "do nothing"), or only when something happens? Recording every one is the most traceable, but it is high volume at short evaluation periods.
