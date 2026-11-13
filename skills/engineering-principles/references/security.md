# Security Checklist

Treat every input (request bodies, query strings, headers, cookies, files,
webhooks, environment, even your own DB if users wrote to it) as hostile
until validated.

## OWASP Top 10:2025 at a glance

The current list (owasp.org/Top10/2025), and where this checklist covers each:

| # | Category | Where |
|---|---|---|
| A01 | Broken Access Control | §4: authorization on every request, IDOR, CORS |
| A02 | Security Misconfiguration | §3 and §5: debug off, headers, CORS, defaults |
| A03 | Software Supply Chain Failures | §6 |
| A04 | Cryptographic Failures | §4 (password hashing, tokens) and §6 (TLS, keys) |
| A05 | Injection | §1 and §2 |
| A06 | Insecure Design | Threat-model in the design doc's security section (`requirements-and-design`) |
| A07 | Authentication Failures | §4: hashing, rate limits, sessions, JWT |
| A08 | Software or Data Integrity Failures | §5 (deserialization) and §6 (signed artifacts, CI) |
| A09 | Security Logging and Alerting Failures | §7 |
| A10 | Mishandling of Exceptional Conditions | §7 |

## 1. Injection (SQL, NoSQL, command, template, LDAP)

- **Always use parameterized queries** or the ORM's binding. Never build
  queries with string concatenation or interpolation.
  ```python
  # ❌ cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
  # ✅
  cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
  ```
  ```typescript
  // ❌ db.query(`SELECT * FROM users WHERE id = ${id}`)
  // ✅
  db.query('SELECT * FROM users WHERE id = $1', [id]);
  ```
- Raw-SQL escape hatches in ORMs (`raw()`, `$queryRawUnsafe`, `extra()`) need extra scrutiny.
- Dynamic identifiers (column names, sort fields) go through an **allowlist**, never directly from input.
- Shell commands: avoid them. If you must, pass an argument array
  (`execFile`, `subprocess.run([...])`), never `shell=True` with user input.
- NoSQL: reject operator objects in input (`{ "$gt": "" }`). Validate types.

## 2. Cross-site scripting (XSS)

- Rely on the framework's auto-escaping (React, Vue, Jinja, Blade). The
  dangerous exits are `dangerouslySetInnerHTML`, `v-html`, `|safe`,
  `{!! !!}`, `innerHTML`, and `document.write`.
- If you must render user HTML (rich text), sanitize it with a maintained
  library (DOMPurify) using an allowlist.
- Set a **Content-Security-Policy**. Avoid `unsafe-inline` and `unsafe-eval`.
- Cookies: `HttpOnly`, `Secure`, `SameSite=Lax` (or `Strict`).
- Validate URLs before putting them in `href` or `src`: block `javascript:` and `data:` schemes.

## 3. Data leakage

- **No secrets in code or git.** Use environment variables or a secret
  manager. Check that `.env` is in `.gitignore`. Scan with gitleaks or
  trufflehog if unsure.
- **No sensitive data in logs:** passwords, tokens, full card numbers,
  national IDs, full request bodies on auth routes. Redact them.
- **Return the minimum:** select only the fields the client needs. Never
  serialize whole ORM objects (they leak `password_hash`, internal flags).
- Error responses to clients are generic. Stack traces go to logs only.
- Disable debug mode, directory listings and source maps (or restrict
  them) in production.

## 4. Authentication and authorization

- Check **authorization on every request**, on the server, against the
  resource: "can *this* user access *this* order?" Missing ownership checks
  (IDOR) are among the most common real-world vulnerabilities.
- Hash passwords with bcrypt, scrypt or Argon2. Never use MD5 or SHA-1, and never store passwords reversibly.
- Rate-limit login, signup, password reset and OTP endpoints.
- Session tokens: random, long, rotated on login, invalidated on logout.
- JWT: verify the signature *and* the algorithm, keep expiry short, and don't put secrets in the payload.

## 5. Other common holes

- **CSRF:** use the framework's CSRF protection for cookie-based auth on state-changing requests.
- **SSRF:** when fetching user-supplied URLs, allowlist hosts and block internal IP ranges and cloud metadata endpoints (169.254.169.254).
- **File uploads:** check type by content, not by extension. Limit size, store outside the web root with random names, and never execute them.
- **Deserialization:** never unpickle or `eval` untrusted data. Use JSON with schema validation.
- **Mass assignment:** allowlist the fields a request may set (no `role` or `is_admin` from the body).
- **CORS:** no `*` with credentials. Allowlist origins.
- **Dependencies:** run `npm audit`, `pip-audit`, `cargo audit`, or Dependabot. Pin versions and keep a lockfile.
- **Security headers:** `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors` in CSP.

## 6. Supply chain and integrity

- **Every dependency is code you run.** Before adding one, check it's the
  real package (typosquats like `reqeusts`), maintained, and worth it
  (`engineering-principles`, "Adding a dependency").
- **Lockfiles are committed** and CI installs from them exactly
  (`npm ci`, `pip install --require-hashes`, `cargo build --locked`).
- **Audit in CI:** `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`,
  or Dependabot/Renovate, with someone owning the alerts.
- **Install scripts** (`postinstall`) of new packages get read before they run.
- **CI and build:** pin third-party actions to a commit SHA, give tokens the
  least permission, keep secrets out of logs and out of pull requests from
  forks, and sign or checksum the artifacts you ship.
- **TLS everywhere, and keys in a secret manager**, rotated, never in the repo.

## 7. Failing safely, and knowing about it

- **Fail closed.** When an authorization check, a validation or a
  dependency errors, deny the action. Never let an exception skip a check.
- **Handle every error path on purpose:** catch narrow exceptions, never
  swallow them, roll back partial work, and release resources in `finally`
  or `defer`.
- **Generic messages out, detail in the logs.** Users see "Something went
  wrong (ref 8f3a)"; the log has the stack trace and the reference.
- **Log security events** (logins, failed logins, permission denials,
  admin actions, input validation failures) with who, what and when, never
  the secrets themselves.
- **Alert on them.** A log nobody watches catches nothing: a spike in
  failed logins or 403s should page someone.

## Review questions

1. Where does untrusted input enter, and where is it validated?
2. Can any input reach a query, a shell, a template, or HTML without escaping or binding?
3. Does every endpoint check *who* is asking and *whether they own* the resource?
4. What would an attacker learn from error messages, logs or API responses?
5. What happens if someone calls this 10,000 times a minute?
6. If this code throws halfway, is the system left safe and is someone told?
7. What new code from outside (packages, actions, scripts) does this change make us run?
