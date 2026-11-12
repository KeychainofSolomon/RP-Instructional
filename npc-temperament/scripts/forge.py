#!/usr/bin/env python3
"""NPC Temperament Engine. Rules: SKILL.md and references/. Python 3.8+, standard library only.

Dice go upstream: every random roll decides something about a character's life, history
or day. Reactions are then computed from those causes, never rolled directly.
"""
import argparse, json, math, random, sys

AX = ["Candour", "Volatility", "Energy", "Warmth", "Discipline", "Openness", "Dominance"]
C, V, E, W, D, O, M = range(7)
DIALS = ["Violence", "Order", "Scarcity", "Strangeness", "Faith", "Power", "Deceit"]
DKEY = dict(zip("VOSXFPD", DIALS))
DEFAULT_DIALS = [1, 1, 1, 0, 1, 1, 1]
RUNGS = ["Survival", "Safety", "Means", "Comfort", "Belonging", "Standing", "Selfhood", "Meaning"]
PHYS = RUNGS[:4]
STATE = {1: "Sated", 0: "Steady", -1: "Wanting", -2: "Starved"}
CREEDS = ["Strength", "Gain", "Excellence", "Pleasure", "Thrill", "Freedom",
          "Mercy", "Justice", "Kin", "Faith", "Order", "Security"]
APPROACHES = ["deference", "familiarity", "bluntness", "flattery", "haggling", "humour",
              "patience", "pressure", "generosity", "principle", "pity"]
LEVITY = ("Flirtatious", "Boastful", "Performing", "Bargaining-Humour", "Gossipy", "Teasing-Fond")
BANDS = ["Hostile", "Cool", "Neutral", "Warm", "Kind"]
DANGER = ["violence", "injury", "disaster", "authority", "contagion", "uncanny"]


def S(name, sketch, ax, emph, dis, creed, kind, mid, host, danger, base, boost="", damp=""):
    return dict(name=name, sketch=sketch, ax=ax, emph=emph, dis=dis, creed=creed, kind=kind,
                mid=mid, host=host, danger=danger, base=base, boost=boost, damp=damp)


STYLES = [
 S("Vigilant", "Watches motives, expects betrayal, remembers slights.",
   (0, 2, -1, -2, 1, -1, 1), ("Safety", "Selfhood"), "Belonging", ("Security", "Kin"),
   ["Protective", "Candid", "Loyal", "Practical"], ["Wary", "Testing", "Evasive", "Dutiful"],
   ["Suspicion", "Fear-Aggression", "Grudge", "Cold Refusal"], (-1, "Suspicion"), 3, "VDX"),
 S("Solitary", "Self-sufficient, unmoved by company, content alone.",
   (1, -2, -3, -1, 0, 0, -1), ("Selfhood", "Comfort"), "Belonging", ("Freedom", "Security"),
   ["Practical", "Gruff-Kind", "Candid", "Generous"], ["Indifferent", "Withdrawn", "Dutiful", "Curious"],
   ["Cold Refusal", "Contempt", "Territorial", "Obstruction"], (0, "Withdrawn"), 3, "SX"),
 S("Visionary", "Sees patterns and meanings others miss; holds odd beliefs.",
   (1, 1, -1, 0, -2, 3, 0), ("Meaning", "Selfhood"), "Standing", ("Freedom", "Faith"),
   ["Confiding", "Mentoring", "Tender", "Generous"], ["Curious", "Preaching", "Distracted", "Evasive"],
   ["Suspicion", "Mockery", "Cold Refusal", "Fear-Aggression"], (0, "Preaching"), 2, "XF"),
 S("Adventurous", "Lives for risk and the moment; rules are suggestions.",
   (-2, -1, 2, 0, -3, 2, 1), ("Comfort", "Means"), "Safety", ("Thrill", "Freedom"),
   ["Teasing-Fond", "Generous", "Protective", "Respectful"], ["Flirtatious", "Bargaining-Humour", "Boastful", "Testing"],
   ["Mockery", "Manipulation", "Violent Outburst", "Toying"], (1, "Teasing-Fond"), 3, "V", "O"),
 S("Mercurial", "Feels everything at full volume; love and hate trade places fast.",
   (0, 3, 1, 1, -2, 1, 0), ("Belonging", "Selfhood"), "Means", ("Pleasure", "Kin"),
   ["Tender", "Confiding", "Generous", "Protective"], ["Mercurial", "Flirtatious", "Melancholic", "Curious"],
   ["Violent Outburst", "Envy/Spite", "Grudge", "Fear-Aggression"], (2, "Mercurial"), 3),
 S("Dramatic", "Needs to be seen; turns life into performance.",
   (-1, 2, 3, 1, -1, 1, 0), ("Standing", "Belonging"), "Meaning", ("Pleasure", "Thrill"),
   ["Hospitable", "Teasing-Fond", "Generous", "Confiding"], ["Performing", "Gossipy", "Flirtatious", "Boastful"],
   ["Mockery", "Envy/Spite", "Manipulation", "Cold Refusal"], (-1, "Performing"), 3, "P", "S"),
 S("Self-Assured", "Certain of their own worth; expects others to notice.",
   (-3, -1, 2, -1, 0, 0, 3), ("Standing", "Means"), "Belonging", ("Excellence", "Strength"),
   ["Generous", "Mentoring", "Protective", "Respectful"], ["Boastful", "Appraising", "Indifferent", "Performing"],
   ["Contempt", "Mockery", "Righteous Wrath", "Envy/Spite"], (1, "Boastful"), 3, "P"),
 S("Sensitive", "Longs to belong, dreads judgement, hides first.",
   (2, 2, -2, 1, 1, 0, -2), ("Belonging", "Safety"), "Standing", ("Kin", "Security"),
   ["Tender", "Confiding", "Hospitable", "Loyal"], ["Withdrawn", "Wary", "Evasive", "Melancholic"],
   ["Fear-Aggression", "Cold Refusal", "Obstruction", "Grudge"], (-1, "Withdrawn"), 3, "P", "V"),
 S("Devoted", "Attaches, serves, defers; loyalty is identity.",
   (2, 1, 0, 3, 1, -1, -3), ("Belonging", "Safety"), "Selfhood", ("Kin", "Faith"),
   ["Loyal", "Hospitable", "Tender", "Reverent"], ["Dutiful", "Ritual", "Gossipy", "Wary"],
   ["Grudge", "Fear-Aggression", "Obstruction", "Envy/Spite"], (1, "Loyal"), 3, "FP"),
 S("Conscientious", "Order, standards, the job done right.",
   (2, 0, -1, -1, 3, -2, 1), ("Selfhood", "Means"), "Comfort", ("Order", "Excellence"),
   ["Practical", "Mentoring", "Candid", "Loyal"], ["Dutiful", "Ritual", "Appraising", "Wary"],
   ["Obstruction", "Righteous Wrath", "Contempt", "Cold Refusal"], (-1, "Obstruction"), 3, "O"),
 S("Leisurely", "Own pace, own way; resists demands without open defiance.",
   (-1, 0, 0, -1, -3, 0, -1), ("Comfort", "Selfhood"), "Standing", ("Pleasure", "Freedom"),
   ["Gruff-Kind", "Hospitable", "Teasing-Fond", "Forgiving"], ["Distracted", "Indifferent", "Bargaining-Humour", "Evasive"],
   ["Sabotage", "Obstruction", "Mockery", "Grudge"], (-1, "Evasive"), 3, "", "O"),
 S("Serious", "Expects the worst, carries the weight, does the duty.",
   (2, 1, -2, 0, 2, -1, -1), ("Meaning", "Safety"), "Comfort", ("Order", "Faith"),
   ["Candid", "Practical", "Protective", "Tender"], ["Melancholic", "Dutiful", "Ritual", "Withdrawn"],
   ["Cold Refusal", "Righteous Wrath", "Contempt", "Grudge"], (0, "Practical"), 3, "S"),
 S("Self-Sacrificing", "Gives until it hurts, and lets you know it hurt.",
   (3, 1, 0, 3, 1, 0, -2), ("Belonging", "Meaning"), "Comfort", ("Mercy", "Faith"),
   ["Generous", "Tender", "Forgiving", "Hospitable"], ["Dutiful", "Melancholic", "Ritual", "Gossipy"],
   ["Reproach", "Grudge", "Obstruction", "Envy/Spite"], (1, "Protective"), 2, "FS"),
 S("Commanding", "Takes control; hierarchy is natural, softness is weakness.",
   (-1, 0, 1, -3, 2, -1, 3), ("Standing", "Means"), "Belonging", ("Strength", "Order"),
   ["Protective", "Practical", "Respectful", "Mentoring"], ["Appraising", "Dutiful", "Boastful", "Testing"],
   ["Territorial", "Righteous Wrath", "Violent Outburst", "Toying"], (1, "Practical"), 2, "OPV"),
 S("Benevolent", "Genuinely warm; helps because that is who they are.",
   (3, -1, 1, 3, 0, 1, -1), ("Belonging", "Meaning"), "Means", ("Mercy", "Justice"),
   ["Hospitable", "Tender", "Forgiving", "Generous"], ["Curious", "Gossipy", "Ritual", "Melancholic"],
   ["Reproach", "Cold Refusal", "Righteous Wrath", "Grudge"], (1, "Tender"), 3, "", "VD"),
 S("Self-Made", "Answers to their own judgement; trades value for value, despises dependence.",
   (1, -2, 0, -2, 3, 1, 2), ("Selfhood", "Means"), "Belonging", ("Excellence", "Freedom"),
   ["Respectful", "Candid", "Mentoring", "Practical"], ["Appraising", "Transactional", "Testing", "Indifferent"],
   ["Contempt", "Cold Refusal", "Righteous Wrath", "Mockery"], (0, "Appraising"), 2, "P"),
 S("Schemer", "Plans inside plans; people are pieces on a board.",
   (-3, -2, 1, 0, 2, 1, 2), ("Means", "Standing"), "Meaning", ("Gain", "Strength"),
   ["Generous", "Confiding", "Protective", "Respectful"], ["Curious", "Gossipy", "Appraising", "Flirtatious"],
   ["Manipulation", "Sabotage", "Predatory", "Mockery"], (0, "Appraising"), 1, "DP"),
 S("Zealot", "Certain; the cause is everything and doubt is betrayal.",
   (1, 1, 1, -1, 2, -3, 2), ("Meaning", "Belonging"), "Comfort", ("Faith", "Order"),
   ["Reverent", "Protective", "Generous", "Mentoring"], ["Preaching", "Ritual", "Testing", "Wary"],
   ["Righteous Wrath", "Contempt", "Violent Outburst", "Suspicion"], (1, "Preaching"), 1, "FFV"),
 S("Predator", "Calm, curious, merciless; violence is the honest law of the world.",
   (-2, -3, 1, -3, 1, 2, 3), ("Selfhood", "Meaning"), "Safety", ("Strength", "Nothing"),
   ["Respectful", "Generous", "Mentoring", "Candid"], ["Testing", "Curious", "Appraising", "Preaching"],
   ["Toying", "Predatory", "Contempt", "Violent Outburst"], (1, "Curious"), 0, "VV", "O"),
 S("Professional", "Competent, cool, deniable; it's only business.",
   (0, -3, 0, -1, 2, 0, 0), ("Means", "Safety"), "Meaning", ("Gain", "Excellence"),
   ["Practical", "Respectful", "Candid", "Protective"], ["Transactional", "Appraising", "Dutiful", "Indifferent"],
   ["Cold Refusal", "Obstruction", "Predatory", "Suspicion"], (0, "Practical"), 2, "PD"),
]
SBY = {s["name"]: s for s in STYLES}
FACES = ["Benevolent", "Devoted", "Conscientious", "Professional", "Self-Assured", "Dramatic"]
INVERTERS = ("Zealot", "Self-Sacrificing", "Predator")

STATIONS = {1: ("Head", 1, 3), 2: ("Warden", 1, 2), 3: ("Steward", 0, 1), 4: ("Steward", 0, 1),
            5: ("Herald", 0, 1), 6: ("Threshold", 0, 1), 7: ("Hand", 0, 0), 8: ("Hand", 0, 0),
            9: ("Sworn", 1, 2), 10: ("Unmoored", -1, 0)}  # name, guard mod, rank
RANK = {v[0]: v[2] for v in STATIONS.values()}
OFFICES = ["Teaches", "Reveals", "Finds", "Reconciles", "Kindles", "Carries", "Builds", "Ruins",
           "Companions", "Transforms", "Mends", "Forecasts"]
OPPOSITES = ["Limit/Boundless", "Odd/Even", "One/Many", "Right/Left", "Pressing/Yielding",
             "Rest/Motion", "Straight/Curved", "Light/Dark", "Good/Petty", "Square/Oblong"]
RATIO = {1: ("1:1", 2, 1), 2: ("2:1", 3, 2), 3: ("3:2", 5, 3), 4: ("4:3", 7, 4)}
QUIRKS = ["counts money twice", "never sits with back to a door",
          "speaks of self in third person when nervous", "hums the same four notes",
          "refuses to say a certain word", "collects small useless objects of one kind",
          "always offers something to drink", "calls everyone by the wrong name, kindly",
          "can't stand whistling", "touches a lucky object before deciding",
          "laughs at the wrong moments", "keeps a dead person's belonging close",
          "answers in sayings", "sleeps at odd hours", "never finishes a drink", "counts steps",
          "lies about trivial things only", "pockets one small thing from every visitor, returns it later",
          "feeds animals obsessively", "always knows the time without looking"]
TIE_KINDS = ["kin", "lover", "friend", "mentor", "rival", "enemy", "creditor", "debtor",
             "master", "group", "place", "cause", "object", "dependant"]
ENEMY_WOULD = ["avoid them", "speak against them", "work against them quietly",
               "hurt someone they love", "hurt them", "see them dead"]
CODES = ["repays every debt", "never harms a child", "a guest under their roof is untouchable",
         "never lies to kin", "never backs down in front of witnesses", "never takes charity",
         "keeps every promise to the letter", "never works for a certain power",
         "their people come first", "never strikes first",
         "tells the truth when asked directly", "never leaves their dead behind"]
COMPULSIONS = ["greed", "gambling", "lust", "cruelty", "jealousy", "lying", "curiosity",
               "cleanliness and order", "a substance", "vengeance", "collecting",
               "can't back down"]

RUNG_TIES = {"Survival": ["dependant", "kin"], "Safety": ["enemy"],
             "Means": ["creditor", "master"], "Comfort": ["place"],
             "Belonging": ["kin", "lover", "friend", "group", "dependant"],
             "Standing": ["group", "rival", "master"], "Selfhood": ["master", "rival", "mentor", "group"],
             "Meaning": ["cause"]}
FALLBACK = {"Survival": "the people they feed", "Safety": "someone who wishes them harm",
            "Means": "the one they owe", "Comfort": "home", "Belonging": "someone close",
            "Standing": "their peers", "Selfhood": "whoever holds power over them",
            "Meaning": "what they believe in"}
CAUSES = {
 "Survival": (["went hungry or thirsty", "fell sick", "was out in the cold or heat too long",
               "supplies ran short for {tie}"],
              ["ate and drank well", "recovered from sickness", "found supplies for {tie}", "slept warm and dry"]),
 "Safety": (["was threatened by {tie}", "saw violence close by", "had their home or den broken into",
             "noticed someone watching them"],
            ["a threat from {tie} receded", "gained protection", "saw a danger dealt with", "felt their street was calm"]),
 "Means": (["lost money or work", "was pressed for payment by {tie}", "had their tools or gear break",
            "was robbed or cheated"],
           ["got paid", "made a good deal", "eased a debt with {tie}", "found a new opportunity"]),
 "Comfort": (["slept badly or was in pain", "went without a small pleasure they rely on",
              "had {tie} spoiled or disturbed", "was bored to the bone"],
             ["indulged a pleasure", "finally rested", "received a small gift", "had a beautiful moment at {tie}"]),
 "Belonging": (["fought with {tie}", "had no word from {tie}", "was left out by others",
                "marked a lonely anniversary"],
               ["spent good time with {tie}", "was welcomed in", "made up with {tie}", "had word from {tie}"]),
 "Standing": (["was humiliated in front of {tie}", "was passed over", "watched {tie} get ahead",
               "heard a rumour about themself"],
              ["was praised in public", "was recognised by {tie}", "got the better of {tie}", "was asked for advice"]),
 "Selfhood": (["was made to act against their own code", "had {tie} override their judgement",
               "failed their own standard", "caught sight of what they've become"],
              ["made a hard choice their own way", "stood up to {tie}", "finished something on their own terms",
               "felt like themself again"]),
 "Meaning": (["doubted {tie}", "saw a hoped-for sign come to nothing", "was let down by {tie}",
              "witnessed something cruel and pointless"],
             ["saw a sign that confirmed {tie}", "made progress in {tie}", "kept a ritual or vow",
              "glimpsed a purpose"]),
}
ORDINARY = ["an ordinary, busy day", "an ordinary, dull day", "an ordinary day; the weather was the news",
            "an ordinary day of routine"]
DRIVES = {
 "Survival": (["to stop fearing hunger", "to beat a dependency", "to accept a failing body", "to stop hoarding"],
              ["a steady source of food or water", "medicine for {tie} or themself", "proper shelter",
               "a cure or treatment"]),
 "Safety": (["to feel safe in their own home", "to stop flinching", "to forgive themself for running",
             "to stop waiting for the knock"],
            ["to be rid of {tie}", "protection for someone they love", "to get out of where they are",
             "to clear their name with the authorities"]),
 "Means": (["to stop measuring life in money", "to make peace with having failed", "to stop envying those who have more",
            "to feel they have earned enough"],
           ["to clear a debt with {tie}", "to recover stolen goods", "to land a deal or job",
            "a permit, tool or licence"]),
 "Comfort": (["to enjoy anything again", "to stop needing a vice", "to rest without guilt", "to feel at home"],
             ["a specific rare pleasure", "to fix up {tie}", "a supply of their vice", "a real day off duty"]),
 "Belonging": (["to be loved back", "to grieve {tie}", "to be forgiven by someone gone", "to stop being the outsider"],
               ["to find {tie}", "to get word to {tie}", "to be accepted by {tie}", "to bring {tie} home"]),
 "Standing": (["to deserve their position", "to stop needing approval", "to outgrow a disgrace",
               "to be seen as {tie} never saw them"],
              ["recognition from {tie}", "to restore their name", "to beat {tie} at something",
               "proof of worth: a commission, title or contract"]),
 "Selfhood": (["to know who they really are", "to stop lying to themself", "to make peace with a choice",
               "to stop being what {tie} made them"],
              ["to get free of an oath, contract or owner", "to recover a record of who they were",
               "to get out from under {tie}", "a chance to act on their own judgement"]),
 "Meaning": (["to believe again", "to know if they were right", "to matter", "something they can't name"],
             ["a relic, text or key to {tie}", "to reach a place that matters", "to finish a work begun for {tie}",
              "to witness proof"]),
}
ODD_PLAIN = ["gives a gift, then asks for it back next time", "insults you while fixing something of yours",
             "helps your rival the same day they helped you", "warns you off, then follows you",
             "swears they don't know you, in front of others", "overpays you, then haggles a coin",
             "praises a thing they clearly hate", "weeps at good news", "shuts the door, leaves food outside it",
             "tells a truth that harms them", "lies to protect you, badly",
             "recounts your last meeting with the details wrong"]
ODD_UNCANNY = ["is mid-conversation with no one when you arrive", "sets a place for someone who never comes",
               "every clock or screen near them is wrong by the same few minutes",
               "repeats your last sentence back exactly, then carries on",
               "animals or machines nearby behave oddly around them",
               "asks, sincerely, what year it is", "carries an object they don't remember getting",
               "checks a door they locked; it is unlocked"]
EVENTS = {  # trust sign, default size, marks [(axis, +-1)], need effects {rung: step}
 "kindness": (1, 1, [(W, 1)], {"Belonging": 1}),
 "rescue": (1, 2, [(W, 1), (C, 1)], {"Safety": 1}),
 "gift": (1, 1, [], {"Means": 1}),
 "respect": (1, 1, [(M, 1)], {"Standing": 1}),
 "betrayal": (-1, 2, [(W, -1), (C, -1), (V, 1)], {"Belonging": -1}),
 "humiliation": (-1, 1, [(V, 1), (M, -1)], {"Standing": -1}),
 "threat": (-1, 1, [(V, 1)], {"Safety": -1}),
 "lie-caught": (-1, 1, [(W, -1)], {}),
 "triumph": (0, 0, [(M, 1), (D, 1)], {"Selfhood": 1}),
 "loss": (0, 0, [(E, -1), (V, 1)], {"Belonging": -2}),
 "code-broken": (0, 0, [(C, -1)], {"Selfhood": -2}),
 "fell-ill": (0, 0, [], {"Survival": -1}),
 "intoxicated": (0, 0, [], {"Comfort": 1}),
}
STRATAGEMS = [(3, "Overwhelm: confront openly, or toy with them"), (1, "Press: demand terms, show strength"),
              (0, "Wait and probe: test them, seek allies, feint"),
              (-2, "Avoid battle: deceive, appear compliant, strike where unguarded"),
              (-99, "Yield, flee, or appeal to a stronger power")]


def d(n):
    return random.randint(1, n)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def rnd(x):
    return int(math.copysign(math.floor(abs(x) + 0.5), x))


def tz(x):
    return int(x)


def wpick(items, weights):
    total = sum(weights)
    if total <= 0:
        return random.choice(items)
    r = random.uniform(0, total)
    for it, w in zip(items, weights):
        r -= w
        if r <= 0:
            return it
    return items[-1]


def tetrad(forms):
    r = d(10)
    return forms[0 if r <= 4 else 1 if r <= 7 else 2 if r <= 9 else 3]


def parse_dials(s):
    if not s:
        return list(DEFAULT_DIALS)
    vals = [clamp(int(x), 0, 3) for x in s.split(",")]
    if len(vals) != 7:
        sys.exit("--dials needs 7 values: Violence,Order,Scarcity,Strangeness,Faith,Power,Deceit")
    return vals


def dial(dials, letter):
    return dials[DIALS.index(DKEY[letter])]


def style_weight(st, dials):
    return max(0, st["base"] + sum(dial(dials, k) for k in st["boost"]) - sum(dial(dials, k) for k in st["damp"]))


def pick_styles(n, dials, exclude=()):
    pool = [s for s in STYLES if s["name"] not in exclude]
    out = []
    for _ in range(n):
        ws = [style_weight(s, dials) for s in pool]
        if sum(ws) == 0:
            ws = [1] * len(pool)
        s = wpick(pool, ws)
        out.append(s)
        pool.remove(s)
    return out


# ---------- derived values (recomputed whenever axes drift) ----------
SENS = {-3: 0.5, -2: 0.5, -1: 1, 0: 1, 1: 1, 2: 2, 3: 3}


def derive(n):
    a = n["axes"]
    c, v, e, w, dd, o, m = a
    st_guard = {s[0]: s[1] for s in STATIONS.values()}[n["station"]]
    h = lambda x: clamp(tz(x / 2), -2, 2)
    row = {"deference": h(m - c), "familiarity": h(e + w), "bluntness": h(c - v), "flattery": h(e - c),
           "haggling": h(e - w), "humour": h(e + o), "patience": h(dd - e), "principle": h(dd - o),
           "pity": h(w + v),
           "pressure": clamp(tz((-v - w) / 2) - 1 - (1 if m >= 2 else 0), -2, 2),
           "generosity": clamp(1 - tz(c / 2) - (1 if m >= 3 else 0), -2, 2)}
    if n["authenticity"]["kind"] == "Hollow":
        row["pity"] = 0
        row["principle"] = 0
    n["derived"] = {
        "baseline": w,
        "sensitivity": SENS[v],
        "guard": clamp(2 + (e <= -2) + (w <= -2) + (m >= 2) - (e >= 2) - (w >= 2) + st_guard, 0, 6),
        "openness_target": clamp(4 + e - (1 if m >= 2 else 0), 1, 8),
        "agency": 10 if n["flags"]["outlier"] else clamp(2 + (o >= 2) + (v >= 2) + (dd <= -2), 2, 5),
        "nerve": clamp(v + 2, 0, 5),
        "fuse": -6 + n["var"]["fuse"] + (1 if v >= 2 else 0) - (1 if dd >= 2 else 0),
        "glow": 6 + n["var"]["glow"] - (1 if e >= 2 else 0) + (1 if (e <= -2 or w <= -2) else 0),
        "displacer": v >= 2 and w <= -1,
        "slip": clamp(3 + 2 * (v >= 2) - 2 * (dd >= 2), 1, 7),
        "approach": row,
    }


def voice_manner(st):
    man = {}
    for band, key in (("Kind", "kind"), ("Middle", "mid"), ("Hostile", "host")):
        p = tetrad(st[key])
        alt = p
        while alt == p:
            alt = tetrad(st[key])
        man[band] = [p, alt]
    return man


def fill(text, n, rung):
    if "{tie}" not in text:
        return text
    prefs = RUNG_TIES.get(rung, [])
    cands = [t for t in n["ties"] if t["kind"] in prefs]
    label = random.choice(cands)["label"] if cands else FALLBACK.get(rung, "someone")
    return text.replace("{tie}", label)


def build(dials, name=None, kind="person"):
    n = {"name": name or "(unnamed)", "type": kind, "dials": dials, "day": 0, "condition": "present",
         "memory": [], "trust": {}, "marks": {}, "starved_days": {r: 0 for r in RUNGS},
         "sated_days": {r: 0 for r in RUNGS}, "recent_causes": [], "today": None, "shifts": {}}
    fl = d(100)
    n["flags"] = {"complete": 91 <= fl <= 99, "outlier": fl == 100}
    br = d(20)
    for top, label, fr in [(6, "Pure", [1]), (11, "Leaning", [0.75, 0.25]), (14, "Fifth", [0.6, 0.4]),
                           (17, "Split", [0.5, 0.5]), (19, "Quartered", [0.25] * 4), (20, "Scattered", [0.125] * 8)]:
        if br <= top:
            break
    sts = pick_styles(len(fr), dials)
    n["blend"] = label
    n["voices"] = [{"style": s["name"], "frac": f, "manner": voice_manner(s)} for s, f in zip(sts, fr)]
    ax = [rnd(sum(f * s["ax"][i] for s, f in zip(sts, fr))) for i in range(7)]
    for i in range(7):
        r = d(6)
        ax[i] = clamp(ax[i] + (-1 if r == 1 else 1 if r == 6 else 0), -3, 3)
    n["axes"] = ax
    n["var"] = {"fuse": d(3) - 2, "glow": d(3) - 2}
    sr = d(10)
    n["station"] = STATIONS[sr][0]
    offs = [OFFICES[d(12) - 1]] + ([OFFICES[d(12) - 1]] if d(4) == 4 else [])
    n["office"] = list(dict.fromkeys(offs))
    dom = sts[0]["name"]
    # authenticity
    gmax = max(9, 16 - dial(dials, "D") - dial(dials, "X") // 2 - (4 if dom == "Schemer" else 0))
    ar = d(20)
    ak = ("Genuine" if ar <= gmax else ("Hollow" if d(2) == 1 else "Unanchored") if ar == 20
          else "Shifting" if ar == 19 else "Borrowed" if ar == 18 else "Masked")
    core_names = [s["name"] for s in sts]
    faces = []
    if ak in ("Masked", "Hollow"):
        faces = [random.choice([f for f in FACES if f not in core_names] or FACES)]
    elif ak == "Borrowed":
        faces = [pick_styles(1, dials, core_names)[0]["name"]]
    elif ak == "Shifting":
        pool = [f for f in FACES if f not in core_names]
        if len(pool) < 2:
            pool = [s["name"] for s in STYLES if s["name"] not in core_names] or FACES
        faces = random.sample(pool, 2)
    n["authenticity"] = {"kind": ak, "faces": [{"style": f, "manner": voice_manner(SBY[f])} for f in faces]}
    # ties
    n["ties"] = []
    for i in range(d(3) + 1):
        k = TIE_KINDS[d(14) - 1]
        t = {"kind": k, "label": "their " + k, "loyalty": d(6), "reach": d(6)}
        if k == "enemy":
            t["would"] = ENEMY_WOULD[d(6) - 1]
        n["ties"].append(t)
    if ak == "Borrowed":
        n["authenticity"]["source"] = random.choice(n["ties"])["label"]
    # needs
    acc = {r: (2.0 if r in ("Survival", "Safety") else 1.0) for r in RUNGS}
    for s, f in zip(sts, fr):
        for r in s["emph"]:
            acc[r] += 2 * f
        acc[s["dis"]] -= f
    wts = {r: clamp(rnd(acc[r]), 0, 3) for r in RUNGS}
    hunger = random.choice(RUNGS)
    wts[hunger] = clamp(wts[hunger] + 1, 0, 3)
    if dial(dials, "F") >= 2: wts["Meaning"] = clamp(wts["Meaning"] + 1, 0, 3)
    if dial(dials, "X") >= 2: wts["Selfhood"] = clamp(wts["Selfhood"] + 1, 0, 3)
    if dial(dials, "P") >= 2: wts["Standing"] = clamp(wts["Standing"] + 1, 0, 3)
    wts["Survival"] = max(1, wts["Survival"]); wts["Safety"] = max(1, wts["Safety"])
    if ak == "Hollow":
        wts["Selfhood"] = 0; wts["Meaning"] = 0; wts["Belonging"] = min(wts["Belonging"], 1)
    orr = d(20)
    inv_lo = 11 if dom in INVERTERS else 16
    order = ("Standard" if orr < inv_lo else "Inverted" if orr <= 18 else "Fixated" if orr == 19 else "Numb")
    states = {r: 0 for r in RUNGS}
    live = [r for r in RUNGS if wts[r] > 0]
    for r in random.sample(live, min(2, len(live))):
        states[r] = -1
    sat = [r for r in live if states[r] == 0]
    if sat:
        states[random.choice(sat)] = 1
    poor = n["station"] in ("Hand", "Unmoored")
    if dial(dials, "S") >= 2: states["Survival"] = min(states["Survival"], -1)
    if dial(dials, "S") >= 3 and poor: states["Survival"] = -2
    if dial(dials, "V") >= 2: states["Safety"] = min(states["Safety"], -1)
    if dial(dials, "P") >= 2 and poor: states["Standing"] = min(states["Standing"], -1)
    if order == "Fixated":
        top = max(RUNGS, key=lambda r: wts[r])
        states[top] = min(states[top], -1)
        n["fixation"] = top
    n["needs"] = {"order": order, "weight": wts, "state": states}
    # drive
    dr = d(20)
    still_top = 3 if n["flags"]["complete"] else 1
    target = drive_target(n)
    if dr <= still_top or order == "Numb":
        n["drive"] = {"type": "Still", "rung": None, "text": "wants nothing in particular"}
    elif dr <= 15:
        n["drive"] = {"type": "Inward", "rung": target, "text": fill(random.choice(DRIVES[target][0]), n, target)}
    else:
        shape = "Full" if (d(6) == 6 and target in PHYS + ["Belonging", "Standing"]) else "Partial"
        n["drive"] = {"type": "Open", "shape": shape, "rung": target,
                      "text": fill(random.choice(DRIVES[target][1]), n, target)}
    # creed
    cr = d(6)
    cands = sts[0]["creed"]
    n["creed"] = cands[0] if cr <= 3 else cands[1] if cr <= 5 else random.choice(CREEDS)
    # codes and compulsions
    n["codes"], n["compulsions"] = [], []
    cc = d(6)
    for _ in range(0 if cc <= 3 else 1 if cc <= 5 else 2):
        ctrl = [6, 9, 12, 15][d(4) - 1]
        if d(2) == 1:
            n["codes"].append({"code": random.choice(CODES), "control": ctrl})
        else:
            n["compulsions"].append({"urge": random.choice(COMPULSIONS), "control": ctrl,
                                     "threshold": ctrl // 3, "pressure": 0})
    rn, die, amax = RATIO[d(4)]
    n["contradiction"] = {"pair": OPPOSITES[d(10) - 1], "ratio": rn, "die": die, "a_max": amax}
    n["quirks"] = random.sample(QUIRKS, 2 if n["flags"]["complete"] else 1)
    hollow_drive(n)
    derive(n)
    # danger scars: rolled once per category, permanent history
    n["scars"] = {}
    ds = sts[0]["danger"]
    for cat in DANGER:
        if d(100) <= n["derived"]["nerve"]:
            dirn = ds[0] if ds[0] != 2 else random.choice([1, -1])
            n["scars"][cat] = {"dir": dirn, "form": ds[1]}
    return n


HOLLOW_RUNGS = ("Belonging", "Selfhood", "Meaning")


def hollow_drive(n):
    """A hollow character performs feeling without having it, so no drive may rest on love,
    grief, selfhood or faith. Retarget to a physical rung or Standing and reword."""
    dr = n["drive"]
    if n["authenticity"]["kind"] != "Hollow" or not dr.get("rung"):
        return
    if dr["rung"] in HOLLOW_RUNGS:
        wts, st = n["needs"]["weight"], n["needs"]["state"]
        ok = [r for r in RUNGS if r not in HOLLOW_RUNGS]
        r = max(ok, key=lambda x: (wts[x] * deficit(st[x]), wts[x]))
        pool = DRIVES[r][0 if dr["type"] == "Inward" else 1]
        dr["rung"], dr["text"] = r, fill(random.choice(pool), n, r)
    dr["text"] = dr["text"].replace("someone they love", "someone useful to them")


def deficit(state):
    return -state if state < 0 else 0


def drive_target(n):
    wts, st = n["needs"]["weight"], n["needs"]["state"]
    inv = n["needs"]["order"] == "Inverted"
    order = list(reversed(RUNGS)) if inv else RUNGS
    best = max(order, key=lambda r: (wts[r] * deficit(st[r]), wts[r]))
    return best


def leading_voice(n):
    st = n["needs"]["state"]
    best, bs = n["voices"][0], -1
    for vo in n["voices"]:
        emph = SBY[vo["style"]]["emph"]
        score = vo["frac"] * (1 + sum(deficit(st[r]) for r in emph))
        if score > bs:
            best, bs = vo, score
    return best


def chronic(n):
    wts, st, order = n["needs"]["weight"], n["needs"]["state"], n["needs"]["order"]
    if order == "Inverted" and (st["Meaning"] == -2 or st["Selfhood"] == -2):
        return -2
    if order != "Inverted" and st["Survival"] == -2:
        return -2
    return -1 if any(st[r] == -2 and wts[r] >= 2 for r in RUNGS) else 0


def total_trust(n, who):
    t = n["trust"].get(who, {"bedrock": 0, "surface": 0})
    return clamp(t["bedrock"] + t["surface"], -5, 5)


def load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit("No such file: %s" % p)
    except ValueError:
        sys.exit("Not a valid ledger file: %s" % p)


def save(n, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(n, f, indent=1, ensure_ascii=False)


# ---------- commands ----------
def show(n):
    a = n["axes"]
    dv = n["derived"]
    print("== %s (%s) ==" % (n["name"], n["type"]))
    print("Voices (%s): %s" % (n["blend"], ", ".join("%s %s" % (fmt_frac(v["frac"]), v["style"]) for v in n["voices"])))
    print("Axes: " + ", ".join("%s %+d" % (AX[i], a[i]) for i in range(7)))
    au = n["authenticity"]
    extra = ""
    if au["faces"]:
        extra = " | Face: " + " / ".join(f["style"] for f in au["faces"])
    if au.get("source"):
        extra += " (copied from %s)" % au["source"]
    print("Authenticity: %s%s" % (au["kind"], extra))
    fl = [k for k, v in n["flags"].items() if v]
    print("Station: %s | Office: %s | Creed: %s%s" % (n["station"], " + ".join(n["office"]), n["creed"],
                                                     " | Flags: " + ", ".join(fl) if fl else ""))
    print("Guard %d | Openness %d | Agency %d%% | Nerve %d%% | Sensitivity x%s | Fuse %d | Glow %d%s" % (
        dv["guard"], dv["openness_target"], dv["agency"], dv["nerve"], dv["sensitivity"], dv["fuse"], dv["glow"],
        " | displaces bad days onto strangers" if dv["displacer"] else ""))
    print("Approach: " + ", ".join("%s %+d" % (k, v) for k, v in dv["approach"].items()))
    nd = n["needs"]
    print("Needs (%s order%s):" % (nd["order"], ", fixated on " + n["fixation"] if n.get("fixation") else ""))
    for half, rs in (("  Physical", RUNGS[:4]), ("  Spiritual", RUNGS[4:])):
        print(half + ": " + ", ".join("%s w%d %s" % (r, nd["weight"][r], STATE[nd["state"][r]]) for r in rs))
    dr = n["drive"]
    print("Drive: %s%s%s" % (dr["type"], "/" + dr["shape"] if dr.get("shape") else "",
                             " (%s) - %s" % (dr["rung"], dr["text"]) if dr["rung"] else " - " + dr["text"]))
    for t in n["ties"]:
        print("Tie: %s, loyalty %d, reach %d%s" % (t["label"], t["loyalty"], t["reach"],
                                                    ", would " + t["would"] if t.get("would") else ""))
    for c in n["codes"]:
        print("Code: %s (control %d)" % (c["code"], c["control"]))
    for c in n["compulsions"]:
        print("Compulsion: %s (control %d, acts after %d temptations)" % (c["urge"], c["control"], c["threshold"]))
    co = n["contradiction"]
    print("Contradiction: %s at %s | Quirk: %s" % (co["pair"], co["ratio"], "; ".join(n["quirks"])))
    if n["scars"]:
        print("Danger history: " + ", ".join("%s (%+d, %s)" % (k, v["dir"], v["form"]) for k, v in n["scars"].items()))


def fmt_frac(f):
    for num, den in ((1, 1), (3, 4), (1, 4), (3, 5), (2, 5), (1, 2), (1, 8)):
        if abs(f - num / den) < 1e-6:
            return "%d/%d" % (num, den) if den != 1 else "1"
    return "%.2f" % f


def cmd_npc(a):
    if a.name and a.seeded:
        random.seed("npc:" + a.name.lower())
    n = build(parse_dials(a.dials), a.name)
    show(n)
    if a.save:
        save(n, a.save)
        print("(saved to %s)" % a.save)


def cmd_circle(a):
    dials = parse_dials(a.dials)
    if not a.members:
        n = build(dials, a.name, "circle")
        show(n)
    else:
        ms = [load(p) for p in a.members]
        wts = [RANK.get(m["station"], 0) + 1 for m in ms]
        tot = sum(wts)
        n = build(dials, a.name, "circle")
        n["axes"] = [rnd(sum(w * m["axes"][i] for m, w in zip(ms, wts)) / tot) for i in range(7)]
        fr = {}
        for m, w in zip(ms, wts):
            for vo in m["voices"]:
                fr[vo["style"]] = fr.get(vo["style"], 0) + vo["frac"] * w / tot
        n["voices"] = [{"style": s, "frac": f, "manner": voice_manner(SBY[s])}
                       for s, f in sorted(fr.items(), key=lambda kv: -kv[1])]
        n["blend"] = "Members"
        n["needs"]["weight"] = {r: clamp(rnd(sum(m["needs"]["weight"][r] for m in ms) / len(ms)), 0, 3) for r in RUNGS}
        creeds = [m["creed"] for m in ms]
        n["creed"] = max(set(creeds), key=creeds.count)
        n["members"] = [m["name"] for m in ms]
        derive(n)
        show(n)
        print("Members: " + ", ".join(n["members"]))
    if a.save:
        save(n, a.save)
        print("(saved to %s)" % a.save)


def cmd_day(a):
    n = load(a.file)
    if n["condition"] in ("dead",):
        sys.exit("%s is dead; no day." % n["name"])
    dials = load(a.world)["dials"] if a.world else n["dials"]
    n["day"] += 1
    af = n.setdefault("afflictions", {})
    for k in list(af):
        af[k] -= 1
        if af[k] <= 0:
            del af[k]
    wts, st = n["needs"]["weight"], n["needs"]["state"]
    live = [r for r in RUNGS if wts[r] > 0]
    rung = wpick(live, [wts[r] for r in live])
    shift = 0
    if rung in PHYS: shift += dial(dials, "S")
    if rung == "Safety": shift += dial(dials, "V")
    if rung == "Selfhood": shift += dial(dials, "X")
    r = max(1, d(20) - shift)
    val = -2 if r <= 2 else -1 if r <= 6 else 0 if r <= 14 else 1 if r <= 18 else 2
    if val == 0:
        cause = random.choice(ORDINARY)
    else:
        pool = CAUSES[rung][0 if val < 0 else 1]
        fresh = [c for c in pool if c not in n["recent_causes"]] or pool
        cause = fill(random.choice(fresh), n, rung)
        n["recent_causes"] = (n["recent_causes"] + [c for c in pool if fill(c, n, rung) == cause][:1])[-7:]
        st[rung] = clamp(st[rung] + (1 if val > 0 else -1) * abs(val), -2, 1)
    if cause.startswith("fell sick"):
        af["sick"] = d(3) + 1
    echo = 0
    if a.circle:
        ct = load(a.circle).get("today") or {}
        if ct.get("value"):
            echo = tz(ct["value"] / 2)
            if echo:
                st[ct["rung"]] = clamp(st[ct["rung"]] + echo, -2, 1)
    if n["needs"].get("order") == "Fixated":
        st[n["fixation"]] = min(st[n["fixation"]], -1)
    sens = n["derived"]["sensitivity"]
    mood = tz(val * sens) + echo
    lv = leading_voice(n)
    co = n["contradiction"]
    side = "A" if d(co["die"]) <= co["a_max"] else "B"
    drv = n["drive"]
    opened = drv["rung"] is not None and (drv["rung"] == rung and val != 0)
    oroll = d(10)
    open_today = opened or oroll <= n["derived"]["openness_target"]
    notes = []
    for cp in n["compulsions"]:
        if d(6) == 6:
            cp["pressure"] += 1
        if af.get("grieving") and cp["urge"] in ("a substance", "gambling", "cruelty", "lust"):
            cp["pressure"] += 1
        if cp["pressure"] >= cp["threshold"]:
            notes.append("compulsion '%s' at threshold: acts on it at the next real opportunity" % cp["urge"])
    for cd in n["codes"]:
        if any(st[x] == -2 and wts[x] > cd["control"] / 4 for x in RUNGS):
            notes.append("code '%s' at risk: a starved need outweighs it if they conflict" % cd["code"])
    # slow drift from long hunger or long contentment
    for x in RUNGS:
        n["starved_days"][x] = n["starved_days"][x] + 1 if st[x] == -2 else 0
        n["sated_days"][x] = n["sated_days"][x] + 1 if st[x] == 1 else 0
        if n["starved_days"][x] == 21:
            wts[x] = clamp(wts[x] + 1, 0, 3)
            notes.append("three weeks starved of %s: it now matters more to them (weight %d)" % (x, wts[x]))
            if x == "Selfhood":
                notes.append(drift_authenticity(n, -1))
        if x == "Selfhood" and n["sated_days"][x] == 21:
            notes.append(drift_authenticity(n, 1))
    if n["day"] % 7 == 0:
        for who, t in n["trust"].items():
            if t["surface"]:
                t["surface"] -= 1 if t["surface"] > 0 else -1
        notes.append("a week has passed: small trust shifts fade one step; memories stay")
    if drv["type"] != "Still":
        newt = drive_target(n)
        if newt != drv["rung"] and wts[newt] * deficit(st[newt]) >= 4:
            notes.append("pressure has moved to %s; consider whether their drive shifts there (slowly)" % newt)
    tired = st["Comfort"] <= -1 or st["Survival"] <= -1 or any(
        w in cause for w in ("slept badly", "sick", "pain", "cold or heat", "hungry"))
    ponder = n["axes"][O] >= 2 or lv["style"] in ("Visionary", "Serious", "Solitary") or opened
    chance = min(8, (4 if tired else 0) + (3 if ponder else 0))
    trailing = None
    if chance and d(100) <= chance:
        trailing = "tired" if (tired and (not ponder or d(2) == 1)) else "pondering"
    n["today"] = {"day": n["day"], "rung": rung, "value": val, "cause": cause, "mood": mood,
                  "voice": lv["style"], "side": side, "open": open_today, "trailing": trailing}
    derive(n)
    print("Day %d for %s: %s (%s %+d) x%s%s = %+d to mood" % (
        n["day"], n["name"], cause, rung, val, sens, " %+d circle echo" % echo if echo else "", mood))
    print("Leading voice today: %s | Contradiction side: %s (%s) | Chronic: %+d" % (
        lv["style"], side, co["pair"], chronic(n)))
    print("Open to speaking of their drive today: %s%s" % (
        "yes" if open_today else "no", " (the day touched it)" if opened else " (d10=%d vs %d)" % (
            oroll, n["derived"]["openness_target"])))
    if af:
        print("Lasting states: " + ", ".join("%s (%d more day%s)" % (k, v, "" if v == 1 else "s") for k, v in af.items()))
    if trailing:
        print("Speech today: trailing off now and then (%s). A few ellipses across the scene, not every line."
              % trailing)
    for x in notes:
        if x:
            print("Note: " + x)
    save(n, a.file)


def drift_authenticity(n, step):
    ladder = ["Genuine", "Masked", "Hollow"]
    k = n["authenticity"]["kind"]
    if k not in ladder:
        return ""
    i = ladder.index(k)
    if step < 0 and i < 2 and d(6) <= 2:
        new = ladder[i + 1]
    elif step > 0 and i > 0:
        new = ladder[i - 1]
    else:
        return ""
    n["authenticity"]["kind"] = new
    if new in ("Masked", "Hollow") and not n["authenticity"]["faces"]:
        f = random.choice(FACES)
        n["authenticity"]["faces"] = [{"style": f, "manner": voice_manner(SBY[f])}]
    if new == "Hollow":
        w = n["needs"]["weight"]
        w["Selfhood"], w["Meaning"], w["Belonging"] = 0, 0, min(w["Belonging"], 1)
        hollow_drive(n)
    if new == "Genuine":
        n["authenticity"]["faces"] = []
    return "authenticity drifted: now %s" % new


def band_of(m, n):
    dv = n["derived"]
    if m <= dv["fuse"]: return "Hostile"
    if m <= -2: return "Cool"
    if m <= 1: return "Neutral"
    if m < dv["glow"]: return "Warm"
    return "Kind"


def tetrad_key(band):
    return "Kind" if band == "Kind" else "Hostile" if band == "Hostile" else "Middle"


# ---------- circumstance: how situations amend the way a person comes across ----------
TAGS_ALL = {"plain", "intimate", "warm", "giving", "leisure", "dominant", "action", "formal", "levity",
            "cold", "display", "guarded", "sad", "petty", "fear", "covert", "rage", "wounded"}
FORM_TAGS = {
 # kindness
 "Candid": {"plain"}, "Confiding": {"intimate", "warm"}, "Forgiving": {"warm"}, "Generous": {"giving", "warm"},
 "Gruff-Kind": {"warm", "plain"}, "Hospitable": {"giving", "leisure", "warm"}, "Loyal": {"warm", "plain"},
 "Mentoring": {"leisure", "dominant"}, "Practical": {"plain"}, "Protective": {"action", "warm"},
 "Respectful": {"plain", "formal"}, "Reverent": {"formal", "warm"}, "Teasing-Fond": {"levity", "intimate", "warm"},
 "Tender": {"warm", "intimate"},
 # middle
 "Appraising": {"cold", "dominant"}, "Bargaining-Humour": {"levity", "leisure"},
 "Boastful": {"display", "levity", "dominant"}, "Curious": {"leisure"}, "Distracted": {"plain"},
 "Dutiful": {"plain", "formal"}, "Evasive": {"guarded"}, "Flirtatious": {"levity", "display", "intimate"},
 "Gossipy": {"levity", "leisure"}, "Indifferent": {"cold"}, "Melancholic": {"sad"}, "Mercurial": {"display"},
 "Performing": {"display", "levity"}, "Preaching": {"display", "formal"}, "Ritual": {"formal"},
 "Testing": {"dominant", "cold"}, "Transactional": {"cold", "plain"}, "Wary": {"guarded"},
 "Withdrawn": {"guarded", "sad"},
 # hostility
 "Cold Refusal": {"cold"}, "Contempt": {"cold", "dominant"}, "Envy/Spite": {"petty"},
 "Fear-Aggression": {"fear", "action"}, "Grudge": {"cold"}, "Manipulation": {"display", "covert"},
 "Mockery": {"levity", "display", "dominant"}, "Obstruction": {"formal", "cold"}, "Predatory": {"dominant", "cold"},
 "Reproach": {"sad"}, "Righteous Wrath": {"action", "dominant"}, "Sabotage": {"covert"},
 "Suspicion": {"guarded"}, "Territorial": {"action", "dominant"}, "Toying": {"levity", "dominant"},
 "Violent Outburst": {"action", "rage"},
 # wounded responses
 "Wounded-Selfless": {"wounded"}, "Wounded-Panic": {"wounded"}, "Wounded-Stoic": {"wounded"},
 "Wounded-Shock": {"wounded"},
}


def _voice_frac(n, style):
    return sum(v["frac"] for v in n["voices"] if v["style"] == style)


def _ax(n, i):
    return n["axes"][i]


R = lambda **k: k
CIRC = {
 "hurt": R(itag={"wounded"}, block=TAGS_ALL - {"wounded"},
           repl={b: (lambda n: violence_response(n, True)) for b in ("Kind", "Middle", "Hostile")},
           inflect="badly hurt; what they feel toward you shows only under the pain",
           speech=("broken by breath", "flow"), slip=99,
           approach={"humour": -2, "flattery": -2, "haggling": -2, "pressure": -1, "pity": 0}),
 "frozen": R(itag={"guarded"}, block={"levity", "display", "leisure", "action", "dominant", "giving", "intimate"},
             repl={"Kind": "Withdrawn", "Middle": "Withdrawn", "Hostile": "Grudge"},
             inflect="does not move; holds whatever they were holding", speech=("silent, or a few words", "volume"),
             slip=2, voices=("Sensitive", "Vigilant"),
             approach={"pressure": -1, "patience": 1, "familiarity": -1}),
 "afraid": R(itag={"fear"}, block={"levity", "display", "leisure", "dominant"},
             repl={"Kind": "Protective", "Middle": "Wary", "Hostile": "Fear-Aggression"},
             exempt=lambda n: _ax(n, V) <= -2,
             soften=(lambda n: _ax(n, M) >= 3, {"dominant", "display", "levity"}, "blusters over the fear"),
             inflect="eyes on the exits; small, fast movements", speech=("clipped", "flow"), slip=2,
             voices=("Vigilant", "Sensitive", "Devoted"),
             approach={"pressure": -1, "patience": 1, "humour": -1, "principle": -1}),
 "enraged": R(block={"warm", "intimate", "leisure", "giving", "sad"}, allow={"Protective"},
              repl={"Kind": "Protective", "Middle": "Dutiful", "Hostile": "Righteous Wrath"},
              inflect=lambda n: ("held very still; every word measured" if _ax(n, D) >= 2
                                 else "loud, close, leaning in"),
              itag=lambda n: {"guarded"} if _ax(n, D) >= 2 else {"action", "display"},
              speech=("short and hard", "flow"), slip=lambda n: 1 if _ax(n, D) >= 2 else 3,
              voices=("Commanding", "Mercurial", "Zealot", "Predator"),
              approach={"humour": -2, "flattery": -1, "pity": -1, "patience": 1, "deference": 1}),
 "stunned": R(itag={"plain"}, block={"levity", "display", "leisure", "dominant", "action"},
              repl={"Kind": "Practical", "Middle": "Distracted", "Hostile": "Cold Refusal"},
              inflect="a beat behind; keeps doing the ordinary thing a moment too long",
              speech=("flat; repeats things", "flow"), slip=2, approach={"patience": 1, "humour": -1}),
 "tending": R(itag={"warm"}, block={"levity", "display", "leisure", "dominant", "giving", "intimate", "formal", "covert",
                     "petty", "fear", "rage"},
              repl={"Kind": "Protective", "Middle": "Distracted", "Hostile": "Cold Refusal"},
              inflect="hands busy with the wounded; barely looks up", speech=("low, mostly to the wounded", "volume"),
              approach={"humour": -2, "haggling": -2, "flattery": -1}),
 "grieving": R(itag={"sad"}, block={"levity", "display", "leisure"},
               repl={"Kind": lambda n: "Tender" if _ax(n, W) >= 1 else "Practical", "Middle": "Melancholic",
                     "Hostile": lambda n: "Reproach" if _ax(n, W) >= 0 else "Grudge"},
               swap={"Fear-Aggression": lambda n: "Reproach" if _ax(n, W) >= 0 else "Grudge"},
               soften=(lambda n: "laughs at the wrong moments" in n["quirks"] or (_ax(n, E) >= 2 and _ax(n, O) >= 2),
                       {"levity"}, "gallows humour, a little too bright"),
               inflect="a stillness at the edges; their mind goes elsewhere mid-sentence", speech=("trailing", "flow"),
               slip=2, voices=("Serious", "Mercurial", "Self-Sacrificing", "Devoted"),
               approach={"humour": -2, "haggling": -2, "flattery": -1, "pressure": -1, "patience": 1}),
 "sick": R(itag={"plain"}, block={"display", "levity", "action"},
           repl={"Kind": "Practical", "Middle": "Distracted", "Hostile": "Cold Refusal"},
           inflect="pale, slow, short of breath", speech=("short", "flow"), slip=1,
           approach={"patience": 1, "pressure": -1, "generosity": 1}),
 "exhausted": R(itag={"plain"}, block={"display", "action", "leisure"},
                repl={"Kind": "Practical", "Middle": "Distracted", "Hostile": "Cold Refusal"},
                inflect="heavy-lidded; leans on things", speech=("trailing", "flow"), slip=1,
                approach={"patience": 1, "humour": -1, "pressure": -1}),
 "intoxicated": R(itag={"plain"}, swap={"Dutiful": "Distracted", "Wary": lambda n: "Flirtatious" if _ax(n, E) >= 0 else "Melancholic",
                        "Cold Refusal": "Mockery", "Ritual": "Melancholic", "Evasive": "Confiding",
                        "Obstruction": "Mockery", "Indifferent": "Gossipy", "Withdrawn": "Melancholic",
                        "Appraising": "Boastful"},
                  exempt=lambda n: _ax(n, D) >= 3, exempt_note="very careful about every word",
                  inflect="loose: too loud or too slow; says more than they mean", speech=("rambling", "flow"), slip=3,
                  voices=("Mercurial", "Adventurous", "Dramatic", "Leisurely"),
                  approach={"humour": 1, "familiarity": 1, "principle": -1, "patience": -1}),
 "starving": R(itag={"plain"}, block={"giving"}, soften=(lambda n: _ax(n, W) >= 3, {"giving"}, "gives what they can't spare"),
               repl={"Kind": "Practical", "Middle": "Transactional", "Hostile": "Grudge"},
               inflect="eyes go to any food", approach={"generosity": 1, "humour": -1}),
 "solemn": R(itag={"formal"}, block={"levity", "display", "leisure", "action"}, allow={"Preaching"},
             exempt=lambda n: n["authenticity"]["kind"] == "Hollow" or _voice_frac(n, "Predator") >= 0.25,
             exempt_note="unmoved by the solemnity around them",
             repl={"Kind": "Reverent", "Middle": "Ritual", "Hostile": "Cold Refusal"},
             inflect="low voices, set forms", speech=("hushed", "volume"), slip=-1,
             approach={"humour": -2, "familiarity": -1, "deference": 1, "principle": 1}),
 "festive": R(itag={"levity", "display"}, swap={"Wary": lambda n: "Curious" if _ax(n, E) >= 1 else None,
                    "Dutiful": lambda n: "Gossipy" if _ax(n, E) >= 1 else None},
              inflect="raised voice over the noise", speech=("loud", "volume"), slip=1,
              voices=("Dramatic", "Adventurous"), approach={"humour": 1, "familiarity": 1, "patience": -1}),
 "superior": R(itag={"formal"}, block={"display", "levity", "rage"},
               swap={"Mockery": "Contempt", "Toying": "Cold Refusal", "Territorial": "Obstruction",
                     "Boastful": "Dutiful"},
               exempt=lambda n: _ax(n, M) >= 3, exempt_note="talks over whoever outranks them",
               repl={"Kind": "Respectful", "Middle": "Dutiful", "Hostile": "Obstruction"},
               inflect="checks the superior's face before answering", speech=("formal", "register"), slip=-1,
               approach={"deference": 1, "familiarity": -1, "humour": -1}),
 "intimate": R(itag={"intimate"}, swap={"Wary": "Confiding", "Withdrawn": "Melancholic", "Dutiful": "Candid",
                     "Evasive": "Confiding", "Performing": "Mercurial"},
               inflect="a lower voice; fewer defences", speech=("soft", "volume"), slip=2,
               approach={"familiarity": 1, "pity": 1}),
 "public": R(itag={"guarded"}, swap={"Confiding": "Loyal",
                   "Tender": lambda n: None if (_ax(n, E) >= 2 or _ax(n, W) >= 3) else "Practical",
                   "Reproach": lambda n: None if _voice_frac(n, "Dramatic") >= 0.25 else "Cold Refusal"},
             inflect="aware of being watched", slip=-1, approach={"familiarity": -1}),
 "duty": R(itag={"formal"}, swap={"Flirtatious": lambda n: None if _ax(n, D) <= -1 else "Dutiful",
                 "Gossipy": lambda n: "Dutiful" if _ax(n, D) >= 1 else None,
                 "Distracted": "Wary", "Hospitable": "Practical",
                 "Bargaining-Humour": lambda n: "Transactional" if _ax(n, D) >= 1 else None},
           inflect="one eye on the post", speech=("procedural", "register"), approach={"principle": 1, "haggling": -1}),
}
CONDS = ["hurt", "frozen", "afraid", "enraged", "stunned", "tending", "grieving", "sick", "exhausted",
         "intoxicated", "starving", "solemn", "festive", "superior", "intimate", "public", "duty"]
SHAKEN_TO = {"Fury": "enraged", "Freeze": "frozen", "Flight": "afraid", "Shock": "stunned",
             "Tending": "tending", "Ritual": "solemn"}
STRESS = {"hurt", "frozen", "afraid", "enraged", "stunned", "tending", "grieving", "solemn", "superior"}
QUIRK_KIND = {
 "counts money twice": "compulsive", "never sits with back to a door": "stress",
 "speaks of self in third person when nervous": "stress", "hums the same four notes": "idle",
 "refuses to say a certain word": "compulsive", "collects small useless objects of one kind": "idle",
 "always offers something to drink": "social", "calls everyone by the wrong name, kindly": "social",
 "can't stand whistling": "compulsive", "touches a lucky object before deciding": "stress",
 "laughs at the wrong moments": "stress", "keeps a dead person's belonging close": "grief",
 "answers in sayings": "social", "sleeps at odd hours": "constant", "never finishes a drink": "social",
 "counts steps": "compulsive", "lies about trivial things only": "social",
 "pockets one small thing from every visitor, returns it later": "compulsive",
 "feeds animals obsessively": "idle", "always knows the time without looking": "constant",
}
SIDE_TEXT = {
 "Limit/Boundless": (("keeps within bounds", {"plain"}), ("goes a step too far", {"action"})),
 "Odd/Even": (("an odd turn of phrase", {"levity"}), ("by the book", {"formal"})),
 "One/Many": (("keeps a little apart", {"guarded"}), ("draws others in", {"display"})),
 "Right/Left": (("says it straight", {"plain"}), ("a sly edge", {"covert"})),
 "Pressing/Yielding": (("pushes", {"dominant", "action"}), ("gives ground", {"guarded"})),
 "Rest/Motion": (("very still", {"plain"}), ("can't keep still", {"action"})),
 "Straight/Curved": (("blunt", {"plain"}), ("says it sideways", {"guarded"})),
 "Light/Dark": (("a lightness under it", {"levity"}), ("a brooding undertone", {"sad"})),
 "Good/Petty": (("fair-minded", {"plain"}), ("a petty jab slips in", {"petty"})),
 "Square/Oblong": (("even-handed", {"plain"}), ("angling for advantage", {"covert"})),
}


def _val(x, n):
    return x(n) if callable(x) else x


def circ_active(n, conds):
    """Conditions in priority order, minus those this person is exempt from by nature."""
    out, notes = [], []
    for c in CONDS:
        if c in conds:
            r = CIRC[c]
            if r.get("exempt") and r["exempt"](n):
                if r.get("exempt_note"):
                    notes.append(r["exempt_note"])
                continue
            out.append(c)
    return out, notes


BAND_FALLBACK = {
 "Kind": ["Practical", "Respectful", "Loyal", "Candid", "Protective", "Tender", "Forgiving"],
 "Middle": ["Withdrawn", "Distracted", "Dutiful", "Wary", "Indifferent", "Melancholic", "Ritual"],
 "Hostile": ["Cold Refusal", "Grudge", "Suspicion", "Obstruction", "Reproach", "Contempt"],
}


def _passes(form, c, n):
    r = CIRC[c]
    bad = FORM_TAGS[form] & r.get("block", set())
    if not bad or form in r.get("allow", set()):
        return True
    sf = r.get("soften")
    return bool(sf and sf[0](n) and bad <= sf[1])


def resolve(form, band_key, active, n):
    """Amend a form until it fits the active circumstances.
    Higher-priority circumstances win: a lower one may only amend into a form every higher one accepts;
    if nothing fits them all, the lowest-priority circumstance yields and stays as colour only.
    Returns (form, softening notes, ok, yielded circumstances)."""
    conds = list(active)
    yielded = []
    seen = {form}
    for _ in range(40):
        fits = lambda f: all(_passes(f, c, n) for c in conds)
        if fits(form):
            moved = False
            for c in conds:
                sw = CIRC[c].get("swap", {})
                if form in sw:
                    t = _val(sw[form], n)
                    if t and t != form and t not in seen and fits(t):
                        form = t; seen.add(t); moved = True
                        break
            if not moved:
                notes = []
                for c in conds:
                    r = CIRC[c]
                    bad = FORM_TAGS[form] & r.get("block", set())
                    if bad and form not in r.get("allow", set()) and r.get("soften") and r["soften"][2] not in notes:
                        notes.append(r["soften"][2])
                return form, notes, True, yielded
            continue
        cand = []
        for c in conds:
            sw = CIRC[c].get("swap", {})
            if form in sw and _val(sw[form], n):
                cand.append(_val(sw[form], n))
        for c in conds:
            if not _passes(form, c, n) and "repl" in CIRC[c]:
                cand.append(_val(CIRC[c]["repl"][band_key], n))
        for c in conds:
            if "repl" in CIRC[c]:
                cand.append(_val(CIRC[c]["repl"][band_key], n))
        cand += BAND_FALLBACK[band_key]
        pick = next((t for t in cand if t in FORM_TAGS and fits(t)), None)
        if pick:
            form = pick; seen.add(pick)
        else:
            yielded.append(conds.pop())
    return form, [], False, yielded


def conditions_for(n, a, band, about_you, plan):
    td = n.get("today") or {}
    af = n.get("afflictions", {})
    c = set()
    if a.hurt: c.add("hurt")
    if td.get("shaken") in SHAKEN_TO: c.add(SHAKEN_TO[td["shaken"]])
    for k in ("grieving", "sick", "intoxicated", "exhausted"):
        if af.get(k): c.add(k)
    if td.get("trailing") == "tired": c.add("exhausted")
    if n["needs"]["state"]["Survival"] == -2 and "sick" not in c: c.add("starving")
    if any(n["scars"].get(x, {}).get("dir") == -1 for x in (a.danger or [])): c.add("afraid")
    if plan and plan.startswith("Yield"): c.add("afraid")
    if band == "Hostile" and n["axes"][V] >= 2 and about_you <= -3: c.add("enraged")
    for flag, cond in (("solemn", "solemn"), ("festive", "festive"), ("superior", "superior"),
                       ("duty", "duty"), ("drunk", "intoxicated"), ("tired", "exhausted"),
                       ("sick", "sick"), ("grieving", "grieving"), ("audience", "public")):
        if getattr(a, flag, False): c.add(cond)
    if a.private and total_trust(n, a.who) >= n["derived"]["guard"] + 2: c.add("intimate")
    return c


def _blocked_by(tags, conds, n):
    return [c for c in conds if tags & CIRC[c].get("block", set())]


def colour_for(n, active, side):
    """Colour notes (circumstance inflections, contradiction side) and speech, each dropped when a
    stronger active circumstance blocks what it carries. Returns (notes, speech, dropped)."""
    notes, dropped = [], []
    for i, c in enumerate(active):
        t = _val(CIRC[c].get("inflect"), n)
        if not t:
            continue
        tg = _val(CIRC[c].get("itag", {"plain"}), n)
        if _blocked_by(tg, active[:i], n):
            dropped.append(t)
        elif t not in notes:
            notes.append(t)
    pair = SIDE_TEXT.get(n["contradiction"]["pair"]) if "contradiction" in n else None
    if pair:
        txt, tg = pair[0 if side == "A" else 1]
        if _blocked_by(tg, active, n):
            dropped.append(txt)
        else:
            notes.append(txt)
    speech, cats = [], set()
    for c in active:
        sp = CIRC[c].get("speech")
        if sp and sp[1] not in cats:
            speech.append(sp[0]); cats.add(sp[1])
    return notes, speech, dropped


def intensity(mood, band, n):
    dv = n["derived"]
    if band == "Hostile":
        k = dv["fuse"] - mood
        return "utterly " if k >= 5 else "openly " if k >= 2 else ""
    if band == "Cool":
        return "barely " if mood == -2 else "fully " if mood <= -5 else ""
    if band == "Warm":
        return "barely " if mood == 2 else "fully " if mood >= dv["glow"] - 1 else ""
    if band == "Kind":
        return "deeply " if mood - dv["glow"] >= 3 else ""
    return ""


def cmd_meet(a):
    n = load(a.file)
    if n["condition"] in ("dead", "comatose"):
        sys.exit("%s is %s." % (n["name"], n["condition"]))
    dv = n["derived"]
    st, order = n["needs"]["state"], n["needs"]["order"]
    td = n.get("today") or {"mood": 0, "voice": n["voices"][0]["style"], "side": "A", "cause": "no day rolled"}
    trust = total_trust(n, a.who)
    ap = dv["approach"].get(a.approach, 0) if a.approach else 0
    starving = st["Survival"] == -2 or st["Safety"] == -2
    if order != "Inverted" and starving and a.approach in ("principle", "humour", "flattery", "familiarity"):
        ap = tz(ap / 2)
    if order != "Inverted" and starving and a.approach == "generosity":
        ap = clamp(ap + 1, -2, 2)
    if order == "Inverted" and (st["Meaning"] == -2 or st["Selfhood"] == -2):
        if a.approach in ("generosity", "haggling"): ap = tz(ap / 2)
        if a.approach == "principle": ap = clamp(ap + 1, -2, 2)
    creed = 0
    if a.creed == "aligned":
        creed = 1 + (1 if a.approach == "principle" else 0)
    elif a.creed == "opposed":
        creed = -1 - (1 if a.approach == "principle" else 0)
    social = 0
    if a.lead:
        sgn = 1 if a.lead == "warm" else -1
        if a.rival_of_lead:
            social = -sgn
        elif n["axes"][M] <= -1 or n["axes"][D] >= 2:
            social = sgn
    cont = a.contagion if (a.contagion and n["axes"][V] >= 1) else 0
    dang, lean = 0, None
    for cat in a.danger or []:
        if cat in n["scars"]:
            dang += n["scars"][cat]["dir"]
            lean = n["scars"][cat]["form"]
    dang = clamp(dang, -1, 1)
    # violence response decided first: it is a circumstance for everything below
    if a.violence:
        resp = violence_response(n, a.hurt)
        steady = violence_steady(n, resp, n["dials"])
        if n.get("today"):
            n["today"]["shaken"] = None if steady else resp
            save(n, a.file)
        td = n.get("today") or td
    # approach is amended by circumstance (pre-band pass uses the conditions known before mood)
    pre, _ = circ_active(n, conditions_for(n, a, None, 0, None))
    for c in pre:
        if a.approach:
            ap += CIRC[c].get("approach", {}).get(a.approach, 0)
    ap = clamp(ap, -2, 2)
    about_you = trust + ap + creed + social + cont + dang
    about_them = td["mood"] + chronic(n)
    mood = dv["baseline"] + about_them + about_you
    capped = ""
    if mood <= dv["fuse"] and not (about_you <= -1 or dv["displacer"]):
        mood, capped = dv["fuse"] + 1, " (capped: nothing about you justifies hostility)"
    if mood >= dv["glow"] and not (about_you >= 1 or n["axes"][W] >= 2):
        mood, capped = dv["glow"] - 1, " (capped: nothing about you earns kindness yet)"
    band = band_of(mood, n)
    plan = None
    if band == "Hostile" or a.opposed:
        own = RANK.get(n["station"], 0) + max([t["reach"] for t in n["ties"]] + [0]) // 2 + a.ground
        diff = own - a.their_strength
        diff += 1 if n["axes"][M] >= 2 else -2 if n["axes"][M] <= -2 else 0
        if n["axes"][V] >= 2 and diff < 0: diff += 1
        if n["axes"][D] >= 2 and diff > 0: diff -= 1
        plan = next(p for lim, p in STRATAGEMS if diff >= lim)
        if n["axes"][C] <= -2 and diff < 3:
            plan += "; prefers deception at any strength"
    active, exempt_notes = circ_active(n, conditions_for(n, a, band, about_you, plan))
    # which voice leads: the circumstance can call a voice forward
    vstyle = td["voice"]
    for c in active:
        aff = [v["style"] for v in n["voices"] if v["style"] in CIRC[c].get("voices", ()) and v["frac"] >= 0.25]
        if aff:
            vstyle = aff[0]
            break
    voice = next(v for v in n["voices"] if v["style"] == vstyle)
    au = n["authenticity"]
    slipmod = sum(_val(CIRC[c].get("slip", 0), n) for c in active)
    face_on = au["kind"] in ("Masked", "Hollow", "Borrowed", "Shifting") and au["faces"] and slipmod < 99
    if face_on and au["kind"] == "Masked" and td.get("shaken") and not (n["axes"][D] >= 2 and n["axes"][V] <= 0):
        face_on = False
    shown = voice["manner"]
    if face_on:
        shown = au["faces"][0]["manner"] if (au["kind"] != "Shifting" or a.audience) else au["faces"][-1]["manner"]
    key = tetrad_key(band)
    use_alt = abs(about_them) > abs(about_you)
    raw = shown[key][1 if use_alt else 0]
    form, soft, ok, yielded = resolve(raw, key, active, n)
    infl, sp, dropped_col = colour_for(n, active, td["side"])
    side_note = infl.pop() if (infl and SIDE_TEXT.get(n["contradiction"]["pair"]) and
                               infl[-1] in [x[0] for x in SIDE_TEXT[n["contradiction"]["pair"]]]) else None
    infl += soft + exempt_notes
    others = sorted([v for v in n["voices"] if v["style"] != vstyle], key=lambda v: -v["frac"])
    if others and others[0]["frac"] >= 0.25:
        tf = resolve(others[0]["manner"][key][0], key, active, n)[0]
        if tf != form:
            infl.append("with a trace of " + tf)
    if side_note:
        infl.append(side_note)
    tint = {"Cool": "colder ", "Warm": "warmer "}.get(band, "")
    print("[narrator only] %s toward %s" % (n["name"], a.who))
    print("Mood %+d = baseline %+d, their day %+d (%s), chronic %+d, trust %+d, approach %+d, creed %+d, "
          "social %+d, contagion %+d, danger %+d%s" % (mood, dv["baseline"], td["mood"], td["cause"], chronic(n),
                                                      trust, ap, creed, social, cont, dang, capped))
    if active:
        print("Circumstances: " + ", ".join(active))
    print("Band: %s%s -> shows as %s%s%s" % (intensity(mood, band, n), band, tint if form == raw else "",
                                            form, "" if form == raw else " (amended from %s)" % raw))
    if infl:
        print("Colour: " + "; ".join(infl))
    if yielded:
        print("Yields to stronger circumstances (colour only): " + ", ".join(yielded))
    if not ok:
        print("WARNING: circumstances could not settle on a form; run `audit`.")
    if vstyle != td["voice"]:
        print("The circumstance calls their %s side forward." % vstyle)
    if face_on:
        core = resolve(voice["manner"][key][1 if use_alt else 0], key, active, n)[0]
        print("Core underneath: %s (%s; slip threshold now %d). Only at or after a deception."
              % (core, au["kind"], clamp(dv["slip"] + slipmod, 0, 10)))
    elif au["kind"] != "Genuine":
        print("Their face has dropped: what shows is who they are.")
    if a.violence and td.get("shaken") is None:
        print("Violence: outwardly unchanged; this is already who they are.")
    if set(a.danger or []) & {"violence", "injury"}:
        print("Violence in the scene: run `violence` for register, dissonance and responses.")
    if lean:
        fits = lean in SBY[voice["style"]][{"Kind": "kind", "Middle": "mid", "Hostile": "host"}[key]]
        print("Danger history stirs: %s %s" % (lean, "replaces the form this scene" if fits else "as a passing beat only"))
    if plan:
        print("Stratagem (their estimate of you %d): %s" % (a.their_strength, plan))
    stress = bool(set(active) & STRESS)
    qs = []
    for q in n["quirks"]:
        k = QUIRK_KIND.get(q, "constant")
        if k == "grief":
            qs.append(q + (" (surfaces)" if "grieving" in active else ""))
        elif stress and k in ("idle", "social"):
            qs.append(q + " (not now)")
        elif stress and k == "stress":
            qs.append(q + " (surfaces)")
        elif (set(active) & {"festive", "intoxicated"}) and k == "social":
            qs.append(q + " (more than usual)")
        else:
            qs.append(q)
    print("Quirks: " + "; ".join(qs))
    if td.get("trailing") and not any(x in ("trailing", "clipped", "short", "short and hard", "rambling",
                                            "broken by breath", "flat; repeats things") for x in sp):
        sp.append("trails off now and then")
    if sp:
        print("Speech: " + ", ".join(sp))


def cmd_audit(a):
    """Preemptive amendment review: every form x every combination of up to three circumstances x
    every band x a spread of personalities must settle on a form that fits. Run after adding any
    form, circumstance, quirk or style."""
    problems = []
    forms = set(FORM_TAGS)
    for s in STYLES:
        for f in s["kind"] + s["mid"] + s["host"]:
            if f not in FORM_TAGS: problems.append("form without tags: %s (%s)" % (f, s["name"]))
    for f in FACES:
        if f not in SBY: problems.append("face is not a style: " + f)
    for q in QUIRKS:
        if q not in QUIRK_KIND: problems.append("quirk without a kind: " + q)
    for r in RESPONSES:
        if r.startswith("Wounded") and r not in FORM_TAGS: problems.append("wounded response without tags: " + r)
        if not r.startswith("Wounded") and r not in SHAKEN_TO and r not in STEADY and r != "Spectator":
            problems.append("violence response with no circumstance: " + r)
    for pair in OPPOSITES:
        if pair not in SIDE_TEXT: problems.append("contradiction without side text: " + pair)
    for c in CONDS:
        r = CIRC[c]
        for t in r.get("block", set()):
            if t not in TAGS_ALL: problems.append("%s blocks unknown tag %s" % (c, t))
        if r.get("block") and set(r.get("repl", {})) != {"Kind", "Middle", "Hostile"}:
            problems.append("%s blocks tags but lacks a replacement for every band" % c)
        for t in r.get("swap", {}):
            if t not in forms: problems.append("%s swaps unknown form %s" % (c, t))
    profiles = []
    for axes in ([0] * 7, [3] * 7, [-3] * 7, [-3, 3, 3, -3, -3, 3, 3], [3, -3, -3, 3, 3, -3, -3],
                 [0, 2, 0, 2, 2, 2, -1], [-2, -2, 2, -1, 3, 1, 3]):
        for extra in ({}, {"quirks": ["laughs at the wrong moments"]}, {"hollow": True}, {"predator": True},
                      {"dramatic": True}):
            n = {"axes": axes, "quirks": extra.get("quirks", []),
                 "voices": [{"style": "Predator" if extra.get("predator") else
                             "Dramatic" if extra.get("dramatic") else "Serious", "frac": 1}],
                 "authenticity": {"kind": "Hollow" if extra.get("hollow") else "Genuine", "faces": []}}
            profiles.append(n)
    import itertools
    combos = [()]
    for k in (1, 2, 3):
        combos += list(itertools.combinations(CONDS, k))
    checked = 0
    yields = {}
    for n in profiles:
        for combo in combos:
            active, _ = circ_active(n, set(combo))
            for f in forms:
                for key in ("Kind", "Middle", "Hostile"):
                    try:
                        out, soft, ok, yl = resolve(f, key, active, n)
                    except Exception as e:
                        problems.append("crash: %s %s %s: %s" % (f, key, combo, e)); continue
                    checked += 1
                    if not ok:
                        problems.append("no settled form: %s/%s under %s" % (f, key, ",".join(combo)))
                        continue
                    if out not in FORM_TAGS:
                        problems.append("unknown result %s from %s under %s" % (out, f, ",".join(combo)))
                        continue
                    if yl:
                        yields[len(combo)] = yields.get(len(combo), 0) + 1
                        if len(active) == 1:
                            problems.append("a circumstance cannot satisfy itself: %s on %s" % (active[0], f))
                    for c in active:
                        if c in yl:
                            continue
                        if not _passes(out, c, n):
                            problems.append("%s still clashes with %s (from %s, %s)" % (out, c, f, ",".join(combo)))
    for c in CONDS:
        r = CIRC[c]
        if r.get("inflect") and "itag" not in r:
            problems.append("circumstance colour without tags: " + c)
        if r.get("speech") and (not isinstance(r["speech"], tuple) or r["speech"][1] not in ("volume", "flow", "register")):
            problems.append("speech without a category: " + c)
    for n in profiles:
        n["contradiction"] = {"pair": "Light/Dark"}
        for pair in SIDE_TEXT:
            n["contradiction"]["pair"] = pair
            for combo in combos:
                active, _ = circ_active(n, set(combo))
                for side in ("A", "B"):
                    notes, speech, _ = colour_for(n, active, side)
                    for i, c in enumerate(active):
                        t = _val(CIRC[c].get("inflect"), n)
                        if t in notes and _blocked_by(_val(CIRC[c].get("itag", {"plain"}), n), active[:i], n):
                            problems.append("colour '%s' kept under stronger %s" % (t, ",".join(active[:i])))
                    txt, tg = SIDE_TEXT[pair][0 if side == "A" else 1]
                    if txt in notes and _blocked_by(tg, active, n):
                        problems.append("contradiction colour '%s' kept under %s" % (txt, ",".join(combo)))
    uniq = list(dict.fromkeys(problems))
    groups = {}
    for u in uniq:
        k = u.split(" (from ")[0]
        groups[k] = groups.get(k, 0) + 1
    print("Audit: %d form/circumstance/band/personality combinations checked across %d circumstances, "
          "%d personality profiles." % (checked, len(CONDS), len(profiles)))
    print("Circumstances yielding to stronger ones (by number combined): " +
          (", ".join("%d at once: %d" % kv for kv in sorted(yields.items())) or "none"))
    cover = {c: sum(1 for f in forms for k in ("Kind", "Middle", "Hostile")
                    if resolve(f, k, [c], profiles[0])[0] != f) for c in CONDS}
    print("Amendments per circumstance (ordinary person): " + ", ".join("%s %d" % kv for kv in cover.items()))
    if uniq:
        print("PROBLEMS (%d, in %d patterns):" % (len(uniq), len(groups)))
        for k, v in sorted(groups.items(), key=lambda kv: -kv[1])[:60]:
            print("  %s  x%d" % (k, v))
        sys.exit(1)
    print("No unhandled combinations.")


def cmd_ask(a):
    n = load(a.file)
    dr = n["drive"]
    if n["condition"] != "present":
        print("NO ASK. They are %s." % n["condition"]); return
    if dr["type"] != "Open":
        print("NO ASK. Drive is %s: decline, deflect, or a trivial courtesy at most." % dr["type"]); return
    if a.asked:
        print("NO ASK. Already asked this scene."); return
    if not a.touched:
        print("NO ASK. The talk has not touched %s." % dr["rung"]); return
    af = n.get("afflictions", {})
    if af.get("grieving") and dr["rung"] != "Belonging":
        print("NO ASK. They are grieving; nothing else is spoken of now."); return
    if af.get("sick") and dr["rung"] != "Survival":
        print("NO ASK. Too sick to raise it."); return
    td = n.get("today")
    if not td:
        print("Roll their day first (the day decides whether they are open)."); return
    if not td["open"]:
        print("NO ASK. Not a day they would speak of it."); return
    tr, g = total_trust(n, a.who), n["derived"]["guard"]
    if tr < g:
        print("HINT ONLY. Open today, but trust %d < guard %d: an oblique remark, no request." % (tr, g)); return
    print("MAY ASK (%s): '%s'. Pride or a code may still make them refuse." % (dr.get("shape", "Partial"), dr["text"]))


def cmd_event(a):
    n = load(a.file)
    sign, size, marks, needs = EVENTS[a.kind]
    sz = a.size or size
    notes = []
    if sign and a.who:
        ax = n["axes"]
        t = n["trust"].setdefault(a.who, {"bedrock": 0, "surface": 0})
        delta = sign * sz
        if a.kind == "gift" and ax[M] >= 2 and ax[C] >= 1 and not a.trade:
            delta = -1
            notes.append("refuses charity; a trade would have landed")
        elif a.kind in ("gift", "rescue", "kindness") and (ax[C] <= -2 or (ax[M] >= 2 and ax[W] <= 0)):
            delta = 0
            notes.append("takes it as owed; no gratitude now")
        elif a.kind in ("gift", "rescue") and ax[V] >= 2 and ax[M] >= 1:
            notes.append("accepts and resents being helped; warmth comes later, if at all")
        if n["authenticity"]["kind"] == "Hollow" and sign > 0 and a.kind not in ("rescue", "gift"):
            delta = 0
            notes.append("performs gratitude; nothing moves underneath")
        if abs(delta) >= 2:
            t["bedrock"] = clamp(t["bedrock"] + delta, -5, 5)
        else:
            t["surface"] = clamp(t["surface"] + delta, -3, 3)
        notes.append("trust toward %s now %+d" % (a.who, total_trust(n, a.who)))
    st = n["needs"]["state"]
    for r, step in needs.items():
        st[r] = clamp(st[r] + step, -2, 1)
    for axis, s in marks:
        key = "%s%+d" % (AX[axis], s)
        n["marks"][key] = n["marks"].get(key, 0) + 1
        if n["marks"][key] >= 3:
            last = n["shifts"].get(AX[axis], -999)
            if n["day"] - last >= 30 and clamp(n["axes"][axis] + s, -3, 3) != n["axes"][axis]:
                n["axes"][axis] = clamp(n["axes"][axis] + s, -3, 3)
                n["shifts"][AX[axis]] = n["day"]
                n["marks"][key] = 0
                notes.append("slow change: %s shifts %+d (now %+d)" % (AX[axis], s, n["axes"][axis]))
    if a.kind == "code-broken":
        notes.append("shame: Selfhood starved; they will not forget doing it")
    af = n.setdefault("afflictions", {})
    if a.kind == "loss":
        af["grieving"] = 7 + d(7)
        notes.append("grieving for %d days" % af["grieving"])
    if a.kind == "fell-ill":
        af["sick"] = d(3) + 1
        notes.append("sick for %d days" % af["sick"])
    if a.kind == "intoxicated":
        af["intoxicated"] = 1
        notes.append("drunk or high for the rest of today")
    n["memory"].append({"day": n["day"], "event": a.kind, "with": a.who, "note": a.note or ""})
    derive(n)
    save(n, a.file)
    print("Recorded %s%s. " % (a.kind, " with " + a.who if a.who else "") + "; ".join(notes))


def cmd_affinity(a):
    x, y = load(a.a), load(a.b)
    parts = []
    if "Nothing" in (x["creed"], y["creed"]):
        cs = 1 if x["creed"] == y["creed"] else -2 if "Faith" in (x["creed"], y["creed"]) else 0
    else:
        dist = abs(CREEDS.index(x["creed"]) - CREEDS.index(y["creed"]))
        dist = min(dist, 12 - dist)
        cs = {0: 2, 1: 1, 5: -1, 6: -2}.get(dist, 0)
    parts.append(("creeds %s/%s" % (x["creed"], y["creed"]), cs))
    mx, my = x["axes"][M], y["axes"][M]
    dm = -1 if (mx >= 2 and my >= 2) else 1 if ((mx >= 2 and my <= -1) or (my >= 2 and mx <= -1)) else 0
    parts.append(("dominance", dm))
    wx, wy = x["axes"][W], y["axes"][W]
    parts.append(("warmth", 1 if wx + wy >= 3 else -1 if min(wx, wy) <= -2 else 0))
    parts.append(("candour gap", -1 if abs(x["axes"][C] - y["axes"][C]) >= 4 else 0))
    comp = any(x["needs"]["weight"][r] == 3 and y["needs"]["weight"][r] == 3 for r in ("Means", "Standing"))
    parts.append(("competing hungers", -1 if comp and x["station"] == y["station"] else 0))
    tie = {"kin": 2, "lover": 3, "friend": 2, "mentor": 1, "rival": -2, "enemy": -4, "creditor": -1,
           "debtor": 0, "master": 0, "dependant": 1}.get(a.tie or "", 0)
    parts.append(("tie " + (a.tie or "none"), tie))
    total = clamp(sum(p[1] for p in parts), -5, 5)
    print("Regard %s <-> %s: %+d  (%s)" % (x["name"], y["name"], total,
                                          ", ".join("%s %+d" % p for p in parts)))
    print("Use it as trust between them; each still reacts through their own mood and manner.")


def cmd_scene(a):
    ns = [load(p) for p in a.files]
    dials = load(a.world)["dials"] if a.world else (ns[0]["dials"] if ns else list(DEFAULT_DIALS))
    lead = max(ns, key=lambda n: n["axes"][M] + n["axes"][E] + RANK.get(n["station"], 0))
    print("[narrator only] Lead of the room: %s" % lead["name"])
    loud = max(ns, key=lambda n: (n["axes"][E], n["axes"][M]))
    sus = [n["name"] for n in ns if n["axes"][V] >= 1 and n is not loud]
    if sus:
        print("Mood carries from %s to: %s (+1 or -1 toward their band, once)" % (loud["name"], ", ".join(sus)))
    turns = [n for n in ns if d(100) <= n["derived"]["agency"]]
    if turns:
        n = random.choice(turns)
        kinds = ["news reached them (by a route they could really have)", "something happened with %s offscreen"
                 % random.choice(n["ties"])["label"], "a decision about their drive ripened",
                 "a compulsion or old hunger spiked", "they are trying out the other side of themself",
                 "something no table covers, consistent in hindsight"]
        print("Hidden turn for %s: %s. Let behaviour show it; never explain it." % (n["name"], kinds[d(6) - 1]))
    for n in ns:
        if n["authenticity"]["kind"] in ("Masked", "Hollow", "Borrowed", "Shifting"):
            r = d(10)
            if r <= n["derived"]["slip"]:
                print("Slip for %s if pressed or alone with someone trusted, and only at or after a deception"
                      % n["name"])
    r = d(100)
    if r == 100:
        pool = ODD_PLAIN + (ODD_UNCANNY if dial(dials, "X") >= 2 else [])
        print("Oddity (%s): %s" % (random.choice(ns)["name"], random.choice(pool)))


def cmd_status(a):
    n = load(a.file)
    old = n["condition"]
    n["condition"] = a.condition
    if a.condition == "amnesiac" and old != "amnesiac":
        n["lost_memory"] = n.get("lost_memory", []) + n["memory"]
        n["memory"] = []
        for t in n["trust"].values():
            t["surface"] = 0
            t["bedrock"] = tz(t["bedrock"] / 2)
    if a.condition == "present" and old == "amnesiac" and a.restore:
        n["memory"] = n.pop("lost_memory", []) + n["memory"]
    save(n, a.file)
    msg = "%s: %s -> %s" % (n["name"], old, a.condition)
    if a.condition == "dead":
        msg += ". Record a loss event for each person tied to them."
    print(msg)

# ---------- violence: register, dissonance, responses ----------
REGISTERS = {
 "Rupture": "Violence tears the ordinary. Short sentences at the moment, then the ordinary resumes around it, "
            "slightly wrong. Sound first, then sight, then what people do.",
 "Trade": "Violence is business. Calm voices, courtesy, euphemism in the mouths of those who deal in it. "
          "The act is quick and plain; the talk around it is polite. Often the act is offscreen and only its "
          "result is found.",
 "Weather": "Violence is as ordinary as weather. Long plain sentences joined with and. Flat verbs, exact "
            "nouns, no feeling named. The land, the light and the animals go on, indifferent and enormous.",
}
DISSONANCE = [
 "a radio, record or street musician keeps playing the same cheerful tune",
 "someone at the next table finishes their meal",
 "a child laughs somewhere out of sight",
 "the weather is beautiful: clean light, a soft wind",
 "a bird lands nearby and goes about its business",
 "a hymn, chant or ritual next door carries on without missing a word",
 "the one who did it apologises for the mess, sincerely",
 "someone straightens a picture or a tablecloth that got knocked",
 "the price of something is mentioned, as if it matters now",
 "an animal comes to sniff at the blood",
 "a pot boils over in the kitchen and no one moves it",
 "a clock or bell marks the hour",
 "a celebration nearby: music, toasts, dancing, going on",
 "the wounded one apologises to someone",
 "a joke is finished, out of habit, and someone laughs at it",
 "a dropped coin rolls in a long circle and settles",
 "the light on the wall is lovely",
 "someone keeps counting money, losing their place, starting again",
 "someone hums a lullaby without knowing they are doing it",
 "a kettle starts to whistle",
]
AFTERMATH = [
 "the blood goes dark and dull faster than expected", "flies arrive", "someone fetches a bucket and a brush",
 "the smell stays in clothes and hair", "the room is too quiet; small sounds are very loud",
 "a shoe has come off and no one puts it back", "the furniture is moved back, almost to where it was",
 "people speak about something else entirely", "someone is sick, quietly, outside",
 "the meal goes cold on the table", "a door that was always open is now kept shut",
 "nobody sits in that chair again that day",
]
RESPONSES = {
 "Wounded-Panic": "pleads, bargains, calls for someone; breath and words break",
 "Wounded-Stoic": "quiet, practical about their own wound, asks for a specific thing (cloth, water, light)",
 "Wounded-Selfless": "asks after someone else before themself",
 "Wounded-Shock": "looks at the wound as if it belongs to someone else; says something ordinary",
 "Curiosity": "calm interest; studies what happened, may remark on it plainly, unhurried",
 "Business": "calm, takes charge; courteous, uses soft words for hard things ('it's handled', 'we'll talk to him')",
 "Tending": "goes to the wounded regardless of the danger; hands busy, voice low",
 "Ritual": "set words, prayer or rite; the body does the old motions",
 "Fury": "loud, forward, wants to hit back now; may break something",
 "Freeze": "does not move; holds whatever they were holding",
 "Flight": "leaves, fast, by the nearest way; may come back later ashamed or not at all",
 "Spectator": "watches, says nothing, misses nothing",
 "Shock": "keeps doing the ordinary thing a moment too long, then stops",
}


def violence_response(n, hurt):
    a = n["axes"]
    styles = {v["style"]: v["frac"] for v in n["voices"]}
    dom = n["voices"][0]["style"]
    if hurt:
        if a[W] >= 2: return "Wounded-Selfless"
        if a[V] >= 2: return "Wounded-Panic"
        if a[V] <= -2: return "Wounded-Stoic"
        return "Wounded-Shock"
    if styles.get("Predator", 0) >= 0.25 or (a[W] <= -3 and a[V] <= -2): return "Curiosity"
    if dom in ("Professional", "Commanding", "Schemer") or (a[D] >= 2 and a[V] <= -1): return "Business"
    if a[W] >= 2 and a[V] <= 1: return "Tending"
    if (n["creed"] == "Faith" or dom in ("Zealot", "Devoted")) and a[E] <= 0 and a[V] <= 1: return "Ritual"
    if a[V] >= 2 and a[M] >= 1: return "Fury"
    if a[V] >= 2: return "Freeze" if a[E] <= -1 else "Flight"
    if a[E] <= -2: return "Spectator"
    return "Shock"


STEADY = ("Business", "Curiosity", "Wounded-Stoic")


def violence_steady(n, resp, dials):
    """True when violence doesn't change how they come across: it is already who they are."""
    if resp in STEADY or n["axes"][V] <= -2:
        return True
    return dial(dials, "V") >= 3 and n["axes"][V] <= 0 and not resp.startswith("Wounded")


def cmd_violence(a):
    ns = [load(p) for p in a.files]
    dials = parse_dials(a.dials) if a.dials else (load(a.world)["dials"] if a.world else
                                                  (ns[0]["dials"] if ns else list(DEFAULT_DIALS)))
    v, o = dial(dials, "V"), dial(dials, "O")
    reg = "Weather" if v >= 3 else "Trade" if (v == 2 or (o >= 2 and dial(dials, "D") >= 2)) else "Rupture"
    print("[narrator only] Register: %s. %s" % (reg, REGISTERS[reg]))
    k = 2 if reg != "Rupture" else 1 + (d(2) == 2)
    for beat in random.sample(DISSONANCE, k):
        print("Dissonance: " + beat)
    print("Aftermath: " + random.choice(AFTERMATH))
    hurt = set(x.lower() for x in (a.hurt or []))
    for n in ns:
        r = violence_response(n, n["name"].lower() in hurt)
        print("%s: %s - %s%s" % (n["name"], r, RESPONSES[r],
              " | outwardly unchanged: this is already who they are" if violence_steady(n, r, dials)
              else " | outward manner changes for the rest of the day"))
    print("Show all of it from outside. Name no one's feelings; let the dissonance sit unexplained.")


def cmd_tide(a):
    import os
    if os.path.exists(a.world):
        w = load(a.world)
    else:
        w = {"dials": parse_dials(a.dials), "week": 0, "history": []}
    w["week"] += 1
    i = d(7) - 1
    r = d(6)
    step = -1 if r == 1 else 1 if r == 6 else 0
    old = w["dials"][i]
    w["dials"][i] = clamp(old + step, 0, 3)
    msg = "Week %d: %s %s" % (w["week"], DIALS[i], "holds" if w["dials"][i] == old else
                             "%d -> %d" % (old, w["dials"][i]))
    w["history"].append(msg)
    save(w, a.world)
    print(msg + " | dials: " + ", ".join("%s %d" % (DIALS[j], w["dials"][j]) for j in range(7)))


def cmd_styles(a):
    print("| Style | Sketch | Can | Vol | Ene | War | Dis | Opn | Dom | Hungers | Shrugs off | Creeds |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in STYLES:
        print("| %s | %s | %s | %s | %s | %s |" % (
            s["name"], s["sketch"], " | ".join("%+d" % x for x in s["ax"]), ", ".join(s["emph"]), s["dis"],
            " / ".join(s["creed"])))
    print()
    print("| Style | Kind (4:3:2:1) | Middle | Hostile | Danger history | Weight (scene) |")
    print("|---|---|---|---|---|---|")
    for s in STYLES:
        dd = s["danger"]
        dtxt = ("+/-1" if dd[0] == 2 else "%+d" % dd[0] if dd[0] else "0") + " " + dd[1]
        wt = str(s["base"]) + "".join(" +" + DIALS["VOSXFPD".index(k)] for k in s["boost"]) + \
             "".join(" -" + DIALS["VOSXFPD".index(k)] for k in s["damp"])
        print("| %s | %s | %s | %s | %s | %s |" % (s["name"], ", ".join(s["kind"]), ", ".join(s["mid"]),
                                                   ", ".join(s["host"]), dtxt, wt))


def cmd_roll(a):
    import re
    m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", a.expr.strip().lower())
    if not m:
        sys.exit("format: NdS[+M]")
    k, s, mod = int(m.group(1) or 1), int(m.group(2)), int(m.group(3) or 0)
    rs = [d(s) for _ in range(k)]
    print("%s: %s = %d" % (a.expr, rs, sum(rs) + mod))


def main():
    p = argparse.ArgumentParser(description="NPC Temperament Engine")
    p.add_argument("--seed", type=int)
    sp = p.add_subparsers(dest="cmd")
    x = sp.add_parser("npc"); x.add_argument("--name"); x.add_argument("--seeded", action="store_true")
    x.add_argument("--dials"); x.add_argument("--save"); x.set_defaults(f=cmd_npc)
    x = sp.add_parser("circle"); x.add_argument("--name", required=True); x.add_argument("--members", nargs="*")
    x.add_argument("--dials"); x.add_argument("--save"); x.set_defaults(f=cmd_circle)
    x = sp.add_parser("day"); x.add_argument("file"); x.add_argument("--world"); x.add_argument("--circle")
    x.set_defaults(f=cmd_day)
    x = sp.add_parser("meet"); x.add_argument("file"); x.add_argument("--who", default="player")
    x.add_argument("--approach", choices=APPROACHES); x.add_argument("--creed", choices=["aligned", "opposed"])
    x.add_argument("--lead", choices=["warm", "hostile"]); x.add_argument("--rival-of-lead", action="store_true")
    x.add_argument("--contagion", type=int, choices=[-1, 1]); x.add_argument("--danger", nargs="*", choices=DANGER)
    x.add_argument("--audience", action="store_true"); x.add_argument("--opposed", action="store_true")
    x.add_argument("--hurt", action="store_true"); x.add_argument("--violence", action="store_true")
    for fl in ("solemn", "festive", "superior", "duty", "drunk", "tired", "sick", "grieving", "private"):
        x.add_argument("--" + fl, action="store_true")
    x.add_argument("--their-strength", type=int, default=2); x.add_argument("--ground", type=int, default=0)
    x.set_defaults(f=cmd_meet)
    x = sp.add_parser("ask"); x.add_argument("file"); x.add_argument("--who", default="player")
    x.add_argument("--touched", action="store_true"); x.add_argument("--asked", action="store_true")
    x.set_defaults(f=cmd_ask)
    x = sp.add_parser("event"); x.add_argument("file"); x.add_argument("kind", choices=list(EVENTS))
    x.add_argument("--who", default="player"); x.add_argument("--size", type=int, choices=[1, 2])
    x.add_argument("--trade", action="store_true"); x.add_argument("--note"); x.set_defaults(f=cmd_event)
    x = sp.add_parser("affinity"); x.add_argument("a"); x.add_argument("b")
    x.add_argument("--tie", choices=["kin", "lover", "friend", "mentor", "rival", "enemy", "creditor", "debtor",
                                     "master", "dependant"]); x.set_defaults(f=cmd_affinity)
    x = sp.add_parser("scene"); x.add_argument("files", nargs="+"); x.add_argument("--world")
    x.set_defaults(f=cmd_scene)
    x = sp.add_parser("status"); x.add_argument("file")
    x.add_argument("condition", choices=["present", "dead", "comatose", "amnesiac"])
    x.add_argument("--restore", action="store_true"); x.set_defaults(f=cmd_status)
    x = sp.add_parser("violence"); x.add_argument("files", nargs="*"); x.add_argument("--world")
    x.add_argument("--dials"); x.add_argument("--hurt", nargs="*"); x.set_defaults(f=cmd_violence)
    x = sp.add_parser("tide"); x.add_argument("world"); x.add_argument("--dials"); x.set_defaults(f=cmd_tide)
    x = sp.add_parser("audit"); x.set_defaults(f=cmd_audit)
    x = sp.add_parser("styles"); x.set_defaults(f=cmd_styles)
    x = sp.add_parser("roll"); x.add_argument("expr"); x.set_defaults(f=cmd_roll)
    a = p.parse_args()
    if not getattr(a, "f", None):
        p.print_help(); return
    if a.seed is not None:
        random.seed(a.seed)
    a.f(a)


if __name__ == "__main__":
    main()
