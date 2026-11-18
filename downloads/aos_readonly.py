#!/usr/bin/env python3
"""aos_readonly — the ONLY code in demo-0007 that talks to an OmniSwitch it does not own
(the production fabric: host, account and owner live in ansible/targets.yml, never here).

It can do exactly one thing: log in, run `show` commands from a fixed ALLOW-LIST, log out. It has no way to send a
config line, by construction:
  * every command must match ALLOW exactly (no free text, no `|`, no `;`, no newline);
  * it only calls `/auth/` (login/logout) and `/?domain=cli&cmd=<allowed show>`; never `domain=mib`;
  * a minimum interval between calls (default 1 s) and ONE session per run, always logged out (finally:).

The API is the AOS Web Services REST API, the same calls the lab network team's Ansible makes (proven live
2026-11-17): GET /auth/?username=&password= then GET /?domain=cli&cmd=..., Accept
application/vnd.alcatellucentaos+json, answer {"result": {"diag": 200, "output": "..."}}.

Output is REDACTED before it is written (user lines, SNMP communities, keys, hashes) because the snapshot is
shown in class (a private run artifact, never put on the public site).

Usage:
  aos_readonly.py snapshot --host 192.0.2.10 --user readonly --password-file F --out DIR [--commands default]
  aos_readonly.py probe    --host 192.0.2.10 --user readonly --password-file F     # login + one show + logout
  aos_readonly.py selftest                                                      # offline: allow-list + redaction
"""
import argparse
import http.cookiejar
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ACCEPT = "application/vnd.alcatellucentaos+json"

# The allow-list. Adding a command is a reviewed change (docs/iac-fabric-management.md §3 is the same table).
ALLOW = (
    "show system",
    "show chassis",
    "show hardware-info",
    "show running-directory",
    "show configuration status",
    "show virtual-chassis topology",
    "show virtual-chassis vf-link",
    "show virtual-chassis consistency",
    "show virtual-chassis auto-vf-link-port",
    "show linkagg",
    "show linkagg port",
    "show vlan",
    "show interfaces status",
    "show interfaces counters",
    "show interfaces counters errors",
    "show fan",
    "show temperature",
    "show power-supply",
    "show ntp status",
    "show ip interface",
    "show auto-fabric config",
    "show lldp remote-system",
    "show microcode",
)
# `show interfaces <port>` for a single port, e.g. 1/1/1. Nothing else is parameterised.
ALLOW_RE = (re.compile(r"^show interfaces [12]/1/([1-9]|[1-4][0-9]|5[0-6])$"),)

DEFAULT_SNAPSHOT = [c for c in ALLOW if c not in ("show lldp remote-system", "show interfaces counters errors")]

REDACT = [
    (re.compile(r"(?im)^(\s*user\s+\S+).*$"), r"\1 <redacted>"),
    (re.compile(r"(?im)^(\s*snmp\s+community\S*).*$"), r"\1 <redacted>"),
    (re.compile(r"(?i)(community\s+)\S+"), r"\1<redacted>"),
    (re.compile(r"(?i)((?:password|passwd|secret|key|hash)\s*[:=]?\s+)\S+"), r"\1<redacted>"),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "<redacted-hex>"),
]


class Refused(Exception):
    pass


def allowed(cmd):
    if not isinstance(cmd, str) or any(ch in cmd for ch in "|;&\n\r`$") or cmd != cmd.strip():
        return False
    return cmd in ALLOW or any(r.match(cmd) for r in ALLOW_RE)


def redact(text):
    for rx, sub in REDACT:
        text = rx.sub(sub, text)
    return text


class Session(object):
    def __init__(self, host, user, password, timeout=60, min_interval=1.0, validate_certs=False):
        self.base = "https://%s" % host
        self.timeout = timeout
        self.min_interval = min_interval
        self._last = 0.0
        ctx = ssl.create_default_context()
        if not validate_certs:   # the OmniSwitch EMP serves a factory self-signed cert (no name, no CA)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        r = self._get("/auth/", {"username": user, "password": password})
        if r.get("diag") != 200:
            raise Refused("login refused (diag %s)" % r.get("diag"))   # never echo the error body: it can quote input

    def _get(self, path, params):
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()
        url = "%s%s?%s" % (self.base, path, urllib.parse.urlencode(params))
        req = urllib.request.Request(url, headers={"Accept": ACCEPT})
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
        try:
            return json.loads(body)["result"]
        except (ValueError, KeyError):
            raise Refused("not an AOS Web Services answer")

    def show(self, cmd):
        if not allowed(cmd):
            raise Refused("not on the read-only allow-list: %r" % cmd)
        r = self._get("/", {"domain": "cli", "cmd": cmd})
        if r.get("diag") != 200:
            raise Refused("%s -> diag %s" % (cmd, r.get("diag")))
        return r.get("output", "")

    def logout(self):
        try:
            self._get("/auth/", {})
        except Exception:
            pass


def read_password(path):
    with open(path) as f:
        pw = f.read().rstrip("\n")
    if not pw:
        raise Refused("empty password file")
    return pw


def cmd_probe(a):
    s = Session(a.host, a.user, read_password(a.password_file), min_interval=a.min_interval)
    try:
        out = s.show("show virtual-chassis topology")
    finally:
        s.logout()
    ok = re.search(r"(?m)^\s*1\s+Master\s+Running", out) and re.search(r"(?m)^\s*2\s+Slave\s+Running", out)
    print("probe: login ok, VC topology %s" % ("2 chassis Running" if ok else "NOT as expected"))
    return 0 if ok else 3


def cmd_snapshot(a):
    cmds = DEFAULT_SNAPSHOT if a.commands == "default" else [c.strip() for c in a.commands.split(",") if c.strip()]
    bad = [c for c in cmds if not allowed(c)]
    if bad:
        raise Refused("not on the allow-list: %s" % bad)
    os.makedirs(a.out, exist_ok=True)
    s = Session(a.host, a.user, read_password(a.password_file), min_interval=a.min_interval)
    index, failed = [], []
    try:
        for c in cmds:
            name = c.replace("show ", "").replace(" ", "_").replace("/", "-") + ".txt"
            try:
                text = redact(s.show(c))
            except Refused as e:
                failed.append({"cmd": c, "error": str(e)})
                continue
            with open(os.path.join(a.out, name), "w") as f:
                f.write(text)
            index.append({"cmd": c, "file": name, "bytes": len(text)})
    finally:
        s.logout()
    meta = {"schemaVersion": "1.0", "host": a.host, "user": a.user, "taken": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "commands": index, "failed": failed}
    with open(os.path.join(a.out, "snapshot.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("snapshot: %d captured, %d failed -> %s" % (len(index), len(failed), a.out))
    return 0 if not failed else 4


def cmd_selftest(_a):
    must_pass = ["show virtual-chassis topology", "show linkagg port", "show interfaces 1/1/1", "show interfaces 2/1/56"]
    must_fail = ["vlan 50 admin-state enable", "show vlan | grep x", "show vlan; write memory", "write memory flash-synchro",
                 "no linkagg lacp agg 1", "show interfaces 3/1/1", "show interfaces 1/1/57", " show vlan", "show vlan\nreload all",
                 "copy running certified", "user readonly password x read-write all", "show configuration snapshot"]
    errs = [c for c in must_pass if not allowed(c)] + ["ALLOWED: %r" % c for c in must_fail if allowed(c)]
    sample = ("user readonly password-expiration disable read-only all\nsnmp community-map hash-key ABCDEF0123456789ABCDEF0123456789 "
              "user x\nsnmp community-map public user x on\n  1   Master   Running\n")
    r = redact(sample)
    if "ABCDEF0123456789ABCDEF0123456789" in r or "read-only all" in r or "public" in r:
        errs.append("redaction leaked: %r" % r)
    if "Master   Running" not in r:
        errs.append("redaction ate a VC line")
    for e in errs:
        print("::error::%s" % e)
    print("selftest: %s (%d allowed, %d refused)" % ("FAIL" if errs else "ok", len(must_pass), len(must_fail)))
    return 1 if errs else 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="mode", required=True)
    for m in ("probe", "snapshot"):
        sp = sub.add_parser(m)
        sp.add_argument("--host", required=True)
        sp.add_argument("--user", required=True)
        sp.add_argument("--password-file", required=True)
        sp.add_argument("--min-interval", type=float, default=1.0)
        if m == "snapshot":
            sp.add_argument("--out", required=True)
            sp.add_argument("--commands", default="default")
    sub.add_parser("selftest")
    a = p.parse_args()
    try:
        return {"probe": cmd_probe, "snapshot": cmd_snapshot, "selftest": cmd_selftest}[a.mode](a)
    except Refused as e:
        print("::error::%s" % e, file=sys.stderr)
        return 2
    except (urllib.error.URLError, OSError) as e:
        print("::error::unreachable: %s" % e.__class__.__name__, file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
