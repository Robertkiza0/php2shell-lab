#!/usr/bin/env python3
"""
PHP2Shell exposure checker (CVE-2026-109618 / CVE-2026-109619).

Passive check: reads the PHP version a site advertises and compares it
with the fixed releases. It sends ordinary GET requests only, no exploit.
Only run it against systems you own or have written permission to test.

Usage:
  python3 check_php2shell.py http://127.0.0.1:8081 http://127.0.0.1:8082
  python3 check_php2shell.py --local 8.3.35      # check a version string from `php -v`
"""
import re
import sys
import urllib.request

FIXED = {(8, 5): (8, 5, 12), (8, 4): (8, 4, 27), (8, 3): (8, 3, 36), (8, 2): (8, 2, 35)}
BACKPORT_ONLY = {(7, 4), (8, 0), (8, 1)}  # EOL; only minimal source backports exist


def parse(v):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", v or "")
    return tuple(int(x) for x in m.groups()) if m else None


def verdict(ver):
    if ver is None:
        return "UNKNOWN", "version not visible; check on the server with `php -v`"
    branch = ver[:2]
    if branch in FIXED:
        fix = FIXED[branch]
        if ver >= fix:
            return "PATCHED", f"at or above {'.'.join(map(str, fix))}"
        return "VULNERABLE", f"upgrade to {'.'.join(map(str, fix))} or later"
    if branch in BACKPORT_ONLY:
        return "LIKELY VULNERABLE", "end-of-life branch; needs vendor/source backport or upgrade to 8.2+"
    if ver < (5, 4, 0):
        return "OUT OF SCOPE", "older than 5.4, but end-of-life and unsafe anyway"
    return "VULNERABLE", "end-of-life branch with no fix; upgrade to a supported branch"


def fetch_version(url):
    req = urllib.request.Request(url, headers={"User-Agent": "php2shell-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            powered = r.headers.get("X-Powered-By", "")
    except urllib.error.HTTPError as e:
        powered = e.headers.get("X-Powered-By", "")
    except Exception as e:
        return None, f"error: {e}"
    return parse(powered), powered or "(no X-Powered-By header)"


def main(args):
    if not args:
        print(__doc__)
        return 1
    if args[0] == "--local":
        ver = parse(" ".join(args[1:]))
        status, note = verdict(ver)
        print(f"{' '.join(args[1:]):30} {status:18} {note}")
        return 0
    for url in args:
        ver, raw = fetch_version(url)
        status, note = verdict(ver)
        print(f"{url:30} {status:18} {raw}  ->  {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
