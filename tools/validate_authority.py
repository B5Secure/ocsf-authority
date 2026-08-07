#!/usr/bin/env python3
"""Validate authority-extension events against the shipped schema.

Standard library only. No network. A third party can check their own events
without B5's software, which is the difference between a specification and a
proposal.

Structure plus the semantic invariants JSON Schema cannot express. Exit 0 all
valid, 1 a failure, 2 unreadable.
"""
import glob, json, os, sys

PENDING = 'PENDING-OCSF-REGISTRATION'
def _locate():
    """Find the schema tree and the samples dir from either layout.

    This repository puts the extension at extensions/authority/ and the samples at
    the repo root, because samples do not belong inside a schema tree submitted
    upstream. The original filing pack nested them differently. Detect rather than
    assume, so the tool works from either.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    for ext in (os.path.join(root, 'extensions', 'authority'),
                os.path.join(root, 'ocsf-extension'),
                os.path.join(here, 'extensions', 'authority')):
        if os.path.isfile(os.path.join(ext, 'extension.json')):
            for smp in (os.path.join(root, 'samples'), os.path.join(ext, 'samples')):
                if os.path.isdir(smp):
                    return ext, smp
            return ext, None
    raise SystemExit('cannot locate extension.json - run this from inside the repo')


EXT, SAMPLES = _locate()
BASE = {'metadata', 'category_uid', 'category_name', 'class_uid', 'class_name',
        'type_uid', 'type_name', 'time', 'severity_id', 'activity_id',
        'activity_name', 'actor', 'resource', 'message', 'status_id', 'count',
        'duration', 'observables', 'raw_data', 'unmapped', '_note'}


def main(paths):
    try:
        cls = json.load(open(os.path.join(EXT, 'events/iam/authorization_decision.json')))
        prof = json.load(open(os.path.join(EXT, 'profiles/authority.json')))
        dic = json.load(open(os.path.join(EXT, 'dictionary.json')))['attributes']
        epo = json.load(open(os.path.join(EXT, 'objects/enforcement_point.json')))
    except Exception as e:
        print('cannot read schema: %s' % e); return 2

    allowed = set(cls['attributes']) | set(prof['attributes']) | BASE
    required = [k for k, v in cls['attributes'].items() if v.get('requirement') == 'required']
    reason_enum = dic['reason_code_id'].get('enum', {})
    stage_enum = dic['stage_id'].get('enum', {})
    act_enum = cls['activity_id']['enum']
    ours = cls.get('uid')
    n = fails = 0

    for p in paths:
        try:
            e = json.load(open(p))
        except Exception as ex:
            print('FAIL %-48s unreadable: %s' % (os.path.basename(p), ex)); return 2
        n += 1
        errs = []
        # a profile-application sample is another vendor's class; only profile rules apply
        is_ours = e.get('class_name') == cls['caption'] or e.get('class_uid') == PENDING

        if is_ours:
            for k in required:
                if k not in e:
                    errs.append('missing required attribute %r' % k)
            a = e.get('activity_id')
            if not isinstance(a, int) or str(a) not in act_enum:
                errs.append('activity_id %r not in the enum' % a)
        for k in e:
            if k not in allowed:
                errs.append('unknown attribute %r' % k)

        # registration discipline
        for k in ('class_uid', 'type_uid'):
            if e.get(k) == PENDING and is_ours:
                pass  # expected before registration
            elif isinstance(e.get(k), int) and k == 'type_uid' and isinstance(e.get('class_uid'), int):
                if e['type_uid'] != e['class_uid'] * 100 + e.get('activity_id', -1):
                    errs.append('type_uid is not class_uid * 100 + activity_id')

        # the taxonomy
        rid = e.get('reason_code_id')
        if rid is not None and str(rid) not in reason_enum:
            errs.append('reason_code_id %r not in the enum' % rid)
        rc = e.get('reason_code', '')
        if 'is_permitted' in e:
            if e['is_permitted'] and not rc.startswith('ALLOW_'):
                errs.append('permitted decision carries reason_code %r' % rc)
            if not e['is_permitted'] and not rc.startswith('DENY_'):
                errs.append('denied decision carries reason_code %r' % rc)
            if rid is not None:
                allow = 1 <= int(rid) <= 9
                if e['is_permitted'] != allow:
                    errs.append('reason_code_id %s disagrees with is_permitted %s'
                                % (rid, e['is_permitted']))
        if is_ours and 'is_shadow' not in e:
            errs.append('shadow status not stated explicitly')

        # the three decision points
        ep = e.get('enforcement_point')
        if is_ours:
            if not isinstance(ep, dict):
                errs.append('enforcement_point missing')
            else:
                s = ep.get('stage_id')
                if s is None:
                    errs.append('enforcement_point states no stage_id')
                elif str(s) not in stage_enum:
                    errs.append('stage_id %r not in the enum' % s)
                elif s == 1 and e.get('released_attributes'):
                    errs.append('stage_id 1 (request) released attributes, so I/O occurred')

        # element names, never values
        rel, wit = e.get('released_attributes', []), e.get('withheld_attributes', [])
        both = sorted(set(rel) & set(wit))
        if both:
            errs.append('attributes both released and withheld: %s' % both)
        if e.get('response_mode') == 'partial' and not wit:
            errs.append('partial response names no withheld attributes')
        if e.get('response_mode') == 'atomic' and wit:
            errs.append('atomic response names withheld attributes')
        if e.get('is_permitted') is False and rel:
            errs.append('denied decision released %d attributes' % len(rel))
        if 'withheld_count' in e and e.get('evidence_granularity') != 'per_operation':
            errs.append('withheld_count without per_operation evidence_granularity')
        for k, v in (('released_attributes', rel), ('withheld_attributes', wit)):
            for nm in v:
                if not all(ch.isalnum() or ch in '._' for ch in nm):
                    errs.append('%s entry %r is not an element name' % (k, nm))
        if rc == 'DENY_LIMIT_DAILY_AMOUNT_EXCEEDED' or rid == 13:
            if not any(l.get('is_exceeded') for l in e.get('limits', [])):
                errs.append('limit denial with no exceeded entry in limits[]')

        if errs:
            fails += 1
            print('FAIL %s' % os.path.basename(p))
            for x in errs:
                print('       - %s' % x)
        else:
            print('ok   %s' % os.path.basename(p))
    print('\n%d events, %d valid, %d invalid' % (n, n - fails, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    args = sys.argv[1:] or sorted(glob.glob(os.path.join(SAMPLES, '*.json')))
    sys.exit(main(args))
