---
title: "Lab S: How this lab was built"
version: 0.1.0
date: 2026-11-18
---

# Lab S: How this lab was built

> **Version 0.1.0 · draft · 2026-11-18** · class/guides/setup-how-the-lab-is-built.md

## What you will learn

Every step of building an HA OmniSwitch Virtual Chassis, in the order it is built. For each one: **what** was built, how to
**check** it (read-only), how to do it **by hand** at the console or in WebView, how it is written **as code**, and where ALE
documents it. Read it alongside Labs 1-3. The labs show the result; this page is how you would build it yourself.

## How the lab is set up

| Built by | What |
|---|---|
| a one-time **console bootstrap** (logged, every command kept) | factory reset, chassis identity, stack links, management addresses, accounts |
| the lab's **network pipeline** (plan / apply / read back / daily drift) | everything else: system, DNS, NTP, syslog, VLANs, server bonds, checks |
| **this demo's pipeline** | nothing on the live switch: one read-only sign-in and a fixed list of `show` commands (the snapshot) |
| **you** | read the snapshot; on the sandbox pair *(coming soon)*, build it yourself |

The values below are the **sandbox example** values. The live fabric uses its own, in the lab's network repository.
**[verify]** marks a WebView path or keyword not yet walked on the sandbox. [Lab diagram](lab-diagram.md).

<!-- 🎬 video slot setup-how-the-lab-is-built: the bootstrap log, then the code, step by step -->
<video controls preload="metadata" playsinline width="100%" poster="img/setup-how-the-lab-is-built.jpg">
  <source src="img/setup-how-the-lab-is-built.mp4" type="video/mp4">Your browser does not play this video.
</video>
<sub>🎬 *Lab S: how this lab was built. Watch it alongside the sections below.*</sub>

---

## S.1 Factory state and the day-0 rule

**What was built:** a factory switch that pulls **nothing** from the network or the cloud.

**Check:** `show auto-fabric config` → `Auto-fabric Status : Disable`.

**By hand (console, 115200 8N1):**

```text
show chassis
show running-directory
auto-fabric admin-state disable          [verify keyword on your release]
cloud-agent admin-state disable
```

**As code:** a check that runs after **every** pipeline run, so a re-enabled Auto-Fabric turns the run red.

**Why:** zero-touch is a feature, and in a lab whose source of truth is git it is also a risk. A new box must not configure itself from the LAN.

## S.2 Form the Virtual Chassis

**What was built:** two chassis, one logical switch. Chassis 1 is the preferred master, and two 100G stack links (VFL) join them.

**Check:** `show virtual-chassis topology` (1 Master Running, 2 Slave Running), `show virtual-chassis vf-link` (both Up),
`show virtual-chassis consistency` (OK, OK).

**By hand (each chassis, stack cables UNPLUGGED):**

```text
! second chassis only (both ship as chassis 1, so this is the critical line)
virtual-chassis chassis-id 1 configured-chassis-id 2
! preferred master
virtual-chassis chassis-id 1 configured-chassis-priority 200      ! 100 on the second chassis
virtual-chassis auto-vf-link-port 1/1/55
virtual-chassis auto-vf-link-port 1/1/56
! remove any other factory auto-VFL candidate port, so a spare QSFP cannot join the VC
write memory
```

Then cable 55↔55 and 56↔56, power on chassis 1 first, then chassis 2, then `write memory flash-synchro`.

**As code:** the read-back asserts in [`vc-pair.example.yml`](../downloads/vc-pair.example.yml) (`asserts:`).

**Lessons from the live build:** the keyword is `configured-chassis-priority`, not `configured-priority`. The two units formed the VC on
55-56 by themselves once the other candidate ports were removed. VC identity lives in `vcsetup.cfg`; everything else is in `vcboot.cfg`.

## S.3 Management plane

**What was built:** one address per chassis, plus a **VC-wide** address that follows whichever chassis is master. Automation always
targets the VC-wide one.

**Check:** `show ip interface`.

**By hand:**

```text
ip interface local chassis-id 1 emp address 192.0.2.7/24
ip interface local chassis-id 2 emp address 192.0.2.8/24
ip interface master emp address 192.0.2.9/24
ip service http admin-state enable
webview force-ssl enable                 [verify]
ip service telnet admin-state disable
ip service ftp admin-state disable
```

**Lesson:** a default route on the management port is refused (*"Default routes with gateway on EMP port not allowed"*). Use specific static routes.

## S.4 Accounts and RBAC

**What was built:** `admin` (break-glass), `automation` (the pipeline, with an SSH key), `readonly` (students and the SME), each with
its own password in a vault. No password is ever in code.

**Check:** `show user` (as an admin; this command is **not** in the class's read-only list).

**By hand:**

```text
user readonly password <from the vault> read-only all
```

**Lesson:** the password policy needs at least one digit and one non-alphanumeric character.

**Next:** sign-in with your Microsoft account through the lab's directory gateway (LDAPS), with your class group mapped to read-only.
*(Coming soon, proven on the sandbox first.)*

## S.5 VLANs

**Check:** `show vlan`.

**By hand:** WebView **Layer 2 → VLAN → Add** [verify], or `vlan 50 admin-state enable name "compute-50"`.

**As code:** `vlans:` in [`vc-pair.example.yml`](../downloads/vc-pair.example.yml).

**Lesson:** the switch prints ranges (`vlan 70-72 …`) and the code lists each VLAN. The first live apply's read-back caught that
mismatch and **saved nothing**.

## S.6 LACP across both chassis

**What was built:** each server bond has one port on each chassis, so a whole chassis can fail and every server keeps a link.

**Check:** `show linkagg`, `show linkagg port`.

**By hand:**

```text
linkagg lacp agg 1 size 2 admin-state disable name "server01-bond0" actor admin-key 1
linkagg lacp port 1/1/1 actor admin-key 1
linkagg lacp port 2/1/1 actor admin-key 1
vlan 50 members linkagg 1 tagged
linkagg lacp agg 1 admin-state enable
```

**As code:** `linkaggs:` in [`vc-pair.example.yml`](../downloads/vc-pair.example.yml).

**Lesson:** bond ids above 127 are refused on this model, so the lab renumbered its bonds in code, once.

## S.7 Save, certify, roll back

**Check:** `show running-directory`, `show configuration status`.

**By hand:** `write memory flash-synchro` (both chassis), `copy running certified`.

**As code:** saved **only after** the read-back passes, and only when the switch is running from WORKING (never over the rollback copy).

**Lesson:** `Running Configuration: SYNCHRONIZED` compares the two chassis, **not** running vs saved. `show configuration status` answers that.

## S.8 Drift, every day

**As code:** the daily plan goes red when the switch differs from the code. The next apply sends the one line, reads it back, saves,
and the re-plan says 0. See [Lab 3](03-fabric-as-code.md) and [`fabric-as-code.example.yml`](../downloads/fabric-as-code.example.yml).

## Thank you

ALE: [OmniSwitch 6900](https://www.al-enterprise.com/en/products/switches/omniswitch-6900) ·
[datasheet (PDF)](https://web-assets.al-enterprise.com/-/media/assets/internet/documents/omniswitch-6900-datasheet-en.pdf). Virtual
Chassis, AAA and the Web Services API are covered in the **AOS Release 8 Switch Management Guide** and Network Configuration Guide
(ALE Business Portal).
