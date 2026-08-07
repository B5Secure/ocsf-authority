# Security Policy

## Supported versions

The current version of the OCSF Authority Extension on the `main` branch is
supported for security review and correction.

The extension remains a proposed, unregistered OCSF extension. The identifier
`PENDING-OCSF-REGISTRATION` is intentional and must not be replaced until OCSF
assigns the required identifiers.

| Version | Supported |
| --- | --- |
| Current `main` branch | Yes |
| Earlier drafts and archived copies | No |

## Reporting a vulnerability

Do not report suspected vulnerabilities through public GitHub issues,
discussions, or pull requests.

Email:

**security@b5secure.com**

Include, when available:

- the affected schema component, object, profile, sample, validator, test, or workflow;
- a clear description of the suspected vulnerability;
- steps necessary to reproduce the issue;
- the potential security or interoperability impact;
- any proof-of-concept material that does not contain sensitive data; and
- any recommended remediation.

Do not include customer data, production records, credentials, access tokens,
private keys, signing keys, personal information, or other sensitive information
in a report.

B5 Secure will review the report, coordinate remediation, and work with the
reporter on appropriate disclosure. Please allow B5 Secure an opportunity to
investigate and address the issue before publishing it.

## Scope

This policy covers security issues involving:

- the proposed OCSF Authority Extension schema;
- the `authorization_decision` event class;
- the `authority` profile;
- extension objects and attributes;
- sample events and negative test cases;
- `validate_authority.py`;
- `finalize_registration.py`;
- GitHub Actions workflows; and
- repository configuration that could affect schema integrity or publication.

General product-security reports concerning B5 Secure should also be sent to
**security@b5secure.com**.

## Disclosure principles

B5 Secure supports responsible, coordinated vulnerability disclosure.

Good-faith research should:

- avoid accessing, modifying, or retaining data belonging to another party;
- avoid privacy violations and service disruption;
- use test data rather than production or customer data;
- report findings privately and promptly; and
- provide B5 Secure reasonable time to investigate and remediate the issue.

## Security resources

- [B5 Secure Trust Center](https://b5secure.com/trust-center/)
- [B5 Secure](https://b5secure.com/)
