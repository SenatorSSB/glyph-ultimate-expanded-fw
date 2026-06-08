# Phase 6 To Phase 7 Implementation Slice Plan

Status: SLICE_PLAN_DESIGN_ONLY_NOT_IMPLEMENTED.

## Purpose

This plan defines future implementation slices after Phase 6. It is not an
approval to implement them.

Every firmware behavior slice requires explicit product approval, build
verification, hardware plan, and recorded hardware result before validation
claims.

## Slice 7A - Firmware Parser For Compiled/Test Payload Only

Allowed files/classes:

- future firmware parser source and tests only after approval;
- test fixture payload compiled into a test-only path if source-backed;
- docs/calibration hardware plan/result packets.

Forbidden scope:

- no storage;
- no device write;
- no WebSerial;
- no production export;
- no hidden writes;
- no runtime-config storage reads.

Build requirement:

- firmware build required before merge.

Hardware plan/result requirement:

- required before claiming parser behavior or fallback behavior.

Stop conditions:

- parser format not source-backed;
- memory/size risk unresolved;
- invalid payload does not fail closed;
- any config attempts to own evaluator priority or timing behavior.

Rollback/fallback expectation:

- invalid compiled/test payload falls back to source-owned baseline.

## Slice 7B - Storage Read-Only Candidate Load

Allowed files/classes:

- future storage read path only after approval;
- parser integration from Slice 7A;
- boot/load entry point selected by source audit;
- docs/calibration hardware plan/result packets.

Forbidden scope:

- no storage write path;
- no WebSerial/device write;
- no auto-delete;
- no auto-rewrite;
- no hidden recovery write.

Build requirement:

- firmware build required before merge.

Hardware plan/result requirement:

- required for missing storage, corrupt storage, invalid candidate, and valid
  candidate if implemented.

Stop conditions:

- storage ownership unclear;
- boot/load entry point unclear;
- fallback changes are not deterministic;
- runtime config can cross mode scope.

Rollback/fallback expectation:

- missing or invalid storage preserves source-owned baseline.

## Slice 7C - Storage Write Path Only If Source-Backed And Approved

Allowed files/classes:

- future non-WebSerial local debug/test route only if source-backed and
  explicitly approved;
- validation-before-write tooling;
- readback if source-backed;
- docs/calibration hardware plan/result packets.

Forbidden scope:

- no WebSerial public write path;
- no hidden write;
- no production export;
- no flashing automation;
- no config-owned storage policy.

Build requirement:

- firmware build required before merge.

Hardware plan/result requirement:

- required for explicit user action, no hidden write, readback if implemented,
  invalid write rejection, and baseline preservation.

Stop conditions:

- write route lacks source authority;
- readback/recovery policy is absent;
- write can happen without explicit operator action.

Rollback/fallback expectation:

- failed writes must preserve previously active source-owned or valid stored
  baseline; recovery mutation requires separate approval.

## Slice 8A - WebSerial/Device Write Only After Authority/Safety Gates

Allowed files/classes:

- future WebSerial/device-write implementation only after source authority,
  product approval, and safety review;
- validation-before-write and readback flow if source-backed;
- docs/calibration hardware plan/result packets.

Forbidden scope:

- no hidden device write;
- no write without validation;
- no write without user-visible action;
- no official compatibility claim from partial evidence;
- no flashing automation.

Build requirement:

- firmware and host/tooling build or type checks as applicable.

Hardware plan/result requirement:

- required for write, readback if implemented, invalid rejection, fallback,
  recovery, and baseline preservation.

Stop conditions:

- transport authority remains missing;
- rollback/recovery gate is absent;
- safety review not complete;
- official configurator compatibility is inferred.

Rollback/fallback expectation:

- write path must have explicit recovery and baseline preservation behavior.

## Slice 8B - Public Write Workflow Packaging

Allowed files/classes:

- release docs/checklists only after Slice 8A hardware validation;
- packaging docs for a validated manual/public write workflow;
- result packets with exact scope.

Forbidden scope:

- no public release claim before result exists;
- no official compatibility claim unless proven;
- no nunchuk validation claim unless separately tested;
- no flashing automation unless separately approved and validated.

Build requirement:

- all relevant firmware/tooling checks from implementation branches.

Hardware plan/result requirement:

- required before public workflow validation claims.

Stop conditions:

- missing hardware result;
- missing rollback/recovery evidence;
- exact app/version/source route unknown if official compatibility is claimed.

Rollback/fallback expectation:

- public workflow must document recovery and rollback route before release
  claims.

## Global Non-Claims

- Runtime-loaded config is not implemented by this plan.
- Runtime-config storage is not implemented by this plan.
- Firmware parser is not implemented by this plan.
- Device write / WebSerial is not implemented by this plan.
- Firmware flashing automation is not implemented by this plan.
