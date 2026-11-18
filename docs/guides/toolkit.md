---
title: "Toolkit: commands, snapshot and code"
version: 0.1.0
date: 2026-11-18
---

# Toolkit: commands, snapshot and code

> **Version 0.1.0 · draft · 2026-11-18** · class/guides/toolkit.md

The reference every lab uses. Every file here is also on [Downloads](../downloads.md).

## T.1 The read-only command cheat sheet

[`aos-show-cheatsheet.txt`](../downloads/aos-show-cheatsheet.txt): every command used in the labs. Each one only **shows**
something.

## T.2 Reading a snapshot

Before class, the pipeline saved one text file per command plus an index, `snapshot.json`:

```json
{ "schemaVersion": "1.0", "taken": "2026-11-18T14:00:00Z",
  "commands": [ { "cmd": "show virtual-chassis topology", "file": "virtual-chassis_topology.txt", "bytes": 512 } ],
  "failed": [] }
```

`failed: []` means every command answered. Account lines, SNMP communities and keys are replaced with `<redacted>` before anything
is saved.

## T.3 The read-only client: `aos_readonly.py`

[`aos_readonly.py`](../downloads/aos_readonly.py) is the exact program the lab uses to read the live switch. It can do one thing:
sign in, run commands from a fixed **allow-list** of `show` commands, sign out. It refuses everything else before anything is sent:

```bash
python3 aos_readonly.py selftest                  # offline: proves the allow-list refuses config and the redaction holds
python3 aos_readonly.py probe    --host <switch> --user <read-only user> --password-file <file>
python3 aos_readonly.py snapshot --host <switch> --user <read-only user> --password-file <file> --out ./snapshot
```

It talks to the switch's **AOS Web Services REST API**: `GET /auth/?username=…&password=…` to sign in, then
`GET /?domain=cli&cmd=<show …>` with the header `Accept: application/vnd.alcatellucentaos+json`.

## T.4 The desired state: `vc-pair.example.yml`

[`vc-pair.example.yml`](../downloads/vc-pair.example.yml): an HA pair declared as data (system, DNS, NTP, VLANs, server bonds,
and the checks that must pass after every run), in the same shape the lab's network pipeline uses. Example values only.

## T.5 The pipeline: `fabric-as-code.example.yml`

[`fabric-as-code.example.yml`](../downloads/fabric-as-code.example.yml): a GitHub Actions workflow that **plans** on every push,
**applies** only when a person dispatches it (behind an approval), and **plans for drift** every morning.
