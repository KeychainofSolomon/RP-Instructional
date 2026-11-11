#!/usr/bin/env python3
"""NPC Temperament Engine dice. See SKILL.md for the rules this implements."""
import argparse, random, re, sys

PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}

TEMP = {  # name, warmth, swing, guard, candor, agency%, kind, middle, hostile
 1: ("Monad - the Sovereign", 0, 4, 4, 2, 15,
     ["Practical","Protective","Mentoring","Generous"],
     ["Dutiful","Indifferent","Boastful","Transactional"],
     ["Contempt","Cold Refusal","Territorial","Righteous Wrath"]),
 2: ("Dyad - the Doubter", -1, 8, 2, 5, 20,
     ["Confiding","Tender","Forgiving","Gruff-Kind"],
     ["Wary","Evasive","Melancholic","Mercurial"],
     ["Suspicion","Fear-Aggression","Obstruction","Grudge"]),
 3: ("Triad - the Mediator", 2, 4, 1, 6, 16,
     ["Hospitable","Teasing-Fond","Forgiving","Confiding"],
     ["Gossipy","Curious","Bargaining-Humour","Flirtatious"],
     ["Mockery","Manipulation","Obstruction","Cold Refusal"]),
 4: ("Tetrad - the Arbiter", 0, 4, 3, 4, 15,
     ["Practical","Loyal","Mentoring","Reverent"],
     ["Dutiful","Transactional","Pious","Wary"],
     ["Obstruction","Righteous Wrath","Grudge","Cold Refusal"]),
 5: ("Pentad - the Changeling", 1, 10, 1, 7, 20,
     ["Teasing-Fond","Generous","Confiding","Protective"],
     ["Mercurial","Flirtatious","Curious","Boastful"],
     ["Mockery","Violent Outburst","Envy/Spite","Manipulation"]),
 6: ("Hexad - the Keeper", 3, 6, 2, 5, 17,
     ["Hospitable","Tender","Protective","Gruff-Kind"],
     ["Gossipy","Distracted","Melancholic","Dutiful"],
     ["Territorial","Fear-Aggression","Grudge","Envy/Spite"]),
 7: ("Heptad - the Seer", -1, 6, 4, 3, 19,
     ["Mentoring","Reverent","Confiding","Gruff-Kind"],
     ["Curious","Evasive","Pious","Indifferent"],
     ["Contempt","Predatory","Cold Refusal","Manipulation"]),
 8: ("Ogdoad - the Bulwark", 1, 4, 3, 3, 16,
     ["Protective","Loyal","Practical","Generous"],
     ["Wary","Dutiful","Boastful","Transactional"],
     ["Territorial","Violent Outburst","Righteous Wrath","Suspicion"]),
 9: ("Ennead - the Horizon", 0, 8, 2, 6, 18,
     ["Forgiving","Generous","Tender","Mentoring"],
     ["Melancholic","Distracted","Curious","Indifferent"],
     ["Cold Refusal","Mockery","Grudge","Predatory"]),
}
KIND = ["Generous","Protective","Tender","Teasing-Fond","Mentoring","Hospitable","Loyal",
        "Forgiving","Practical","Reverent","Confiding","Gruff-Kind"]
MIDDLE = ["Dutiful","Transactional","Distracted","Curious","Wary","Indifferent","Flirtatious",
          "Melancholic","Boastful","Gossipy","Evasive","Pious","Bargaining-Humour","Mercurial"]
HOSTILE = ["Contempt","Cold Refusal","Mockery","Suspicion","Territorial","Righteous Wrath",
           "Manipulation","Obstruction","Envy/Spite","Fear-Aggression","Grudge","Predatory",
           "Violent Outburst"]
STATION = {1:("Sovereign",1),2:("Warden",1),3:("Steward",0),4:("Steward",0),5:("Herald",0),
           6:("Threshold",0),7:("Hand",0),8:("Hand",0),9:("Sworn",1),10:("Unmoored",-1)}
OFFICE = ["Teaches","Reveals","Finds","Reconciles","Kindles","Carries","Builds","Ruins",
          "Companions","Transforms","Mends","Foretells"]
OPPOSITES = ["Limit/Boundless","Odd/Even","One/Many","Right/Left","Pressing/Yielding",
             "Rest/Motion","Straight/Curved","Light/Dark","Good/Petty","Square/Oblong"]
RATIO = {1:("Unison 1:1",2,1),2:("Octave 2:1",3,2),3:("Fifth 3:2",5,3),4:("Fourth 4:3",7,4)}
INWARD = ["to grieve properly","to be forgiven by someone dead","to stop being afraid",
 "to feel young again","to be left alone","to believe in something again",
 "to be seen as their parent never saw them","to forget a face","to stay exactly as they are",
 "to be loved back","to make peace with a choice","to not be the last of their line",
 "to deserve their position","to stop wanting a drink","for a sibling's ship to come home",
 "to understand their own anger","to know if they were right","to sleep without dreaming",
 "to matter","something they can't name"]
OPEN = ["recover an object","deliver word to someone far","be rid of a debt or creditor",
 "find a missing person","protect someone for a stretch","gain proof of a wrong",
 "get something past a gate or law","learn a fact they can't reach","break a rival's hold",
 "bring someone home","acquire rare material","end a threat"]
QUIRK = ["counts coins twice","never sits with back to a door",
 "speaks of self in third person when nervous","hums the same four notes",
 "refuses to say a certain word","collects small bones","always offers salt",
 "calls everyone by the wrong name, kindly","can't abide whistling",
 "touches iron before deciding","laughs at funerals","keeps a dead person's hat",
 "answers in proverbs","sleeps in the afternoon","never finishes a drink","counts steps",
 "lies about trivial things only","pockets one small thing from every visitor, returns it later",
 "feeds birds obsessively","always knows the hour without looking"]
OCCUR = ["gives a gift, then asks for it back next time","insults you while mending your coat",
 "helps your rival the same day they helped you","warns you off, then follows you",
 "swears they don't know you, in front of others","overpays you, then haggles a copper",
 "praises a thing they clearly hate","weeps at good news",
 "shuts the door, leaves food outside it","tells a truth that harms them",
 "lies to protect you, badly","acts as if a past meeting went the opposite way"]
AGENCY = {1:"Off-pattern form",2:"Off-pattern form",3:"Inversion",4:"Drive surfaces",
          5:"The other face",6:"Free will"}

d = lambda n: random.randint(1, n)

def reduce_name(name):
    raw = sum(PYTH[c] for c in name.upper() if c in PYTH)
    n = raw
    while n > 9:
        n = sum(int(x) for x in str(n))
    return raw, n

def tetrad_pick(forms):
    r = d(10)
    return forms[0 if r <= 4 else 1 if r <= 7 else 2 if r <= 9 else 3], r

def cmd_npc(a):
    if a.name:
        raw, num = reduce_name(a.name)
        decad = raw > 0 and raw % 10 == 0
        print(f"Name: {a.name}  (sum {raw} -> {num}{', DECAD-TOUCHED' if decad else ''})")
    else:
        num, decad = d(9), False
        print(f"Unnamed NPC  (d9 -> {num})")
    t = TEMP[num]
    sr = d(10); st, gmod = STATION[sr]
    guard = max(0, t[3] + gmod)
    print(f"Temperament: {num} {t[0]} | Warmth {t[1]:+d}, Swing d{t[2]}, Candor {t[4]}, Agency {t[5]}%")
    print(f"Station: {st} (d10={sr}) | Guard {guard}")
    offs = [OFFICE[d(12)-1]]
    if d(4) == 4:
        offs.append(OFFICE[d(12)-1])
    print("Office: " + " + ".join(dict.fromkeys(offs)))
    dr = d(20)
    if dr <= (4 if decad else 2):
        print(f"Drive: STILL (d20={dr}) - wants nothing in particular")
    elif dr <= 15:
        print(f"Drive: INWARD (d20={dr}) - {INWARD[d(20)-1]}  [never a request]")
    else:
        kind = "FULL" if d(3) == 3 else "PARTIAL"
        print(f"Drive: OPEN/{kind} (d20={dr}) - {OPEN[d(12)-1]}  [only through the five gates]")
    rname, die, a_max = RATIO[d(4)]
    print(f"Opposites: {OPPOSITES[d(10)-1]} at {rname}  (check d{die}: 1-{a_max} side A)")
    qs = random.sample(QUIRK, 2 if decad else 1)
    print("Quirk: " + "; ".join(qs))

def cmd_meet(a):
    t = TEMP[a.temp]
    s1, s2 = d(t[2]), d(t[2])
    mood = t[1] + a.trust + s1 - s2
    if mood <= -6: band, forms = "Hostile", t[8]
    elif mood <= -2: band, forms = "Cool", t[7]
    elif mood <= 1: band, forms = "Neutral", t[7]
    elif mood <= 5: band, forms = "Warm", t[7]
    else: band, forms = "Kind", t[6]
    form, r = tetrad_pick(forms)
    print(f"Mood {t[1]:+d}{a.trust:+d}+({s1}-{s2}) = {mood:+d} -> {band}: {form} (d10={r})")
    ag = d(100)
    if ag <= t[5]:
        k = d(6); res = AGENCY[k]
        extra = ""
        if res == "Off-pattern form":
            pool = [f for f in KIND + MIDDLE + HOSTILE if f not in t[6] + t[7] + t[8]]
            extra = f" -> {random.choice(pool) if pool else random.choice(KIND+MIDDLE+HOSTILE)}"
        print(f"AGENCY (d100={ag} <= {t[5]}): {res}{extra}")
    else:
        print(f"Agency: no (d100={ag} > {t[5]})")
    o = d(20)
    if o == 1:
        print(f"Contradictory occurrence: {OCCUR[d(12)-1]}")

def cmd_ask(a):
    t = TEMP[a.temp]
    guard = a.guard if a.guard is not None else t[3]
    if a.drive != "open":
        print(f"NO ASK. Drive is {a.drive}: decline, deflect, or a trivial courtesy at most."); return
    if a.asked:
        print("NO ASK. Already asked this scene."); return
    if not a.touched:
        print("NO ASK. Conversation hasn't touched the drive."); return
    r = d(10)
    kairos = r <= t[4] or (a.temp == 7 and r == 7)
    if not kairos:
        print(f"NO ASK. Kairos failed (d10={r} > Candor {t[4]})."); return
    if a.trust < guard:
        print(f"HINT ONLY. Kairos ok (d10={r}) but Trust {a.trust} < Guard {guard}: oblique hint."); return
    print(f"MAY ASK (d10={r} <= {t[4]}, Trust {a.trust} >= Guard {guard}). Pride may still refuse.")

def cmd_roll(a):
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", a.expr.strip().lower())
    if not m: sys.exit("format: NdS[+M]")
    n, s, mod = int(m[1] or 1), int(m[2]), int(m[3] or 0)
    rs = [d(s) for _ in range(n)]
    print(f"{a.expr}: {rs} {mod:+d} = {sum(rs)+mod}" if mod else f"{a.expr}: {rs} = {sum(rs)}")

p = argparse.ArgumentParser(description="NPC Temperament Engine")
p.add_argument("--seed", type=int)
sp = p.add_subparsers(dest="cmd", required=True)
x = sp.add_parser("npc"); x.add_argument("name", nargs="?"); x.set_defaults(f=cmd_npc)
x = sp.add_parser("meet"); x.add_argument("temp", type=int, choices=range(1, 10))
x.add_argument("--trust", type=int, default=0); x.set_defaults(f=cmd_meet)
x = sp.add_parser("ask"); x.add_argument("temp", type=int, choices=range(1, 10))
x.add_argument("--trust", type=int, default=0); x.add_argument("--guard", type=int)
x.add_argument("--drive", choices=["still", "inward", "open"], required=True)
x.add_argument("--touched", action="store_true"); x.add_argument("--asked", action="store_true")
x.set_defaults(f=cmd_ask)
x = sp.add_parser("roll"); x.add_argument("expr"); x.set_defaults(f=cmd_roll)

if __name__ == "__main__":
    args = p.parse_args(sys.argv[1:] if "--seed" not in sys.argv else sys.argv[1:])
    random.seed(args.seed)
    args.f(args)
