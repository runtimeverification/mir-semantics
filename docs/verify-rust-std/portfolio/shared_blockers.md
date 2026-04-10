# Shared Blockers

This file tracks blocker families that affect multiple verify-rust-std
challenges. The leader challenge should carry the smallest reproducer and the
first semantic-fix attempt; follower challenges should validate the same fix on
their own proof harnesses before any broader rollout.

## Allocator-Body `malloc/noBody`

- Class: `MIR_SEMANTICS`
- Leader: `0026-rc`
- Followers: `0027-arc`
- Current frontier:
  `#setUpCalleeData(monoItemFn(... name: symbol("malloc"), body: noBody), ...)`
- Current status:
  a transparent-wrapper transmute rule moved both families past the earlier
  helper-level `CastKind::Transmute` leaf; the next step is allocator-body call
  handling.

## `NonZero` Niche Cast

- Class: `UNKNOWN`
- Leader: `0012-nonzero`
- Followers: none yet
- Current frontier:
  exact `u8 -> Option<NonZeroU8>` `castKindTransmute`
- Current status:
  generic same-size transmute support is already green via the transparent
  wrapper control, so the remaining gap is specific to the niche enum shape.

## Donor-Link Root-Name Preservation

- Class: `MIR_SEMANTICS`
- Leader: `0013-cstr`
- Followers: none yet
- Current frontier:
  donor-linked bodies qualify root item names before `make_call_config`
  resolves the original unqualified start symbols
- Current status:
  body supply is technically feasible, but proof setup fails before the donor
  body can execute.

## `AllocRef` Dereference In Probe Path

- Class: `MIR_SEMANTICS`
- Leader: `0028-flt2dec`
- Followers: none yet
- Current frontier:
  `#traverseProjection(toLocal(2), AllocRef(...), projectionElemDeref ...)`
- Current status:
  the probe has advanced past the old thunked unsize-cast leaf, but it still
  stops in library/projection scaffolding rather than formatter-owned logic.
