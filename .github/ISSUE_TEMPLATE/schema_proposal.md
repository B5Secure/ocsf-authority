---
name: Schema proposal
about: Propose a new or changed event, profile, object, attribute, enumeration, or mapping
title: "[Schema] "
labels: enhancement
assignees: ""
---

## Security notice

Do not report suspected security vulnerabilities in a public issue.

Use GitHub private vulnerability reporting or email security@b5secure.com.

## Proposal summary

Provide a concise description of the proposed schema change.

## Problem or interoperability gap

What security, authorization, evidence, or interoperability problem does this
proposal address?

Describe why the existing OCSF classes, profiles, objects, or attributes do not
fully represent the required information.

## Proposed component

Select all that apply:

- [ ] Event class
- [ ] Profile
- [ ] Object
- [ ] Attribute
- [ ] Enumeration
- [ ] Requirement-level change
- [ ] Sample event
- [ ] Validator rule
- [ ] External schema mapping
- [ ] Other

## Proposed schema change

Describe the proposed additions, modifications, or removals.

Include proposed names, types, requirements, captions, descriptions, and
enumeration values where applicable.

Do not assign or invent an OCSF extension UID, `class_uid`, or `type_uid`.

## Example use case

Describe at least one concrete authorization or security-event use case that
requires the proposed change.

## Example event

Provide a sanitized JSON example when useful.

Use attribute names rather than protected data-element values. Do not include
credentials, access tokens, private keys, customer information, production
records, or other sensitive data.

```json
{
}
```

## Compatibility and impact

Address:

- backward compatibility;
- effects on existing samples;
- effects on negative tests;
- validator changes;
- mapping changes;
- producer and consumer impact; and
- any potential ambiguity with existing OCSF components.

## Security and privacy considerations

Explain whether the proposal could:

- disclose protected information;
- expose data-element values;
- weaken authorization evidence;
- create ambiguous permit or denial outcomes;
- confuse simulated and enforced decisions;
- reduce auditability; or
- introduce unsafe defaults.

## External mappings

Identify any relevant mappings to:

- Microsoft Sentinel ASIM
- Splunk CIM
- Google SecOps UDM
- AWS Security Lake
- Other security schemas

Clearly distinguish documented mappings from inferred mappings.

## Registration status

- [ ] I understand that this extension is not registered.
- [ ] I have not assigned or invented an OCSF UID.
- [ ] I preserved `PENDING-OCSF-REGISTRATION` where applicable.
- [ ] I am not claiming OCSF endorsement or approval.

## Validation considerations

Describe the valid sample and negative test cases that should accompany this
proposal.

## Additional context

Include relevant standards, public documentation, prior discussions, or other
supporting information.
