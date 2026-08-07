# Contributing

## Sign your commits

This repository follows the same Developer Certificate of Origin practice as the
upstream OCSF repositories:

```bash
git commit -s -m "your message"
```

The `-s` adds a `Signed-off-by` line. Commits without one cannot be taken upstream.

## Before you open a pull request

1. `python3 tools/validate_authority.py` — all 9 samples must be valid.
2. `for f in tests/*.json; do python3 tools/validate_authority.py "$f"; done` —
   **every one must fail.** If you add an attribute, add the negative case that
   proves the validator catches its misuse.
3. If you touch the schema, run a local
   [`ocsf-server`](https://github.com/ocsf/ocsf-server) against a tree containing
   `extensions/authority/`. The upstream contributing guide requires the run to be
   completely error free.

## Attributes are typed once

`extensions/authority/dictionary.json` is the only place an attribute is typed. The
class and the profile state *requirements* only. A class may restate a profile
attribute to **tighten** its requirement — never to loosen it.

## Do not invent the uid

`uid`, `class_uid` and `type_uid` stay as `PENDING-OCSF-REGISTRATION` until OCSF
assigns a range. Use `tools/finalize_registration.py` then.
