#!/usr/bin/env python3
"""Behavioural benchmark: do people stay themselves, stay different from each other, remember
coherently, change believably, and avoid repeating themselves?

Twenty characters, one for each of the twenty styles, start from identical circumstances in the
same world and live the same scripted year: the same dice for their days, the same approaches from
the player, the same events on the same dates. Then the year is measured.

    python benchmark.py [--days 365] [--seed 1]
"""
import argparse, collections, contextlib, io, json, os, random, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forge  # noqa: E402

APPROACHES = ["deference", "familiarity", "bluntness", "flattery", "pressure", "humour", "patience", "pity"]
SCRIPT = {30: "humiliation", 60: "gift", 90: "respect", 120: "threat", 150: "kindness", 180: "betrayal",
          210: "rescue", 240: "humiliation", 270: "gift", 300: "lie-caught", 330: "joy"}


def run(*argv):
    out = io.StringIO()
    sys.argv = ["forge.py"] + [str(x) for x in argv]
    with contextlib.redirect_stdout(out):
        try:
            forge.main()
        except SystemExit:
            pass
    return dict(forge.VIEW), out.getvalue()


def tvd(c1, c2):
    keys = set(c1) | set(c2)
    t1, t2 = sum(c1.values()) or 1, sum(c2.values()) or 1
    return 0.5 * sum(abs(c1.get(k, 0) / t1 - c2.get(k, 0) / t2) for k in keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    work = tempfile.mkdtemp()
    dials = list(forge.DEFAULT_DIALS)
    people = []
    for i, st in enumerate(forge.STYLES):
        random.seed("bench:%d:%s" % (a.seed, st["name"]))
        n = forge.build(dials, "Bench %s" % st["name"])
        n["blend"] = "Pure"
        n["voices"] = [{"style": st["name"], "frac": 1, "manner": forge.voice_manner(st)}]
        n["axes"] = list(st["ax"]); n["core"] = list(st["ax"])
        n["needs"]["state"] = {r: 0 for r in forge.RUNGS}
        n["authenticity"] = {"kind": "Genuine", "faces": []}
        forge.derive(n)
        forge.speech_build(n, random.Random("speech:%s" % st["name"]))
        forge.strain_build(n, random.Random("strain:%s" % st["name"]))
        p = os.path.join(work, "%02d.json" % i)
        forge.save(n, p)
        people.append(p)
    start = {p: forge.load(p) for p in people}
    forms = {p: collections.defaultdict(lambda: [collections.Counter(), collections.Counter()]) for p in people}
    allforms = {p: collections.Counter() for p in people}
    trust_track = {p: [] for p in people}
    repeats = {p: 0 for p in people}
    last = {p: None for p in people}
    colour_lines = {p: collections.Counter() for p in people}
    events_done = {p: 0 for p in people}
    strain_ok = speech_ok = True
    for day in range(1, a.days + 1):
        for i, p in enumerate(people):
            random.seed("bench-day:%d:%d" % (a.seed, day))  # the same dice for everyone
            run("day", p)
            app = APPROACHES[(day + i * 0) % len(APPROACHES)]
            random.seed("bench-meet:%d:%d" % (a.seed, day))
            v, _ = run("meet", p, "--approach", app)
            f = v.get("form")
            half = 0 if day <= a.days // 2 else 1
            forms[p][app][half][f] += 1
            allforms[p][(app, f)] += 1
            sig = (f, tuple(v.get("colour") or []), tuple((v.get("talk") or {}).get("habits") or []))
            if sig == last[p]:
                repeats[p] += 1
            last[p] = sig
            for c in v.get("colour") or []:
                colour_lines[p][c] += 1
            if day in SCRIPT:
                run("event", p, SCRIPT[day])
                events_done[p] += 1
            n = forge.load(p)
            trust_track[p].append(forge.total_trust(n, "player"))
            if n["strain"] != start[p]["strain"]:
                strain_ok = False
            if n["speech"]["main"] != start[p]["speech"]["main"]:
                speech_ok = False
    # measures
    consistency = []
    for p in people:
        for app, (h1, h2) in forms[p].items():
            if sum(h1.values()) >= 5 and sum(h2.values()) >= 5:
                consistency.append(1 - tvd(h1, h2))
    cons = sum(consistency) / len(consistency)
    pair = [tvd(allforms[p], allforms[q]) for i, p in enumerate(people) for q in people[i + 1:]]
    diff_mean, diff_min = sum(pair) / len(pair), min(pair)
    mem_ok = all(len([m for m in forge.load(p)["memory"] if m["event"] in SCRIPT.values()]) == events_done[p]
                 for p in people)
    finals = [trust_track[p][-1] for p in people]
    rel_spread = len(set(finals))
    before_after = []
    for p in people:
        t = trust_track[p]
        for d_, ev in SCRIPT.items():
            if d_ < len(t) and d_ >= 2:
                sign = forge.EVENTS[ev][0]
                if sign:
                    before_after.append((t[d_ - 1] - t[d_ - 2]) * sign >= 0)
    rel_dir = sum(before_after) / max(1, len(before_after))
    rep = sum(repeats.values()) / (len(people) * a.days)
    top_colour = max((c.most_common(1)[0][1] / a.days) if c else 0 for c in colour_lines.values())
    checks = [
        ("Consistency: same person, same treatment, first half vs second half", cons, ">=", 0.45),
        ("Consistency: way of talking and ways of taking strain unchanged all year", 1.0 if (speech_ok and strain_ok) else 0.0, ">=", 1.0),
        ("Differentiation: average difference between any two people", diff_mean, ">=", 0.5),
        ("Differentiation: the two most alike people still differ by", diff_min, ">=", 0.15),
        ("Memory coherence: every scripted event remembered, nothing invented", 1.0 if mem_ok else 0.0, ">=", 1.0),
        ("Relationships: distinct places twenty people end the year with the player", rel_spread, ">=", 4),
        ("Relationships: trust moves the way events push it (or holds)", rel_dir, ">=", 0.8),
        ("Repetition: identical meeting twice in a row", rep, "<=", 0.10),
        ("Repetition: the most-used colour line, share of one person's days", top_colour, "<=", 0.6),
    ]
    print("Behavioural benchmark: %d people, %d days, identical starts and script.\n" % (len(people), a.days))
    failed = 0
    for name, val, op, lim in checks:
        ok = val >= lim if op == ">=" else val <= lim
        failed += not ok
        print("%s  %-78s %6.2f  (%s %s)" % ("ok  " if ok else "FAIL", name, val, op, lim))
    shutil.rmtree(work, ignore_errors=True)
    print("\n%s" % ("All behavioural checks passed." if not failed else "%d behavioural check(s) failed." % failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
