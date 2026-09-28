# AI Factory Design Review Checklist

## Capacity
- [ ] demand and workload assumptions documented
- [ ] Installed/Design/Usable/Allocatable/Productive capacity separated
- [ ] power and thermal headroom defined
- [ ] growth envelope defined

## Facility
- [ ] A/B power and failure domains defined
- [ ] maintenance bypass path reviewed
- [ ] rack power density validated
- [ ] cooling flow / delta-T / pressure envelope validated
- [ ] floor loading and service path validated

## Compute
- [ ] GPU / CPU / NUMA topology documented
- [ ] NIC locality documented
- [ ] NVLink/NVSwitch domain documented
- [ ] firmware/driver compatibility matrix owned

## Fabric
- [ ] scale-out topology documented
- [ ] oversubscription assumptions explicit
- [ ] PFC/ECN/congestion policy reviewed where applicable
- [ ] NCCL test plan defined

## Runtime
- [ ] queue/quota/admission model defined
- [ ] gang/topology placement requirements defined
- [ ] training/inference SLOs defined
- [ ] storage/checkpoint/KV data paths reviewed

## Reliability
- [ ] failure domains enumerated
- [ ] observability covers sensor-to-workload path
- [ ] recovery objectives defined
- [ ] fault injection plan defined

## Acceptance
- [ ] test matrix has measurable thresholds
- [ ] real workload tests included
- [ ] evidence retention defined
- [ ] re-validation triggers defined
