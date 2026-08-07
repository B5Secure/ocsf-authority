# OCSF `authority` extension

An [OCSF](https://github.com/ocsf) extension for **authorization decisions at the
data element**: which actor, which action, which data element, under whose grant,
and why.

**Status: not registered.** The extension identifier is deliberately the invalid
string `PENDING-OCSF-REGISTRATION`, so nothing here can be mistaken for a reserved
range — including by us. See [Registration](#registration).

## The gap

OCSF's Identity & Access Management category has Account Change, Authentication,
Authorize Session, Entity Management, User Access Management and Group Management.
`authorize_session` is session-level. `api_activity` and
`web_resources_access_activity` are request-shaped.

None of them can express:

> may this actor perform this action on **this data element**, under which grant,
> and why?

So that event lands in `unmapped`, where nothing can be queried across producers —
which is the whole reason to have a schema.

## Two parts, and the second is the more useful one

**1. An `authorization_decision` event class** (IAM category). Six required
attributes: `activity_id`, `actor`, `resource`, `is_permitted`, `reason_code`,
`enforcement_point`.

**2. An `authority` profile** — a *mixin*. Any producer's Authentication, API
Activity, Datastore Activity or HTTP Activity event can carry the grant in force,
the reason for the outcome, and which data elements were actually released,
**without adopting a new event class**.

An identity vendor will not adopt someone else's event class. It might adopt a
handful of optional attributes that make its own events more useful. Two samples
in `samples/` show the profile applied to *other vendors'* classes for exactly
that reason.

## Four attributes nobody writes unless they have built this

| | Why it exists |
|---|---|
| `is_shadow` | A decision evaluated but not enforced. If simulated traffic is indistinguishable from enforced traffic it silently poisons every detection and metric built on the stream. |
| `state_age` | A permit against three-second-old authority state is not the same permit as one against three-hour-old state. |
| `limits[]` | The aggregates consulted, **including those not exceeded**. Without them a threshold denial is indistinguishable from a scope denial. |
| `released_attributes[]` | The element **names** returned — never values. Most logs say "user X read account Y". This says which elements were released and which withheld, which is the evidence HIPAA minimum-necessary, GDPR Art. 5(1)(c) and PCI DSS 4.0 all presuppose. |

**Element names, never element values.** A stream carrying values becomes a
duplicate of the data it protects — aggregated across principals and retained for
an audit period, therefore a more attractive target than the original store. The
validator enforces it.

## Layout

```
extensions/authority/     the extension, ready to drop into an OCSF schema tree
samples/                  9 events, including 2 on other vendors' classes
tools/validate_authority.py     stdlib only, no network
tools/finalize_registration.py  fills the identifiers once a range is issued
tests/                    14 events that MUST be rejected
MAPPINGS.md               ASIM, Splunk CIM, Google SecOps UDM, AWS Security Lake
```

`samples/`, `MAPPINGS.md`, `tools/` and `tests/` sit at the repo root on purpose —
they do not belong inside a schema tree submitted upstream.

## Validate

```bash
python3 tools/validate_authority.py                 # 9 samples, expect 9 valid
for f in tests/*.json; do python3 tools/validate_authority.py "$f"; done
```

The second loop is the one that matters: **every one of the 14 must fail.** A
validator that has only seen valid input is untested. The cases include flipping a
denial to a permit, a denial that released data, released and withheld sets that
overlap, and an element *value* where a name belongs.

## Registration

OCSF requires each extension to be registered so two organisations cannot ship
colliding identifiers. The `uid` is therefore a **reservation issued by OCSF**, not
a choice.

`extensions/authority/extension.json` carries `"uid": "PENDING-OCSF-REGISTRATION"`
— a string where OCSF requires an integer. It is invalid on purpose: any tool that
reads it fails loudly rather than quietly assuming a range. `class_uid` and
`type_uid` in the samples carry the same placeholder, because both are *derived*
from the extension uid and cannot exist before it does.

When a range is issued:

```bash
python3 tools/finalize_registration.py --uid <n> --class-uid <n>
```

It refuses to run twice and reports any remaining placeholder.

## Honest status

- One implementation: [B5 Secure](https://b5secure.com/). No second producer.
- Nothing registered. No claim of OCSF endorsement or membership.
- AWS Security Lake is a *consumer* of OCSF, not a second producer of this
  extension.
- `MAPPINGS.md` marks every inferred field as inferred rather than presenting it as
  read from vendor documentation.

## Related

- Technical paper: *Authorize the Data Element Before the Fetch Happens*
- Whitepaper: *Never Trust. Continuous Authorization from the Record Down to the Data Element*
- Offline evidence verifier — no network, no dependency on our software, so a third
  party can verify an export we did not hand them:
  https://b5secure.com/platform/evidence-verifier/

## License

Apache-2.0, matching OCSF. See `LICENSE`.

Copyright B5 SECURE LLC.
