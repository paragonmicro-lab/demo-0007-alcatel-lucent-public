---
title: "Lab 4: OmniVista Cirrus, the SaaS view (coming soon)"
version: 0.2.0
date: 2026-11-18
---

# Lab 4: OmniVista Cirrus, the SaaS view *(coming soon)*

> **Version 0.2.0 · draft · 2026-11-18** · class/guides/04-omnivista-cirrus.md

!!! warning "Not available yet"
    This lab is being built. Your instructor will tell you if it is part of your class.

## What you will learn

How the same switches look through **OmniVista Cirrus**, ALE's cloud network management service. You sign in with your class
Microsoft account and get the **Viewer** role: you can see everything and change nothing.

**Time:** 20 minutes · **Before you start:** [Lab 3](03-fabric-as-code.md) done

## How the lab is set up for this lab

Your class group in Microsoft Entra maps to a Cirrus role at sign-in (single sign-on, SAML). Nobody hands out a Cirrus password.
The switches connect out to Cirrus through their own cloud agent. [Lab diagram](lab-diagram.md).

<!-- 🎬 video slot 04-omnivista-cirrus: sign in with Microsoft, inventory, topology, health, a refused change -->
<video controls preload="metadata" playsinline width="100%" poster="img/04-omnivista-cirrus.jpg">
  <source src="img/04-omnivista-cirrus.mp4" type="video/mp4">Your browser does not play this video.
</video>
<sub>🎬 *Lab 4: OmniVista Cirrus. Watch it, then follow the same steps below.*</sub>

---

## 4.1 Sign in with Microsoft

## 4.2 Inventory and topology

The two chassis, their links, and the devices behind them.

## 4.3 Health

Alarms, interface usage, hardware state.

## 4.4 Read-only means read-only

Try a change and see it refused.

!!! success "Done when"
    You have signed in, found both chassis, and seen a change refused.

## Thank you

OmniVista Cirrus: [getting started](https://docs.ovcirrus.com/ov/getting-started) ·
[single sign-on settings](https://docs.ovcirrus.com/ov/single-sign-on-settings) · [API quick start](https://docs.ovcirrus.com/ov/quick-start-guide).
