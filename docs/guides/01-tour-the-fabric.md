---
title: "Lab 1: Tour a live HA fabric"
version: 0.2.0
date: 2026-11-18
---

# Lab 1: Tour a live HA fabric

> **Version 0.2.0 · draft · 2026-11-18** · class/guides/01-tour-the-fabric.md

## What you will learn

How to read the health of a two-chassis OmniSwitch **Virtual Chassis** (VC): which chassis is master, whether the stack links are
up, whether both chassis agree, and how servers attach to both. Then you work out what each failure would cost.

**Time:** 25 minutes · **Before you start:** [Lab 0](00-access-and-tools.md) done

## How the lab is set up for this lab

The live VC is two OmniSwitch 6900 chassis with two 100G stack links, carrying a working lab's servers and storage. Your
instructor shows this booking's snapshot. The outputs below are trimmed examples. [Lab diagram](lab-diagram.md).

<!-- 🎬 video slot 01-tour-the-fabric: the snapshot, command by command, with the diagram -->
<video controls preload="metadata" playsinline width="100%" poster="img/01-tour-the-fabric.jpg">
  <source src="img/01-tour-the-fabric.mp4" type="video/mp4">Your browser does not play this video.
</video>
<sub>🎬 *Lab 1: tour a live HA fabric. Watch it, then follow the same steps below.*</sub>

---

## 1.1 Who is in charge?

`show virtual-chassis topology`

```text
Chas  Role     Status
----+--------+---------
 1    Master   Running
 2    Slave    Running
```

One chassis is **master** (it runs the control plane). The other is **slave**, ready to take over. A configured **priority**
picks the master, so the result is the same after every reboot.

## 1.2 Are the stack links up?

`show virtual-chassis vf-link`. The **VFL** (virtual fabric link) joins the chassis: two 100G ports per chassis, bundled.
With one port down, the VC stays whole.

## 1.3 Do both chassis agree?

`show virtual-chassis consistency`: same software, same chassis group, same control VLAN. *Inconsistent* means the second
chassis will not join.

## 1.4 How do servers attach?

`show linkagg` and `show linkagg port`. Each server bond has **one port on chassis 1** (`1/1/x`) and **one on chassis 2**
(`2/1/x`), bundled with LACP. Port names are `chassis/slot/port`.

## 1.5 Is it saved, and can it roll back?

`show running-directory`: the switch runs from **WORKING**. **CERTIFIED** is the known-good copy it can roll back to.

!!! question "Think about it"
    The master chassis loses power. What happens to the servers' traffic, to the management address, and to the configuration?
    (The slave becomes master. Each server keeps its leg on the surviving chassis. The VC-wide management address follows the new master.)

!!! success "Done when"
    You can point at the master, the stack links and one server's two legs, and say what each failure would cost.

## Thank you

Alcatel-Lucent Enterprise: [OmniSwitch 6900](https://www.al-enterprise.com/en/products/switches/omniswitch-6900): Virtual Chassis
is described in the [datasheet (PDF)](https://web-assets.al-enterprise.com/-/media/assets/internet/documents/omniswitch-6900-datasheet-en.pdf).

## Bonus

Find a server bond in `show linkagg port` whose two legs are on **the same** chassis. (There should be none. Why would one be a problem?)
