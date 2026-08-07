# Mapping the Authorization Decision class to vendor schemas

One schema, four destinations. This is the whole commercial argument for the extension: a
producer maps once, and the event lands in Microsoft Sentinel, Splunk, Google SecOps and AWS
Security Lake without a bespoke connector for each.

**Confidence is marked on every row.** Where I am certain of a field name it is stated plainly.
Where I am inferring from a schema's shape rather than from its documentation, it is marked
`[confirm]` — those need checking against the vendor's current field reference before anyone
builds on them. A mapping table that looks authoritative and is half-guessed is worse than one
that says which half.

---

## 1. Microsoft Sentinel — ASIM

ASIM is Sentinel's own normalisation model, and mapping to it is what makes ingested data work
with Sentinel's built-in analytics rules rather than only with custom KQL.

**The honest finding: ASIM has no authorization-decision schema.** Its schemas cover
Authentication, Audit Event, DHCP, DNS, File Event, Network Session, Process Event, Registry
Event, User Management and Web Session. The nearest fit is **Audit Event**, and the fit is
imperfect in a way that is itself an argument for the OCSF extension.

| Authority attribute | ASIM Audit Event | Confidence |
|---|---|---|
| `time` | `TimeGenerated` / `EventStartTime` | certain |
| `activity_name` | `Operation` | certain |
| `resource.uid` | `Object` | certain |
| `resource.type` | `ObjectType` | `[confirm]` |
| `actor.user.name` | `ActorUsername` | certain |
| `actor.user.uid` | `ActorUserId` | `[confirm]` |
| `is_permitted` | `EventResult` (`Success` / `Failure`) | certain — **lossy** |
| `reason_code` | `EventOriginalResultDetails` | certain |
| `enforcement_point.name` | `EventOriginalType` or a custom column | `[confirm]` |
| `delegation.*` | **no ASIM home** — custom columns | certain |
| `decision_evidence.*` | **no ASIM home** — custom columns | certain |
| `limits[]` | **no ASIM home** — custom columns | certain |
| `is_shadow` | **no ASIM home** — custom column, and it MUST exist | certain |

**Two consequences worth stating to Microsoft.** `EventResult` collapses a denial's *reason*
into pass/fail, so the field that makes authorization data useful survives only in
`EventOriginalResultDetails` as free text. And there is nowhere at all for the grant in force.
Those are the two gaps the extension fills, and they are the substance of a proposal to the ASIM
team rather than a complaint.

**Ingestion:** a Codeless Connector Framework connector with a Data Collection Rule performing
the transform. Push mode where volume warrants it. No Azure Function to host or support.

---

## 2. Splunk — Common Information Model

The published OCSF-to-CIM add-on maps OCSF class 3003 into the **Authentication** data model,
which is wrong for a per-record decision. **Change** is the better target.

| Authority attribute | CIM (Change) | Confidence |
|---|---|---|
| `activity_name` | `action` | certain |
| `resource.uid` | `object` | certain |
| `resource.type` | `object_category` | certain |
| `actor.user.name` | `user` | certain |
| `is_permitted` | `result` / `status` | certain |
| `reason_code` | `reason` | `[confirm]` |
| `policy.name` | `change_type` | `[confirm]` — a poor fit; a custom field is better |
| `delegation.grantor` | no CIM field | certain |
| `enforcement_point.name` | `dest` or `app` | `[confirm]` — neither is right |

CIM has no concept of delegated authority. Custom fields carry it, which is exactly the
fragmentation OCSF exists to end.

---

## 3. Google SecOps — UDM

Google publishes an OCSF parser, so **the fastest route is to emit OCSF and let their parser
normalise it** rather than mapping to UDM by hand. If a direct mapping is needed:

| Authority attribute | UDM | Confidence |
|---|---|---|
| event type | `USER_RESOURCE_ACCESS` | `[confirm]` |
| `actor` | `principal.user` | certain |
| `resource` | `target.resource` | certain |
| `is_permitted` | `security_result.action` (`ALLOW` / `BLOCK`) | certain |
| `reason_code` | `security_result.rule_name` or `description` | `[confirm]` |
| `delegation.*` | `additional.fields` | certain |

Because Google's OCSF parser already handles Authentication and Authorize Session, an
extension class will need either parser support or ingestion as an OCSF-conformant custom log
type. Worth asking them directly — it is a short conversation with a clear answer.

---

## 4. AWS Security Lake

<cite index="12-1">Logs written to Security Lake from custom sources must conform to the OCSF schema and use Apache Parquet.</cite>
So this destination requires no mapping at all — it requires the extension. That is the cleanest
demonstration of the argument: with the extension, B5 is a first-class custom source in a
security data lake. Without it, B5 is unparsed JSON.

---

## What this table is really for

Read the four sections together and the pattern is unmistakable: **every vendor schema can carry
who acted and whether it was allowed, and not one of them can carry the authority under which it
was allowed.** Three of the four need custom fields for the grant, the evidence chain and the
shadow flag.

That is not four integration problems. It is one missing schema, and it is the one B5 is
uniquely positioned to write.


## v0.2.0 additions - the data-element attributes

Added 2026-08-03, before registration, because a reserved identifier range makes
every later attribute change a migration for adopters.

| authority attribute | ASIM (Sentinel) | Splunk CIM | Google SecOps UDM | AWS Security Lake |
|---|---|---|---|---|
| `released_attributes[]` | no field | no field | no field | native, OCSF |
| `withheld_attributes[]` | no field | no field | no field | native, OCSF |
| `response_mode` | no field | no field | no field | native, OCSF |
| `entitlement_mode` | no field | no field | no field | native, OCSF |
| `withheld_count` | no field | no field | no field | native, OCSF |
| `evidence_granularity` | no field | no field | no field | native, OCSF |

Every cell in the first three columns reads "no field" and that is the finding,
not a gap in the research. No existing schema has a place for which data elements
a decision released, because no existing schema decides at the element. Security
Lake needs no mapping at all because custom sources there must conform to OCSF,
so the extension is the integration.

**These rows are the strongest single argument in this document.** The v0.1.0
table showed three of four vendors needing custom fields for the grant and the
evidence chain. This table shows four of four with nowhere to put the released
element set at all.
