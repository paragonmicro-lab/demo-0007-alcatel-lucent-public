---
title: "Lab 0: Access and tools"
version: 0.2.0
date: 2026-11-18
---

# Lab 0: Access and tools

> **Version 0.2.0 · draft · 2026-11-18** · class/guides/00-access-and-tools.md

## What you will learn

What you may touch in this class (nothing on the live switch), where everything is, and how to read an OmniSwitch command
line. Every later lab starts from here.

**Time:** 10 minutes · **You need:** a web browser

## How the lab is set up for this lab

Before class, a pipeline signed in to the live switch **read-only**, ran a fixed list of `show` commands, and saved the output as
this booking's **snapshot**. Your instructor shows it on screen. Nothing in this class changes the live switch.
[Lab diagram](lab-diagram.md).

<!-- 🎬 video slot 00-access-and-tools: the class site, the cheat sheet, how the instructor shows the snapshot -->
<video controls preload="metadata" playsinline width="100%" poster="img/00-access-and-tools.jpg">
  <source src="img/00-access-and-tools.mp4" type="video/mp4">Your browser does not play this video.
</video>
<sub>🎬 *Lab 0: access and tools: a walk-through of this page. Watch it, then do the same with the steps below.*</sub>

---

## 0.1 Know what you can and cannot touch

The switch in this class carries a working lab. You **read** it and never change it. When a step says *"run"*, it means
*"watch your instructor run"*, or read the output on the page.

## 0.2 Open the toolkit

Open the [Toolkit](toolkit.md) in a second tab. It has the read-only command cheat sheet and the code samples every lab uses.
The same files are on [Downloads](../downloads.md).

## 0.3 Learn to read a command line

```text
show virtual-chassis topology
^^^^ ^^^^^^^^^^^^^^^ ^^^^^^^^
verb feature         what about it
```

`show` only reads. Commands that change things (`vlan …`, `linkagg …`, `write memory`) appear in [Lab S](setup-how-the-lab-is-built.md)
and Lab 2 as **code that a pipeline sends**, never typed by hand on the live switch.

!!! success "Done when"
    You have the Toolkit open, and you can say which of these only reads: `show linkagg`, `write memory`, `vlan 50 admin-state enable`.

## Thank you

Alcatel-Lucent Enterprise: [OmniSwitch 6900](https://www.al-enterprise.com/en/products/switches/omniswitch-6900) ·
[datasheet (PDF)](https://web-assets.al-enterprise.com/-/media/assets/internet/documents/omniswitch-6900-datasheet-en.pdf).
