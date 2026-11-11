#!/usr/bin/env python3
"""NPC Temperament Engine dice. See SKILL.md for the rules this implements."""
import argparse, random, re, sys

PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
APPROACHES = ["deference","familiarity","bluntness","flattery","haggling","humour","patience","pressure"]

# name, warmth, sensitivity, guard, candor, agency%, nerve%, danger(dir, form),
# approach {+2,+1,-1,-2}, kind, middle, hostile
T = {
 1: ("Monad - the Sovereign", 0, 1, 4, 2, 2, 1, (1, "Dutiful"),
     ("deference","patience","familiarity","pressure"),
     ["Practical","Protective","Mentoring","Generous"],
     ["Dutiful","Indifferent","Boastful","Transactional"],
     ["Contempt","Cold Refusal","Territorial","Righteous Wrath"]),
 2: ("Dyad - the Doubter", -1, 3, 2, 5, 4, 5, (-1, "Fear-Aggression"),
     ("patience","bluntness","flattery","pressure"),
     ["Confiding","Tender","Forgiving","Gruff-Kind"],
     ["Wary","Evasive","Melancholic","Mercurial"],
     ["Suspicion","Fear-Aggression","Obstruction","Grudge"]),
 3: ("Triad - the Mediator", 2, 1, 1, 6, 3, 2, (1, "Confiding"),
     ("humour","familiarity","patience","bluntness"),
     ["Hospitable","Teasing-Fond","Forgiving","Confiding"],
     ["Gossipy","Curious","Bargaining-Humour","Flirtatious"],
     ["Mockery","Manipulation","Obstruction","Cold Refusal"]),
 4: ("Tetrad - the Arbiter", 0, 1, 3, 4, 2, 1, (-1, "Obstruction"),
     ("bluntness","haggling","humour","flattery"),
     ["Practical","Loyal","Mentoring","Reverent"],
     ["Dutiful","Transactional","Ritual","Wary"],
     ["Obstruction","Righteous Wrath","Grudge","Cold Refusal"]),
 5: ("Pentad - the Changeling", 1, 3, 1, 7, 5, 4, (0, "Mercurial"),
     ("familiarity","humour","deference","patience"),
     ["Teasing-Fond","Generous","Confiding","Protective"],
     ["Mercurial","Flirtatious","Curious","Boastful"],
     ["Mockery","Violent Outburst","Envy/Spite","Manipulation"]),
 6: ("Hexad - the Keeper", 3, 2, 2, 5, 3, 3, (-1, "Territorial"),
     ("deference","humour","haggling","pressure"),
     ["Hospitable","Tender","Protective","Gruff-Kind"],
     ["Gossipy","Distracted","Melancholic","Dutiful"],
     ["Territorial","Fear-Aggression","Grudge","Envy/Spite"]),
 7: ("Heptad - the Seer", -1, 2, 4, 3, 4, 0, None,
     ("patience","deference","humour","familiarity"),
     ["Mentoring","Reverent","Confiding","Gruff-Kind"],
     ["Curious","Evasive","Ritual","Indifferent"],
     ["Contempt","Predatory","Cold Refusal","Manipulation"]),
 8: ("Ogdoad - the Bulwark", 1, 1, 3, 3, 2, 2, (1, "Protective"),
     ("bluntness","pressure","haggling","deference"),
     ["Protective","Loyal","Practical","Generous"],
     ["Wary","Dutiful","Boastful","Transactional"],
     ["Territorial","Violent Outburst","Righteous Wrath","Suspicion"]),
 9: ("Ennead - the Horizon", 0, 2, 2, 6, 3, 3, (1, "Tender"),
     ("familiarity","patience","pressure","haggling"),
     ["Forgiving","Generous","Tender","Mentoring"],
     ["Melancholic","Distracted","Curious","Indifferent"],
     ["Cold Refusal","Mockery","Grudge","Predatory"]),
}
ALL_FORMS = sorted({f for t in T.values() for f in t[9] + t[10] + t[11]})
STATION = {1:("Head",1),2:("Warden",1),3:("Steward",0),4:("Steward",0),5:("Herald",0),
           6:("Threshold",0),7:("Hand",0),8:("Hand",0),9:("Sworn",1),10:("Unmoored",-1)}
OFFICE = ["Teaches","Reveals","Finds","Reconciles","Kindles","Carries","Builds","Ruins",
          "Companions","Transforms","Mends","Forecasts"]
OPPOSITES = ["Limit/Boundless","Odd/Even","One/Many","Right/Left","Pressing/Yielding",
             "Rest/Motion","Straight/Curved","Light/Dark","Good/Petty","Square/Oblong"]
RATIO = {1:("Unison 1:1",2,1),2:("Octave 2:1",3,2),3:("Fifth 3:2",5,3),4:("Fourth 4:3",7,4)}
INWARD = ["to grieve properly","to be forgiven by someone dead","to stop being afraid",
 "to feel young again","to be left alone","to believe in something again",
 "to be seen as a parent never saw them","to forget a face","to stay exactly as they are",
 "to be loved back","to make peace with a choice","to not be the last of their line",
 "to deserve their position","to stop needing a vice","for someone gone to come home",
 "to understand their own anger","to know if they were right","to sleep without dreaming",
 "to matter","something they can't name"]
OPEN = ["recover an object","get word to someone out of reach","be rid of a debt or creditor",
 "find a missing person","keep someone safe for a stretch","get proof of a wrong",
 "get something past a gate, law or system","learn a fact they can't reach",
 "break a rival's hold","bring someone home","obtain something rare","end a threat"]
QUIRK = ["counts money twice","never sits with back to a door",
 "speaks of self in third person when nervous","hums the same four notes",
 "refuses to say a certain word","collects small useless objects of one kind",
 "always offers something to drink","calls everyone by the wrong name, kindly",
 "can't stand whistling","touches a lucky object before deciding",
 "laughs at the wrong moments","keeps a dead person's belonging close","answers in sayings",
 "sleeps at odd hours","never finishes a drink","counts steps","lies about trivial things only",
 "pockets one small thing from every visitor, returns it later","feeds animals obsessively",
 "always knows the time without looking"]
CIRC = {-2: ["lost money or work","humiliated in front of others","someone close is hurt or sick",
             "received a threat"],
        -1: ["slept badly or in pain","argued with someone close","a plan fell through",
             "owes more than expected"],
         0: ["an ordinary day (busy)","an ordinary day (bored)","an ordinary day (weather)",
             "an ordinary day (routine)"],
         1: ["got paid or made a good sale","a small win or compliment","a friend visited",
             "a worry lifted"],
         2: ["big good news","a debt cleared","someone loved came back","a long effort paid off"]}
ODDITY = ["gives a gift, then asks for it back next time","insults you while fixing something of yours",
 "helps your rival the same day they helped you","warns you off, then follows you",
 "swears they don't know you, in front of others","overpays you, then haggles a coin",
 "praises a thing they clearly hate","weeps at good news","shuts the door, leaves food outside it",
 "tells a truth that harms them","lies to protect you, badly",
 "remembers a past meeting the opposite way","calls you by a name you've never given",
 "is mid-conversation with no one when you arrive","sets a place for someone who never comes",
 "knows something about you they shouldn't, and treats it as normal",
 "every clock or screen near them is a few minutes off",
 "repeats your last sentence back exactly, then carries on",
 "an animal or machine nearby reacts to them strangely","asks you, sincerely, what year it is"]
AGENCY = {1:"Off-pattern form",2:"Off-pattern form",3:"Inversion",4:"Drive surfaces",
          5:"The other face",6:"Free will"}
FLIP = {"Hostile":"Kind","Kind":"Hostile","Cool":"Warm","Warm":"Cool"}

d = lambda n: random.randint(1, n)

def band_of(m):
    return ("Hostile" if m <= -6 else "Cool" if m <= -2 else "Neutral" if m <= 1
            else "Warm" if m <= 5 else "Kind")

def forms_for(t, band):
    return t[9] if band == "Kind" else t[11] if band == "Hostile" else t[10]

def tetrad(forms):
    r = d(10)
    return forms[0 if r <= 4 else 1 if r <= 7 else 2 if r <= 9 else 3], r

def cmd_npc(a):
    if a.name:
        raw = sum(PYTH[c] for c in a.name.upper() if c in PYTH)
        num = raw
        while num > 9:
            num = sum(int(x) for x in str(num))
        num = num or 9
        random.seed("npc:" + a.name.lower())
        print(f"Name seed: {a.name} (sum {raw} -> {num})  [table-side only]")
    else:
        num = d(9)
        print(f"Temperament roll d9 -> {num}")
    t = T[num]
    flag = d(100)
    complete, outlier = 91 <= flag <= 99, flag == 100
    agency = 10 if outlier else t[5]
    sr = d(10); st, gm = STATION[sr]
    print(f"Temperament: {num} {t[0]} | Warmth {t[1]:+d}, Sensitivity x{t[2]}, Candor {t[4]}, "
          f"Agency {agency}%, Nerve {t[6]}%")
    if complete: print(f"Flag (d100={flag}): COMPLETE - Still on drive 1-4, second quirk")
    if outlier: print(f"Flag (d100={flag}): OUTLIER - Agency 10%")
    print(f"Station: {st} | Guard {max(0, t[3] + gm)}")
    offs = [OFFICE[d(12)-1]] + ([OFFICE[d(12)-1]] if d(4) == 4 else [])
    print("Office: " + " + ".join(dict.fromkeys(offs)))
    a_ = t[8]
    print(f"Approach: +2 {a_[0]}, +1 {a_[1]}, -1 {a_[2]}, -2 {a_[3]}")
    dr = d(20)
    if dr <= (4 if complete else 2):
        print(f"Drive: STILL (d20={dr}) - wants nothing in particular")
    elif dr <= 15:
        print(f"Drive: INWARD (d20={dr}) - {INWARD[d(20)-1]}  [never a request]")
    else:
        k = "FULL" if d(6) == 6 else "PARTIAL"
        print(f"Drive: OPEN/{k} (d20={dr}) - {OPEN[d(12)-1]}  [only through the five gates]")
    rn, die, amax = RATIO[d(4)]
    print(f"Opposites: {OPPOSITES[d(10)-1]} at {rn} (check d{die}: {"1" if amax == 1 else f"1-{amax}"} side A)")
    print("Quirk: " + "; ".join(random.sample(QUIRK, 2 if complete else 1)))

def cmd_day(a):
    r = d(20)
    v = -2 if r <= 2 else -1 if r <= 6 else 0 if r <= 14 else 1 if r <= 18 else 2
    s = T[a.temp][2]
    print(f"Circumstance (d20={r}): {v:+d} '{random.choice(CIRC[v])}' "
          f"x{s} = {v*s:+d} to mood today")

def cmd_meet(a):
    t = T[a.temp]
    ap = 0
    if a.approach:
        row = t[8]
        ap = {row[0]: 2, row[1]: 1, row[2]: -1, row[3]: -2}.get(a.approach, 0)
    circ = a.circ * t[2]
    mood = t[1] + a.trust + circ + ap
    lean = None
    if a.danger:
        r = d(100)
        if t[7] and r <= t[6]:
            dirn, lform = t[7]
            if dirn == 0: dirn = 1 if d(2) == 1 else -1
            mood += dirn; lean = (dirn, lform, r)
        else:
            print(f"Danger: no leaning (d100={r} > Nerve {t[6]})")
    band = band_of(mood)
    form, r = tetrad(forms_for(t, band))
    print(f"Mood {t[1]:+d} warmth {a.trust:+d} trust {circ:+d} day {ap:+d} approach"
          f"{f' {lean[0]:+d} danger' if lean else ''} = {mood:+d} -> {band}: {form} (d10={r}, keep for today)")
    if lean:
        fits = lean[1] in forms_for(t, band)
        print(f"DANGER LEANING (d100={lean[2]} <= {t[6]}): {lean[1]} "
              + ("replaces form this scene" if fits else "as a flavour beat only"))
    ag = 10 if a.outlier else t[5]
    r = d(100)
    if r <= ag:
        res = AGENCY[d(6)]
        extra = ""
        if res == "Off-pattern form":
            pool = [f for f in ALL_FORMS if f not in t[9] + t[10] + t[11]]
            extra = f" -> {random.choice(pool)}"
        elif res == "Inversion":
            nb = FLIP.get(band, random.choice(["Warm", "Cool"]))
            extra = f" -> {nb}: {tetrad(forms_for(t, nb))[0]}"
        print(f"AGENCY (d100={r} <= {ag}): {res}{extra}  [decide the hidden cause]")
    else:
        print(f"Agency: no (d100={r} > {ag})")

def cmd_scene(a):
    r = d(100)
    print(f"ODDITY (d100=100): {ODDITY[d(20)-1]}" if r == 100 else f"Oddity: none (d100={r})")

def cmd_ask(a):
    t = T[a.temp]
    guard = a.guard if a.guard is not None else t[3]
    if a.drive != "open":
        print(f"NO ASK. Drive is {a.drive}: decline, deflect, or a trivial courtesy at most."); return
    if a.asked: print("NO ASK. Already asked this scene."); return
    if not a.touched: print("NO ASK. The talk hasn't touched the matter."); return
    r = d(10)
    if r > t[4]: print(f"NO ASK. Kairos failed (d10={r} > Candor {t[4]})."); return
    if a.trust < guard:
        print(f"HINT ONLY. Kairos ok (d10={r}) but Trust {a.trust} < Guard {guard}."); return
    print(f"MAY ASK (d10={r} <= {t[4]}, Trust {a.trust} >= Guard {guard}). "
          "Default shape: Partial. Pride may still refuse.")

def cmd_roll(a):
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", a.expr.strip().lower())
    if not m: sys.exit("format: NdS[+M]")
    n, s, mod = int(m[1] or 1), int(m[2]), int(m[3] or 0)
    rs = [d(s) for _ in range(n)]
    print(f"{a.expr}: {rs} = {sum(rs) + mod}")

p = argparse.ArgumentParser(description="NPC Temperament Engine")
p.add_argument("--seed", type=int)
sp = p.add_subparsers(dest="cmd", required=True)
x = sp.add_parser("npc"); x.add_argument("--name"); x.set_defaults(f=cmd_npc)
x = sp.add_parser("day"); x.add_argument("temp", type=int, choices=range(1, 10)); x.set_defaults(f=cmd_day)
x = sp.add_parser("meet"); x.add_argument("temp", type=int, choices=range(1, 10))
x.add_argument("--trust", type=int, default=0); x.add_argument("--circ", type=int, default=0,
               choices=range(-2, 3)); x.add_argument("--approach", choices=APPROACHES)
x.add_argument("--danger", action="store_true"); x.add_argument("--outlier", action="store_true")
x.set_defaults(f=cmd_meet)
x = sp.add_parser("scene"); x.set_defaults(f=cmd_scene)
x = sp.add_parser("ask"); x.add_argument("temp", type=int, choices=range(1, 10))
x.add_argument("--trust", type=int, default=0); x.add_argument("--guard", type=int)
x.add_argument("--drive", choices=["still", "inward", "open"], required=True)
x.add_argument("--touched", action="store_true"); x.add_argument("--asked", action="store_true")
x.set_defaults(f=cmd_ask)
x = sp.add_parser("roll"); x.add_argument("expr"); x.set_defaults(f=cmd_roll)

if __name__ == "__main__":
    args = p.parse_args()
    if args.seed is not None: random.seed(args.seed)
    args.f(args)
