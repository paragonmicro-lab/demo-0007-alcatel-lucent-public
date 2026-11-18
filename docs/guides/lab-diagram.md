---
title: "Lab diagram"
version: 0.1.0
date: 2026-11-18
---

# Lab diagram

> **Version 0.1.0 · draft · 2026-11-18** · class/guides/lab-diagram.md

```mermaid
flowchart TB
  subgraph LIVE["Live fabric: read-only in this class"]
    direction LR
    C1["OmniSwitch 6900<br/>chassis 1 (master)"] <== "VFL: 2 x 100G" ==> C2["OmniSwitch 6900<br/>chassis 2 (slave)"]
    SRV["servers, storage,<br/>firewall uplinks"] -- "LACP leg 1" --> C1
    SRV -- "LACP leg 2" --> C2
  end
  subgraph SBX["Sandbox pair (coming soon): yours to build"]
    direction LR
    S1["chassis 1"] <== "VFL" ==> S2["chassis 2"]
  end
  NETPIPE["Lab network pipeline<br/>plan · apply · read back · drift"] -- "the only writer" --> LIVE
  DEMOPIPE["This demo's pipeline<br/>read-only snapshot"] -. "show commands only" .-> LIVE
  DEMOPIPE -- "build · reset" --> SBX
  CIRRUS["OmniVista Cirrus (coming soon)<br/>Viewer via Microsoft sign-in"] -. "read-only view" .-> SBX
  YOU(["You"]) --> CIRRUS
  YOU -. "watch the instructor" .-> DEMOPIPE
```

| Box | Who may change it |
|---|---|
| Live fabric | only the lab's network pipeline, after review |
| Sandbox pair | this demo's pipeline, the instructor, and you during Lab 2 |
| OmniVista Cirrus | Viewer for you, Admin for the instructor |
