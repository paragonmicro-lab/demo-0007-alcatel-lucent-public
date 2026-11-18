---
title: "Lab 2: Build it by hand, then as code"
version: 0.2.0
date: 2026-11-18
---

# Lab 2: Build it by hand, then as code

> **Version 0.2.0 · draft · 2026-11-18** · class/guides/02-ui-versus-code.md

## What you will learn

Each step of building an HA pair, done two ways: typed at the console or clicked in the web UI (WebView), and declared once as code
that a pipeline applies and checks. You will see why the lab uses the second.

**Time:** 40 minutes · **Before you start:** [Lab 1](01-tour-the-fabric.md) done

## How the lab is set up for this lab

**Sandbox pair *(coming soon)*:** you do each step by hand, then the instructor applies the same steps as code. **Until then:** the
instructor walks the steps on screen, and [Lab S](setup-how-the-lab-is-built.md) has every command, the code, and ALE's documentation.

<!-- 🎬 video slot 02-ui-versus-code: each step at the console, then the same step in code, then the plan -->
<video controls preload="metadata" playsinline width="100%" poster="img/02-ui-versus-code.jpg">
  <source src="img/02-ui-versus-code.mp4" type="video/mp4">Your browser does not play this video.
</video>
<sub>🎬 *Lab 2: build it by hand, then as code. Watch it, then follow the same steps below.*</sub>

---

## 2.1 The steps, side by side

| Step | By hand (console or WebView) | As code (declared once, applied by a pipeline) | Lab S |
|---|---|---|---|
| Factory safety | disable Auto-Fabric and the cloud agent | a check after every run: `Auto-fabric Status : Disable` | [S.1](setup-how-the-lab-is-built.md#s1-factory-state-and-the-day-0-rule) |
| Chassis identity + master | `configured-chassis-id 2` on the second box; priorities 200 / 100 | written once, applied by a logged bootstrap | [S.2](setup-how-the-lab-is-built.md#s2-form-the-virtual-chassis) |
| Stack links | `virtual-chassis auto-vf-link-port 1/1/55` and `…/56` | checks: both chassis *Running*, both VFLs *Up* | [S.2](setup-how-the-lab-is-built.md#s2-form-the-virtual-chassis) |
| Management | per-chassis + VC-wide addresses | the same values in one file | [S.3](setup-how-the-lab-is-built.md#s3-management-plane) |
| Accounts | `user … read-only all` | passwords in a vault, never in code | [S.4](setup-how-the-lab-is-built.md#s4-accounts-and-rbac) |
| VLANs | `vlan 50 admin-state enable name "…"` | `vlans: {50: …}` | [S.5](setup-how-the-lab-is-built.md#s5-vlans) |
| Server bonds | `linkagg lacp agg 1 size 2 …` + one port per chassis | `{ id: 1, ports: [1/1/1, 2/1/1] }` | [S.6](setup-how-the-lab-is-built.md#s6-lacp-across-both-chassis) |
| Save | `write memory flash-synchro` | saved **only after** a read-back proves every line | [S.7](setup-how-the-lab-is-built.md#s7-save-certify-roll-back) |

## 2.2 Three things to notice

1. **The code is shorter than the typing.** One line declares a bond; the pipeline works out the commands.
2. **The code checks itself.** On this fabric's first run, the read-back found a mismatch (the switch prints `vlan 70-72`, the code
   listed 70, 71, 72) and **saved nothing**. The fix went into the code, not onto the switch.
3. **The switch refused some commands** (a bond number above 127). The fix was to renumber the bonds in the code, once.

!!! success "Done when"
    You can explain why "saved only after the read-back" matters more than how quickly a change was made.

## Thank you

The sample declaration and the read-only client are in the [Toolkit](toolkit.md). ALE: [OmniSwitch 6900](https://www.al-enterprise.com/en/products/switches/omniswitch-6900).

## Bonus

In [`vc-pair.example.yml`](../downloads/vc-pair.example.yml), add a third server bond. Which two ports do you choose, and why?
