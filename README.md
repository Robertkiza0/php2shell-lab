# PHP2Shell Lab

A hands-on lab for learning to **detect and remediate** PHP2Shell
(CVE-2026-109618 and CVE-2026-109619) — the two critical, unauthenticated
remote-code-execution flaws in the PHP interpreter disclosed on 21 October 2026.

This project is **defensive**. It is built to practise finding vulnerable
servers, patching them, and proving the fix — the work a security analyst
actually delivers to clients. It contains **no exploit code**.

> **Full write-up (French):** see [`ARTICLE.fr.md`](./ARTICLE.fr.md) for a
> plain-language explanation of how PHP2Shell works and how to protect against it.

## What it demonstrates

- Fingerprinting a PHP version from outside a server (and why that isn't enough)
- Confirming the true version on the host with `php -v`
- Understanding why hiding the version is not a fix
- Patching a vulnerable server and verifying the result
- Writing a clear before/after remediation report

## What's inside

| File | Purpose |
| --- | --- |
| `Dockerfile` | Builds WordPress on a chosen PHP version |
| `docker-compose.yml` | Runs a vulnerable (8.3.35) and patched (8.3.36) site side by side |
| `init.sql` | Creates the two WordPress databases |
| `check_php2shell.py` | Passive version checker — reports vulnerable / patched |

## Quick start

Requires Docker Desktop.

```bash
docker compose up -d --build
```

- Vulnerable site: http://127.0.0.1:8081  (WordPress DB: `wp_vuln`)
- Patched site:    http://127.0.0.1:8082  (WordPress DB: `wp_patched`)

In the WordPress installer use host `db`, user `wp`, password `wplab`.

Everything binds to `127.0.0.1` only. Keep it that way: the vulnerable
container must never be reachable from a network.

## Exercises

1. **Fingerprint from outside**
   ```bash
   curl -sI http://127.0.0.1:8081 | grep -i x-powered-by
   python3 check_php2shell.py http://127.0.0.1:8081 http://127.0.0.1:8082
   ```
2. **Check from inside** (how you'd verify on a client server)
   ```bash
   docker compose exec vulnerable php -v
   python3 check_php2shell.py --local 8.3.35
   ```
3. **Hide the version** — set `expose_php = Off` in the `Dockerfile`, rebuild,
   re-run step 1. The checker drops to UNKNOWN, but `php -v` still shows 8.3.35.
   Lesson: a hidden header is not a fix.
4. **Remediate** — change the vulnerable service to `8.3.36`, rebuild, confirm
   WordPress still works, re-run the checker. This is the service you deliver.
5. **Upgrade drill** — try `PHP_VERSION: "7.4"` -> `8.2.35` with a few old
   plugins installed, and note what breaks. That breakage is where clients most
   need help.
6. **Study the fix** — in a clone of `php-src`, run
   `git diff php-8.3.35 php-8.3.36` and find the OOM-handling and global-state
   changes described in the advisories.

## Fixed versions

| PHP branch | Fixed release |
| --- | --- |
| 8.5 | 8.5.12 |
| 8.4 | 8.4.27 |
| 8.3 | 8.3.36 |
| 8.2 | 8.2.35 |
| 8.1 / 8.0 / 7.4 | end-of-life — minimal source backport, migrate instead |

## Clean up

```bash
docker compose down -v
```

## Ethical use

Run the checker and the lab only against systems you own or have **written
permission** to test. This repository is for defensive learning and client
remediation work.

## References

- [Wiz — PHP2Shell](https://www.wiz.io/blog/php2shell-php-rce)
- [Help Net Security](https://www.helpnetsecurity.com/2026/10/21/php2shell-php-vulnerabilities-patched-cve-2026-109618-cve-2026-109619/)
- [Huntress Rapid Response](https://www.huntress.com/blog/php2shell-leaked-critical-php-vulnerabilities)
- [runZero](https://www.runzero.com/blog/php/)

## Author

**Lungwe Kiza Robert** — Cybersecurity analyst, VertaGuard.

## License

MIT — see [`LICENSE`](./LICENSE).
