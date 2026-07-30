# Graph Report - plugin-django  (2026-07-30)

## Corpus Check
- 9 files · ~2,476 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 59 nodes · 85 edges · 9 communities (7 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd354172`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- fields.py
- test_integration.py
- verify
- KrynoxCaptchaField
- KrynoxCaptchaFieldTests
- Krynox Captcha for Django
- Changelog
- django-krynox-captcha

## God Nodes (most connected - your core abstractions)
1. `KrynoxCaptchaField` - 14 edges
2. `verify()` - 12 edges
3. `KrynoxCaptchaFieldTests` - 8 edges
4. `KrynoxCaptchaWidget` - 7 edges
5. `SignupForm` - 7 edges
6. `ClientVerifyTests` - 7 edges
7. `MockPlane` - 6 edges
8. `PlaneTestCase` - 5 edges
9. `Krynox Captcha for Django` - 5 edges
10. `_post()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `ClientVerifyTests` --uses--> `KrynoxCaptchaField`  [INFERRED]
  tests/test_integration.py → krynox_captcha/fields.py
- `KrynoxCaptchaFieldTests` --uses--> `KrynoxCaptchaField`  [INFERRED]
  tests/test_integration.py → krynox_captcha/fields.py
- `MockPlane` --uses--> `KrynoxCaptchaField`  [INFERRED]
  tests/test_integration.py → krynox_captcha/fields.py
- `PlaneTestCase` --uses--> `KrynoxCaptchaField`  [INFERRED]
  tests/test_integration.py → krynox_captcha/fields.py
- `SignupForm` --uses--> `KrynoxCaptchaField`  [INFERRED]
  tests/test_integration.py → krynox_captcha/fields.py

## Import Cycles
- None detected.

## Communities (9 total, 2 thin omitted)

### Community 0 - "fields.py"
Cohesion: 0.27
Nodes (5): Form field that verifies the Krynox Captcha solution server-side., Krynox Captcha for Django — privacy-first, proof-of-work CAPTCHA form field., KrynoxCaptchaWidget, Form widget that renders the <krynox-captcha> web component., Renders the widget script + element. The web component injects the solved token…

### Community 1 - "test_integration.py"
Cohesion: 0.29
Nodes (4): MockPlane, PlaneTestCase, Real-HTTP integration tests for django-krynox-captcha. A mock Krynox data plane…, Scripted mock of the Krynox data plane on a real HTTP socket. Every received…

### Community 2 - "verify"
Cohesion: 0.22
Nodes (8): Any, _fail(), _post(), Server-side verification client for Krynox Captcha (stdlib only)., Verify a solved token against POST /siteverify. Returns a dict: ``{success,…, POST JSON, retrying transient failures (network / 429 / 5xx). Returns parsed…, verify(), ClientVerifyTests

### Community 3 - "KrynoxCaptchaField"
Cohesion: 0.33
Nodes (3): KrynoxCaptchaField, Drop into any Django form:: class SignupForm(forms.Form): email =…, Bind a request to this form instance using Django's socket peer IP. If Django…

### Community 5 - "Krynox Captcha for Django"
Cohesion: 0.29
Nodes (6): Honeypot, Install, Krynox Captcha for Django, License, Use, Verify manually

### Community 6 - "Changelog"
Cohesion: 0.40
Nodes (4): [0.1.0] - 2026-07-22, Added, Changelog, [Unreleased]

## Knowledge Gaps
- **7 isolated node(s):** `django-krynox-captcha`, `[Unreleased]`, `Added`, `Install`, `Verify manually` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `KrynoxCaptchaField` connect `KrynoxCaptchaField` to `fields.py`, `test_integration.py`, `verify`, `KrynoxCaptchaFieldTests`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `verify()` connect `verify` to `fields.py`, `test_integration.py`, `KrynoxCaptchaField`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `MockPlane` connect `test_integration.py` to `KrynoxCaptchaField`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `KrynoxCaptchaField` (e.g. with `KrynoxCaptchaWidget` and `ClientVerifyTests`) actually correct?**
  _`KrynoxCaptchaField` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `django-krynox-captcha`, `[Unreleased]`, `Added` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._