# Multiplayer Session Matrix

## Joint artifact identity
- Client/Web BUILD_ID and Web hash:
- Source hash / revision:
- Server instance ID / runtime record:
- Server code revision/hash:
- URL / LAN IP / port:
- Certificate fingerprint / browser trust state:
- Client A device/browser/identity:
- Client B device/browser/identity:
- Room/session identity:

## Contracted path
- Required synchronized rounds/session length:
- Authoritative state owner:
- Join/role rules:
- Normal turn/action propagation:
- Completion/settlement:

## Evidence layers
- Service alive on intended instance: PASS / FAIL / UNVERIFIED
- Client A normal path: PASS / FAIL / UNVERIFIED
- Client B normal path: PASS / FAIL / UNVERIFIED
- Two distinct identities: PASS / FAIL / UNVERIFIED
- Same room/session: PASS / FAIL / UNVERIFIED
- Cross-client state synchronization: PASS / FAIL / UNVERIFIED
- Required physical-device/LAN run: PASS / FAIL / UNVERIFIED / NOT_APPLICABLE

## Lifecycle cases

For each applicable case record pre-state -> event -> expected server state -> expected A -> expected B -> recovery -> actual evidence.

### Explicit leave

### Network loss / offline

### Refresh

### Tab/window close

### Reconnect

### Server restart

## Mixed surface input (if DOM + Godot canvas)
- Focus / blur:
- Required IME composition:
- Confirm / Enter behavior:
- Mobile keyboard (if targeted):
- DPR / resize alignment:

## Result
- Highest verified layer:
- Open failures / unverified claims:
- DONE / BLOCKED decision against the brief:
