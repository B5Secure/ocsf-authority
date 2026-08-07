
## 0.3.0 - 2026-08-03 (the version to file)

Eight gaps closed, all additive. No pre-existing key changed value; asserted
per file.

1. **`reason_code_id` gained its enum** - 13 values. It existed, was typed
   `integer_t`, and had NO enum, so the only usable field was the free-text
   `reason_code`. That reproduced the exact problem the extension exists to fix,
   one level up: every producer would invent its own codes. `reason_code` stays
   as the vendor-specific detail alongside the enum.
2. **`activity_id` gained its enum** - 11 values. It was `required` with no enum
   defined anywhere; `ocsf-server` would have rejected it.
3. **`class_uid` and `type_uid`** added to every sample as the deliberately
   invalid placeholder. They cannot be real numbers yet: class_uid is DERIVED
   from the registered extension uid, and type_uid is class_uid * 100 +
   activity_id. `tools/finalize_registration.py` fills all three in one pass.
4. **`tenant_uid` declared.** It appeared in every sample and in no schema file.
5. **`enforcement_point.stage_id`** - request, access or delivery. The three
   decision points were not expressible at all, so an event that PREVENTED a
   query and one that filtered a result set were indistinguishable. Stage 1
   prevention is the central claim and the schema could not carry it.
6. **Two profile-application samples** on Authentication (3002) and Datastore
   Activity (6005), marked illustrative and not produced by B5. The PR argues
   the profile is the contribution; it now shows evidence of that, not only of
   the class.
7. **A shipped validator** - `tools/validate_authority.py`, standard library
   only. v0.1.0 had none; the checks lived in a build script outside the tree,
   so no third party could check their own events.
8. **OCSF plumbing** - `observables`, `unmapped`, `raw_data` declared, and
   `metadata.correlation_uid` populated. Correlation matters specifically
   because the design emits several events per operation across three stages
   and nothing tied them together.

Dictionary 16 -> 19, class 20 -> 24, samples 7 -> 9.
53 build checks, 9 samples valid, 14 of 14 attacks rejected.
