---
title: "Owner decision: where should the test server run?"
labels: owner
---
**Question:** The Phase 0 gate needs you to log in from your PC to a running Spirebound server and walk around the test town. Where should that server run?

**Options**
- **A. Rent a small staging server now (recommended).** A Linux VPS in Miami, about 4 vCPU / 8 GB, roughly $20–40 a month. The design already needs it by Phase 2 (docs/20_HANDOFF.md), every later gate uses it, and it can stay on while your PC is off. I compare current offers and give you a 3–4 step checklist; you pay and paste nothing into chat — the server login goes into GitHub's encrypted secrets.
- **B. Run it on your own PC.** Free, but you install Docker Desktop and keep a window open while testing, and it only works while your PC is on. We would still need option A by Phase 2.
- **C. Wait.** Phase 0 stays open at the owner-login step. Phase 1 can't start until it closes (one phase at a time), so this pauses the build.

**My recommendation:** A. Reply with A, B, or C (a comment here or in chat is fine).

Context: everything else in Phase 0 that can be checked automatically passes (see STATUS.md). The server boots with zero warnings and a scripted client logs in and lands at the temple.
