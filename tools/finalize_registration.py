#!/usr/bin/env python3
"""Fill the registered identifiers, everywhere, in one pass. Standard library only.

An OCSF extension's uid is a RESERVATION issued by OCSF. Two more identifiers are
DERIVED from it and therefore cannot exist until it does:

    class_uid = <the value OCSF assigns for this extension's class>
    type_uid  = class_uid * 100 + activity_id

So the schema and every sample carry the string PENDING-OCSF-REGISTRATION, which
is not a valid integer. Nothing can be mistaken for registered, including by us.

On the day the range is issued:

    python3 tools/finalize_registration.py --uid 42 --class-uid 300142

It refuses to run twice, refuses non-integers, and reports every file it changed.
Run the validator afterwards; it will now check type_uid arithmetic, which it
cannot do while the placeholders are in place.
"""
import argparse, glob, json, os, sys

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--uid', type=int, required=True, help='the extension uid OCSF assigned')
    ap.add_argument('--class-uid', type=int, required=True,
                    help='the class_uid for authorization_decision under that extension')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    ex = os.path.join(EXT, 'extension.json')
    cur = json.load(open(ex))['uid']
    if cur != PENDING:
        print('refusing: extension.json already carries uid %r. '
              'Finalization is a one-time operation.' % cur)
        return 1

    changed = []

    def save(p, o):
        if not a.dry_run:
            json.dump(o, open(p, 'w'), indent=2 if 'samples' not in p else 1)
            open(p, 'a').write('\n')
        changed.append(os.path.relpath(p, os.path.dirname(EXT)))

    o = json.load(open(ex)); o['uid'] = a.uid; save(ex, o)

    for p in sorted(glob.glob(os.path.join(SAMPLES, '*.json'))):
        ev = json.load(open(p))
        touched = False
        if ev.get('class_uid') == PENDING:
            ev['class_uid'] = a.class_uid; touched = True
        if ev.get('type_uid') == PENDING:
            act = ev.get('activity_id')
            if not isinstance(act, int):
                print('cannot compute type_uid for %s: activity_id is %r'
                      % (os.path.basename(p), act)); return 1
            ev['type_uid'] = a.class_uid * 100 + act; touched = True
        if isinstance(ev.get('metadata'), dict):
            m = ev['metadata'].get('extension')
            if isinstance(m, dict) and m.get('uid') == PENDING:
                m['uid'] = a.uid; touched = True
        if touched:
            save(p, ev)

    print('extension uid : %d' % a.uid)
    print('class_uid     : %d' % a.class_uid)
    print('type_uid      : class_uid * 100 + activity_id')
    print('%s %d file(s):' % ('would change' if a.dry_run else 'changed', len(changed)))
    for c in changed:
        print('   %s' % c)
    remaining = sum(open(p).read().count(PENDING)
                    for p in glob.glob(os.path.join(EXT, '**', '*.json'), recursive=True) + glob.glob(os.path.join(SAMPLES, '*.json')))
    print('remaining placeholders: %d' % remaining)
    if remaining and not a.dry_run:
        print('WARNING: placeholders remain. Grep for %s before filing.' % PENDING)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
