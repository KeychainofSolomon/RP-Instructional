#!/usr/bin/env python3
"""NPC Temperament Engine. Rules: SKILL.md and references/. Python 3.8+, standard library only.

Dice go upstream: every random roll decides something about a character's life, history
or day. Reactions are then computed from those causes, never rolled directly.
"""
import argparse, collections, hashlib, json, math, random, sys

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
KIND_FORMS = sorted({f for t in STYLES for f in t["kind"]})
MIDDLE_FORMS = sorted({f for t in STYLES for f in t["mid"]})
HOSTILE_FORMS = sorted({f for t in STYLES for f in t["host"]})
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

RUNG_TIES = {"Survival": ["dependant", "kin", "pet"], "Safety": ["enemy"],
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
 "reunion": (1, 1, [(W, 1), (E, 1)], {"Belonging": 2}),
 "joy": (0, 0, [(E, 1), (O, 1)], {"Comfort": 1}),
 "witnessed": (0, 0, [(V, 1)], {"Safety": -1}),
}
STRATAGEMS = [(3, "Overwhelm: confront openly, or toy with them"), (1, "Press: demand terms, show strength"),
              (0, "Wait and probe: test them, seek allies, feint"),
              (-2, "Avoid battle: deceive, appear compliant, strike where unguarded"),
              (-99, "Yield, flee, or appeal to a stronger power")]


SCENE_ABSENT = []
VIEW = {}   # structured result of the last command, for programs that drive the engine


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
    n = {"id": new_id(), "schema": SCHEMA, "name": name or "(unnamed)", "type": kind, "dials": dials, "day": 0, "condition": "present",
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
            n["codes"].append({"code": random.choice([x for x in CODES if x not in [c["code"] for c in n["codes"]]]),
                               "control": ctrl})
        else:
            n["compulsions"].append({"urge": random.choice([x for x in COMPULSIONS
                                                            if x not in [c["urge"] for c in n["compulsions"]]]),
                                     "control": ctrl,
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
    speech_build(n, random.Random(random.random()))
    strain_build(n, random.Random(random.random()))
    tempo_build(n, random.Random(random.random()))
    life_build(n, random.Random("life:%s" % n["id"]), add_ties=True)   # own dice: the rest of the build is untouched
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
            return migrate(json.load(f))
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
    sp_ = speech_of(n)
    print("Speech: %s%s (%s)%s | bends words: %s" % (
        ("%s " % fmt_frac(sp_["frac"])) if sp_["side"] else "", sp_["main"],
        REG_WORD[sp_["reg"]], (" + %s %s" % (fmt_frac(1 - sp_["frac"]), sp_["side"])) if sp_["side"] else "",
        sp_["bend"] + ("; slang: " + ", ".join(sp_["slang"]) if sp_["slang"] else "") + ("; code-switches" if sp_["switches"] else "")))
    co = n["contradiction"]
    print("Contradiction: %s at %s | Quirk: %s" % (co["pair"], co["ratio"], "; ".join(n["quirks"])))
    if n["scars"]:
        print("Danger history: " + ", ".join("%s (%+d, %s)" % (k, v["dir"], v["form"]) for k, v in n["scars"].items()))
    show_life(n)


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
        dead = [m["name"] for m in ms if m["condition"] == "dead"]
        ms = [m for m in ms if m["condition"] != "dead"]
        if dead:
            print("Left out (dead): " + ", ".join(dead))
        if not ms:
            sys.exit("A circle needs at least one living member.")
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
        n["creed"] = max(sorted(set(creeds)), key=creeds.count)  # sorted: ties break the same way every run
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
        if k == "grief_pending":
            continue
        af[k] -= 1
        if af[k] <= 0:
            del af[k]
            if k == "grief_delay" and af.get("grief_pending"):
                af["grieving"] = af.pop("grief_pending")
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
        if rung == "Comfort" and cause in ("indulged a pleasure", "went without a small pleasure they rely on"):
            likes = [t["thing"] for t in life_of(n)["tastes"] if t["side"] == "like" and t["cat"] in PLEASURE_CATS]
            if likes:
                cause += ": " + random.choice(likes)
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
    back = resurface(n)
    if back:
        notes.append("an old memory came back to them today: the %s%s" % (back["event"], ", on its anniversary" if back["anniversary"] else ""))
    belief_day(n)
    notes += affect_day(n)
    notes += incline_day(n)
    notes += clarity_check(n)
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
        shown = {k: v for k, v in af.items() if k not in ("grief_delay", "grief_pending")}
        if af.get("grief_delay"):
            shown["grief yet to come, in"] = af["grief_delay"]
        print("Lasting states: " + ", ".join("%s (%d more day%s)" % (k, v, "" if v == 1 else "s") for k, v in shown.items()))
    if trailing:
        print("Speech today: trailing off now and then (%s). A few ellipses across the scene, not every line."
              % trailing)
    for x in notes:
        if x:
            print("Note: " + x)
    save(n, a.file)
    VIEW.clear()
    VIEW.update({"cmd": "day", "name": n["name"], "cause": cause, "value": val, "rung": rung,
                 "open": open_today, "trailing": trailing, "notes": [x for x in notes if x],
                 "lasting": {k: v for k, v in af.items() if k not in ("grief_delay", "grief_pending")}, "resurfaced": back})


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
 "Wounded-Shock": {"wounded"}, "Wounded-Betrayed": {"wounded"},
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
 "protecting": R(itag={"action"}, block={"levity", "display", "leisure", "giving", "intimate", "sad"},
                 repl={"Kind": "Protective", "Middle": "Wary", "Hostile": "Territorial"},
                 inflect="keeps between them and harm", speech=("short", "flow"), slip=1,
                 voices=("Commanding", "Devoted", "Vigilant"), approach={"humour": -1, "pressure": -1}),
 "grieving": R(itag=lambda n: {"sad"} | PROCESSING[processing(n)][1], block={"levity", "display", "leisure"},
               repl={"Kind": lambda n: "Tender" if _ax(n, W) >= 1 else "Practical", "Middle": "Melancholic",
                     "Hostile": lambda n: "Reproach" if _ax(n, W) >= 0 else "Grudge"},
               swap={"Fear-Aggression": lambda n: "Reproach" if _ax(n, W) >= 0 else "Grudge"},
               soften=(lambda n: "laughs at the wrong moments" in n["quirks"] or (_ax(n, E) >= 2 and _ax(n, O) >= 2),
                       {"levity"}, "gallows humour, a little too bright"),
               inflect=lambda n: "a stillness at the edges; " + PROCESSING[processing(n)][0],
               speech=("trailing", "flow"),
               slip=2, voices=("Serious", "Mercurial", "Self-Sacrificing", "Devoted"),
               approach={"humour": -2, "haggling": -2, "flattery": -1, "pressure": -1, "patience": 1}),
 "clear": R(itag={"plain"}, block={"fear", "rage", "petty", "display"},
            repl={"Kind": "Candid", "Middle": "Curious", "Hostile": "Cold Refusal"},
            inflect="unusually clear and unhurried; sees what's in front of them",
            speech=("plain and unhurried", "flow"), slip=1, approach={"pressure": -1, "bluntness": 1}),
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
CONDS = ["hurt", "frozen", "afraid", "enraged", "stunned", "tending", "protecting", "grieving", "clear", "sick", "exhausted",
         "intoxicated", "starving", "solemn", "festive", "superior", "intimate", "public", "duty"]
STRESS = {"hurt", "frozen", "afraid", "enraged", "stunned", "tending", "protecting", "grieving", "solemn", "superior"}
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

SIDE_VARIANTS = {
 "keeps within bounds": ["keeps within bounds", "careful not to overstep", "stops short of too much"],
 "goes a step too far": ["goes a step too far", "pushes past where they should stop", "one remark too many"],
 "an odd turn of phrase": ["an odd turn of phrase", "a strange choice of words", "a phrase that doesn't quite fit"],
 "by the book": ["by the book", "proper about it", "does it the set way"],
 "keeps a little apart": ["keeps a little apart", "a half-step back from everyone", "holds something back"],
 "draws others in": ["draws others in", "pulls people into it", "makes room for others"],
 "says it straight": ["says it straight", "no hedging", "plain about it"],
 "a sly edge": ["a sly edge", "a knowing look", "something left unsaid, on purpose"],
 "pushes": ["pushes", "leans in", "presses the point"],
 "gives ground": ["gives ground", "lets it go", "steps back"],
 "very still": ["very still", "barely moves", "hands at rest"],
 "can't keep still": ["can't keep still", "fidgets", "restless hands"],
 "blunt": ["blunt", "doesn't soften it", "short and to the point"],
 "says it sideways": ["says it sideways", "comes at it from the side", "hints instead of saying"],
 "a lightness under it": ["a lightness under it", "a smile not far off", "easy about it"],
 "a brooding undertone": ["a brooding undertone", "something heavy underneath", "a shadow in it"],
 "fair-minded": ["fair-minded", "gives credit where it's due", "weighs both sides"],
 "a petty jab slips in": ["a petty jab slips in", "a small dig", "a needling aside"],
 "even-handed": ["even-handed", "level", "evenly weighed"],
 "angling for advantage": ["angling for advantage", "looking for the edge", "working an angle"],
}

CHRONIC_VARIANTS = {
 "eyes go to any food": ["eyes go to any food", "a hollow look about them", "notices every crumb", "thin in the face"],
 "pale, slow, short of breath": ["pale, slow, short of breath", "a cough they keep swallowing", "moves carefully, as if it hurts"],
 "heavy-lidded; leans on things": ["heavy-lidded; leans on things", "slow to answer", "rubs their eyes", "sits whenever they can"],
 "out of habit": ["out of habit", "the way they always do", "by long habit"],
 "loud, close, leaning in": ["loud, close, leaning in", "voice rising, too near", "in your face", "a finger jabbing the air"],
 "held very still; every word measured": ["held very still; every word measured", "a dangerous calm", "jaw set, voice level"],
 "eyes on the exits; small, fast movements": ["eyes on the exits; small, fast movements", "keeps glancing at the door", "jumpy"],
 "aware of being watched": ["aware of being watched", "plays a little to the room", "glances at who's listening"],
 "one eye on the post": ["one eye on the post", "never quite off duty", "keeps checking the time"],
 "low voices, set forms": ["low voices, set forms", "the proper words", "quiet and formal"],
 "loose: too loud or too slow; says more than they mean": ["loose: too loud or too slow; says more than they mean",
                                                          "the drink in their voice", "a little too frank"],
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
    if (n.get("affect") or {}).get("clarity_days"): c.add("clear")
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
    if pair and random.random() < 0.55:
        txt, tg = pair[0 if side == "A" else 1]
        txt = random.choice(SIDE_VARIANTS.get(txt, [txt]))
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



# ---------- speech: a baseline way of talking, bent by mood and the moment, never wholly ----------
# Each manner: register (0 street, 1 plain, 2 formal, 3 ceremonial), length (0 terse, 1 measured,
# 2 expansive), keywords, devices (structural habits, three each), how it turns warm, how it turns
# hostile, and what it fits: axes, styles, creeds, world settings.
REG_WORD = ["street", "plain", "formal", "ceremonial"]
LEN_WORD = ["terse", "measured", "expansive"]
SPEECH = {
    "Gutterquick": dict(reg=0, len=0, keys="street talk, quick, slangy, all nicknames",
        dev=["coins and clips words; slang for anything that matters", "calls everyone by a nickname or a street name",
             "drops the subject and the small words: seen it, didn't like it"],
        warm="the nicknames turn fond; strangers get kin-words", cold="slang spat like gravel; your name bent into an insult",
        ax={E: 1, D: -1, C: 0.5}, st=("Adventurous", "Mercurial", "Self-Made"), cr=("Thrill", "Freedom"), dl="SV", low=True),
    "Dealmaker": dict(reg=1, len=1, keys="transactional, streetwise, easy, always pricing",
        dev=["everything framed as a deal, a cut, a favour owed", "trade talk: terms, margins, who's good for it",
             "a friendly opener that gets to the number"],
        warm="throws something in for free; calls you a regular", cold="the price climbs mid-sentence; talks about you as a cost",
        ax={M: 0.5, W: -0.5, C: -0.5}, st=("Self-Made", "Schemer", "Professional"), cr=("Gain",), dl="SD", low=True),
    "Velvet": dict(reg=2, len=1, keys="oblique, courteous, unhurried, family-minded",
        dev=["never names a threat; makes it an offer, a friendship, a favour", "speaks of respect, of what is owed, of family",
             "slow and quiet; lets silences do the work"],
        warm="the favour is real and generous, the respect sincere", cold="the courtesy thickens; the offer becomes one nobody refuses",
        ax={D: 1, M: 1, C: -1}, st=("Commanding", "Schemer", "Benevolent"), cr=("Kin", "Security"), dl="DPV"),
    "Hearthside": dict(reg=1, len=1, keys="homely, proverbial, rooted, warm",
        dev=["answers with a saying or a proverb", "images of weather, bread, animals, the seasons",
             "little names and kin-words for people"],
        warm="folk comfort; small blessings", cold="a proverb used like a door closing",
        ax={W: 1.5, O: -0.5, V: -0.5}, st=("Leisurely", "Benevolent", "Devoted", "Self-Sacrificing"), cr=("Kin", "Mercy", "Security"), dl="FS", low=True),
    "Salon": dict(reg=2, len=2, keys="elegant, performed, gossiping, borrowed phrases",
        dev=["a learned or foreign phrase dropped in for effect", "compliments with a hook in them",
             "talks of who is who and who is seen with whom"],
        warm="charming; sweeps you into the circle", cold="a compliment that cuts; laughs at you for the room",
        ax={E: 1, C: -1, W: 0.5}, st=("Dramatic", "Mercurial", "Self-Assured"), cr=("Pleasure", "Excellence"), dl="PD"),
    "Courtly": dict(reg=3, len=1, keys="titled, precise, weighed, ranked",
        dev=["titles and the proper forms of address, always", "every word weighed; nothing that could be held against them",
             "insult only by omission, or by too much courtesy"],
        warm="grants you a title; speaks of your standing", cold="withholds your title; cold correctness",
        ax={D: 2, M: 1, C: -0.5}, st=("Commanding", "Conscientious", "Serious"), cr=("Order", "Excellence"), dl="PO", rank=True),
    "Liturgical": dict(reg=3, len=2, keys="scriptural, rolling, archaic, invoking",
        dev=["clauses chained with and, and, and", "old forms and set phrases; blessings and curses",
             "calls on higher powers as witnesses"],
        warm="blessings and benedictions; calls you child", cold="pronounces judgement in the old words",
        ax={O: 0.5, D: 0.5}, st=("Zealot", "Devoted", "Visionary"), cr=("Faith",), dl="FX"),
    "Orator": dict(reg=2, len=2, keys="declaiming, sweeping, argued, certain",
        dev=["builds a long case to a point; asks questions and answers them", "speaks of history, nature, the whole of mankind",
             "addresses the room even one to one"],
        warm="takes you into the argument as a peer", cold="lectures you on your smallness, reasonably and terribly",
        ax={M: 2, O: 1, E: 1}, st=("Visionary", "Commanding", "Dramatic", "Predator"), cr=("Strength", "Excellence"), dl="PV"),
    "Laconic": dict(reg=1, len=0, keys="spare, flat, few words, silences",
        dev=["answers in a word, or not at all", "no small talk; says what's needed and stops",
             "a silence where an answer would go"],
        warm="a nod; one short word that is enough", cold="one word, and it's final",
        ax={E: -2, D: 1, C: 0.5}, st=("Solitary", "Vigilant", "Serious"), cr=("Security", "Strength"), dl="VS", low=True),
    "Aphorist": dict(reg=2, len=0, keys="compressed, barbed, paradoxical, provoking",
        dev=["short sharp sayings that turn an idea upside down", "mockery with a thinker's edge",
             "leaves the thought unfinished for you to finish"],
        warm="plays with you; laughs at the world beside you", cold="a single line that flays",
        ax={O: 2, C: 1, M: 0.5}, st=("Visionary", "Self-Assured", "Solitary"), cr=("Freedom", "Strength"), dl="X"),
    "Double-Edged": dict(reg=2, len=1, keys="layered, testing, careful, second meanings",
        dev=["every line can be read two ways", "answers a question with a question",
             "watches what their words do to you"],
        warm="lets you in on the second meaning", cold="the second meaning is a blade",
        ax={D: 1, C: -1.5, O: 1}, st=("Schemer", "Vigilant", "Conscientious"), cr=("Order", "Gain"), dl="DPX"),
    "Strategist": dict(reg=1, len=1, keys="positional, conditional, patient, unrevealing",
        dev=["talks of ground, timing, who holds what", "if this, then that; never commits early",
             "concedes the small thing to keep the large"],
        warm="advises you as an ally", cold="sizes you up aloud as an obstacle",
        ax={D: 2, V: -1, O: 0.5}, st=("Vigilant", "Commanding", "Professional"), cr=("Order", "Security"), dl="VP"),
    "Ironclad": dict(reg=1, len=1, keys="absolute, principled, declarative, unbending",
        dev=["states principles as facts: I will, I won't", "sorts people into the worthy and the leeches",
             "refuses compromise in so many words"],
        warm="respect, stated plainly, to an equal", cold="contempt, stated as a principle",
        ax={M: 1, C: 2, W: -1}, st=("Self-Made", "Self-Assured", "Zealot"), cr=("Excellence", "Freedom", "Justice"), dl="O"),
    "Muddler": dict(reg=1, len=1, keys="colloquial, mundane, worried, off on tangents",
        dev=["frets about small things: money, machines, what's owed", "a sudden question about what's real, then back to the bills",
             "unfinished thoughts; anyway, never mind"],
        warm="confides small troubles; shares what they have", cold="petty and aggrieved; it's your fault too",
        ax={D: -1, O: 1, V: 0.5}, st=("Sensitive", "Leisurely", "Mercurial"), cr=("Security", "Pleasure"), dl="SX", low=True),
    "Static": dict(reg=1, len=1, keys="jittery, suspicious, self-interrupting, unsure",
        dev=["breaks off mid-sentence and starts again", "repeats a word as if to check it",
             "asks whether you saw or heard that too"],
        warm="trusts you as the one solid thing", cold="accuses; you're part of it",
        ax={V: 2, D: -1, O: 0.5}, st=("Vigilant", "Sensitive"), cr=("Security", "Freedom"), dl="XD"),
    "Corporate": dict(reg=2, len=1, keys="procedural, euphemistic, polished, speaks as we",
        dev=["passive voice; nothing is anyone's fault", "a soft word for anything ugly",
             "speaks for an institution: we, policy, the process"],
        warm="a warm script; remembers your name; offers what the rules allow", cold="regret expressed, decision final, smiling",
        ax={D: 1, C: -1, W: -0.5}, st=("Professional", "Conscientious", "Schemer"), cr=("Order", "Gain"), dl="OP"),
    "Barracks": dict(reg=0, len=0, keys="blunt, profane, gallows humour, practical",
        dev=["swears like punctuation", "jokes about death, the food, the officers",
             "orders, not requests"],
        warm="rough affection; insults as love", cold="threats in plain words",
        ax={C: 1, M: 1}, st=("Adventurous", "Professional", "Commanding"), cr=("Strength", "Kin"), dl="VO", low=True),
    "Tender": dict(reg=1, len=1, keys="affectionate, soft, attentive, endearing",
        dev=["endearments: love, dear, little one", "softens everything: just, maybe, if you like",
             "asks after you before anything else"],
        warm="every endearment they have", cold="the sweetness stays, and turns to ice",
        ax={W: 2, V: -0.5}, st=("Benevolent", "Self-Sacrificing", "Sensitive", "Devoted"), cr=("Mercy", "Kin"), dl="F"),
    "Cutting": dict(reg=1, len=0, keys="callous, belittling, dismissive, sneering",
        dev=["calls you by a slight instead of a name", "dismissive one-liners", "interrupts"],
        warm="the barbs turn to teasing", cold="cruelty in very few words",
        ax={W: -2, M: 1, C: 0.5}, st=("Predator", "Self-Assured", "Schemer"), cr=("Strength", "Thrill"), dl="VP"),
    "Yarn-Spinner": dict(reg=1, len=2, keys="anecdotal, digressive, chummy, rambling",
        dev=["every point becomes a story", "that reminds me of the time...", "names people you've never met as if you had"],
        warm="tells you the good story, the one they save", cold="a story about someone like you, who came to a bad end",
        ax={E: 2, W: 1, D: -1}, st=("Leisurely", "Adventurous", "Dramatic"), cr=("Pleasure", "Kin"), dl="", low=True),
    "Pedant": dict(reg=2, len=2, keys="exact, qualifying, correcting, citing",
        dev=["qualifies everything; corrects small errors", "uses the proper term and explains it",
             "cites the rule, the source, the precedent"],
        warm="teaches gladly", cold="corrects you into the floor",
        ax={O: 1, D: 2, E: -1}, st=("Conscientious", "Serious", "Solitary"), cr=("Order", "Excellence"), dl="O"),
    "Sign-Reader": dict(reg=2, len=1, keys="dreamlike, symbolic, oblique, strange",
        dev=["speaks of signs, omens, colours and numbers", "now and then addresses someone who isn't there",
             "pairs images that don't belong together"],
        warm="a blessing in a strange shape", cold="an omen, about you",
        ax={O: 2, V: 1}, st=("Visionary", "Sensitive", "Zealot"), cr=("Faith", "Freedom"), dl="XF"),
    "Braggart": dict(reg=1, len=2, keys="loud, superlative, self-crowning, grand",
        dev=["superlatives, and their own name", "tall claims, every number rounded up", "exclaims"],
        warm="makes you part of the legend", cold="brags at your expense",
        ax={E: 2, M: 1, C: -1}, st=("Dramatic", "Self-Assured", "Adventurous"), cr=("Thrill", "Excellence"), dl="V"),
    "Earnest": dict(reg=1, len=1, keys="simple, literal, honest, guileless",
        dev=["short honest sentences", "plain questions; takes words at face value", "says what they think, then waits"],
        warm="open gladness", cold="plain hurt, plainly said",
        ax={C: 2, O: -0.5, M: -1}, st=("Devoted", "Sensitive", "Leisurely"), cr=("Mercy", "Security"), dl="", low=True),
    "Operator": dict(reg=1, len=0, keys="brief, coded, exact, businesslike",
        dev=["the shorthand of their trade", "facts first, no preamble", "reads back what you said to confirm it"],
        warm="a professional courtesy; a tip, off the record", cold="terms, and nothing else",
        ax={D: 2, E: -1, C: 1}, st=("Professional", "Vigilant", "Conscientious"), cr=("Order", "Security"), dl="OV"),
}

# How slang is made, in any language: the narrator invents the actual words to suit the setting.
SLANG = {
    "reversal": "flips syllables or letters of ordinary words; the flipped word drifts to a new meaning",
    "rhyme": "says a phrase that rhymes with the word, then drops the rhyming half",
    "borrowing": "words taken from neighbouring tongues, the old country, or newcomers",
    "cant": "a dozen words for the watch, for money, for stealing; one for everything else",
    "figure": "a picture for a thing: windows for eyes, a fish for a fake",
    "suffix": "tacks a made-up ending onto ordinary words to make them theirs",
    "clipping": "cuts words short and runs them together",
    "codes": "numbers and initials that sound like words or stand for them",
    "tags": "ends lines with a tag that asks for agreement",
    "oaths": "swears by something holy or by their mother as a flourish, true or not",
}

# How they bend words: honest and manipulative speech. None of these is ever a tell on its own:
# plain dealers flatter sincerely, and practised manipulators sound frank. Tells still come only
# from a slip, at or after a deception.
BEND = {
    "Plain": dict(base="specific and concrete; says no plainly; admits what they don't know",
        work="lays their reasons out, even the unflattering ones"),
    "Tactful": dict(base="true, but softened; leaves the hardest part unsaid",
        work="picks the kindest true thing to say, and stops there"),
    "Palterer": dict(base="never quite lies; true things, arranged to mislead",
        work="answers a different question, truthfully; lets the wrong impression stand"),
    "Spinner": dict(base="frames everything; flattery, what everyone else is doing, what you surely already agree",
        work="builds the question so that every answer is yes"),
    "Worker": dict(base="works on you: obligation, guilt, a deadline that isn't real",
        work="a small yes first, then the real ask; if caught, turns it round so that you're the one at fault"),
}


def _speech_score(key, n, dials):
    s = SPEECH[key]
    ax = n["axes"]
    sc = 1.0 + sum(w * ax[i] for i, w in s["ax"].items()) * 0.6
    sc += sum(3 * v["frac"] for v in n["voices"] if v["style"] in s["st"])
    sc += 1.5 if n.get("creed") in s["cr"] else 0
    sc += 0.5 * sum(dial(dials, k) for k in s["dl"])
    if s.get("rank"):
        sc += 0.5 * RANK.get(n.get("station"), 0)
    if s.get("low") and RANK.get(n.get("station"), 0) >= 2:
        sc -= 1
    if n.get("authenticity", {}).get("kind") == "Hollow" and key in ("Salon", "Corporate", "Velvet"):
        sc += 2
    return max(0.05, sc) ** 2


def speech_build(n, rng=None):
    """A person's baseline way of talking, worked out from who they are and the world they grew in."""
    rng = rng or random.Random("speech:%s:%s" % (n.get("name"), n.get("axes")))
    dials = n.get("dials") or list(DEFAULT_DIALS)
    keys = sorted(SPEECH)
    wts = [_speech_score(k, n, dials) for k in keys]
    main = rng.choices(keys, wts)[0]
    side, frac = None, 1.0
    if rng.random() < 0.45:
        rest = [k for k in keys if k != main and abs(SPEECH[k]["reg"] - SPEECH[main]["reg"]) <= 2]
        side = rng.choices(rest, [_speech_score(k, n, dials) for k in rest])[0]
        frac = rng.choice([0.75, 0.75, 0.6, 0.5])
    reg = SPEECH[main]["reg"] if not side else round(frac * SPEECH[main]["reg"] + (1 - frac) * SPEECH[side]["reg"])
    slang = []
    if reg <= 1:
        k = 2 if reg == 0 else (1 if rng.random() < 0.5 else 0)
        sw = {s: 1.0 for s in SLANG}
        if dial(dials, "D") >= 2 or n["axes"][C] <= -1: sw["cant"] += 2; sw["reversal"] += 1
        if dial(dials, "S") >= 2: sw["borrowing"] += 1; sw["figure"] += 1
        if n["axes"][O] >= 2: sw["rhyme"] += 1; sw["codes"] += 1
        while len(slang) < k:
            pick = rng.choices(list(sw), list(sw.values()))[0]
            if pick not in slang: slang.append(pick)
    switches = bool(slang) and (n["axes"][D] >= 1 or n["axes"][O] >= 1 or rng.random() < 0.3)
    c, dec = n["axes"][C], dial(dials, "D")
    dom = n["voices"][0]["style"]
    lean = c - 0.5 * dec + (-2 if dom in ("Schemer", "Predator") else 0) + (-1.5 if n.get("authenticity", {}).get("kind") in ("Masked", "Hollow") else 0)
    lean += rng.choice([-1, 0, 0, 1])
    bend = "Plain" if lean >= 1.5 else "Tactful" if lean >= -0.5 else "Palterer" if lean >= -1.5 else "Spinner" if lean >= -3.5 else "Worker"
    n["speech"] = {"main": main, "side": side, "frac": frac, "reg": reg, "slang": slang, "switches": switches, "bend": bend}
    return n["speech"]


def speech_of(n):
    """Ledgers made before speech existed get theirs on first use, the same every time."""
    if not isinstance(n.get("speech"), dict) or n["speech"].get("main") not in SPEECH:
        speech_build(n)
    return n["speech"]


REG_UP = {"solemn", "superior", "duty", "public", "tending"}
REG_DOWN = {"festive", "intoxicated", "intimate", "exhausted"}
SHORTER = {"hurt", "afraid", "exhausted", "sick", "starving", "enraged", "stunned", "frozen"}


def speech_now(n, active, band, scheming=False, rng=None):
    """How their way of talking comes out right now. The moment pulls register and length one step
    at most; the manner and its habits stay. Returns a dict of plain notes."""
    rng = rng or random
    sp = speech_of(n)
    act = set(active)
    m = SPEECH[sp["main"]]
    base_reg, base_len = sp["reg"], m["len"]
    up, down = bool(act & REG_UP), bool(act & REG_DOWN)
    if "enraged" in act and n["axes"][D] < 2: down = True
    shift = (1 if up and not down else -1 if down and not up else 0)
    if sp["switches"] and up and not down: shift = 1  # those who code-switch do it readily for authority
    reg = clamp(base_reg + shift, max(0, base_reg - 1), min(3, base_reg + 1))
    ln = base_len - (1 if act & SHORTER else 0) + (1 if act & {"festive", "intoxicated"} and n["axes"][E] >= 0 else 0)
    ln = clamp(ln, max(0, base_len - 1), min(2, base_len + 1))
    if act & {"frozen", "stunned"}: ln = 0
    pool = list(m["dev"])
    devs = rng.sample(pool, 2)
    if sp["side"] and rng.random() < 1 - sp["frac"] + 0.25:
        devs.append(rng.choice(SPEECH[sp["side"]]["dev"]))
    keys = m["keys"] + ((", with something " + SPEECH[sp["side"]]["keys"].split(",")[0] + " in it") if sp["side"] else "")
    tone = m["warm"] if band in ("Kind", "Warm") else m["cold"] if band == "Hostile" else \
        "less of it than usual; held back" if band == "Cool" else None
    here = []
    if reg > base_reg:
        here.append("the moment pulls them toward a more %s register; the manner underneath stays" % REG_WORD[reg])
    elif reg < base_reg:
        here.append("the moment loosens them toward a more %s register; the manner underneath stays" % REG_WORD[reg])
    if ln < base_len:
        here.append("fewer words than usual")
    elif ln > base_len:
        here.append("more words than usual")
    slang = [SLANG[s] for s in sp["slang"]]
    if slang and reg >= 2 and sp["switches"]:
        slang = []
        here.append("they drop the street words here, and would pick them up again with their own")
    b = BEND[sp["bend"]]
    bend = b["work"] if scheming else b["base"]
    return {"manner": sp["main"], "keys": keys, "habits": devs, "tone": tone, "here": here,
            "register": REG_WORD[reg], "length": LEN_WORD[ln], "slang": slang, "bend": bend, "bend_kind": sp["bend"]}



# ---------- identity under strain: a recognisable pattern of choices, kept for life ----------
STRAIN_WAYS = {
    "withdraw": "goes quiet and pulls back, and keeps their distance afterwards",
    "confront": "faces it head-on, there and then",
    "laugh_remember": "laughs it off in front of others, and remembers it exactly",
    "reconcile": "reaches to mend things, because the bond matters more than the sting",
    "retaliate_later": "says nothing now and settles it later, in their own time",
    "freeze": "goes still and blank, and acts only once it's over",
    "appease": "gives ground and tries to make it right, even when it isn't theirs to",
    "deflect": "turns it aside with a joke or a change of subject",
    "formal": "retreats into correctness: rules, roles, the proper forms",
    "rally": "goes to their own people and makes it a matter for all of them",
    "coldness": "turns politely and lastingly cold",
    "self_blame": "turns it on themself; works harder, sleeps worse",
    "basks": "basks in it, and wants more",
    "suspects": "wonders what it's for",
    "shares": "hands the credit to others",
}
STRAIN_FIT = {  # axis weights, styles that lean this way
    "withdraw": ({E: -1, M: -1}, ("Solitary", "Sensitive")),
    "confront": ({M: 1.5, V: 1, C: 0.5}, ("Commanding", "Adventurous", "Zealot")),
    "laugh_remember": ({E: 1, D: 0.5, C: -1}, ("Dramatic", "Schemer", "Mercurial")),
    "reconcile": ({W: 1.5, M: -0.5}, ("Benevolent", "Devoted", "Self-Sacrificing")),
    "retaliate_later": ({D: 1, W: -1, C: -1}, ("Predator", "Schemer", "Vigilant")),
    "freeze": ({V: 1, E: -1, M: -1.5}, ("Sensitive",)),
    "appease": ({W: 1, M: -1.5}, ("Self-Sacrificing", "Devoted")),
    "deflect": ({E: 1, O: 0.5, V: -0.5}, ("Leisurely", "Mercurial", "Dramatic")),
    "formal": ({D: 1.5, O: -1}, ("Conscientious", "Professional", "Serious")),
    "rally": ({W: 0.5, M: 0.5}, ("Commanding", "Devoted")),
    "coldness": ({W: -1, D: 1}, ("Serious", "Self-Assured")),
    "self_blame": ({V: 0.5, M: -1, C: 0.5}, ("Sensitive", "Conscientious", "Self-Sacrificing")),
    "basks": ({E: 1, M: 1}, ("Dramatic", "Self-Assured")),
    "suspects": ({C: -0.5, O: -0.5, D: 0.5}, ("Vigilant", "Schemer")),
    "shares": ({W: 1, M: -1}, ("Benevolent", "Devoted")),
}
STRAINS = {
    "humiliation": ("withdraw", "confront", "laugh_remember", "reconcile", "retaliate_later", "deflect", "coldness", "self_blame"),
    "threat": ("confront", "freeze", "appease", "rally", "withdraw", "deflect", "formal", "retaliate_later"),
    "loss": ("withdraw", "formal", "self_blame", "rally", "deflect", "freeze"),
    "betrayal": ("confront", "coldness", "retaliate_later", "reconcile", "withdraw", "self_blame", "rally", "laugh_remember"),
    "praise": ("basks", "suspects", "shares", "deflect", "withdraw", "self_blame"),
    "cornered": ("confront", "freeze", "appease", "deflect", "formal", "rally", "retaliate_later", "laugh_remember"),
}
EVENT_STRAIN = {"humiliation": "humiliation", "threat": "threat", "loss": "loss", "betrayal": "betrayal",
                "lie-caught": "betrayal", "respect": "praise", "triumph": "praise"}
HOLDS_IT = {"laugh_remember", "retaliate_later", "coldness"}


def _strain_score(way, n):
    ax_w, styles = STRAIN_FIT[way]
    sc = 1.0 + 0.6 * sum(w * n["axes"][i] for i, w in ax_w.items())
    sc += sum(2 * v["frac"] for v in n["voices"] if v["style"] in styles)
    if way == "rally" and n.get("creed") in ("Kin", "Order"):
        sc += 1
    return max(0.05, sc) ** 2


def strain_build(n, rng=None):
    rng = rng or random.Random("strain:%s" % n.get("id", n.get("name")))
    # traits set the odds; a personal idiosyncrasy per choice keeps similar people from being copies
    n["strain"] = {p: rng.choices(ways, [_strain_score(w, n) * rng.lognormvariate(0, 0.7) for w in ways])[0]
                   for p, ways in STRAINS.items()}
    return n["strain"]


def strain_of(n):
    if not isinstance(n.get("strain"), dict) or set(n["strain"]) != set(STRAINS):
        strain_build(n)
    return n["strain"]


# ---------- ordinary life: most days, most business, most odd moments mean nothing ----------
ORDINARY += [
    "a chore that took longer than it should have", "a small errand, done", "mended something that keeps breaking",
    "waited a long time for something that came in the end", "a good meal, nothing special about it",
    "lost something small and found it again", "talked about the weather with a neighbour",
    "an argument about nothing, already forgotten", "a bit of gossip that went nowhere", "a stiff neck from sleeping wrong",
    "paid a small bill", "a long walk somewhere and back", "too much to do and too little time, as usual",
    "a quiet day; nothing happened", "heard a song they couldn't get out of their head", "cleaned up after someone else",
    "had to wait their turn", "a visit from someone who stayed too long", "the usual work, the usual way",
    "an old acquaintance passed in the street and they didn't stop", "a minor mix-up over who was meant to do what",
    "ran out of something ordinary and had to borrow", "a dull day, and glad of it", "fixed a squeak, a leak or a draught",
    "a small win at a game, a small loss at another", "sorted through old things and kept most of them",
    "got caught in the rain or the heat", "a misunderstanding with a stranger, cleared up", "slept well for once",
    "the same as yesterday",
]
BUSINESS = [
    "counting something under their breath", "eating while they talk", "mending or fiddling with something small",
    "waiting for someone who's late", "looking for something they've put down", "finishing a task they won't leave half done",
    "keeping half an eye on something across the room", "tidying what doesn't need tidying", "making a list",
    "complaining mildly about something unrelated", "trying to remember a name", "rubbing a sore hand or shoulder",
    "carrying something they need to put down", "on their way somewhere else", "humming without noticing",
    "fussing with a stain or a loose thread", "working out what they owe someone, or what someone owes them",
    "half-listening to another conversation", "warming their hands or fanning themself", "fed up with a neighbour's noise",
]
MISHEAR = [
    "mishears a word you say and answers the wrong question",
    "takes something you say more seriously than you meant it",
    "takes something you say as a joke when it wasn't",
    "thinks you mean someone else when you mention a person",
    "reads a gesture of yours the wrong way",
    "assumes you already know something you don't",
]


def ordinary_beats(n, active, rng=None):
    """Inconsequential business and the odd honest misunderstanding: texture, never clues."""
    rng = rng or random
    act = set(active)
    beats = {"business": None, "mishear": None}
    if not act & {"frozen", "stunned", "hurt", "afraid", "enraged"} and rng.random() < 0.3:
        beats["business"] = rng.choice(BUSINESS)
    chance = 0.02 + (0.02 if act & {"exhausted", "intoxicated", "sick"} else 0) + \
        (0.01 if act & {"public", "festive"} else 0) + (0.01 if n["axes"][O] <= -2 else 0)
    if not act & {"frozen", "stunned"} and rng.random() < min(chance, 0.05):
        beats["mishear"] = rng.choice(MISHEAR)
    return beats


# ---------- schema and identity ----------
SCHEMA = 4


def new_id(rng=None):
    return "p%012x" % (rng or random).getrandbits(48)


def tempo_build(n, rng=None):
    """How fast this person, in particular, recovers and how readily old things come back to them.
    People are not clocks: the mechanics stay, the pace is theirs."""
    rng = rng or random.Random("tempo:%s" % n.get("id", n.get("name")))
    v = n["axes"][V]
    n["tempo"] = {"grief": round(clamp(rng.lognormvariate(0.05 * v, 0.35), 0.4, 2.5), 2),
                  "fade": round(clamp(rng.lognormvariate(-0.05 * n["axes"][D], 0.3), 0.5, 2.0), 2),
                  "recall": round(clamp(rng.lognormvariate(0.1 * v, 0.5), 0.2, 3.0), 2)}
    return n["tempo"]


def tempo_of(n):
    if not isinstance(n.get("tempo"), dict) or set(n["tempo"]) != {"grief", "fade", "recall"}:
        tempo_build(n)
    return n["tempo"]


def resurface(n):
    """Now and then an old memory comes back unbidden, more on its anniversary, less as it ages."""
    tp = tempo_of(n)
    for m in reversed((n.get("memory") or [])[-40:]):
        if not (m.get("weight", 0) >= 2 or m.get("took") in HOLDS_IT or m.get("event") in ("loss", "betrayal", "rescue")):
            continue
        age = n["day"] - m.get("day", 0)
        if age <= 0:
            continue
        p_ = 0.015 * tp["recall"] / (1 + age / 60.0) + (0.25 if age % 365 == 0 else 0)
        if random.random() < p_:
            sign = EVENTS.get(m["event"], (0,))[0] or (-1 if m["event"] in ("loss", "witnessed") else 1)
            af = affect(n)
            af["feeling"] = clamp(af["feeling"] + 0.5 * sign * max(1, m.get("weight", 1)), -10, 10)
            return {"event": m["event"], "with": m.get("with"), "anniversary": age % 365 == 0}
    return None



# ---------- life: family, tastes, pets, outlook on the unseen ----------
# Four layers that stand beside temperament rather than flowing from it. People are not
# internally consistent: how far each one strays from their own grain is itself rolled.
IDIO = ["Consistent", "Ordinary", "Marked", "Riddled"]
IDIO_WORD = {"Consistent": "all of a piece; what they like suits who they are",
             "Ordinary": "mostly of a piece, with the usual odd corner",
             "Marked": "full of corners; several tastes cut against their grain",
             "Riddled": "a bundle of contradictions; little about them predicts the rest"}

FAMILY_FEEL = ["Close", "Dutiful", "Strained", "Scattered", "Estranged", "Broken"]
BONDS = ["close", "fond", "dutiful", "distant", "strained", "estranged"]
BOND_MIX = {"Close": (50, 35, 10, 0, 5, 0), "Dutiful": (10, 25, 50, 0, 15, 0),
            "Strained": (0, 15, 25, 0, 45, 15), "Scattered": (5, 25, 20, 40, 10, 0),
            "Estranged": (0, 10, 0, 5, 30, 55), "Broken": (15, 15, 0, 0, 30, 40)}
BOND_LOYALTY = {"close": 5, "fond": 4, "dutiful": 3, "distant": 2, "strained": 2, "estranged": 1}
FLIP = {"close": "estranged", "fond": "strained", "dutiful": "close", "distant": "close",
        "strained": "close", "estranged": "close"}
FAMILY_ROLES = ("parent", "sibling", "spouse", "child", "kin")
RAISED_BY = ["a grandparent", "an aunt", "an uncle", "strangers who took them in", "a house of charity or an order",
             "the street, mostly", "whoever would have them"]
HANDED_DOWN = ["a saying they repeat without noticing", "their trade", "a grudge against another family",
               "a recipe no one else may cook", "a name to live up to", "an old debt", "an heirloom they won't sell",
               "a silence about something", "a song", "a way of praying or of refusing to", "a temper",
               "a gift for numbers", "a house, or the claim to one", "a family enemy", "their hands: the same scars, the same skill"]
# (text, requirement on the family, effect)
WOUNDS = [("a death no one speaks of", None, None),
          ("a quarrel over an inheritance", None, None),
          ("a sibling who left and never wrote", "sibling", "distant"),
          ("a parent's temper", "parent", None),
          ("a parent's drinking", "parent", None),
          ("a child who turned against them", "child", "estranged"),
          ("a marriage made for money, not love", "spouse", None),
          ("a family shamed in public, long ago", None, None),
          ("a debt that ruined them once", None, None),
          ("a doubt about who their real father is", None, None),
          ("a favourite who wasn't them", "sibling", None),
          ("a home lost", None, None)]
# why a bond went cold: (text, who walked away). "them" = the relative left; "self" = they did; "both"/"none"
COLD_WHY = {
 "parent": [("walked out when they were small and never came back", "them"),
            ("was never there: no money, no visits, only promises", "them"),
            ("drank or gambled everything away", "them"), ("chose a new family over them", "them"),
            ("only turns up when they want something", "them"), ("was cruel to them as a child", "them"),
            ("they cut off for good after one last broken promise", "self"),
            ("disowned them over who they married or what they became", "them"),
            ("a quarrel neither will be first to mend", "both"), ("they simply drifted; no one wrote", "none")],
 "sibling": [("took the inheritance and left nothing", "them"), ("was always the favourite and let them know it", "them"),
             ("they left home and never looked back", "self"), ("a quarrel over a parent's care", "both"),
             ("sided with someone against them", "them"), ("borrowed money and vanished", "them"),
             ("they simply drifted; no one wrote", "none")],
 "spouse": [("left them for someone else", "them"), ("they left, and don't regret it", "self"),
            ("years of small cruelties, on both sides", "both"), ("never home, then not at all", "them"),
            ("the children, and who keeps them", "both"), ("money, always money", "both")],
 "child": [("left and won't say why", "them"), ("blames them for how they were raised", "them"),
           ("married into a family they despise", "both"), ("they threw them out, years ago", "self"),
           ("took up a life they can't forgive", "both"), ("only writes to ask for money", "them"),
           ("they simply drifted; no one wrote", "none")],
}
PLACE_IN_FAMILY = ["the responsible one", "the favourite", "the black sheep", "the peacemaker", "the provider",
                   "the one who left", "the forgotten one", "the heir", "the baby of the family", "the clever one",
                   "the disappointment", "the one everyone confides in"]

# Tastes stand apart from temperament. Each: (thing, category, lean). A lean (axis, sign) means
# the thing naturally suits people far toward that end; liking it from the other end is against
# the grain. Categories: sense, food, people, pastime, thing.
TASTES = [
 ("rain on a roof", "sense", None), ("the smell of smoke", "sense", None), ("bells", "sense", None),
 ("silence", "sense", (E, -1)), ("loud music", "sense", (E, 1)), ("bright colours", "sense", (E, 1)),
 ("the colour yellow", "sense", None), ("the cold", "sense", None), ("hot weather", "sense", None),
 ("wind", "sense", None), ("fog", "sense", None), ("the dark", "sense", None),
 ("early mornings", "sense", (D, 1)), ("late nights", "sense", (D, -1)), ("the sound of chewing", "sense", None),
 ("rough cloth against the skin", "sense", None), ("strong perfume", "sense", None), ("birdsong", "sense", None),
 ("sweet things", "food", None), ("bitter drinks", "food", None), ("fiery spice", "food", (O, 1)),
 ("plain food", "food", (O, -1)), ("fish", "food", None), ("raw onion", "food", None), ("anything fried", "food", None),
 ("fruit", "food", None), ("salty food", "food", None), ("milk", "food", None), ("eggs", "food", None),
 ("food they've never tried", "food", (O, 1)), ("eating the same meal every day", "food", (O, -1)),
 ("loud laughter", "people", (E, 1)), ("being touched", "people", (W, 1)), ("small talk", "people", (W, 1)),
 ("children", "people", (W, 1)), ("the very old", "people", None), ("people who are late", "people", (D, -1)),
 ("people who stand too close", "people", (W, 1)), ("gossip", "people", None), ("being watched while eating", "people", None),
 ("crowds", "people", (E, 1)), ("being alone", "people", (E, -1)), ("strangers", "people", (O, 1)),
 ("people in uniform", "people", (M, 1)), ("being fussed over", "people", (M, -1)), ("being thanked", "people", None),
 ("people who talk with their hands", "people", None), ("tears, theirs or anyone's", "people", (V, 1)),
 ("games of chance", "pastime", (V, 1)), ("cards and board games", "pastime", None), ("mending things", "pastime", (D, 1)),
 ("cleaning", "pastime", (D, 1)), ("walking at night", "pastime", None), ("dancing", "pastime", (E, 1)),
 ("singing", "pastime", (E, 1)), ("old stories", "pastime", None), ("riddles and puzzles", "pastime", (O, 1)),
 ("growing things", "pastime", None), ("cooking for others", "pastime", (W, 1)), ("long journeys", "pastime", (O, 1)),
 ("routine", "pastime", (D, 1)), ("surprises", "pastime", (O, 1)), ("swimming", "pastime", None),
 ("heights", "pastime", (V, -1)), ("animals", "pastime", (W, 1)), ("dogs", "thing", None), ("cats", "thing", None),
 ("birds", "thing", None), ("old things", "thing", (O, -1)), ("new things", "thing", (O, 1)), ("the sea", "thing", None),
 ("boats", "thing", None), ("the smell of old paper", "thing", None), ("mirrors", "thing", None),
 ("ticking clocks", "thing", None), ("fire", "thing", None), ("candlelight", "thing", None), ("gardens", "thing", None),
 ("cellars", "thing", None), ("markets", "thing", (E, 1)), ("holy places", "thing", None), ("graveyards", "thing", None),
 ("small rooms", "thing", None), ("open sky", "thing", None), ("blood", "thing", (V, 1)), ("weapons", "thing", (M, 1)),
 ("fine clothes", "thing", (M, 1)), ("dirt on their hands", "thing", (D, -1)),
]
TASTE_BY = {t[0]: t for t in TASTES}
# loves one, can't stand its neighbour: the contradictions that make people people
TASTE_PAIRS = [("the sea", "boats"), ("children", "the noise children make"), ("dancing", "being watched"),
               ("animals", "the smell of animals"), ("cooking for others", "eating in front of others"),
               ("old stories", "being told how things were"), ("fire", "the smell of smoke"),
               ("singing", "their own voice"), ("markets", "haggling"), ("gardens", "insects"),
               ("holy places", "the people who keep them"), ("being alone", "silence")]
TASTE_STRENGTH = {"like": ["likes", "loves", "delights in"], "dislike": ["dislikes", "can't stand", "loathes"]}
PLEASURE_CATS = ("sense", "food", "pastime", "thing")

PET_COMMON = ["a dog", "a cat", "a caged songbird", "a rabbit", "a hen that follows them about",
              "a goat they will never eat", "an old mule or pony", "a pair of doves", "fish in a bowl", "a tame rat"]
PET_EXOTIC = ["a snake", "a fox raised from a kit", "a tortoise older than they are", "a monkey", "a bird of prey",
              "a lizard", "a spider kept in a jar", "a crow that knows a few words", "a parrot", "a hedgehog",
              "a ferret", "a young boar"]
PET_UNCANNY = ["an animal no one can quite name", "a cat that is sometimes not there", "a bird that never sings by day"]
PET_WAY = ["dotes on it", "treats it as a working animal and nothing more", "talks to it more than to people",
           "pretends not to care for it, and feeds it first", "keeps it for someone who is gone",
           "lets it go where it likes", "is never seen without it"]

# Outlook on the unseen, without naming any world's gods. Eleven views of how things ultimately are.
VIEWS = {
 "eternal": "the self is everlasting: it was before birth and will be after death",
 "partial": "some things last forever (a first power, a maker, the order of things) and the rest of us pass",
 "measure": "turns over whether the world has an edge, has none, has both or neither, and finds it matters",
 "evasive": "won't say yes, won't say no, won't say both or neither; keeps every answer slippery",
 "chance": "everything arose by chance, without cause or purpose",
 "aware": "something of us goes on after death, aware",
 "unaware": "something of us goes on after death, without awareness",
 "between": "something goes on after death that is neither aware nor unaware",
 "nothing": "death is the end; after it there is nothing",
 "here": "whatever good there is must be found in this life, now",
 "unexamined": "has never thought about it; holds what they were taught, or nothing",
}
AFTERLIFE = {
 "none": "nothing; the end is the end", "aware": "goes on as themselves, aware",
 "return": "comes back into another life", "join": "dissolves back into everything",
 "judged": "is weighed by their deeds, then rewarded or punished", "sleep": "rests without dreams or knowing",
 "lingers": "a faint trace lingers near where they lived", "unknown": "no idea, and it troubles them",
 "shrug": "no idea, and it doesn't trouble them", "taught": "whatever they were taught; they haven't looked closely",
}
VIEW_AFTER = {"eternal": ("aware", "return", "join", "judged"), "partial": ("judged", "aware", "sleep", "lingers"),
              "measure": ("return", "join", "unknown", "aware", "none"), "evasive": ("unknown", "shrug"),
              "chance": ("none", "shrug"), "aware": ("aware", "judged", "return", "lingers"),
              "unaware": ("sleep", "lingers"), "between": ("join", "lingers", "unknown"), "nothing": ("none",),
              "here": ("none", "shrug", "unknown", "return"), "unexamined": ("taught", "shrug")}
SPIRIT_FOR = {
 "self": "for themselves: their own safety, reward or escape",
 "others": "for others: so they can do right by people and ease what hurts",
 "kin": "for their own people: family, household, those like them",
 "one": "no line between themselves and anyone else to serve; it simply is",
 "bargain": "a bargain with the unseen: they give, it gives back",
 "unnamed": "lives it without a name for it, and won't take one",
 "nothing": "nothing in particular; it is simply how things are",
}
PRACTICE = {"none": "no practice", "private": "small private habits", "observant": "keeps the observances",
            "devout": "devout; it orders their days", "ascetic": "denies themselves for it",
            "secret": "practises in secret", "outward": "goes through the motions for others to see"}
CERTAINTY = ["doubting", "wavering", "settled", "unshakeable"]
TOWARD = {"private": "keeps it to themselves", "tolerant": "lets others believe what they will",
          "curious": "asks others what they hold, and listens", "persuades": "tries to bring others round",
          "scornful": "has contempt for what others hold"}
GRIEF_SPIRIT = {"none": "takes no comfort in what comes after; there is nothing to take",
                "aware": "talks of seeing them again", "return": "watches newborns for them",
                "join": "says they are everywhere now", "judged": "worries over how they will be weighed, or is sure they're safe",
                "sleep": "is glad they are at rest", "lingers": "listens for them in the house",
                "unknown": "doesn't know where they've gone, and that is the worst of it",
                "shrug": "doesn't ask where they've gone", "taught": "reaches for the words they were taught"}
SPIRIT_ODD = ["says death ends everything, yet leaves food out for the dead",
              "keeps the observances and believes none of it", "prays only when no one could possibly hear",
              "scorns all belief, but will not walk past a holy place without touching it",
              "is certain of what comes after, and terrified of it anyway",
              "believes everything is chance, and carries a charm", "talks to the dead, and denies doing it"]


def _w(rng, items, weights):
    tot = sum(weights)
    if tot <= 0:
        return items[0]
    x = rng.uniform(0, tot)
    for it, w in zip(items, weights):
        x -= w
        if x <= 0:
            return it
    return items[-1]


def idio_of(n, rng=None):
    if n.get("idio") not in IDIO:
        rng = rng or random.Random("idio:%s" % n.get("id"))
        k = _w(rng, IDIO, [15, 45, 30, 10])
        fl = n.get("flags") or {}
        if fl.get("outlier"):
            k = "Riddled"
        elif fl.get("complete") and k != "Riddled":
            k = IDIO[IDIO.index(k) + 1]
        n["idio"] = k
    return n["idio"]


def _gender(rng, f, m):
    return f if rng.random() < 0.5 else m


def family_build(n, rng, add_ties=False):
    dials = n.get("dials") or DEFAULT_DIALS
    risk = max(0, dial(dials, "S") - 1) + max(0, dial(dials, "V") - 1)
    station = n.get("station")
    w = [25, 25, 20, 12, 10, 8]
    if station == "Unmoored":
        w = [8, 10, 20, 27, 22, 13]
    feel = _w(rng, FAMILY_FEEL, w)
    idio = idio_of(n)
    members = []

    def bond():
        return _w(rng, BONDS, BOND_MIX[feel])

    def add(rel, role, label, alive):
        m = {"rel": rel, "role": role, "label": label, "alive": alive, "bond": bond()}
        members.append(m)
        return m

    for par, (f, mo) in (("mother", ("mother", "mother")), ("father", ("father", "father"))):
        r = rng.random() * 100
        dead = 37 + 5 * risk
        if r < 8:
            add(par, "parent", "the %s they never knew" % par, None)["bond"] = "distant"
        elif r < 8 + dead:
            add(par, "parent", "their late " + par, False)
        else:
            add(par, "parent", "their " + par, True)
    nsib = _w(rng, list(range(7)), [18, 24, 22, 15, 10, 6, 5])
    pos = rng.randint(0, nsib)          # how many come before them
    twin = nsib >= 1 and rng.random() < 0.03
    seen = {}
    for i in range(nsib):
        word = _gender(rng, "sister", "brother")
        if twin and i == 0:
            side = "twin"
        else:
            side = "elder" if i < pos else "younger"
        base = "their %s %s" % (side, word) if side != "twin" else "their twin " + word
        seen[base] = seen.get(base, 0) + 1
        label = base if seen[base] == 1 else "%s (%d)" % (base, seen[base])
        alive = rng.random() * 100 >= 8 + 3 * risk
        add(word, "sibling", label if alive else label.replace("their ", "their late ", 1), alive)
    order = "only child" if nsib == 0 else "twin" if twin else "eldest" if pos == 0 else "youngest" if pos == nsib else "middle"
    pw = [38, 34, 10, 9, 9]
    if station == "Sworn":
        pw[0] += 30
    partner = _w(rng, ["none", "spouse", "lover", "widowed", "separated"], pw)
    lover_tie = next((t for t in n.get("ties", []) if t["kind"] == "lover"), None)
    if partner == "none" and lover_tie:
        partner = "lover"
    pword = _w(rng, ["wife", "husband", "partner"], [47, 47, 6])
    if partner == "spouse":
        add(pword, "spouse", "their " + pword, True)
    elif partner == "widowed":
        add(pword, "spouse", "their late " + pword, False)["bond"] = rng.choice(["close", "fond", "fond", "strained"])
    elif partner == "separated":
        add(pword, "spouse", "their former " + pword, True)["bond"] = rng.choice(["strained", "estranged", "distant", "fond"])
    elif partner == "lover":
        m = add("lover", "spouse", (lover_tie or {}).get("label") or "their lover", True)
        if m["bond"] in ("estranged", "distant", "dutiful"):
            m["bond"] = rng.choice(["fond", "strained"])     # a lover gone cold is an ex, not a lover
        if lover_tie:
            m["bond"] = "close" if lover_tie["loyalty"] >= 4 else "fond"
    if partner in ("spouse", "widowed", "separated"):
        nk = _w(rng, list(range(7)), [20, 22, 22, 16, 11, 6, 3])
    else:
        nk = _w(rng, list(range(4)), [70, 18, 8, 4])
    for i in range(nk):
        word = _gender(rng, "daughter", "son")
        place = "" if nk == 1 else "eldest " if i == 0 else "youngest " if i == nk - 1 else \
            ["", "second ", "third ", "fourth ", "fifth "][min(i, 4)]
        alive = rng.random() * 100 >= 6 + 4 * risk
        add(word, "child", ("their %s%s" if alive else "their late %s%s") % (place, word), alive)
    raised = None
    parents = [m for m in members if m["role"] == "parent"]
    if not any(m["alive"] for m in parents) and rng.random() < 0.7:
        pool = RAISED_BY + (["an elder brother or sister"] if any(m["role"] == "sibling" and m["alive"] and "elder" in m["label"]
                                                                   for m in members) else [])
        raised = rng.choice(pool)
    elif rng.random() < 0.06:
        raised = rng.choice(RAISED_BY[:3])
    # the exception: in a family of one feeling, one person who is the other way
    exc = None
    living = [m for m in members if m["alive"]]
    if idio in ("Marked", "Riddled") and living and rng.random() < (0.5 if idio == "Marked" else 0.8):
        exc = rng.choice(living)
        exc["bond"] = FLIP[exc["bond"]]
        if exc["rel"] == "lover" and exc["bond"] == "estranged":
            exc["bond"] = "strained"
        exc["exception"] = True
    wound = None
    if rng.random() < (0.5 if feel in ("Strained", "Estranged", "Broken") else 0.3):
        ok = [wd for wd in WOUNDS if wd[1] is None or any(m["role"] == wd[1] and (m["alive"] or wd[1] == "parent")
                                                           for m in members)]
        wd = rng.choice(ok)
        wound = wd[0]
        if wd[2]:
            tgt = [m for m in members if m["role"] == wd[1] and m["alive"]]
            if tgt:
                m_ = rng.choice(tgt)
                m_["bond"] = wd[2]
                m_["why"], m_["left"] = {"sibling": ("left and never wrote", "them"),
                                         "child": ("turned against them", "them")}[wd[1]]
    for m in members:
        if m["bond"] in ("estranged", "strained", "distant") and m["role"] in COLD_WHY and not m.get("why"):
            pool = COLD_WHY[m["role"]]
            if m["bond"] == "distant":
                pool = [x for x in pool if x[1] in ("none", "self", "them")] or pool
            if m["role"] == "parent" and m["alive"] is None:
                pool = [x for x in pool if x[0].startswith(("walked out", "was never there", "chose a new"))]
            if m["role"] == "spouse" and "former" not in m["label"] and m["alive"]:
                pool = [x for x in pool if not x[0].startswith(("left them", "they left", "never home"))] or pool
            if m["alive"] is False:
                pool = [x for x in pool if x[0] not in ("only turns up when they want something", "only writes to ask for money")]
            m["why"], m["left"] = rng.choice(pool)
    # where they live and their place among their own
    alive_partner = next((m for m in members if m["role"] == "spouse" and m["alive"] and m["rel"] != "lover"
                          and not m["label"].startswith("their former")), None)
    kids_home = [m for m in members if m["role"] == "child" and m["alive"] and m["bond"] != "estranged"
                 and rng.random() < 0.55]
    if station == "Unmoored":
        home = "nowhere fixed"
    elif alive_partner and alive_partner["bond"] != "estranged":
        home = "with their " + alive_partner["rel"] + (" and children" if kids_home else "")
    elif kids_home:
        home = "with their children"
    elif station == "Sworn" and rng.random() < 0.5:
        home = "among those they are sworn with"
    elif any(m["role"] == "parent" and m["alive"] and m["bond"] not in ("estranged", "strained") for m in members) \
            and rng.random() < 0.4:
        home = "with their parents" if sum(1 for m in parents if m["alive"]) == 2 else "with a parent"
    elif station == "Hand" and rng.random() < 0.3:
        home = "in the household they serve"
    elif any(m["role"] == "sibling" and m["alive"] for m in members) and rng.random() < 0.25:
        home = "with a brother or sister"
    else:
        home = "alone"
    places = list(PLACE_IN_FAMILY)
    if order != "youngest":
        places.remove("the baby of the family")
    if nsib == 0:
        places = [p for p in places if p not in ("the favourite", "the forgotten one", "the peacemaker")]
    if home.startswith("with") and "parent" in home:
        places.remove("the one who left")
    hollow = (n.get("authenticity") or {}).get("kind") == "Hollow"
    dearest = None
    for want in (("close",), ("fond",)):
        cands = [m for m in members if m["alive"] and m["bond"] in want]
        if cands:
            prio = {"child": 0, "spouse": 1, "sibling": 2, "parent": 3}
            best = min(prio[m["role"]] for m in cands)
            dearest = rng.choice([m for m in cands if prio[m["role"]] == best])["label"]
            break
    fam = {"feel": feel, "order": order, "members": members, "raised_by": raised,
           "handed_down": rng.choice(HANDED_DOWN), "wound": wound, "place": rng.choice(places),
           "home": home, "dearest": dearest, "performed": hollow}
    n["family"] = fam
    if add_ties:
        family_ties(n, rng)
    return fam


def family_ties(n, rng):
    """New people only: give their generic kin ties a face from the family, and make sure the
    one they hold dearest is a tie, so family turns up in their days."""
    fam = n["family"]
    tied = {(t.get("who") or "").lower() for t in n["ties"]}
    for t in n["ties"]:
        if t["kind"] != "kin" or t.get("role"):
            continue
        free = [m for m in fam["members"] if m["alive"] and m["label"].lower() not in tied and m["role"] != "spouse"]
        if free:
            m = rng.choice(free)
            cold = m["bond"] in ("estranged", "strained", "distant") and m["role"] != "child"
            t["role"], t["label"], t["who"] = ("kin" if cold else m["role"]), m["label"], m["label"]
            t["loyalty"] = clamp(BOND_LOYALTY[m["bond"]] + rng.choice([-1, 0, 0, 1]), 1, 6)
        else:
            lab = rng.choice(["their cousin", "an aunt", "an uncle", "a grandparent", "a niece", "a nephew"])
            t["role"], t["label"], t["who"] = "kin", lab, lab
        tied.add(t["label"].lower())
    dm = next((m for m in fam["members"] if m["label"] == fam["dearest"]), None)
    if dm and dm["label"].lower() not in tied:
        if dm["rel"] == "lover":
            return
        n["ties"].append({"kind": "lover" if dm["role"] == "spouse" else "kin", "role": dm["role"],
                          "label": dm["label"], "who": dm["label"],
                          "loyalty": clamp(BOND_LOYALTY[dm["bond"]] + rng.choice([0, 1]), 1, 6), "reach": rng.randint(1, 6)})


def taste_build(n, rng):
    idio = idio_of(n)
    nl, nd = {"Consistent": (1, 1), "Ordinary": (2, rng.randint(1, 2)), "Marked": (3, rng.randint(2, 3)),
              "Riddled": (4, rng.randint(3, 4))}[idio]
    ax = n["axes"]

    def grain(name, side):
        lean = TASTE_BY[name][2] if name in TASTE_BY else None
        if not lean:
            return "neutral"
        fit = ax[lean[0]] * lean[1] * (1 if side == "like" else -1)
        return "against" if fit <= -2 else "with" if fit >= 2 else "neutral"

    out, used = [], set()

    def take(side, name, against_ok):
        if name in used:
            return False
        g = grain(name, side)
        if g == "against" and not against_ok:
            return False
        bump = 1 if idio == "Riddled" else 0
        lvl = min(2, (0 if rng.random() < 0.55 else 1 if rng.random() < 0.75 else 2) + (bump if rng.random() < 0.4 else 0))
        out.append({"side": side, "thing": name, "level": lvl, "grain": g,
                    "cat": TASTE_BY[name][1] if name in TASTE_BY else "thing"})
        used.add(name)
        return True

    if idio in ("Marked", "Riddled") and rng.random() < (0.4 if idio == "Marked" else 0.8):
        a_, b_ = rng.choice(TASTE_PAIRS)
        take("like", a_, True)
        take("dislike", b_, True)
    names = [t[0] for t in TASTES]
    need_against = {"Consistent": 0, "Ordinary": 0, "Marked": 1, "Riddled": 2}[idio]
    for side, k in (("like", nl), ("dislike", nd)):
        tries = 0
        while sum(1 for x in out if x["side"] == side) < k and tries < 400:
            tries += 1
            nm = rng.choice(names)
            have_against = sum(1 for x in out if x["grain"] == "against")
            if have_against < need_against and grain(nm, side) != "against" and tries < 300:
                continue
            take(side, nm, idio != "Consistent")
    n["tastes"] = out
    return out


def taste_text(t):
    return "%s %s" % (TASTE_STRENGTH[t["side"]][t["level"]], t["thing"])


def pet_chances(n):
    dials = n.get("dials") or DEFAULT_DIALS
    ax = n["axes"]
    rank = RANK.get(n.get("station"), 0)
    have = clamp(7 + 2 * ax[W] - 4 * max(0, dial(dials, "S") - 1) + (2 if rank >= 2 else 0), 0, 14)
    exotic = clamp(2 + 2 * rank + 2 * dial(dials, "X") + ax[O], 0, 10)
    return have, exotic


def pet_build(n, rng, add_tie=False):
    have, exotic = pet_chances(n)
    pet = None
    if rng.random() * 100 < have:
        ex = rng.random() * 100 < exotic
        pool = PET_EXOTIC + (PET_UNCANNY if dial(n.get("dials") or DEFAULT_DIALS, "X") >= 2 else []) if ex else PET_COMMON
        kind = rng.choice(pool)
        hollow = (n.get("authenticity") or {}).get("kind") == "Hollow"
        way = "treats it as a working animal and nothing more" if hollow else rng.choice(PET_WAY)
        loy = clamp(rng.randint(2, 6) + (1 if n["axes"][W] >= 2 else 0) - (2 if hollow else 0), 1, 6)
        label = "their " + kind.split(" ", 1)[1] if kind.startswith(("a ", "an ")) else "their " + kind
        if kind.startswith("a pair of "):
            label = "their " + kind[len("a pair of "):]
        pet = {"kind": kind, "exotic": ex, "label": label, "way": way, "loyalty": loy, "alive": True}
        hates = [t for t in (n.get("tastes") or []) if t["side"] == "dislike" and t["thing"] in ("animals", "dogs", "cats", "birds")]
        if hates:
            pet["despite"] = "keeps it despite not caring for " + hates[0]["thing"]
        if add_tie:
            n["ties"].append({"kind": "pet", "role": "pet", "label": label, "who": label, "loyalty": loy, "reach": 1})
    n["pet"] = pet
    return pet


def spirit_build(n, rng):
    dials = n.get("dials") or DEFAULT_DIALS
    fd = dial(dials, "F")
    ax = n["axes"]
    styles = [v["style"] for v in n.get("voices", [])]
    dom = styles[0] if styles else ""
    hollow = (n.get("authenticity") or {}).get("kind") == "Hollow"
    keys = list(VIEWS)
    w = {k: 8 for k in keys}
    w["unexamined"] = 14
    w["aware"] = 14
    if fd == 0:
        w["nothing"] += 10; w["chance"] += 6; w["unexamined"] += 6; w["here"] += 4
    if fd >= 2:
        w["aware"] += 10; w["eternal"] += 6; w["partial"] += 6; w["nothing"] -= 5; w["chance"] -= 4
    if n.get("creed") == "Nothing" or dom == "Predator":
        w["nothing"] += 14; w["chance"] += 8
    if n.get("creed") == "Faith" or dom == "Zealot":
        w["aware"] += 8; w["eternal"] += 6; w["partial"] += 6
    if n.get("creed") == "Pleasure":
        w["here"] += 10
    if ax[O] >= 2 or dom == "Visionary":
        w["measure"] += 8; w["between"] += 4; w["eternal"] += 3
    if ax[O] <= -2:
        w["unexamined"] += 8; w["measure"] -= 6
    if ax[C] <= -2:
        w["evasive"] += 8
    view = _w(rng, keys, [max(1, w[k]) for k in keys])
    after = rng.choice(VIEW_AFTER[view])
    if after == "unknown" and ax[V] <= -1 and rng.random() < 0.5:
        after = "shrug"
    fw = {"self": 16, "others": 14, "kin": 16, "one": 6, "bargain": 12, "unnamed": 14, "nothing": 10}
    if dom in ("Self-Sacrificing", "Benevolent") or ax[W] >= 2:
        fw["others"] += 14
    if dom in ("Predator", "Self-Made", "Schemer") or ax[W] <= -2:
        fw["self"] += 14; fw["bargain"] += 6
    if view in ("eternal", "between", "measure"):
        fw["one"] += 10
    if view in ("nothing", "chance", "unexamined", "evasive"):
        fw["nothing"] += 12; fw["one"] = 2
    if ax[M] >= 2:
        fw["self"] += 4
    fk = list(fw)
    what_for = _w(rng, fk, [fw[k] for k in fk])
    pk = list(PRACTICE)
    pw = {"none": 20, "private": 22, "observant": 18, "devout": 6, "ascetic": 3, "secret": 4, "outward": 8}
    pw["observant"] += 8 * fd; pw["devout"] += 4 * fd; pw["none"] = max(2, pw["none"] - 6 * fd)
    if dom == "Zealot" or n.get("creed") == "Faith":
        pw["devout"] += 18; pw["ascetic"] += 6
    if ax[D] >= 2:
        pw["observant"] += 8; pw["ascetic"] += 3
    if dial(dials, "D") >= 2 or dial(dials, "O") >= 3:
        pw["secret"] += 6; pw["outward"] += 8
    if view in ("nothing", "chance"):   # last, so nothing above can make them devout in nothing
        pw["none"] += 30; pw["devout"] = 0; pw["ascetic"] = 0; pw["observant"] = 3
    practice = _w(rng, pk, [pw[k] for k in pk])
    cert = clamp(1 + (1 if ax[D] >= 1 else 0) + (1 if dom == "Zealot" else 0) - (1 if ax[O] >= 2 else 0)
                 + rng.choice([-1, 0, 0, 1]) + (1 if fd >= 3 else 0), 0, 3)
    if view == "evasive":
        cert = min(cert, 1)
    if view == "unexamined":
        cert = min(cert, 2)
    tw = {"private": 30, "tolerant": 30, "curious": 12, "persuades": 10, "scornful": 8}
    if ax[O] >= 2: tw["curious"] += 20
    if ax[O] <= -2: tw["scornful"] += 12; tw["curious"] = 2
    if cert == 3: tw["persuades"] += 15; tw["scornful"] += 10
    if ax[W] >= 2: tw["tolerant"] += 10
    if what_for == "one": tw["scornful"] = 1
    tk = list(tw)
    toward = _w(rng, tk, [tw[k] for k in tk])
    if hollow:
        what_for, cert = "nothing", 0
        practice = "outward" if practice != "none" else "none"
    odd = None
    idio = idio_of(n)
    if idio in ("Marked", "Riddled") and rng.random() < (0.35 if idio == "Marked" else 0.7):
        fits = [o for o in SPIRIT_ODD if
                ("death ends" not in o or after == "none") and
                ("believes none" not in o or (practice in ("observant", "devout", "outward") and cert <= 1)) and
                ("scorns all belief" not in o or toward == "scornful") and
                ("certain of what comes after" not in o or (cert >= 2 and after not in ("none", "unknown", "shrug", "taught"))) and
                ("chance" not in o or view == "chance") and
                ("prays only" not in o or practice in ("private", "secret", "none"))]
        if fits:
            odd = rng.choice(fits)
    sp = {"view": view, "after": after, "for": what_for, "practice": practice, "certainty": cert,
          "toward": toward, "odd": odd, "performed": hollow}
    n["spirit"] = sp
    return sp


def spirit_text(sp):
    return "%s. After death: %s. What it is for: %s. Practice: %s. Certainty: %s. Toward others: %s." % (
        VIEWS[sp["view"]][0].upper() + VIEWS[sp["view"]][1:], AFTERLIFE[sp["after"]], SPIRIT_FOR[sp["for"]],
        PRACTICE[sp["practice"]], CERTAINTY[sp["certainty"]], TOWARD[sp["toward"]])


def life_build(n, rng=None, add_ties=False):
    """Family, tastes, pet and outlook. Worked out the same way every time from the person's id
    when not given a generator, so an old ledger gains them without changing anything else."""
    rng = rng or random.Random("life:%s" % n.get("id"))
    idio_of(n, rng)
    family_build(n, rng, add_ties)
    taste_build(n, rng)
    pet_build(n, rng, add_ties)
    spirit_build(n, rng)


def life_of(n):
    if not (isinstance(n.get("family"), dict) and isinstance(n.get("tastes"), list) and "pet" in n
            and isinstance(n.get("spirit"), dict) and n.get("idio") in IDIO):
        life_build(n)
    return n


def taste_match(n, text):
    low = (text or "").strip().lower()
    if not low:
        return None
    for t in n.get("tastes") or []:
        if low in t["thing"].lower() or t["thing"].lower() in low:
            return t
    return None


# how much of a grief a bond carries: a range, rolled each time, because people aren't clocks
BOND_GRIEF = {"close": (0.9, 1.4), "fond": (0.7, 1.15), "dutiful": (0.5, 0.95), "distant": (0.2, 0.7),
              "strained": (0.3, 0.9), "estranged": (0.0, 0.5)}
REGRET_CHANCE = 0.2   # a cold bond that, once it can never be mended, hits harder than anyone expected


def grief_length(n, days, role, member):
    """Days of grief, from the role's usual length, this person's pace and how they felt about the
    one they lost. A loved child is never a short grief; a hated one can be no grief at all."""
    if not days:
        return 0, None
    note = None
    days = days * tempo_of(n)["grief"] * random.lognormvariate(0, 0.25)
    bond = (member or {}).get("bond")
    if bond in BOND_GRIEF:
        lo, hi = BOND_GRIEF[bond]
        if bond in ("strained", "estranged", "distant") and random.random() < REGRET_CHANCE:
            lo, hi = 1.0, 1.6
            note = "the bond was %s, and now it can never be mended: it hits harder than anyone expected" % bond
        elif bond == "estranged" and member.get("left") in ("self", "both") and role == "child":
            lo, hi = 0.0, 0.3       # they cut this child off, or hated them
        days *= random.uniform(lo, hi)
        if role == "child" and bond in ("close", "fond") and not note:
            days = max(days, random.uniform(18, 30))     # never short for a child they loved
        elif role == "child" and bond == "dutiful":
            days = max(days, random.uniform(9, 18))
    days = int(round(days))
    if bond in BOND_GRIEF and days == 0:
        note = "no grief to speak of; if anything, relief, or nothing at all"
    elif not bond:
        days = max(1, days)
    return days, note


def kin_of(n, name):
    """A family member or pet by label: (role, loyalty, record), or None."""
    low = (name or "").strip().lower()
    if not low:
        return None
    for m in (n.get("family") or {}).get("members", []):
        if m["label"].lower() == low:
            if m["bond"] in ("estranged", "strained", "distant") and m["role"] != "child":
                return ("kin", BOND_LOYALTY[m["bond"]], m)
            return (m["role"], BOND_LOYALTY[m["bond"]], m)
    p = n.get("pet")
    if p and p["label"].lower() == low:
        return ("pet", p["loyalty"], p)
    return None


def show_life(n):
    life_of(n)
    fam = n["family"]
    alive = [m for m in fam["members"] if m["alive"]]
    print("Family (%s%s): %s; %s; lives %s%s" % (
        fam["feel"], ", performed" if fam.get("performed") else "", fam["order"], fam["place"], fam["home"],
        "; raised by " + fam["raised_by"] if fam.get("raised_by") else ""))
    print("  " + ", ".join("%s (%s%s%s)" % (m["label"], m["bond"] if m["alive"] is not False else "dead; was " + m["bond"],
                                           ", the exception" if m.get("exception") else "",
                                           ": " + m["why"] if m.get("why") else "") for m in fam["members"]))
    print("  Handed down: %s%s%s" % (fam["handed_down"], " | Wound: " + fam["wound"] if fam.get("wound") else "",
                                    " | Dearest: " + fam["dearest"] if fam.get("dearest") else
                                    (" | no one living they'd call dear" if alive else "")))
    p = n.get("pet")
    if p:
        print("Pet: %s%s, %s%s%s" % (p["kind"], " (exotic)" if p["exotic"] else "", p["way"],
                                     "; " + p["despite"] if p.get("despite") else "", "" if p["alive"] else " (dead)"))
    print("Tastes (%s): %s" % (n["idio"], "; ".join(taste_text(t) + (" (against the grain)" if t["grain"] == "against" else "")
                                                   for t in n["tastes"])))
    sp = n["spirit"]
    print("Outlook%s: %s%s" % (" (performed)" if sp.get("performed") else "", spirit_text(sp),
                               " Odd: " + sp["odd"] + "." if sp.get("odd") else ""))



def life_audit(count=3000, seed=7):
    """Family, tastes, pets and outlook: every rule checked across thousands of people in
    worlds from peaceful and secular to starving, strange and fervent."""
    import copy, tempfile, os, contextlib, io
    problems = []
    state = random.getstate()
    random.seed(seed)
    worlds = [DEFAULT_DIALS, [0, 0, 0, 0, 0, 0, 0], [3, 3, 3, 3, 3, 3, 3], [2, 1, 3, 0, 0, 2, 1], [0, 2, 0, 3, 3, 1, 2]]
    pets = exotic = uncanny = 0
    chances = []
    marked_against = marked_n = 0
    views = collections.Counter()
    for i in range(count):
        dials = list(worlds[i % len(worlds)])
        n = build(dials, "A%d" % i)
        fam, tastes, pet, sp, idio = n["family"], n["tastes"], n["pet"], n["spirit"], n["idio"]
        mem = fam["members"]
        labels = [m["label"] for m in mem]
        P = lambda msg: problems.append(msg)
        if idio not in IDIO: P("unknown idiosyncrasy " + str(idio))
        if n["flags"]["outlier"] and idio != "Riddled": P("an outlier who is not riddled with contradictions")
        # tastes
        nl = {"Consistent": (1, 1), "Ordinary": (2, 2), "Marked": (3, 3), "Riddled": (4, 4)}[idio]
        nd_lo = {"Consistent": 1, "Ordinary": 1, "Marked": 2, "Riddled": 3}[idio]
        likes = [t["thing"] for t in tastes if t["side"] == "like"]
        hates = [t["thing"] for t in tastes if t["side"] == "dislike"]
        if len(likes) != nl[0]: P("%s person with %d likes" % (idio, len(likes)))
        if not nd_lo <= len(hates) <= nd_lo + (0 if idio == "Consistent" else 1): P("%s person with %d dislikes" % (idio, len(hates)))
        if set(likes) & set(hates): P("likes and dislikes the same thing")
        if idio == "Consistent" and any(t["grain"] == "against" for t in tastes): P("a consistent person with a taste against their grain")
        if idio in ("Marked", "Riddled"):
            marked_n += 1
            need = 1 if idio == "Marked" else 2
            marked_against += sum(1 for t in tastes if t["grain"] == "against") >= need
        for t in tastes:
            if not 0 <= t["level"] <= 2 or t["cat"] not in ("sense", "food", "people", "pastime", "thing"):
                P("malformed taste %s" % t)
            if t["thing"] in TASTE_BY:
                lean = TASTE_BY[t["thing"]][2]
                fit = n["axes"][lean[0]] * lean[1] * (1 if t["side"] == "like" else -1) if lean else 0
                if (t["grain"] == "against") != (fit <= -2): P("taste grain miscounted: %s" % t["thing"])
        # pet
        have, ex = pet_chances(n)
        chances.append(have)
        if not (0 <= have <= 14 and 0 <= ex <= 10): P("pet chances out of range: %s %s" % (have, ex))
        pet_ties = [t for t in n["ties"] if t["kind"] == "pet"]
        if pet:
            pets += 1; exotic += pet["exotic"]
            if pet["kind"] in PET_UNCANNY:
                uncanny += 1
                if dial(dials, "X") < 2: P("an uncanny pet in a world where reality is reliable")
            if pet["exotic"] != (pet["kind"] in PET_EXOTIC + PET_UNCANNY): P("exotic flag wrong for " + pet["kind"])
            if len(pet_ties) != 1 or pet_ties[0]["label"] != pet["label"]: P("pet without its tie")
            if relation_to(n, pet["label"])[0] not in ("charge", "familiar"): P("a pet that is not a charge")
            if n["authenticity"]["kind"] == "Hollow" and "working animal" not in pet["way"]: P("a hollow person doting on a pet")
            if pet.get("despite") and not any(t["side"] == "dislike" and t["thing"] in pet["despite"] for t in tastes):
                P("keeps a pet 'despite' a dislike they don't have")
        elif pet_ties:
            P("a pet tie without a pet")
        # family
        if len(set(labels)) != len(labels): P("two family members with one name: %s" % labels)
        sibs = [m for m in mem if m["role"] == "sibling"]
        par = [m for m in mem if m["role"] == "parent"]
        kids = [m for m in mem if m["role"] == "child"]
        spouse = [m for m in mem if m["role"] == "spouse"]
        if len(par) != 2: P("not exactly two parents on record")
        if len(spouse) > 1: P("more than one partner on record")
        o = fam["order"]
        elder = any("elder" in m["label"] for m in sibs); younger = any("younger" in m["label"] for m in sibs)
        if (o == "only child") != (not sibs): P("only child with siblings, or the reverse")
        if o == "eldest" and elder: P("eldest with an elder sibling")
        if o == "youngest" and younger: P("youngest with a younger sibling")
        if o == "middle" and not (elder and younger): P("middle child without both sides")
        for m in mem:
            if m["alive"] is False and "late" not in m["label"]: P("a dead relative not marked late: " + m["label"])
            if m["alive"] and "late" in m["label"]: P("a living relative marked late: " + m["label"])
            if m["bond"] not in BONDS: P("unknown bond " + m["bond"])
            if m["bond"] in ("estranged", "strained", "distant") and m["role"] in COLD_WHY and not m.get("why"):
                P("a cold bond with no cause: " + m["label"])
            if m.get("why") and m["alive"] is not True and m["why"].startswith("only "):
                P("the dead or unknown still turning up: " + m["label"])
            if m.get("why") and m.get("left") not in ("them", "self", "both", "none"): P("cold bond without a direction")
            if m["alive"] is None and m.get("why") and not m["why"].startswith(("walked out", "was never there", "chose a new")):
                P("a parent they never knew, estranged for a reason that needs knowing them")
            if relation_to(n, m["label"])[0] == "stranger": P("a family member reads as a stranger: " + m["label"])
        h = fam["home"]
        alive_sp = [m for m in spouse if m["alive"] and m["rel"] != "lover" and "former" not in m["label"]]
        if h.startswith("with their ") and h.split(" ")[2] in ("wife", "husband", "partner"):
            if not alive_sp or alive_sp[0]["bond"] == "estranged": P("lives with a partner who isn't there: " + h)
        if "children" in h and not any(m["alive"] and m["bond"] != "estranged" for m in kids): P("lives with children who aren't there")
        if h == "with their parents" and sum(1 for m in par if m["alive"]) != 2: P("lives with both parents, not both alive")
        if h == "with a parent" and not any(m["alive"] for m in par): P("lives with a parent, none alive")
        if h == "with a brother or sister" and not any(m["alive"] for m in sibs): P("lives with a sibling, none alive")
        if h == "nowhere fixed" and n["station"] != "Unmoored": P("homeless without being unmoored")
        if any(m["rel"] == "lover" and m["bond"] in ("estranged", "distant") for m in mem): P("an estranged lover")
        if fam["place"] == "the baby of the family" and o != "youngest": P("the baby of the family who isn't the youngest")
        if fam["place"] == "the one who left" and "parent" in h: P("the one who left, still living with parents")
        if fam["place"] in ("the favourite", "the forgotten one", "the peacemaker") and not sibs: P("%s, as an only child" % fam["place"])
        if fam.get("raised_by") == "an elder brother or sister" and not elder: P("raised by an elder sibling they don't have")
        if fam.get("wound"):
            req = next(w for w in WOUNDS if w[0] == fam["wound"])[1]
            if req and not any(m["role"] == req for m in mem): P("a family wound needing a %s they don't have" % req)
        if fam.get("dearest"):
            dm = [m for m in mem if m["label"] == fam["dearest"]]
            if not dm or not dm[0]["alive"] or dm[0]["bond"] not in ("close", "fond"): P("dearest is not a living, loved relative")
            elif dm[0]["rel"] != "lover" and not any((t.get("who") or "") == fam["dearest"] for t in n["ties"]):
                P("the dearest relative is not among their ties")
        lover_t = [t for t in n["ties"] if t["kind"] == "lover" and not t.get("role")]
        if lover_t and not spouse: P("a lover tie but no partner on record")
        for t in n["ties"]:
            if t.get("role") in FAMILY_ROLES and t["role"] != "kin" and t["who"] not in labels:
                P("a family tie to someone not in the family: " + t["label"])
            if t.get("role") in ("parent", "sibling", "spouse") and t["who"] in labels:
                m = next(m for m in mem if m["label"] == t["who"])
                if m["bond"] in ("estranged", "strained", "distant"): P("an estranged relative tied as beloved")
            if "{tie}" in t["label"]: P("unfilled tie label")
        # outlook
        views[sp["view"]] += 1
        if sp["after"] not in VIEW_AFTER[sp["view"]] and not (sp["view"] in ("measure", "partial", "eternal", "aware", "here") and sp["after"] == "shrug"):
            if not (sp["after"] == "shrug" and "unknown" in VIEW_AFTER[sp["view"]]):
                P("afterlife %s doesn't follow from view %s" % (sp["after"], sp["view"]))
        if sp["view"] == "evasive" and sp["certainty"] > 1: P("certain about refusing to be certain")
        if sp["view"] in ("nothing", "chance") and sp["practice"] in ("devout", "ascetic"): P("devout in a belief in nothing")
        if n["authenticity"]["kind"] == "Hollow" and (sp["for"] != "nothing" or sp["certainty"] != 0 or sp["practice"] not in ("outward", "none")):
            P("a hollow person who truly believes")
        if sp["for"] == "one" and sp["toward"] == "scornful": pass  # rare, allowed: weight 1
        if sp.get("odd"):
            o_ = sp["odd"]
            if "death ends" in o_ and sp["after"] != "none": P("odd outlook contradicts its own premise: " + o_)
            if "believes none" in o_ and (sp["practice"] not in ("observant", "devout", "outward") or sp["certainty"] > 1):
                P("odd: keeps observances they don't keep, or believes after all")
            if "scorns all belief" in o_ and sp["toward"] != "scornful": P("odd: scorns belief without scorning")
            if "chance" in o_ and sp["view"] != "chance": P("odd: chance believer who isn't one")
            if idio not in ("Marked", "Riddled"): P("an oddity of outlook in someone of a piece")
        for k in ("view", "after", "for", "practice", "toward"):
            if sp[k] not in {"view": VIEWS, "after": AFTERLIFE, "for": SPIRIT_FOR, "practice": PRACTICE, "toward": TOWARD}[k]:
                P("unknown outlook %s: %s" % (k, sp[k]))
        if sp["after"] not in GRIEF_SPIRIT: P("no grief line for afterlife " + sp["after"])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                show_life(n)
        except Exception as e:
            P("show_life crash: %s" % e)
        # an old ledger gains the same life every time, and no new ties
        if i % 50 == 0:
            old = copy.deepcopy(n)
            for k in ("family", "tastes", "pet", "spirit", "idio"):
                old.pop(k, None)
            old["ties"] = [t for t in old["ties"] if t["kind"] != "pet"]
            t0 = len(old["ties"])
            a1, a2 = migrate(copy.deepcopy(old)), migrate(copy.deepcopy(old))
            if json.dumps([a1["family"], a1["tastes"], a1["pet"], a1["spirit"]], sort_keys=True) != \
               json.dumps([a2["family"], a2["tastes"], a2["pet"], a2["spirit"]], sort_keys=True):
                P("migration does not give the same life twice")
            if len(a1["ties"]) != t0: P("migration added ties to an old ledger")
    # whole-population checks
    rate = 100.0 * pets / count
    if not (0 < rate <= 14): P("pet ownership %.1f%%, outside 0-14%%" % rate)
    ex_rate = 100.0 * exotic / max(1, pets)
    if ex_rate > 10: P("exotic pets %.1f%% of pets, above 10%%" % ex_rate)
    if marked_n and marked_against / marked_n < 0.85: P("marked people rarely have tastes against their grain (%.0f%%)" % (100.0 * marked_against / marked_n))
    if len(views) < len(VIEWS): P("some views never arise: %s" % sorted(set(VIEWS) - set(views)))
    # tables
    for v, afs in VIEW_AFTER.items():
        if v not in VIEWS or not afs or any(x not in AFTERLIFE for x in afs): P("view table broken at " + v)
    for a_, b_ in TASTE_PAIRS:
        if a_ == b_: P("a taste paired with itself")
    if len({t[0] for t in TASTES}) != len(TASTES): P("a taste listed twice")
    for q in QUIRKS:
        if any(q == t[0] for t in TASTES): P("a taste duplicates a quirk: " + q)
    # grief follows the bond, within a range
    gp = build(list(DEFAULT_DIALS), "G")
    for pace in (0.4, 1.0, 2.5):
        gp["tempo"]["grief"] = pace
        for bond in BONDS:
            for left in ("them", "self", "both", "none"):
                r = [grief_length(gp, 21 + d(14), "child", {"bond": bond, "left": left})[0] for _ in range(300)]
                if bond in ("close", "fond") and min(r) < 18: P("a loved child grieved for under 18 days (%s)" % bond)
                if bond != "estranged" and 0 in r: P("no grief at all for a child who was %s" % bond)
                if len(set(r)) < 5: P("grief for a %s child barely varies" % bond)
    # a death in the family, end to end
    work = tempfile.mkdtemp()
    for i in range(40):
        n = build(list(DEFAULT_DIALS), "L%d" % i)
        tgt = [m for m in n["family"]["members"] if m["alive"]] + ([n["pet"]] if n["pet"] else [])
        if not tgt:
            continue
        m = random.choice(tgt)
        p_ = os.path.join(work, "l%d.json" % i)
        save(n, p_)
        sys.argv = ["forge.py", "event", p_, "loss", "--about", m["label"]]
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                main()
        except SystemExit as e:
            P("loss event exits: %s" % e); continue
        except Exception as e:
            P("loss event crash: %s" % e); continue
        n2 = load(p_)
        m2 = kin_of(n2, m["label"].replace("their ", "their late ", 1)) or kin_of(n2, m["label"])
        if not m2 or m2[2]["alive"]: P("a relative still alive after their loss")
        if n2["family"].get("dearest") == m["label"]: P("the dead are still the dearest")
        if "in their outlook" not in out.getvalue() and "performs the grief" not in out.getvalue() and \
                "no grief to speak of" not in out.getvalue() and \
                relation_to(n, m["label"])[0] != "stranger":
            P("grief without the outlook's colour")
    random.setstate(state)
    return problems, {"people": count, "pet_rate": rate, "exotic_rate": ex_rate, "uncanny": uncanny,
                      "pet_chance_mean": sum(chances) / len(chances), "views": dict(views)}


def migrate(n):
    """Bring a person's ledger up to the current schema. Never changes who they are: an id
    once given is kept for life; missing layers are worked out the same way every time."""
    if not isinstance(n, dict) or "axes" not in n:
        return n
    if not n.get("id"):
        n["id"] = "p" + hashlib.sha256(("%s|%s|%s" % (n.get("name"), n.get("axes"), n.get("voices"))).encode()).hexdigest()[:12]
    speech_of(n)
    strain_of(n)
    tempo_of(n)
    life_of(n)
    n["schema"] = SCHEMA
    return n



# ---------- knowledge: what people believe, where it came from, and how sure they are ----------
# Four domains stay apart: what happened (the campaign's facts, kept outside any person), what
# each person believes (here), what the narrator is told (briefs), what the player has found out.
# A belief never carries whether it is true. People can be confidently wrong.
SOURCE_BASE = {"witnessed": 0.85, "read": 0.6, "heard": 0.5, "inferred": 0.45, "imagined": 0.3}
DISTORT = {"who": "has the wrong person in it", "when": "has the timing wrong", "count": "has the numbers wrong",
           "where": "has it happening in the wrong place", "bigger": "has grown in the telling",
           "smaller": "has shrunk in the telling", "motive": "adds a reason nobody gave",
           "order": "has things in the wrong order"}
MEANINGS = {
    "proof": ("proof of what they already thought", {O: -1, D: 0.5}, ()),
    "warning": ("a warning to them", {V: 0.5, W: -0.5}, ("Vigilant",)),
    "not_mine": ("none of their business", {W: -1, E: -0.5}, ("Solitary",)),
    "a_lie": ("a lie somebody is spreading", {C: -0.5, O: 0.5}, ("Vigilant", "Schemer")),
    "chance": ("an opportunity", {M: 0.5, W: -0.5}, ("Schemer", "Self-Made", "Predator")),
    "sign": ("a sign of something larger", {O: 1}, ("Visionary", "Zealot")),
    "scandal": ("a scandal worth repeating", {E: 1, C: -0.5}, ("Dramatic", "Mercurial")),
    "wrong": ("a wrong that should be put right", {C: 1, M: 0.5}, ("Zealot", "Commanding")),
    "shame": ("a shame on someone's people", {W: 0.5, D: 0.5}, ("Devoted", "Serious")),
    "joke": ("a joke, mostly", {E: 1, V: -0.5}, ("Leisurely", "Adventurous")),
    "worry": ("something to worry about", {V: 1, M: -0.5}, ("Sensitive", "Self-Sacrificing")),
}
CREED_MEANING = {"Justice": "wrong", "Kin": "shame", "Faith": "sign", "Gain": "chance", "Security": "warning",
                 "Order": "wrong", "Pleasure": "scandal", "Thrill": "joke", "Freedom": "a_lie"}
GOSSIP_TALK = ("Salon", "Yarn-Spinner", "Braggart", "Muddler")


def sure_word(c):
    return "certain" if c >= 0.85 else "sure" if c >= 0.65 else "fairly sure" if c >= 0.45 else \
        "unsure" if c >= 0.25 else "half-believes it"


def _meaning(n, rng, source=None):
    keys = sorted(MEANINGS)
    if source in ("witnessed", "inferred", "imagined"):
        keys = [k for k in keys if k != "a_lie"]   # nobody takes their own eyes or reasoning for someone else's lie
    w = []
    for k in keys:
        _, axw, styles = MEANINGS[k]
        sc = 1 + 0.5 * sum(x * n["axes"][i] for i, x in axw.items()) + sum(1.5 * v["frac"] for v in n["voices"] if v["style"] in styles)
        if CREED_MEANING.get(n.get("creed")) == k:
            sc += 1.5
        w.append(max(0.05, sc) * rng.lognormvariate(0, 0.5))
    return keys[w.index(max(w))]


def credulity(n):
    a = n["axes"]
    c = 0.05 * a[W] - 0.05 * a[D] + (0.1 if speech_of(n)["main"] == "Earnest" else 0)
    c -= 0.1 if any(v["style"] in ("Vigilant", "Schemer") for v in n["voices"] if v["frac"] >= 0.4) else 0
    c -= 0.1 if strain_of(n).get("praise") == "suspects" else 0
    return c


def learn_belief(n, subject, claim, source, frm=None, reliability=None, fact=None, secret=False, stressed=False,
                 distortions=None, hops=0, rng=None):
    """Add what someone has come to believe. Returns the belief as they hold it."""
    rng = rng or random
    subject, claim = (subject or "").strip(), (claim or "").strip()
    if not subject or not claim:
        sys.exit("A belief needs something it's about and something it claims.")
    if source not in SOURCE_BASE:
        sys.exit("A belief comes from one of: " + ", ".join(SOURCE_BASE))
    if reliability is None:
        reliability = 1.0 if source == "witnessed" else (total_trust(n, frm) + 5) / 10.0 if frm else 0.5
    reliability = clamp(reliability, 0.0, 1.0)
    conf = SOURCE_BASE[source] * (0.5 + 0.5 * reliability) + (credulity(n) if source != "witnessed" else 0)
    dist = list(distortions or [])
    slip = (0.35 if stressed else 0.10) if source == "witnessed" else 0.0
    if source == "imagined":
        slip = 0.3
    if rng.random() < slip:
        dist.append(rng.choice([k for k in DISTORT if k not in dist] or list(DISTORT)))
    kb = n.setdefault("knows", [])
    same = [b for b in kb if b["subject"].lower() == subject.lower() and b["claim"] == claim]
    if same:  # heard again: more sure, true or not
        b = same[0]
        b["confidence"] = round(clamp(1 - (1 - b["confidence"]) * (1 - 0.7 * conf), 0, 0.98), 3)
        b["reinforced"] = b.get("reinforced", 0) + 1
        b["last"] = n["day"]
        if frm and frm not in b["also_from"]:
            b["also_from"].append(frm)
        return b
    b = {"k": "b%08x" % rng.getrandbits(32), "subject": subject, "claim": claim, "source": source, "from": frm,
         "also_from": [], "day": n["day"], "last": n["day"], "confidence": round(clamp(conf, 0.05, 0.98), 3),
         "reliability": round(reliability, 2), "meaning": _meaning(n, rng, source), "distortions": dist, "hops": hops,
         "fact": fact, "secret": bool(secret), "reinforced": 0}
    kb.append(b)
    n["knows"] = kb[-200:]
    return b


def tell_belief(teller, hearer, subject, rng=None):
    """Teller passes on what they believe about a subject, as they would tell it. Rumours drift."""
    rng = rng or random
    held = sorted([b for b in teller.get("knows", []) if b["subject"].lower() == subject.lower()],
                  key=lambda b: -b["confidence"])
    if not held:
        return None, "%s knows nothing about that to pass on." % teller["name"]
    b = held[0]
    if b["secret"] and total_trust(teller, hearer["name"]) < 3:
        return None, "%s keeps it to themself." % teller["name"]
    dist = list(b["distortions"])
    p_ = 0.25
    bend = speech_of(teller)["bend"]
    if bend in ("Spinner", "Worker", "Palterer"): p_ += 0.15
    if speech_of(teller)["main"] in GOSSIP_TALK: p_ += 0.10
    if rng.random() < p_:
        pool = ["bigger", "motive"] if bend in ("Spinner", "Worker") else list(DISTORT)
        new = [k for k in pool if k not in dist]
        if new:
            dist.append(rng.choice(new))
    got = learn_belief(hearer, b["subject"], b["claim"], "heard", frm=teller["name"], fact=b.get("fact"),
                       secret=False, distortions=dist, hops=b["hops"] + 1, rng=rng)
    return got, None


def belief_day(n, rng=None):
    """Second-hand certainty fades unless repeated; memory quietly rewrites the odd detail."""
    rng = rng or random
    tp = tempo_of(n)
    for b in n.get("knows", []):
        if b["source"] != "witnessed" and n["day"] - b.get("last", b["day"]) > 7:
            b["confidence"] = round(max(0.05, b["confidence"] - 0.004 * tp["fade"]), 3)
        if rng.random() < 0.002 * tp["recall"] and len(b["distortions"]) < 3:
            b["distortions"].append(rng.choice([k for k in DISTORT if k not in b["distortions"]]))


def beliefs_about(n, subject):
    return sorted([b for b in n.get("knows", []) if b["subject"].lower() == (subject or "").lower()],
                  key=lambda b: -b["confidence"])


def belief_plain(b, subject=True):
    """What the narrator may be told about one belief: what they believe and how they'd tell it."""
    src = {"witnessed": "saw it themself", "read": "read it", "heard": "heard it" + (" from " + b["from"] if b["from"] else ""),
           "inferred": "worked it out", "imagined": "suspects it, with nothing to go on"}[b["source"]]
    hops = " (it came a long way round)" if b["hops"] >= 3 else ""
    told = ("; as they tell it, it " + " and ".join(DISTORT[x] for x in b["distortions"])) if b["distortions"] else ""
    return "%s%s. They %s%s; %s; to them it's %s%s%s." % (
        (b["subject"] + ": ") if subject else "", b["claim"], src, hops, sure_word(b["confidence"]), MEANINGS[b["meaning"]][0], told,
        "; they keep it to themself" if b["secret"] else "")


SHOUT_FORMS = {"Violent Outburst", "Righteous Wrath", "Fear-Aggression", "Wounded-Panic", "Territorial"}
BRIGHT_FORMS = {"Boastful", "Performing", "Teasing-Fond", "Mockery", "Flirtatious", "Gossipy", "Hospitable",
                "Generous", "Mercurial", "Bargaining-Humour"}
MEASURED_FORMS = {"Ritual", "Preaching", "Dutiful", "Obstruction", "Candid", "Mentoring", "Appraising",
                  "Respectful", "Reverent", "Transactional", "Reproach"}


def punctuation(n, active, form):
    """Latitude in how their words land on the page: exclamations, the odd semicolon, a word in
    CAPITALS when they shout. Worked out from who they are and the moment; a latitude, never a tic.
    Returns a list of plain notes (empty when nothing beyond ordinary punctuation fits)."""
    act = set(active)
    if act & {"frozen", "stunned"}:
        return []
    ax = n["axes"]
    notes = []
    loud = (form in SHOUT_FORMS or ("enraged" in act and ax[D] < 2)
            or ("afraid" in act and ax[V] >= 2) or ("hurt" in act and ax[V] >= 2 and ax[D] < 1))
    if loud and "clear" not in act:
        notes.append("exclamations, and now and then a word in CAPITALS when they raise their voice")
    elif (form in BRIGHT_FORMS or act & {"festive", "intoxicated"} or (ax[E] >= 2 and ax[V] >= 1)
          or ("afraid" in act and ax[D] < 2)):
        notes.append("an exclamation comes easily to them, here and there")
    measured = (form in MEASURED_FORMS or act & {"solemn", "duty", "superior"}
                or (ax[D] >= 2 and processing(n) in ("Intellectual", "Contained")))
    if measured and not act & {"intoxicated", "exhausted", "enraged"} and not loud:
        notes.append("full, joined-up sentences; a semicolon would not be out of place")
    return notes


def cmd_meet(a):
    n = load(a.file)
    if n["condition"] in ("dead", "comatose"):
        sys.exit("%s is %s." % (n["name"], n["condition"]))
    if (a.who or "").strip().lower() == n["name"].lower():
        sys.exit("%s can't meet themself." % n["name"])
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
        members = load(a.circle).get("members", []) if a.circle else []
        vcls = relation_to(n, a.victim, members)[0]
        acls = relation_to(n, a.attacker, members)[0]
        if a.attacker and a.attacker.lower() == n["name"].lower() and not a.hurt:
            resp = attacker_response(n, vcls)
        else:
            resp = violence_response(n, a.hurt, vcls, acls, a.symbol)
        steady = violence_steady(n, resp, n["dials"], vcls)
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
    life_of(n)
    sp_ = n["spirit"]
    outlook = 0
    if a.spirit and not sp_.get("performed"):
        if a.spirit == "shared":
            outlook = 1 if (sp_["certainty"] >= 2 or sp_["toward"] == "persuades") and sp_["for"] != "nothing" else 0
        else:
            outlook = 0 if (sp_["for"] == "nothing" or sp_["view"] == "evasive") else \
                -2 if (sp_["certainty"] == 3 or sp_["practice"] in ("devout", "ascetic")) else -1
            if sp_["toward"] == "curious" and outlook < 0:
                outlook += 1
    taste, tmatch = 0, None
    if a.taste:
        tmatch = taste_match(n, a.taste)
        if tmatch:
            taste = (1 if tmatch["side"] == "like" else -1) * (2 if tmatch["level"] == 2 else 1)
    about_you = trust + ap + creed + social + cont + dang + outlook
    feel = clamp(int(round((n.get("affect") or {}).get("feeling", 0) / 2)), -3, 3)
    about_them = td["mood"] + chronic(n) + feel + taste
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
    if not face_on and abs(about_you) <= 1 and abs(about_them) <= 1 and random.random() < 0.2:
        # nothing strong is pushing them: now and then the rest of their own repertoire shows
        raw = tetrad(SBY[vstyle][{"Kind": "kind", "Middle": "mid", "Hostile": "host"}[key]])
    habit_note = None
    hf = habit_form(n, key, active)
    # a habit fills the gaps now and then, more as it deepens; it never takes over every meeting
    if hf and random.random() >= ((n.get("inclinations") or {}).get(hf, {}).get("strength", 0) - 0.3):
        hf = None
    if hf and hf != raw and abs(about_you) <= 2 and abs(about_them) <= 2:
        raw, habit_note = hf, "out of habit"
    form, soft, ok, yielded = resolve(raw, key, active, n)
    infl, sp, dropped_col = colour_for(n, active, td["side"])
    rs = td.get("shaken")
    if rs in RESP and RESP[rs][0] in active:
        higher = active[:active.index(RESP[rs][0])]
        if not _blocked_by(RESP[rs][2], higher, n) and RESP[rs][1] not in infl:
            infl.insert(0, RESP[rs][1])
    side_note = infl.pop() if (infl and SIDE_TEXT.get(n["contradiction"]["pair"]) and
                               infl[-1] in [v for x in SIDE_TEXT[n["contradiction"]["pair"]]
                                            for v in SIDE_VARIANTS.get(x[0], [x[0]])]) else None
    infl += soft + exempt_notes
    if habit_note and form == raw:
        infl.append(habit_note)
    pull = max(((k, r["strength"]) for k, r in (n.get("inclinations") or {}).items()
                if k in FORM_TAGS and 0.3 <= r["strength"] < 0.5 and k != form), key=lambda kv: kv[1], default=None)
    if pull and all(_passes(pull[0], c, n) for c in active):
        infl.append("a pull toward " + pull[0])
    others = sorted([v for v in n["voices"] if v["style"] != vstyle], key=lambda v: -v["frac"])
    if others and others[0]["frac"] >= 0.25:
        tf = resolve(others[0]["manner"][key][0], key, active, n)[0]
        if tf != form:
            infl.append("with a trace of " + tf)
    if side_note:
        infl.append(side_note)
    fw = feeling_words((n.get("affect") or {}).get("feeling", 0))
    if fw and "clear" not in active and not ({"hurt", "frozen"} & set(active)):
        infl.append(fw)
    # the same state can last for weeks; the same words for it shouldn't come every time
    prev, fresh, bases = set(n.get("last_colour") or []), [], []
    for line in infl:
        base = line
        line = random.choice(CHRONIC_VARIANTS[line]) if line in CHRONIC_VARIANTS else line
        if base in prev and len(infl) > 1 and random.random() < 0.5:
            continue
        fresh.append(line); bases.append(base)
    infl = fresh
    n["last_colour"] = bases
    tint = {"Cool": "colder ", "Warm": "warmer "}.get(band, "")
    print("[narrator only] %s toward %s" % (n["name"], a.who))
    print("Mood %+d = baseline %+d, their day %+d (%s), chronic %+d, feeling %+d, trust %+d, approach %+d, "
          "creed %+d, social %+d, contagion %+d, danger %+d%s" % (mood, dv["baseline"], td["mood"], td["cause"],
                                                                 chronic(n), feel, trust, ap, creed, social, cont,
                                                                 dang, capped)
          + ("" if not (a.taste or a.spirit) else " | taste %+d%s, outlook %+d" % (
              taste, "" if tmatch or not a.taste else " (not one of their tastes)", outlook)))
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
    if td.get("thought"):
        th = td["thought"] if isinstance(td["thought"], list) else [td["thought"], None, False, 0.5]
        th = list(th) + [False, 0.5][len(th) - 2:] if len(th) < 4 else th
        lvl, hold = thought_hold(n, th, active)
        rip = thought_ripple(n, active)
        if rip != "nothing shows" and lvl >= 2:
            rip += {2: "; a small frown at their own mind", 3: "; then it's set down"}[lvl]
        print("Unbidden thought: %s. How they hold it now: %s. It shows as: %s. Never name it in narration; "
              "show only that, or the words they let slip.%s" % (
                  th[0], hold, rip, (" If they wonder where it came from, their own guess: %s."
                                     % (th[1] or "nothing they can name")) if lvl >= 1 else ""))
    if form in FORM_TAGS and not form.startswith("Wounded") and not a.dry_run:
        axes_ = [ax for tg in FORM_TAGS[form] for ax in TAG_AXES.get(tg, [])]
        for note in incline(n, form, axes_, gain=0.5):
            print("Inclination: " + note)
        save(n, a.file)
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
    if tmatch:
        print("Taste touched: %s. Show it in the body or a word, never explained." % taste_text(tmatch))
    if set(active) & {"grieving", "solemn"} or a.spirit:
        print("Outlook (narrator only): %s%s" % (spirit_text(sp_), " Odd: " + sp_["odd"] + "." if sp_.get("odd") else ""))
    if td.get("trailing") and not any(x in ("trailing", "clipped", "short", "short and hard", "rambling",
                                            "broken by breath", "flat; repeats things") for x in sp):
        sp.append("trails off now and then")
    if sp:
        print("Speech: " + ", ".join(sp))
    punct = punctuation(n, active, form)
    if punct:
        print("Punctuation: " + "; ".join(punct))
    talk = speech_now(n, active, band, scheming=bool(plan) or face_on)
    print("Way of talking: %s (%s, %s)." % (talk["keys"], talk["register"], talk["length"]))
    print("  Habits of speech: " + "; ".join(talk["habits"]) + ".")
    if talk["tone"]:
        print("  Toward %s now: %s." % ("you" if a.who == "player" else a.who, talk["tone"]))
    if talk["slang"]:
        print("  Their slang: " + "; ".join(talk["slang"]) + ". Invent the words to suit the world.")
    for h in talk["here"]:
        print("  Here: " + h + ".")
    print("  How they bend words: %s. Never a tell by itself." % talk["bend"])
    strained = bool(a.approach == "pressure" or a.opposed or a.hurt or set(a.danger or []) & {"violence", "authority"})
    under = STRAIN_WAYS[strain_of(n)["cornered"]] if strained else None
    if under:
        print("Under strain, as always: " + under + ".")
    beats = ordinary_beats(n, active)
    if beats["business"]:
        print("Ordinary business (means nothing): " + beats["business"] + ".")
    if beats["mishear"]:
        print("An honest misunderstanding this scene: " + beats["mishear"] + ". It can be cleared up; it means nothing more.")
    carried = []
    for m in reversed(n["memory"]):
        if m.get("with") == a.who and (m.get("took") in HOLDS_IT or m.get("weight", 0) >= 2):
            carried.append({"event": m["event"], "took": m.get("took")})
        if len(carried) == 2:
            break
    believes = [belief_plain(b, subject=False) for b in beliefs_about(n, a.who if a.who != "player" else "you")[:2]]
    for bp in believes:
        print("Believes, about " + ("you" if a.who == "player" else a.who) + ": " + bp)
    for c_ in carried:
        print("Carries from before: the %s%s." % (c_["event"], ("; how they took it: " + STRAIN_WAYS[c_["took"]]) if c_.get("took") else ""))
    L = locals()
    VIEW.clear()
    VIEW.update({
        "cmd": "meet", "name": n["name"], "who": a.who, "band": band, "intensity": intensity(mood, band, n).strip(),
        "form": form, "amended": form != raw, "active": list(active), "colour": list(infl), "yielded": list(yielded),
        "voice_forward": vstyle if vstyle != td["voice"] else None,
        "thought": ({"text": L["th"][0], "hold": L["hold"], "level": L["lvl"], "ripple": L["rip"],
                     "guess": L["th"][1] if L["lvl"] >= 1 else None} if td.get("thought") else None),
        "face": au["kind"] if face_on else None, "core": L.get("core") if face_on else None,
        "face_dropped": (not face_on) and au["kind"] != "Genuine",
        "violence_steady": bool(a.violence and td.get("shaken") is None),
        "shaken": td.get("shaken"), "danger_beat": lean, "danger_replaces": bool(lean and L.get("fits")),
        "stratagem": plan, "quirks": qs, "speech": sp, "punctuation": punct, "talk": talk, "under_strain": under, "business": beats["business"], "mishear": beats["mishear"], "carried": carried, "believes": believes, "today": td.get("cause"),
        "taste": taste, "taste_touched": taste_text(tmatch) if tmatch else None, "outlook": outlook,
    })


def cmd_audit(a):
    """Preemptive amendment review: every form x every combination of up to three circumstances x
    every band x a spread of personalities must settle on a form that fits. Run after adding any
    form, circumstance, quirk or style."""
    life_p, life_s = life_audit(800 if not getattr(a, "life", False) else 3000)
    print("Life: %(people)d people built; %(pet_rate).1f%% keep a pet (mean chance %(pet_chance_mean).1f%%), "
          "%(exotic_rate).1f%% of those exotic, %(uncanny)d uncanny." % life_s)
    if getattr(a, "life", False):
        for u in dict.fromkeys(life_p):
            print("  PROBLEM: " + u)
        print("No unhandled cases in family, tastes, pets or outlook." if not life_p else "")
        sys.exit(1 if life_p else 0)
    problems = list(life_p)
    forms = set(FORM_TAGS)
    for s in STYLES:
        for f in s["kind"] + s["mid"] + s["host"]:
            if f not in FORM_TAGS: problems.append("form without tags: %s (%s)" % (f, s["name"]))
    for f in FACES:
        if f not in SBY: problems.append("face is not a style: " + f)
    for q in QUIRKS:
        if q not in QUIRK_KIND: problems.append("quirk without a kind: " + q)
    for r, (cond, desc, tg) in RESP.items():
        if r.startswith("Wounded") and r not in FORM_TAGS: problems.append("wounded response without tags: " + r)
        if cond is not None and cond not in CONDS: problems.append("response %s points at unknown circumstance %s" % (r, cond))
        if not tg <= TAGS_ALL: problems.append("response %s has unknown colour tags" % r)
    for k, (txt, tg) in PROCESSING.items():
        if not tg <= TAGS_ALL: problems.append("processing %s has unknown colour tags" % k)
    for role in ROLES:
        if role not in GRIEF_DAYS and role not in ("enemy",): problems.append("role without grief length: " + role)
    profiles = []
    for axes in ([0] * 7, [3] * 7, [-3] * 7, [-3, 3, 3, -3, -3, 3, 3], [3, -3, -3, 3, 3, -3, -3],
                 [0, 2, 0, 2, 2, 2, -1], [-2, -2, 2, -1, 3, 1, 3]):
        for extra in ({}, {"quirks": ["laughs at the wrong moments"]}, {"hollow": True}, {"predator": True},
                      {"dramatic": True}):
            n = {"axes": axes, "quirks": extra.get("quirks", []),
                 "voices": [{"style": "Predator" if extra.get("predator") else
                             "Dramatic" if extra.get("dramatic") else "Serious", "frac": 1}],
                 "authenticity": {"kind": "Hollow" if extra.get("hollow") else "Genuine", "faces": []},
                 "creed": "Faith" if extra.get("dramatic") else "Order", "station": "Hand", "name": "x"}
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
    classes = ("stranger", "familiar", "beloved", "charge", "revered", "authority", "rival", "enemy", "conceptual")
    for n0 in [dict(p, creed=c, station=st, name="x") for p in profiles[:10] for c in CREEDS for st in ("Hand", "Sworn")]:
        for vc in classes:
            for ac in classes:
                for hurt in (False, True):
                    try:
                        r = violence_response(n0, hurt, vc, ac, None)
                    except Exception as e:
                        problems.append("response crash %s/%s: %s" % (vc, ac, e)); continue
                    if r not in RESP: problems.append("unknown response %s" % r)
                    ar = attacker_response(n0, vc)
                    if ar not in RESP: problems.append("unknown attacker response %s" % ar)
                    if vc in CLOSE and not hurt and violence_steady(n0, r, [0] * 7, vc) and r != "Performed":
                        problems.append("steady while someone close is hurt: %s (%s)" % (r, vc))
                    if not hurt and vc in ("beloved", "charge") and ac not in CLOSE and r in ("Satisfied", "Spectator", "Curiosity", "Business"):
                        problems.append("cold response to a hurt %s: %s" % (vc, r))
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
    for k in EVENTS:
        if k not in EVENT_AFFECT: problems.append("event without affect: " + k)
    for k in PROCESSING:
        if k not in PROCESS_SPLIT: problems.append("processing without a split: " + k)
    random.seed(1)
    probe = build(list(DEFAULT_DIALS))
    probe["axes"] = [0, 0, 0, 0, 0, 0, 0]; probe["core"] = [0] * 7; probe["flags"]["complete"] = False
    probe["authenticity"]["kind"] = "Genuine"; derive(probe)
    seen = []
    for _ in range(6):
        seen.append(intensity_of(probe, "betrayal", "familiar")[1])
        affect(probe)["habit"]["betrayal"] = min(0.9, affect(probe)["habit"].get("betrayal", 0) + 0.15)
    if not all(x > y for x, y in zip(seen, seen[1:])):
        problems.append("habituation does not lessen repeated pain")
    h0 = affect(probe)["habit"]["betrayal"]
    for _ in range(30): affect_day(probe)
    if affect(probe)["habit"].get("betrayal", 0) >= h0:
        problems.append("habituation never fades")
    probe["axes"] = [0, 0, 0, 3, 0, 0, 0]; probe["core"] = [0, 0, 0, 3, 0, 0, 0]
    affect(probe)["pressure"] = [0.0] * 7; probe["shifts"] = {}
    affect(probe)["pressure"][W] = -3.0
    settle_traits(probe)
    if probe["axes"][W] != 3:
        problems.append("a moderate push moved a deeply rooted trait")
    affect(probe)["pressure"][W] = -40.0
    settle_traits(probe, overwhelming=40)
    if probe["axes"][W] != 2:
        problems.append("an overwhelming event moved a trait more or less than one step")
    probe["axes"][W] = 2; probe["core"][W] = 3
    for _ in range(CORE_DRIFT_DAYS + 1): affect_day(probe)
    if probe["core"][W] != 2:
        problems.append("a long-held change never became part of who they are")
    for f_, tg in FORM_TAGS.items():
        for t_ in tg:
            if t_ not in TAG_AXES: problems.append("tag without inclination axes: " + t_)
    random.seed(2)
    q = build(list(DEFAULT_DIALS)); q["shifts"] = {}
    steps = []
    for _ in range(8):
        b4 = (q.get("inclinations") or {}).get("Mockery", {}).get("strength", 0)
        incline(q, "Mockery", [(W, -1)])
        steps.append(q["inclinations"]["Mockery"]["strength"] - b4)
    if not all(x > y for x, y in zip(steps, steps[1:])):
        problems.append("inclinations do not grow by less each time")
    s0 = q["inclinations"]["Mockery"]["strength"]
    for _ in range(10):
        q["day"] += 1; incline_day(q)
    if (q.get("inclinations") or {}).get("Mockery", {}).get("strength", 0) >= s0:
        problems.append("inclinations never fade")
    for _ in range(30): incline(q, "drinking", ACT_AXES["drinking"])
    if sum(1 for c in q["compulsions"] if c.get("from_habit") == "drinking") != 1:
        problems.append("a strong habit did not become exactly one compulsion")
    q["inclinations"]["Mockery"] = {"strength": 0.9, "count": 50, "last": q["day"]}
    for combo in combos:
        active, _ = circ_active(q, set(combo))
        hf = habit_form(q, "Hostile", active)
        if hf and not all(_passes(hf, c, q) for c in active):
            problems.append("a habit broke through a circumstance: %s under %s" % (hf, ",".join(combo)))
    allforms = sorted(set(KIND_FORMS + MIDDLE_FORMS + HOSTILE_FORMS) | set(FORM_TAGS))
    for n in profiles:
        for combo in combos:
            active, _ = circ_active(n, set(combo))
            for f in allforms:
                pn = punctuation(n, active, f)
                if set(active) & {"frozen", "stunned"} and pn:
                    problems.append("punctuation flourish while frozen: %s under %s" % (f, ",".join(combo)))
                if "clear" in active and any("CAPITALS" in x for x in pn):
                    problems.append("capitals in a moment of clarity: %s" % f)
                if len(pn) > 2 or (any("CAPITALS" in x for x in pn) and any("semicolon" in x for x in pn)):
                    problems.append("punctuation notes pull against each other: %s under %s" % (f, ",".join(combo)))
    # speech: enough distinct manners, every field present, the moment bends but never replaces
    if len(SPEECH) < 20: problems.append("fewer than twenty ways of talking")
    for k, v in SPEECH.items():
        if not all(v.get(f) for f in ("keys", "dev", "warm", "cold")) or len(v["dev"]) < 3 or v["reg"] not in range(4) or v["len"] not in range(3):
            problems.append("way of talking incomplete: " + k)
    for v in BEND.values():
        if not (v.get("base") and v.get("work")): problems.append("a way of bending words is incomplete")
    _st = random.getstate()
    seen_m, seen_b, seen_s = collections.Counter(), collections.Counter(), collections.Counter()
    rs = random.Random(11)
    for i in range(3000):
        random.seed(5000 + i)
        dl = [rs.randint(0, 3) for _ in range(7)]
        q = build(dl, "probe%d" % i)
        sp_ = q["speech"]; seen_m[sp_["main"]] += 1; seen_b[sp_["bend"]] += 1
        for x in sp_["slang"]: seen_s[x] += 1
        if speech_of(q) is not sp_ or speech_build(dict(q, speech=None))["main"] is None:
            problems.append("speech not stable on re-read")
        for combo in combos[:: max(1, len(combos) // 40)]:
            active, _ = circ_active(q, set(combo))
            for band in BANDS:
                t = speech_now(q, active, band, scheming=bool(i % 2))
                if abs(REG_WORD.index(t["register"]) - sp_["reg"]) > 1:
                    problems.append("the moment moved register more than a step: %s under %s" % (sp_["main"], ",".join(combo)))
                if len(t["habits"]) < 2:
                    problems.append("the moment stripped the manner bare: %s" % sp_["main"])
                if set(active) & {"frozen", "stunned"} and t["length"] != "terse":
                    problems.append("many words while frozen")
                if band == "Neutral" and t["tone"]:
                    problems.append("tone shift without cause in a neutral meeting")
    random.setstate(_st)
    missing = [k for k in SPEECH if not seen_m[k]]
    if missing: problems.append("ways of talking that never occur: " + ", ".join(missing))
    top = seen_m.most_common(1)[0]
    if top[1] > 0.15 * 3000: problems.append("one way of talking dominates: %s %d of 3000" % top)
    if [k for k in BEND if not seen_b[k]]: problems.append("a way of bending words never occurs")
    if [k for k in SLANG if not seen_s[k]]: problems.append("a kind of slang never occurs")
    print("Speech: %d ways of talking; most common %s %d/3000, rarest %s %d/3000; bends %s; slang kinds %d." % (
        len(SPEECH), top[0], top[1], seen_m.most_common()[-1][0], seen_m.most_common()[-1][1],
        ", ".join("%s %d" % kv for kv in sorted(seen_b.items())), len(seen_s)))
    # identity under strain, ordinary life, schema
    _st = random.getstate()
    seen_w = {p_: collections.Counter() for p_ in STRAINS}
    profiles_seen = collections.Counter()
    mis = bus = tries = 0
    for i in range(2000):
        random.seed(9000 + i)
        q = build(list(DEFAULT_DIALS), "strain%d" % i)
        for p_, w_ in q["strain"].items():
            seen_w[p_][w_] += 1
            if w_ not in STRAINS[p_]: problems.append("a way under strain that doesn't fit its strain: %s/%s" % (p_, w_))
        profiles_seen[(q["speech"]["main"], tuple(sorted(q["strain"].items())))] += 1
        before_id, before = q["id"], dict(q["strain"])
        mq = migrate(json.loads(json.dumps(q)))
        if mq["id"] != before_id or mq["strain"] != before or mq["speech"] != q["speech"] or mq["schema"] != SCHEMA:
            problems.append("migration changed who someone is")
        for combo in combos[:: max(1, len(combos) // 20)]:
            active, _ = circ_active(q, set(combo))
            b_ = ordinary_beats(q, active)
            tries += 1; mis += bool(b_["mishear"]); bus += bool(b_["business"])
            if set(active) & {"frozen", "stunned"} and b_["mishear"]:
                problems.append("a misunderstanding while frozen")
    for p_, c_ in seen_w.items():
        if [w_ for w_ in STRAINS[p_] if not c_[w_]]:
            problems.append("a way of taking %s never occurs" % p_)
    if mis / tries > 0.05: problems.append("misunderstandings too common: %.3f" % (mis / tries))
    twins = sum(v for v in profiles_seen.values() if v > 1)
    biggest = profiles_seen.most_common(1)[0][1]
    if biggest > 3: problems.append("people converge: %d of 2000 share one way of talking and taking things" % biggest)
    if twins > 0.05 * 2000: problems.append("too many people share the same way of talking and taking things: %d" % twins)
    q = build(list(DEFAULT_DIALS), "steady")
    keep = dict(q["strain"])
    for k_ in ["humiliation", "threat", "betrayal", "respect", "loss", "kindness"] * 30:
        q["strain"] = strain_of(q)
        if q["strain"] != keep: problems.append("a way of taking things changed with ordinary events"); break
    ordinary_days = 0
    for i in range(1000):
        random.seed(7000 + i)
        r_ = max(1, d(20) - 1)
        ordinary_days += 7 <= r_ <= 14
    if ordinary_days < 350: problems.append("too few ordinary days")
    if len(set(ORDINARY)) < 30 or len(BUSINESS) < 15: problems.append("too little ordinary life to draw on")
    random.setstate(_st)
    print("Identity: %d ways of taking things across %d strains; %d of 2000 share a full profile (largest group %d); "
          "misunderstandings %.1f%%, ordinary business %.0f%% of encounters; ordinary days about %d%%." % (
              len(STRAIN_WAYS), len(STRAINS), twins, biggest, 100 * mis / tries, 100 * bus / tries, ordinary_days / 10))
    # voice survives anger, exhaustion, a superior, privacy and grief without becoming someone else's
    _st = random.getstate()
    random.seed(424242)
    conds = {"angry": {"enraged"}, "exhausted": {"exhausted"}, "superior": {"superior"}, "private": {"intimate"},
             "grieving": {"grieving"}}
    people = [build(list(DEFAULT_DIALS), "voice%d" % i) for i in range(300)]
    confusable = 0
    for q in people:
        sp_ = speech_of(q)
        mine = set(SPEECH[sp_["main"]]["dev"]); side = set(SPEECH[sp_["side"]]["dev"]) if sp_["side"] else set()
        for cname, cs in conds.items():
            active, _ = circ_active(q, cs)
            t = speech_now(q, active, "Hostile" if cname == "angry" else "Neutral")
            if t["manner"] != sp_["main"] or len(set(t["habits"]) & mine) < 2 or not set(t["habits"]) <= mine | side:
                problems.append("voice lost under %s: %s" % (cname, sp_["main"]))
    for q1, q2 in zip(people[::2], people[1::2]):
        if speech_of(q1)["main"] != speech_of(q2)["main"]:
            t1 = speech_now(q1, ["grieving"], "Neutral"); t2 = speech_now(q2, ["grieving"], "Neutral")
            if t1["keys"] == t2["keys"] and set(t1["habits"]) == set(t2["habits"]):
                confusable += 1
    if confusable: problems.append("two different voices read the same under grief: %d" % confusable)
    # thoughts are often mundane or irrelevant, and seldom about what they actually want
    groups = collections.Counter()
    for q in people[:150]:
        ctx = {"dials": DEFAULT_DIALS, "present": ["player"], "prose": "The rain kept on at the shutters."}
        for _ in range(20):
            groups[_draw(q, ctx)[2]] += 1
    tot = sum(groups.values())
    stray = (groups["n"] + groups["z"]) / tot
    motive = groups["w"] / tot
    if stray < 0.30: problems.append("thoughts too seldom mundane or stray: %.2f" % stray)
    if motive > 0.15: problems.append("thoughts track motives too closely: %.2f" % motive)
    # recovery varies between people, even from the same kind of loss
    spans = []
    for q in people[:120]:
        tp = tempo_of(q)
        spans.append(tp["grief"] * random.lognormvariate(0, 0.25))
    if max(spans) / min(spans) < 2.0: problems.append("grief runs like clockwork: everyone recovers alike")
    # knowledge: provenance, drift, secrecy, no truth stored in anyone
    w_c, h_c, dist_by_hop = [], [], collections.defaultdict(list)
    for i, q in enumerate(people[:100]):
        o = people[(i + 1) % 100]
        q["knows"] = []; o["knows"] = []
        b = learn_belief(q, "the well", "it was poisoned", "witnessed")
        w_c.append(b["confidence"])
        if not (0.05 <= b["confidence"] <= 0.98): problems.append("belief confidence out of range")
        if any(k in b for k in ("true", "truth", "is_true")): problems.append("a belief carries whether it is true")
        chain = [q] + [people[(i + j) % 100] for j in range(2, 7)]
        for c_ in chain[1:]:
            c_["knows"] = []
        for j in range(len(chain) - 1):
            got, err = tell_belief(chain[j], chain[j + 1], "the well")
            if got:
                dist_by_hop[got["hops"]].append(len(got["distortions"]))
                if got["hops"] == 1: h_c.append(got["confidence"])
        s_ = learn_belief(o, "a hiding place", "under the third stone", "witnessed", secret=True)
        o["trust"][q["name"]] = {"bedrock": 0, "surface": 0}
        if tell_belief(o, q, "a hiding place")[0] is not None: problems.append("a secret told to someone they don't trust")
    if sum(w_c) / len(w_c) <= sum(h_c) / max(1, len(h_c)): problems.append("hearsay held as surely as what they saw")
    if dist_by_hop[1] and dist_by_hop[5] and sum(dist_by_hop[5]) / len(dist_by_hop[5]) <= sum(dist_by_hop[1]) / len(dist_by_hop[1]):
        problems.append("rumours don't drift as they spread")
    if tell_belief(people[0], people[1], "something nobody knows")[0] is not None: problems.append("told what they don't know")
    random.setstate(_st)
    print("Voices: kept under anger, exhaustion, a superior, privacy and grief for 300 people. Thoughts: %.0f%% stray or "
          "mundane, %.0f%% about what they want. Grief tempo varies %.1fx between people. Rumours: %.1f details wrong "
          "after one telling, %.1f after five." % (100 * stray, 100 * motive, max(spans) / min(spans),
          sum(dist_by_hop[1]) / max(1, len(dist_by_hop[1])), sum(dist_by_hop[5]) / max(1, len(dist_by_hop[5]))))
    def clar_probe(seed):
        random.seed(seed)
        c = build(list(DEFAULT_DIALS)); c["axes"] = [0] * 7; c["core"] = [0] * 7
        c["authenticity"]["kind"] = "Genuine"; c.pop("affect", None); c["inclinations"] = {}; derive(c)
        return c
    c = clar_probe(3); flood = 0
    for day_ in range(200):
        c["day"] += 1; affect_day(c)
        apply_affect(c, "betrayal", "familiar", EVENTS["betrayal"][2])
        flood += bool(clarity_check(c))
    if flood:
        problems.append("clarity struck from one kind of moment repeated, without convergence")
    c = clar_probe(4); lop = 0
    for day_ in range(200):
        c["day"] += 1; affect_day(c)
        for k in ("betrayal", "loss", "humiliation"):
            apply_affect(c, k, "familiar", EVENTS[k][2])
        lop += bool(clarity_check(c))
    if lop:
        problems.append("clarity struck in pure pain, far from balance")
    hits = 0; days_ = 0
    for seed in range(40):
        c = clar_probe(100 + seed)
        for day_ in range(30):
            c["day"] += 1; affect_day(c)
            for k in ("betrayal", "reunion", "threat", "joy"):
                apply_affect(c, k, "familiar", EVENTS[k][2])
            onset = (clarity_window(c)[0] and not affect(c).get("converged") and not affect(c)["clarity_days"]
                     and affect(c).get("apart", 99) >= CLARITY_WINDOW)
            days_ += onset
            hits += bool(clarity_check(c))
    rate = 100.0 * hits / max(1, days_)
    if days_ == 0 or not (1.0 <= rate <= 20.0):
        problems.append("clarity per convergence outside its margin: %.1f%% (%d convergences)" % (rate, days_))
    c = clar_probe(5)
    base = clarity_chance(c)
    c["inclinations"]["clarity"] = {"strength": 0.8, "count": 10, "last": c["day"]}
    if clarity_chance(c) <= base:
        problems.append("an inclination toward clarity does not make it likelier")
    m0 = clarity_margin(clar_probe(6))
    c = clar_probe(6); c["axes"][D] = 3; c["axes"][V] = -2
    if clarity_margin(c) <= m0:
        problems.append("discipline and calm do not widen the margin for clarity")
    for n_ in profiles:
        n_.setdefault("needs", {"state": {r: 0 for r in RUNGS}}); n_.setdefault("drive", {"text": "x"})
        for combo in combos:
            active, _ = circ_active(n_, set(combo))
            rp = thought_ripple(n_, active)
            if ({"frozen", "afraid"} & set(active)) and rp != "nothing shows":
                problems.append("a thought showed through %s" % ",".join(combo))
    random.seed(8)
    arisen = 0
    seeds_seen = set()
    for k_ in range(4000):
        nn = build(list(DEFAULT_DIALS))
        ctx_ = {"place": {"fixtures": [{"kind": "smell", "text": "woodsmoke"}], "marks": ["a stain"]},
                "present": ["Bram", nn["name"]], "danger": ["violence"], "prose": "The kettle whistled.",
                "dials": [3, 1, 3, 3, 3, 1, 1], "circle": {"today": {"cause": "a lean week", "value": -1}}}
        if random.uniform(0, 100) <= THOUGHT_ARISE:
            arisen += 1
            text_, guess_, g_ = _draw(nn, ctx_)
            seeds_seen.add(g_)
            old_labels = ("a memory:", "the place:", "today:", "their people:", "what they want:", "the pull of",
                          "the habit of", "a line they don't cross:", "something small and theirs:", "the body:",
                          "a word in the air:", "nothing to do with anything:", "someone or something of theirs:",
                          "the danger in the room")
            if text_.lower().startswith(old_labels) or not text_.strip():
                problems.append("a thought carries a label or is empty: %r" % text_)
    def _m(axes, styles, active, clarity=0.0):
        q = build(list(DEFAULT_DIALS)); q["axes"] = axes; q["voices"] = [{"style": s_, "frac": 1.0 / len(styles),
                                                                           "manner": voice_manner(SBY[s_])} for s_ in styles]
        q["authenticity"] = {"kind": "Genuine", "faces": []}; q["inclinations"] = {"clarity": {"strength": clarity, "count": 1, "last": 0}}
        derive(q)
        lv = [thought_hold(q, ["x", None, False, k / 20.0], active)[0] for k in range(21)]
        return sum(lv) / 21.0, q
    low, _ = _m([0, 2, 1, 0, -2, -2, 1], ["Adventurous", "Dramatic"], [])
    high, hq = _m([1, -1, 0, 1, 2, 3, 0], ["Visionary", "Serious"], [])
    hurt_, _ = _m([1, -1, 0, 1, 2, 3, 0], ["Visionary", "Serious"], ["hurt"])
    clear_, _ = _m([0, 1, 0, 0, 0, 0, 0], ["Leisurely"], ["clear"])
    plain_, _ = _m([0, 1, 0, 0, 0, 0, 0], ["Leisurely"], [])
    if not low < high: problems.append("reflective natures do not notice their thoughts more than impulsive ones")
    if not hurt_ < high: problems.append("pain does not cloud how a thought is held")
    if not clear_ > plain_: problems.append("clarity does not lift how a thought is held")
    lat_lo = _lateral_chance(_m([0, 0, 0, 0, 0, -3, 0], ["Conscientious"], [])[1])
    lat_hi = _lateral_chance(hq)
    if not lat_lo < lat_hi: problems.append("open, visionary minds do not leap sideways more often")
    if len(seeds_seen) < 8:
        problems.append("thoughts draw from too few levels: %s" % sorted(seeds_seen))
    if not (15 <= arisen / 40.0 <= 35):
        problems.append("thoughts arise %.0f%% of scenes, outside 15-35%%" % (arisen / 40.0))
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


def _ask_out(kind, msg, text=None, shape=None):
    VIEW.clear()
    VIEW.update({"cmd": "ask", "result": kind, "text": text, "shape": shape})
    print(msg)


def cmd_ask(a):
    n = load(a.file)
    dr = n["drive"]
    if n["condition"] != "present":
        _ask_out("no", "NO ASK. They are %s." % n["condition"]); return
    if dr["type"] != "Open":
        _ask_out("no", "NO ASK. Drive is %s: decline, deflect, or a trivial courtesy at most." % dr["type"]); return
    if a.asked:
        _ask_out("no", "NO ASK. Already asked this scene."); return
    if not a.touched:
        _ask_out("no", "NO ASK. The talk has not touched %s." % dr["rung"]); return
    af = n.get("afflictions", {})
    if af.get("grieving") and dr["rung"] != "Belonging":
        _ask_out("no", "NO ASK. They are grieving; nothing else is spoken of now."); return
    if af.get("sick") and dr["rung"] != "Survival":
        _ask_out("no", "NO ASK. Too sick to raise it."); return
    td = n.get("today")
    if not td:
        _ask_out("no", "Roll their day first (the day decides whether they are open)."); return
    if not td["open"]:
        _ask_out("no", "NO ASK. Not a day they would speak of it."); return
    tr, g = total_trust(n, a.who), n["derived"]["guard"]
    if tr < g:
        _ask_out("hint", "HINT ONLY. Open today, but trust %d < guard %d: an oblique remark, no request." % (tr, g),
                 dr["text"]); return
    _ask_out("may", "MAY ASK (%s): '%s'. Pride or a code may still make them refuse." % (dr.get("shape", "Partial"),
             dr["text"]), dr["text"], dr.get("shape", "Partial"))


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
        took_ = strain_of(n)[EVENT_STRAIN[a.kind]] if a.kind in EVENT_STRAIN else None
        to_bedrock = abs(delta) >= 2
        if took_ in ("reconcile", "self_blame", "appease") and delta < 0:
            delta = int(delta / 2)                       # the bond matters more, or the fault is theirs
        elif took_ in ("retaliate_later", "coldness", "laugh_remember") and delta < 0:
            to_bedrock = True                            # it goes deep and stays
            delta -= 1 if took_ == "retaliate_later" else 0
        elif took_ == "suspects" and delta > 0:
            delta = 0                                    # praise makes them wary, not warmer
        elif took_ in ("basks", "shares") and delta > 0:
            delta += 1
        delta = int(round(delta * clamp(n["derived"]["sensitivity"], 0.5, 1.5))) if delta else 0
        if to_bedrock:
            t["bedrock"] = clamp(t["bedrock"] + delta, -5, 5)
        else:
            t["surface"] = clamp(t["surface"] + delta, -3, 3)
        notes.append("trust toward %s now %+d" % (a.who, total_trust(n, a.who)))
    st = n["needs"]["state"]
    for r, step in needs.items():
        st[r] = clamp(st[r] + step, -2, 1)
    cls = relation_to(n, a.about)[0] if a.about else (relation_to(n, a.who)[0] if a.who else "stranger")
    if a.kind == "loss" and cls == "enemy":
        pass
    else:
        notes += apply_affect(n, a.kind, cls, marks, a.size)
    if a.kind == "code-broken":
        notes.append("shame: Selfhood starved; they will not forget doing it")
    af = n.setdefault("afflictions", {})
    if a.kind == "loss":
        cls, role, loy = relation_to(n, a.about) if a.about else ("familiar", "kin", 3)
        if cls == "enemy":
            st["Safety"] = clamp(st["Safety"] + 1, -2, 1)
            notes.append("an enemy gone: no grief; whatever they show, they show plainly")
        else:
            if cls == "stranger":
                notes.append("a death they know of, not a grief of their own; sobered for a while, no more")
                base, spread = 0, 0
            else:
                base, spread = GRIEF_DAYS.get(role or "kin", (7, 7))
            days = base + (d(spread) if spread else 0)
            kin = kin_of(n, a.about) if a.about else None
            days, gnote = grief_length(n, days, role, kin[2] if kin and kin[2] is not n.get("pet") else None)
            if gnote:
                notes.append(gnote)
            if role in ("mentor", "spiritual", "symbol"):
                st["Meaning"] = clamp(st["Meaning"] - 2, -2, 1)
            if kin and kin[2].get("alive"):
                kin[2]["alive"] = False
                if kin[2] is not n.get("pet") and not kin[2]["label"].startswith("their late "):
                    kin[2]["label"] = kin[2]["label"].replace("their ", "their late ", 1)
                    for t in n["ties"]:
                        if (t.get("who") or "").lower() == a.about.lower():
                            t["who"] = t["label"] = kin[2]["label"]
                    if (n["family"].get("dearest") or "").lower() == a.about.lower():
                        n["family"]["dearest"] = None
            sp_ = life_of(n)["spirit"]
            if days and cls != "stranger":
                notes.append(("performs the grief their people expect" if sp_.get("performed") else
                              "in their outlook: " + GRIEF_SPIRIT[sp_["after"]]))
                if (role in ("child", "spouse", "lover") and 0 < sp_["certainty"] < 3 and not sp_.get("performed")
                        and random.random() < 0.5):
                    sp_["certainty"] -= 1
                    notes.append("what they believe is shaken (now %s)" % CERTAINTY[sp_["certainty"]])
            if days:
                if processing(n) == "Numb":
                    af["grief_delay"] = d(3)
                    af["grief_pending"] = days
                    notes.append("numb: grief arrives in %d days and lasts %d" % (af["grief_delay"], days))
                else:
                    af["grieving"] = days
                    notes.append("grieving for %d days (%s)" % (days, PROCESSING[processing(n)][0]))
    if a.kind == "fell-ill":
        af["sick"] = d(3) + 1
        notes.append("sick for %d days" % af["sick"])
    if a.kind == "intoxicated":
        af["intoxicated"] = 1
        notes.append("drunk or high for the rest of today")
    party = a.who if EVENTS[a.kind][0] else (a.about or "")
    took = strain_of(n)[EVENT_STRAIN[a.kind]] if a.kind in EVENT_STRAIN else None
    if took:
        notes.append("takes it as they always do: " + STRAIN_WAYS[took])
    n["memory"].append({"day": n["day"], "event": a.kind, "with": party, "note": a.note or "",
                        "weight": sz, "took": took})
    derive(n)
    save(n, a.file)
    print("Recorded %s%s. " % (a.kind, (" with " if EVENTS[a.kind][0] else " concerning ") + party if party else "")
          + "; ".join(notes))
    VIEW.clear()
    VIEW.update({"cmd": "event", "name": n["name"], "kind": a.kind, "took": took, "took_text": STRAIN_WAYS.get(took)})



def cmd_learn(a):
    n = load(a.file)
    b = learn_belief(n, a.subject, a.claim, a.source, frm=a.source_name, reliability=a.reliability, fact=a.fact,
                     secret=a.secret, stressed=a.stressed)
    save(n, a.file)
    print("%s now believes: %s" % (n["name"], belief_plain(b)))
    VIEW.clear(); VIEW.update({"cmd": "learn", "name": n["name"], "belief": b, "plain": belief_plain(b)})


def cmd_tell(a):
    t, h = load(a.teller), load(a.hearer)
    if t.get("id") == h.get("id"):
        sys.exit("Someone can't tell themself a rumour.")
    if h["condition"] in ("dead", "comatose") or t["condition"] in ("dead", "comatose"):
        sys.exit("Only the living and awake pass things on.")
    b, err = tell_belief(t, h, a.about)
    VIEW.clear()
    if err:
        print(err); VIEW.update({"cmd": "tell", "refused": err}); return
    save(h, a.hearer)
    print("%s now believes: %s" % (h["name"], belief_plain(b)))
    VIEW.update({"cmd": "tell", "teller": t["name"], "hearer": h["name"], "belief": b, "plain": belief_plain(b)})


def cmd_beliefs(a):
    n = load(a.file)
    bs = beliefs_about(n, a.about) if a.about else sorted(n.get("knows", []), key=lambda b: -b["confidence"])
    for b in bs:
        print(belief_plain(b))
    if not bs:
        print("%s believes nothing about that." % n["name"])
    VIEW.clear(); VIEW.update({"cmd": "beliefs", "name": n["name"], "beliefs": bs, "plain": [belief_plain(b) for b in bs]})


def cmd_affinity(a):
    x, y = load(a.a), load(a.b)
    if x["name"] == y["name"] and x.get("axes") == y.get("axes"):
        sys.exit("Regard needs two different people.")
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
    VIEW.clear()
    VIEW.update({"cmd": "affinity", "a": x["name"], "b": y["name"], "regard": total})
    print("Regard %s <-> %s: %+d (%s)" % (x["name"], y["name"], total,
                                          ", ".join("%s %+d" % p for p in parts)))
    print("Use it as trust between them; each still reacts through their own mood and manner.")


def cmd_scene(a):
    pairs = [(p, load(p)) for p in a.files]
    gone = [n["name"] for _, n in pairs if n["condition"] in ("dead", "comatose")]
    pairs = [(p, n) for p, n in pairs if n["condition"] not in ("dead", "comatose")]
    if gone:
        print("Not taking part: %s (dead or comatose)" % ", ".join(gone))
    SCENE_ABSENT[:] = gone
    if not pairs:
        sys.exit("No one present can take part.")
    a.files = [p for p, _ in pairs]
    ns = [n for _, n in pairs]
    dials = load(a.world)["dials"] if a.world else (ns[0]["dials"] if ns else list(DEFAULT_DIALS))
    lead = max(ns, key=lambda n: n["axes"][M] + n["axes"][E] + RANK.get(n["station"], 0))
    print("[narrator only] Lead of the room: %s" % lead["name"])
    VIEW.clear()
    VIEW.update({"cmd": "scene", "lead": lead["name"], "loud": None, "spread_to": [], "hidden_turn": None,
                 "slips": [], "thoughts": {}, "oddity": None, "absent": []})
    loud = max(ns, key=lambda n: (n["axes"][E], n["axes"][M]))
    sus = [n["name"] for n in ns if n["axes"][V] >= 1 and n is not loud]
    VIEW["loud"] = loud["name"]
    VIEW["spread_to"] = sus
    if sus:
        print("Mood carries from %s to: %s (+1 or -1 toward their band, once)" % (loud["name"], ", ".join(sus)))
    turns = [n for n in ns if d(100) <= n["derived"]["agency"]]
    if turns:
        n = random.choice(turns)
        kinds = ["news reached them (by a route they could really have)", "something happened with %s offscreen"
                 % random.choice(n["ties"])["label"], "a decision about their drive ripened",
                 "a compulsion or old hunger spiked", "they are trying out the other side of themself",
                 "something no table covers, consistent in hindsight"]
        hk = kinds[d(6) - 1]
        VIEW["hidden_turn"] = {"name": n["name"], "what": hk}
        print("Hidden turn for %s: %s. Let behaviour show it; never explain it." % (n["name"], hk))
    for n in ns:
        if n["authenticity"]["kind"] in ("Masked", "Hollow", "Borrowed", "Shifting"):
            r = d(10)
            if r <= n["derived"]["slip"]:
                VIEW["slips"].append(n["name"])
                print("Slip for %s if pressed or alone with someone trusted, and only at or after a deception"
                      % n["name"])
    pl = load(a.place) if getattr(a, "place", None) else None
    ctx = {"world": load(a.world) if a.world else None, "dials": dials, "place": pl,
           "circle": load(a.circle) if getattr(a, "circle", None) else None,
           "present": [m["name"] for m in ns] + (a.present or []), "danger": a.danger or [],
           "prose": a.prose or ""}
    for path, n in zip(a.files, ns):
        th = arise_thought(n, pl, ctx, getattr(a, "seal", None))
        if n.get("today") is not None:
            n["today"]["thought"] = list(th) if th else None
            save(n, path)
        if th:
            VIEW["thoughts"][n["name"]] = th[0]
            lvl, hold = thought_hold(n, th, [])
            print("A thought arises in %s: %s. Left to itself, %s.%s" % (
                n["name"], th[0], hold, (" If they wonder where it came from, their own guess: %s."
                                          % (th[1] or "nothing they can name")) if lvl >= 1 else ""))
    r = d(100)
    if r == 100:
        pool = ODD_PLAIN + (ODD_UNCANNY if dial(dials, "X") >= 2 else [])
        on, oo = random.choice(ns)["name"], random.choice(pool)
        mundane = oo in ODD_PLAIN and random.random() < 0.75
        VIEW["oddity"] = {"name": on, "what": oo, "mundane": mundane}
        print("Oddity (%s): %s%s" % (on, oo, " (an ordinary reason nobody will mention; not a clue)" if mundane else ""))


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

# ---------- affect: pain, elation, clarity; habituation; trait pressure against anchors ----------
# kind: (valence, base intensity, category for habituation)
EVENT_AFFECT = {
 "kindness": (1, 2, "kindness"), "rescue": (1, 6, "rescue"), "gift": (1, 2, "gifts"),
 "respect": (1, 2, "praise"), "betrayal": (-1, 6, "betrayal"), "humiliation": (-1, 4, "humiliation"),
 "threat": (-1, 3, "threat"), "lie-caught": (-1, 2, "betrayal"), "triumph": (1, 4, "success"),
 "loss": (-1, 5, "loss"), "code-broken": (-1, 5, "shame"), "fell-ill": (-1, 2, "illness"),
 "intoxicated": (1, 1, "pleasure"), "reunion": (1, 5, "reunion"), "joy": (1, 3, "pleasure"),
 "witnessed": (-1, 3, "violence"),
}
CLOSENESS = {"stranger": 0.5, "familiar": 1.0, "rival": 1.0, "enemy": 0.6, "authority": 1.2, "charge": 1.5,
             "conceptual": 1.5, "revered": 1.8, "beloved": 2.0}
# how processing splits an experience: (felt now, pressure on who they are, delayed portion)
PROCESS_SPLIT = {"Expressive": (1.3, 0.7, 0.0), "Contained": (0.6, 1.3, 0.0), "Numb": (0.2, 1.0, 0.8),
                 "Devotional": (0.9, 0.8, 0.0), "Intellectual": (0.7, 0.7, 0.0), "Action": (1.0, 0.9, 0.0),
                 "Caretaking": (1.0, 1.0, 0.0), "Bargaining": (0.8, 0.9, 0.4), "Performed": (0.0, 0.3, 0.0)}
CORE_DRIFT_DAYS = 90
CLARITY_WINDOW = 7       # days of recent moments that can converge
CLARITY_KINDS = 3        # different kinds of moment needed
CLARITY_WEIGHT = 8.0     # how much they must amount to, pain and elation together
CLARITY_MARGIN = 5.0     # how near to balance pain and elation must sit
CLARITY_CHANCE = 5       # percent a day while converged, before inclination
PRESSURE_GAIN = 0.3   # how much of an experience presses on who they are; most of it passes


def affect(n):
    a = n.setdefault("affect", {})
    a.setdefault("feeling", 0.0)       # pain (-) / elation (+), fades by half each day
    a.setdefault("pending", [])        # [days until it arrives, amount] for the numb and the bargaining
    a.setdefault("habit", {})          # category -> 0..0.9: how used to it they are
    a.setdefault("pressure", [0.0] * 7)
    a.setdefault("clarity_days", 0)
    a.setdefault("clarity_count", 0)
    a.setdefault("away", [0] * 7)      # days each trait has sat away from its core
    if "core" not in n:
        n["core"] = list(n["axes"])    # who they were when they came on the scene
    return a


def anchor(n, i, direction):
    """How strongly their underlying nature holds a trait against change in this direction."""
    core = n["core"][i]
    cur = n["axes"][i]
    base = 3.0 + 0.5 * abs(core)
    if n["axes"][D] >= 2: base += 1.0
    if n["flags"].get("complete"): base += 1.0
    toward_core = (core - cur) * direction > 0
    return base * (0.5 if toward_core else 1.0 + 0.5 * abs(cur - core))


def intensity_of(n, kind, cls, size=None):
    """Effective intensity after closeness, sensitivity and habituation."""
    val, base, cat = EVENT_AFFECT[kind]
    if size == 2: base *= 1.5
    sens = 1.0 + n["axes"][V] / 3.0
    h = affect(n)["habit"].get(cat, 0.0)
    return val, base * CLOSENESS.get(cls, 1.0) * max(0.2, sens) * (1.0 - h), cat, h


def apply_affect(n, kind, cls, marks, size=None):
    """Feel an event: feeling now, delayed feeling, pressure on traits, habituation, maybe clarity.
    Returns notes for the narrator."""
    af = affect(n)
    notes = []
    val, eff, cat, h = intensity_of(n, kind, cls, size)
    proc = processing(n)
    now_k, press_k, later_k = PROCESS_SPLIT[proc]
    af["feeling"] = clamp(af["feeling"] + val * eff * now_k, -10, 10)
    af.setdefault("recent", []).append([n["day"], cat, round(val * eff, 2)])
    if later_k:
        af["pending"].append([d(3), val * eff * later_k])
    for axis, sgn in marks:
        af["pressure"][axis] += sgn * eff * press_k * PRESSURE_GAIN
    step = 0.15 * (0.5 if n["axes"][V] >= 2 else 1.5 if n["axes"][V] <= -2 else 1.0)
    af["habit"][cat] = min(0.9, h + step)
    if h >= 0.3:
        notes.append("they are used to %s now; it lands at %d%% of what it once did" % (cat, round(100 * (1 - h))))
    notes.append("%s %.1f (%s)" % ("pain" if val < 0 else "elation", eff, proc.lower()))
    notes += settle_traits(n, overwhelming=eff)
    return notes


def settle_traits(n, overwhelming=0.0):
    """Turn trait pressure into change where it outweighs the anchor of their underlying nature."""
    af = affect(n)
    notes = []
    for i in range(7):
        p = af["pressure"][i]
        if abs(p) < 0.01:
            continue
        sgn = 1 if p > 0 else -1
        anc = anchor(n, i, sgn)
        new = clamp(n["axes"][i] + sgn, -3, 3)
        if new == n["axes"][i]:
            af["pressure"][i] = sgn * min(abs(p), anc)
            continue
        last = n["shifts"].get(AX[i], -999)
        big = overwhelming >= 2 * anc
        if abs(p) > anc and (n["day"] - last >= 30 or big):
            n["axes"][i] = new
            n["shifts"][AX[i]] = n["day"]
            af["pressure"][i] = p - sgn * anc
            notes.append("%s shifts %+d (now %+d)%s" % (AX[i], sgn, new, ", all at once" if big and n["day"] - last < 30 else ""))
    if notes:
        derive(n)
    return notes


def affect_day(n):
    """Everything arises and changes: feeling fades, habits loosen, pressure eases, cores follow."""
    af = affect(n)
    notes = []
    fade = tempo_of(n)["fade"]
    af["feeling"] = round(af["feeling"] * clamp(0.5 ** (1.0 / fade), 0.25, 0.8), 2) if abs(af["feeling"]) >= 0.5 else 0.0
    arrived = 0.0
    keep = []
    for item in af["pending"]:
        item[0] -= 1
        if item[0] <= 0:
            arrived += item[1]
        else:
            keep.append(item)
    af["pending"] = keep
    if arrived:
        af["feeling"] = clamp(af["feeling"] + arrived, -10, 10)
        notes.append("what they didn't feel at the time arrives now (%+.1f)" % arrived)
    for k in list(af["habit"]):
        af["habit"][k] = round(max(0.0, af["habit"][k] - 0.02 / fade), 3)
        if af["habit"][k] == 0:
            del af["habit"][k]
    af["pressure"] = [round(x * 0.98, 3) for x in af["pressure"]]
    if af["clarity_days"]:
        af["clarity_days"] -= 1
    for i in range(7):
        if n["axes"][i] != n["core"][i]:
            af["away"][i] += 1
            if af["away"][i] >= CORE_DRIFT_DAYS:
                n["core"][i] += 1 if n["axes"][i] > n["core"][i] else -1
                af["away"][i] = 0
                notes.append("%s has become part of who they are (core now %+d)" % (AX[i], n["core"][i]))
        else:
            af["away"][i] = 0
    return notes


def clarity_margin(n):
    """How near to balance is near enough. Widens as discipline, calm and a leaning toward clarity grow."""
    a = n["axes"]
    inc = (n.get("inclinations") or {}).get("clarity", {}).get("strength", 0.0)
    return CLARITY_MARGIN + max(0, a[D]) + max(0, -a[V]) + 3.0 * inc


def clarity_window(n):
    """(converged?, kinds, weight, net) over the recent window."""
    af = affect(n)
    span = CLARITY_WINDOW + (2 if n["axes"][D] >= 2 else 0)
    recent = [r for r in af.get("recent", []) if n["day"] - r[0] < span]
    af["recent"] = recent
    kinds = len({r[1] for r in recent})
    weight = sum(abs(r[2]) for r in recent)
    net = sum(r[2] for r in recent)
    need = CLARITY_WEIGHT * max(0.4, 1.0 + n["axes"][V] / 3.0)   # calm people feel less, so need less
    return (kinds >= CLARITY_KINDS and weight >= need and abs(net) <= clarity_margin(n),
            kinds, weight, net)


def clarity_chance(n):
    a = n["axes"]
    inc = (n.get("inclinations") or {}).get("clarity", {}).get("strength", 0.0)
    pct = CLARITY_CHANCE + 5 * inc + (2 if a[D] >= 2 else 0) + (1 if a[V] <= -1 else 0) - (2 if a[V] >= 2 else 0)
    return max(1.0, pct)


def clarity_check(n):
    """Clarity strikes only where different moments converge and pain and elation nearly cancel."""
    af = affect(n)
    ok, kinds, weight, net = clarity_window(n)
    span = CLARITY_WINDOW + (2 if n["axes"][D] >= 2 else 0)
    if not ok:
        af["apart"] = af.get("apart", span) + 1
        af["converged"] = False
        return []
    fresh = not af.get("converged", False) and af.get("apart", span) >= span
    af["converged"] = True
    af["apart"] = 0
    if not fresh or af["clarity_days"]:
        return []          # one chance per genuine convergence: the moments must have been apart a while
    if random.uniform(0, 100) > clarity_chance(n):
        return []
    rarity = 1.0 / (1 + af["clarity_count"])
    prof = rarity * (1.5 if n["axes"][V] >= 1 else 1.0)
    af["clarity_count"] += 1
    af["clarity_days"] = 1 + d(3)
    af["feeling"] = 0.0
    for r in af["recent"]:
        af["habit"][r[1]] = min(0.9, af["habit"].get(r[1], 0.0) + 0.2)
    af["pressure"][V] -= 2.0 * prof
    af["pressure"][O] += 1.5 * prof
    af["pressure"][D] += 1.0 * prof
    af["recent"] = []
    notes = ["clarity: %d kinds of moment converged, pain and elation nearly even (%+.1f); unusually clear "
             "and unhurried for %d days%s" % (kinds, net, af["clarity_days"],
                                               "; rare for them, and it leaves a trace" if prof >= 1 else "")]
    notes += incline(n, "clarity", [(D, 1), (V, -1)])
    return notes


def feeling_words(f):
    if f <= -6: return "heavy; everything costs effort"
    if f <= -3: return "weighed down"
    if f >= 6: return "bright, a little reckless"
    if f >= 3: return "lighter than usual"
    return ""


# ---------- inclinations: what is repeated becomes easier, then wanted ----------
TAG_AXES = {  # what showing a manner, again and again, presses on
 "levity": [(E, 1)], "display": [(E, 1)], "dominant": [(M, 1)], "warm": [(W, 1)], "intimate": [(W, 1)],
 "giving": [(W, 1)], "cold": [(W, -1)], "action": [(E, 1)], "rage": [(V, 1)], "fear": [(V, 1)],
 "guarded": [(E, -1)], "formal": [(D, 1)], "covert": [(C, -1)], "petty": [(C, -1)], "sad": [(E, -1)],
 "leisure": [(O, 1)], "plain": [], "wounded": [],
}
ACT_AXES = {  # common repeated acts; anything else still forms an inclination, without pressing a trait
 "drinking": [(D, -1)], "gambling": [(D, -1), (O, 1)], "praying": [(D, 1)], "fighting": [(V, 1), (M, 1)],
 "lying": [(C, -1)], "stealing": [(C, -1)], "giving": [(W, 1)], "working": [(D, 1)], "mocking": [(W, -1)],
 "flattering": [(C, -1)], "training": [(D, 1)], "killing": [(W, -1), (V, -1)], "healing": [(W, 1)],
 "lording": [(M, 1), (W, -1)], "yielding": [(M, -1)], "studying": [(O, 1)], "carousing": [(E, 1), (D, -1)],
 "hiding": [(E, -1)], "using": [(D, -1)], "hunting": [(V, -1)],
}
INDULGENT = ("drinking", "gambling", "using", "carousing", "lust", "a substance")
INCLINE_GAIN = 0.12
INCLINE_FADE = 0.01
INCLINE_PRESS = 0.15


def incline(n, key, axes=None, times=1, gain=1.0):
    """Someone did or showed `key` again. Returns notes. A manner shown in passing builds slowly
    (gain below one); an act done on purpose builds at the full rate."""
    inc = n.setdefault("inclinations", {})
    rec = inc.setdefault(key, {"strength": 0.0, "count": 0, "last": n["day"]})
    notes = []
    before = rec["strength"]
    for _ in range(times):
        rec["strength"] = round(rec["strength"] + gain * INCLINE_GAIN * (1 - rec["strength"]), 4)
        rec["count"] += 1
        for axis, sgn in (axes or []):
            affect(n)["pressure"][axis] += sgn * INCLINE_PRESS
    rec["last"] = n["day"]
    if before < 0.5 <= rec["strength"]:
        notes.append("%s has become a habit: it fills the gaps when nothing else decides" % key)
    same = [c for c in n["compulsions"] if c["urge"].lower() == key.lower() or c.get("from_habit") == key]
    comp_at = 0.85 if key in FORM_TAGS else 0.7
    if rec["strength"] >= comp_at and not same:
        n["compulsions"].append({"urge": key, "control": 9, "threshold": 3, "pressure": 0, "from_habit": key})
        notes.append("%s has become a compulsion (control 9)" % key)
    elif rec["strength"] >= comp_at and same and not same[0].get("fed_by_habit"):
        c0 = same[0]
        c0["control"] = max(6, c0["control"] - 3)
        c0["threshold"] = c0["control"] // 3
        c0["fed_by_habit"] = True
        notes.append("the old pull of %s grows stronger (control %d)" % (key, c0["control"]))
    if key in INDULGENT and rec["strength"] >= 0.5:
        h = affect(n)["habit"]
        was = h.get("pleasure", 0.0)
        h["pleasure"] = min(0.9, was + 0.05)
        if was < 0.4 <= h["pleasure"]:
            notes.append("it satisfies less than it did; they reach for more of it")
    notes += settle_traits(n)
    return notes


def incline_day(n):
    """Inclinations fade when not fed; strong ones crave."""
    notes = []
    inc = (n.get("inclinations") or {})
    for key in list(inc):
        rec = inc[key]
        idle = n["day"] - rec["last"]
        if idle >= 1:
            rec["strength"] = round(max(0.0, rec["strength"] - INCLINE_FADE), 4)
        if rec["strength"] >= 0.6 and idle == 3:
            st = n["needs"]["state"]
            st["Comfort"] = clamp(st["Comfort"] - 1, -2, 1)
            notes.append("craving %s: three days without it" % key)
        if rec["strength"] <= 0:
            del inc[key]
    return notes


def habit_form(n, band_key, active):
    """The strongest manner they've made a habit of, if it fits this band and every circumstance."""
    inc = (n.get("inclinations") or {})
    pool = {"Kind": KIND_FORMS, "Middle": MIDDLE_FORMS, "Hostile": HOSTILE_FORMS}[band_key]
    best = None
    for key, rec in inc.items():
        if key in pool and rec["strength"] >= 0.5 and all(_passes(key, c, n) for c in active):
            if best is None or rec["strength"] > inc[best]["strength"]:
                best = key
    return best


def cmd_habit(a):
    n = load(a.file)
    key = " ".join(a.act.split()).lower()
    if not key:
        sys.exit("Name the act (drinking, praying, fighting, or anything else).")
    if a.times < 1:
        sys.exit("--times must be 1 or more.")
    if n["condition"] in ("dead", "comatose"):
        sys.exit("%s is %s." % (n["name"], n["condition"]))
    notes = incline(n, key, ACT_AXES.get(key), a.times)
    rec = n["inclinations"][key]
    save(n, a.file)
    print("%s: %s x%d, inclination %.2f%s" % (n["name"], key, rec["count"], rec["strength"],
                                             ". " + "; ".join(notes) if notes else ""))


# ======================================================================================
# SEALED. Narrators and agents voicing characters: do not read this section. Where a
# thought comes from is not knowable to anyone in the fiction, including whoever voices
# them. The audit checks it from the outside.
# ======================================================================================
THOUGHT_ARISE = 25
DRIFT = ["a tune from long ago", "a street they lived on as a child", "a sum that doesn't come out",
         "the face of a stranger from years back", "a word in a language they barely know",
         "what there is to eat tonight", "a smell from somewhere else entirely", "a door they forgot to lock",
         "someone's laugh", "the weather on a day that doesn't matter", "a promise they half remember",
         "the colour of a room they were once in", "a joke they never told", "an animal they once had"]
STOP = set("the a an and or but of to in on at for with from by as is was were be been it its this that "
           "they them their there here have has had not no you your he she his her him we our us i me my "
           "into onto over under then than so if when what which who whom whose just very more most".split())
_DANGER_SHAPE = {"violence": "a blade", "injury": "blood", "disaster": "smoke", "authority": "uniforms",
                 "contagion": "someone coughing", "uncanny": "something that shouldn't be"}
_EVENT_SHAPE = {"kindness": "a kindness", "rescue": "being pulled out of it", "gift": "a gift",
                "respect": "being respected", "betrayal": "being betrayed", "humiliation": "being laughed at",
                "threat": "a threat", "lie-caught": "a lie found out", "triumph": "having won",
                "loss": "someone gone", "code-broken": "a line crossed", "fell-ill": "being ill",
                "intoxicated": "a night drinking", "reunion": "someone come back", "joy": "a good hour",
                "witnessed": "what they saw"}
STRAY = ["an old kitchen, the light in it", "whether they left something on", "the price of something they don't need",
         "a dream from last week", "a stain on a sleeve", "a word that sounds wrong if you repeat it",
         "how many steps there are somewhere", "a dog barking a long way off", "someone's handwriting",
         "the taste of something from childhood", "a chair that wobbles", "an itch", "a name they can't place",
         "the shape of a cloud, or a crack in a wall", "what day it is", "a story someone told badly",
         "nothing at all, for a moment", "a rhyme that doesn't mean anything", "the back of someone's neck",
         "an errand for tomorrow", "a hat", "boiled vegetables", "the sound a door makes", "three, for no reason",
         "whether fish sleep", "a pair of shoes they used to own", "rain on a different roof", "the word 'parsley'"]
_BODY_SHAPE = {"Survival": "hunger", "Safety": "a door at their back", "Means": "money", "Comfort": "sleep"}


def _prose_words(text):
    words = [w.strip(".,;:!?\"'()[]").lower() for w in (text or "").split()]
    return [w for w in words if len(w) > 4 and w not in STOP]


def _draw_sources(n, ctx):
    src = []
    lv = ["t"]
    add = lambda text, w, seen=None: src.append((text, max(0.05, w), seen, lv[0]))
    lv[0] = "t"
    w = ctx.get("world") or {}
    for h in (w.get("history") or [])[-3:]:
        if "->" in h:
            add("how things have been changing", 0.6)
    dl = ctx.get("dials") or n.get("dials") or DEFAULT_DIALS
    if dial(dl, "V") >= 2: add("the killings lately", 0.4 * dial(dl, "V"))
    if dial(dl, "S") >= 2: add("whether there will be enough", 0.4 * dial(dl, "S"))
    if dial(dl, "F") >= 2: add("a prayer, half-remembered", 0.3 * dial(dl, "F"))
    if dial(dl, "X") >= 2: add("whether something they saw was real", 0.3 * dial(dl, "X"))
    lv[0] = "c"
    c = ctx.get("circle") or {}
    if (c.get("today") or {}).get("cause"):
        add(c["today"]["cause"], 1.0 + abs((c["today"] or {}).get("value", 0)))
    lv[0] = "m"
    for m in (n.get("memory") or [])[-12:]:
        age = max(1, n["day"] - m.get("day", 0))
        base = abs(EVENT_AFFECT.get(m["event"], (0, 2, ""))[1])
        add(m.get("note") or _EVENT_SHAPE.get(m["event"], m["event"]), base / (1 + age / 10.0))
    lv[0] = "r"
    for t in n.get("ties", []):
        add(t["label"], 0.3 * t["loyalty"])
    lv[0] = "w"
    dr = n.get("drive", {})
    if dr.get("rung"):
        add(dr["text"], 0.5 + 0.4 * deficit(n["needs"]["state"][dr["rung"]]))
    for cp in n.get("compulsions", []):
        add(cp["urge"], min(2.0, 0.4 + 0.5 * cp.get("pressure", 0)))
    for k, r in (n.get("inclinations") or {}).items():
        add(k.lower(), 1.0 * r["strength"])
    for code in n.get("codes", []):
        add(code["code"], 0.3)
    if n.get("core") and n["core"] != n["axes"]:
        add("how they used to be", 0.5)
    lv[0] = "q"
    for q in n.get("quirks", []):
        add(q, 0.3)
    lv[0] = "d"
    td = n.get("today") or {}
    if td.get("cause"):
        add(td["cause"], 1.0 + abs(td.get("value", 0)))
    f = (n.get("affect") or {}).get("feeling", 0)
    if abs(f) >= 3:
        add("a weight" if f < 0 else "a lightness", abs(f) / 3.0)
    lv[0] = "b"
    for r in RUNGS[:4]:
        if n["needs"]["state"][r] < 0:
            add(_BODY_SHAPE[r], 0.6 * deficit(n["needs"]["state"][r]), "their own body")
    lv[0] = "e"
    for who in ctx.get("present") or []:
        if who and who.lower() != n["name"].lower():
            add(who, 0.5 + 0.2 * abs(total_trust(n, who)), who)
    lv[0] = "p"
    pl = ctx.get("place") or {}
    for fx in pl.get("fixtures", []):
        add(fx["text"], 0.8, fx["text"])
    for mk in pl.get("marks", []):
        add(mk, 0.9, mk)
    lv[0] = "x"
    for cat in ctx.get("danger") or []:
        add(_DANGER_SHAPE.get(cat, cat), 1.5, _DANGER_SHAPE.get(cat, cat))
    lv[0] = "s"
    for wd in _prose_words(ctx.get("prose")):
        add(wd, 0.7, wd)
    lv[0] = "z"
    for drift in random.sample(DRIFT, 3):
        add(drift, 0.5)
    lv[0] = "n"
    for stray in random.sample(STRAY, 4):
        add(stray, 1.5)
    lv[0] = "f"
    rr = [r for r in RUNGS if r != dr.get("rung")]
    pool_ = DRIVES[random.choice(rr)][random.randint(0, 1)]
    add(fill(random.choice(pool_), n, None).replace("{tie}", "someone"), 0.45)
    return src


def _draw(n, ctx):
    src = _draw_sources(n, ctx)
    groups = {}
    for item in src:
        groups.setdefault(item[3], []).append(item)
    gw = {g: max(x[1] for x in items) * random.lognormvariate(0, 0.9) for g, items in groups.items()}
    g = max(gw, key=gw.get)
    items = groups[g]
    iw = [x[1] * random.lognormvariate(0, 0.6) for x in items]
    text, _, seen, _ = items[iw.index(max(iw))]
    perceivable = [x[2] for x in src if x[2]]
    if seen and random.random() < 0.6:
        guess = seen
    elif perceivable:
        guess = random.choice(perceivable)
    else:
        guess = None
    return text, guess, g


_LATERAL_STYLE = {"Visionary": 0.15, "Dramatic": 0.05, "Adventurous": 0.05, "Mercurial": 0.05, "Schemer": 0.04}
_META_STYLE = {"Visionary": 0.6, "Serious": 0.4, "Solitary": 0.4, "Conscientious": 0.3, "Self-Made": 0.3,
               "Benevolent": 0.2, "Zealot": -0.2, "Adventurous": -0.4, "Dramatic": -0.3, "Mercurial": -0.3,
               "Leisurely": -0.2, "Commanding": -0.1, "Predator": 0.2, "Professional": 0.1}
_META_PROC = {"Intellectual": 0.5, "Devotional": 0.3, "Contained": 0.2, "Caretaking": 0.0, "Action": -0.3,
              "Expressive": -0.3, "Numb": -0.2, "Bargaining": -0.4, "Performed": -1.0}
_META_CIRC = {"clear": 1.5, "solemn": 0.3, "intimate": 0.2, "hurt": -2.0, "frozen": -2.0, "afraid": -1.5,
              "enraged": -1.5, "stunned": -1.0, "intoxicated": -1.0, "exhausted": -0.7, "sick": -0.5,
              "grieving": -0.3, "festive": -0.3, "tending": -0.8, "protecting": -0.8}
HOLD = {0: "they don't notice having it", 1: "they notice it", 2: "they question it: why this, why now",
        3: "they see it as only a thought, and can set it down"}
HOLD_AGAIN = "they notice they keep coming back to it"


def _lateral_chance(n):
    a = n["axes"]
    p_ = 0.10 + 0.06 * a[O] + sum(_LATERAL_STYLE.get(v["style"], 0) * v["frac"] for v in n["voices"])
    if (n.get("afflictions") or {}).get("intoxicated"): p_ += 0.10
    if (n.get("affect") or {}).get("feeling", 0) >= 3: p_ += 0.05
    if (n.get("affect") or {}).get("clarity_days"): p_ += 0.05
    return clamp(p_, 0.02, 0.45)


def _meta_capacity(n, active):
    a = n["axes"]
    cap = 1.0 + 0.4 * a[O] + 0.3 * a[D] - 0.3 * max(0, a[V])
    cap += sum(_META_STYLE.get(v["style"], 0) * v["frac"] for v in n["voices"])
    cap += _META_PROC.get(processing(n), 0)
    cap += 1.5 * (n.get("inclinations") or {}).get("clarity", {}).get("strength", 0.0)
    cap += 0.2 * min(2, (n.get("affect") or {}).get("clarity_count", 0))
    cap += sum(_META_CIRC.get(c, 0) for c in active)
    return cap


def thought_hold(n, thought, active):
    """How this person holds this thought, now. Deterministic given the roll made when it arose."""
    u = thought[3] if len(thought) > 3 and thought[3] is not None else 0.5
    z = _meta_capacity(n, active) + (u - 0.5) * 2.0
    lvl = 0 if z < 1.0 else 1 if z < 2.0 else 2 if z < 3.0 else 3
    if lvl >= 2 and thought[2]:
        return lvl, HOLD_AGAIN
    return lvl, HOLD[lvl]


def arise_thought(n, pl=None, ctx=None, sealed=None):
    """Whether a thought arises, and what it is. Returns (thought, what they might blame it on) or None.
    The thought carries no trace of where it came from."""
    if random.uniform(0, 100) > THOUGHT_ARISE:
        return None
    ctx = dict(ctx or {})
    if pl is not None:
        ctx.setdefault("place", pl)
    text, guess, g = _draw(n, ctx)
    leap = None
    if random.random() < _lateral_chance(n):
        for _ in range(6):
            t2, g2_guess, g2 = _draw(n, ctx)
            if g2 != g and t2 != text:
                leap = (t2, g2)
                text = "%s, and somehow %s" % (text, t2)
                guess = guess or g2_guess
                break
    recent = n.setdefault("recent_thoughts", [])
    again = text in recent
    n["recent_thoughts"] = (recent + [text])[-6:]
    u = random.random()
    if sealed:
        with open(sealed, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"day": n["day"], "name": n["name"], "thought": text, "from": g,
                                 "joined_with": leap[1] if leap else None, "roll": round(u, 3)}) + "\n")
    return text, guess, again, u
# ====================================== END SEALED ======================================


def thought_ripple(n, active):
    """Whether and how an arisen thought shows. The thought is never theirs to steer; this is."""
    a = n["axes"]
    if {"frozen", "afraid"} & set(active):
        return "nothing shows"
    if "clear" in active:
        return "a pause; the eyes come back; it is let go"
    if ({"intoxicated", "exhausted", "hurt"} & set(active)) and a[D] <= 1:
        return "half a sentence of it said aloud, then caught"
    if "grieving" in active:
        return "a name, or a word, under the breath"
    if n["authenticity"]["kind"] == "Hollow" or a[D] >= 2:
        return "a hand stops for a moment, or nothing at all"
    if a[V] >= 2:
        return "it crosses the face: a flinch, or a smile at nothing"
    if a[E] >= 2:
        return "they mention it, out of nowhere"
    return "a glance at something, a pause mid-sentence"


# ---------- relationships and processing ----------
ROLES = ["child", "parent", "sibling", "spouse", "lover", "kin", "friend", "dependant", "student", "mentor",
         "spiritual", "master", "subordinate", "follower", "comrade", "rival", "enemy", "creditor", "debtor",
         "symbol", "pet"]
ROLE_OF_KIND = {"pet": "pet", "kin": "kin", "lover": "lover", "friend": "friend", "mentor": "mentor", "rival": "rival",
                "enemy": "enemy", "creditor": "creditor", "debtor": "debtor", "master": "master", "group": "comrade",
                "dependant": "dependant", "cause": "symbol", "object": "symbol", "place": "symbol"}


def rel_class(role, loyalty):
    """What a relationship is to the one feeling it."""
    if role in ("child", "parent", "sibling", "spouse", "lover", "dependant"):
        return "beloved"
    if role in ("kin", "friend"):
        return "beloved" if loyalty >= 4 else "familiar"
    if role in ("student", "subordinate", "follower"):
        return "charge" if loyalty >= 3 else "familiar"
    if role in ("mentor", "spiritual"):
        return "revered"
    if role == "master":
        return "authority"
    if role in ("comrade", "creditor", "debtor"):
        return "familiar"
    if role in ("rival", "enemy"):
        return role
    if role == "symbol":
        return "conceptual"
    if role == "pet":
        return "charge" if loyalty >= 3 else "familiar"
    return "stranger"


def relation_to(n, name, circle_members=()):
    """(class, role, loyalty) of n toward the named person or thing, from n's own ties."""
    if not name:
        return ("stranger", None, 0)
    low = name.lower()
    for t in n["ties"]:
        if (t.get("who") or "").lower() == low:
            role = t.get("role") or ROLE_OF_KIND.get(t["kind"], "comrade")
            return (rel_class(role, t["loyalty"]), role, t["loyalty"])
    kin = kin_of(n, name)
    if kin:
        return (rel_class(kin[0], kin[1]), kin[0], kin[1])
    if low in [m.lower() for m in circle_members] and n["name"] in circle_members:
        return ("familiar", "comrade", 2)
    return ("stranger", None, 0)


def processing(n):
    """How this person processes what happens to them. Worked out from traits, not rolled."""
    a = n["axes"]
    if n["authenticity"]["kind"] == "Hollow":
        return "Performed"
    if a[V] >= 2 and a[E] <= -1: return "Numb"
    if a[V] >= 2: return "Expressive"
    dom = n["voices"][0]["style"]
    if (n["creed"] == "Faith" or dom in ("Zealot", "Devoted")) and a[V] <= 1: return "Devotional"
    if a[M] >= 2: return "Action"
    if a[D] >= 2: return "Contained"
    if a[W] >= 2: return "Caretaking"
    if a[O] >= 2: return "Intellectual"
    if a[C] <= -1: return "Bargaining"
    return "Contained"


PROCESSING = {  # how grief and shock show, by processing style: (colour, colour tags)
 "Expressive": ("weeps or rages openly, then apologises for it", {"display", "action"}),
 "Numb": ("goes about the day as if nothing has happened", {"plain"}),
 "Devotional": ("keeps vigil; the old words, the old motions", {"formal"}),
 "Action": ("busies themself with arrangements, or with who did it", {"action"}),
 "Contained": ("keeps working; won't stop working", {"plain"}),
 "Caretaking": ("looks after everyone else", {"warm"}),
 "Intellectual": ("talks about it in facts and dates", {"cold"}),
 "Bargaining": ("talks as if it can still be undone", {"guarded"}),
 "Performed": ("says the right things, a beat late", {"plain"}),
}
GRIEF_DAYS = {"child": (21, 14), "spouse": (14, 14), "lover": (14, 14), "parent": (10, 10), "sibling": (10, 10),
              "dependant": (10, 10), "kin": (7, 7), "friend": (7, 7), "mentor": (7, 7), "spiritual": (10, 10),
              "student": (5, 5), "subordinate": (3, 4), "follower": (3, 4), "comrade": (2, 3), "master": (3, 4),
              "rival": (1, 3), "creditor": (0, 2), "debtor": (0, 2), "symbol": (7, 7),
              "pet": (4, 7)}


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
DISSONANCE = [  # fallback only: a place sheet is the real source
 "a radio, record or street musician keeps playing the same cheerful tune",
 "someone at the next table finishes their meal", "a child laughs somewhere out of sight",
 "the weather is beautiful: clean light, a soft wind", "a bird lands nearby and goes about its business",
 "a hymn, chant or ritual next door carries on without missing a word",
 "the one who did it apologises for the mess, sincerely",
 "someone straightens a picture or a tablecloth that got knocked",
 "the price of something is mentioned, as if it matters now", "an animal comes to sniff at the blood",
 "a pot boils over in the kitchen and no one moves it", "a clock or bell marks the hour",
 "a celebration nearby: music, toasts, dancing, going on", "the wounded one apologises to someone",
 "a joke is finished, out of habit, and someone laughs at it", "a dropped coin rolls in a long circle and settles",
 "the light on the wall is lovely", "someone keeps counting money, losing their place, starting again",
 "someone hums a lullaby without knowing they are doing it", "a kettle starts to whistle",
]
PLACE_KINDS = {  # how a place's own fixtures turn dissonant (no verbs that must agree with the noun)
 "sound": ["{x}, going on exactly on time", "{x}, not stopping"],
 "light": ["{x}, lovely", "{x}, falling across all of it the same"],
 "animal": ["{x}, going about their business", "{x}, coming to look, then losing interest"],
 "routine": ["{x}, happening anyway, on schedule", "someone starting on {x} out of habit"],
 "object": ["{x}, untouched", "someone straightening {x}"],
 "smell": ["{x}, still in the air", "{x}, cutting through everything"],
 "taste": ["{x}, still on the tongue", "{x} in the mouth, under everything"],
 "person": ["{x}, keeping at what they were doing", "{x}, looking up, then back down"],
 "weather": ["{x}, going on outside", "{x}, not caring"],
 "mark": ["{x}, still", "{x}, and nobody mentioning it"],
}
AFTERMATH = [  # (what happens now, what the place keeps)
 ("the blood goes dark and dull faster than expected", "a stain that won't scrub out"),
 ("flies arrive", "a smell that comes back in warm weather"),
 ("someone fetches a bucket and a brush", "flagstones scrubbed paler than the rest"),
 ("the smell stays in clothes and hair", "a smell no one mentions"),
 ("the room is too quiet; small sounds are very loud", "a quiet that settles there at that hour"),
 ("a shoe has come off and no one puts it back", "a shoe no one will move"),
 ("the furniture is moved back, almost to where it was", "a chair standing a little out of place"),
 ("people speak about something else entirely", "a subject no one raises there"),
 ("someone is sick, quietly, outside", "a corner people avoid"),
 ("the meal goes cold on the table", "a place at table no one sits in"),
 ("a door that was always open is now kept shut", "a door that stays shut"),
 ("nobody sits in that chair again that day", "a chair nobody uses"),
]
RESP = {  # response: (circumstance it puts them in, or None when outwardly unchanged; description; colour tags)
 "Wounded-Selfless": ("hurt", "asks after someone else before themself", {"wounded"}),
 "Wounded-Panic": ("hurt", "pleads, bargains, calls for someone; breath and words break", {"wounded"}),
 "Wounded-Stoic": ("hurt", "quiet, practical about their own wound; asks for cloth, water, light", {"wounded"}),
 "Wounded-Shock": ("hurt", "looks at the wound as if it belongs to someone else; says something ordinary", {"wounded"}),
 "Wounded-Betrayed": ("hurt", "looks at the one who did it; asks why", {"wounded"}),
 "Frantic": ("tending", "frantic hands; says their name over and over", {"action", "display"}),
 "Tending": ("tending", "goes to the wounded regardless of the danger; hands busy, voice low", {"warm"}),
 "Clinical": ("tending", "presses, counts, gives short orders; the voice flat", {"plain"}),
 "Vigil": ("tending", "kneels by them and keeps the old words", {"formal"}),
 "Shield": ("protecting", "puts their body between them and harm; faces the one who did it", {"action"}),
 "Covering": ("protecting", "steps between the one who did it and everyone else", {"action"}),
 "Fury": ("enraged", "loud, forward, wants to hit back now; may break something", {"action", "display"}),
 "Freeze": ("frozen", "does not move; holds whatever they were holding", {"guarded"}),
 "Torn": ("frozen", "looks from one of them to the other", {"guarded"}),
 "Flight": ("afraid", "leaves, fast, by the nearest way; may come back later or not at all", {"action"}),
 "Shock": ("stunned", "keeps doing the ordinary thing a moment too long, then stops", {"plain"}),
 "Denial": ("stunned", "tells them to get up, that it's nothing", {"guarded"}),
 "Conflicted": ("stunned", "starts forward, stops", {"guarded"}),
 "Ritual": ("solemn", "set words, prayer or rite; the body does the old motions", {"formal"}),
 "Obeys": ("superior", "does what they're told; doesn't look at the body", {"formal"}),
 "Business": (None, "calm, takes charge; courteous, soft words for hard things", {"formal"}),
 "Curiosity": (None, "calm interest; studies what happened, may remark on it plainly", {"cold"}),
 "Spectator": (None, "watches, says nothing, misses nothing", {"guarded"}),
 "Satisfied": (None, "watches to the end; doesn't move to help", {"cold"}),
 "Performed": (None, "the right gestures, a beat late", {"plain"}),
 # the one who did it
 "Cold": (None, "calm afterwards; wipes the blade or checks the gun; already thinking of the next thing", {"cold"}),
 "Shaking": ("stunned", "hands start shaking only after; can't quite let go of what they used", {"plain"}),
 "Justified": (None, "sure they were right; says so, or doesn't need to", {"formal"}),
 "Regret": ("stunned", "looks at what they did; reaches toward it, or away", {"guarded"}),
 "Set": (None, "jaw set; says nothing; doesn't look away", {"guarded"}),
}
RESPONSES = {k: v[1] for k, v in RESP.items()}
SHAKEN_TO = {k: v[0] for k, v in RESP.items() if v[0] and v[0] != "hurt"}
STEADY = tuple(k for k, v in RESP.items() if v[0] is None)
CLOSE = ("beloved", "revered", "charge", "conceptual")
BY_PROC = {
 "beloved": {"Expressive": "Frantic", "Contained": "Tending", "Numb": "Freeze", "Action": "Shield",
             "Devotional": "Vigil", "Intellectual": "Clinical", "Bargaining": "Denial", "Caretaking": "Tending"},
 "revered": {"Expressive": "Frantic", "Contained": "Tending", "Numb": "Freeze", "Action": "Shield",
             "Devotional": "Vigil", "Intellectual": "Clinical", "Bargaining": "Denial", "Caretaking": "Tending"},
 "charge": {"Expressive": "Frantic", "Contained": "Tending", "Numb": "Freeze", "Action": "Shield",
            "Devotional": "Tending", "Intellectual": "Clinical", "Bargaining": "Tending", "Caretaking": "Tending"},
 "conceptual": {"Expressive": "Fury", "Contained": "Shock", "Numb": "Freeze", "Action": "Fury",
                "Devotional": "Ritual", "Intellectual": "Shock", "Bargaining": "Denial", "Caretaking": "Shock"},
}


def attacker_response(n, vcls):
    """How the one who did it comes across afterwards, from their nature and who they hurt."""
    a = n["axes"]
    styles = {v["style"]: v["frac"] for v in n["voices"]}
    if processing(n) == "Performed" or styles.get("Predator", 0) >= 0.25 or (a[W] <= -2 and a[V] <= -1):
        return "Cold"
    if vcls in CLOSE and a[W] >= 0:
        return "Regret"
    if a[V] >= 2:
        return "Shaking"
    if n["creed"] in ("Justice", "Order", "Faith", "Strength") or styles.get("Zealot", 0) >= 0.25:
        return "Justified"
    if a[W] >= 2:
        return "Regret"
    if styles.get("Professional", 0) + styles.get("Commanding", 0) + styles.get("Schemer", 0) >= 0.5:
        return "Cold"
    return "Set"


def violence_response(n, hurt, vcls="stranger", acls="stranger", symbol=None):
    """Response to violence, from who was hurt, who did it, how this person processes, and their nature."""
    a = n["axes"]
    styles = {v["style"]: v["frac"] for v in n["voices"]}
    dom = n["voices"][0]["style"]
    proc = processing(n)
    if hurt:
        if acls in ("beloved", "revered", "charge"): return "Wounded-Betrayed"
        if a[W] >= 2: return "Wounded-Selfless"
        if a[V] >= 2: return "Wounded-Panic"
        if a[V] <= -2: return "Wounded-Stoic"
        return "Wounded-Shock"
    if proc == "Performed":
        return "Performed"
    if symbol and symbol == n["creed"] and vcls == "stranger":
        vcls = "conceptual"
    if acls in CLOSE and vcls not in CLOSE:
        return "Covering" if (proc in ("Action", "Contained", "Intellectual") or a[M] >= 1) else "Torn"
    if vcls in CLOSE and acls in CLOSE:
        return "Torn"
    if acls == "authority" and vcls not in CLOSE and (a[D] >= 1 or a[M] <= -1 or n["station"] == "Sworn"):
        return "Obeys"
    if vcls in BY_PROC:
        return BY_PROC[vcls][proc]
    if vcls == "authority":
        if n["station"] == "Sworn" or a[D] >= 2 or dom == "Devoted": return "Shield"
        if dom in ("Professional", "Commanding", "Schemer"): return "Business"
    if vcls == "rival":
        if a[W] >= 2: return "Tending"
        if styles.get("Predator", 0) >= 0.25: return "Curiosity"
        return "Conflicted"
    if vcls == "enemy":
        if a[W] >= 2 or n["creed"] == "Mercy": return "Tending"
        if a[C] <= -1 or a[W] <= -2: return "Satisfied"
        return "Spectator"
    if vcls == "familiar" and a[W] >= 1 and a[V] <= 1:
        return "Tending"
    # a stranger: nature and creed decide
    if styles.get("Predator", 0) >= 0.25 or (a[W] <= -3 and a[V] <= -2): return "Curiosity"
    if dom in ("Professional", "Commanding", "Schemer") or (a[D] >= 2 and a[V] <= -1): return "Business"
    if (a[W] >= 2 or n["creed"] == "Mercy") and a[V] <= 1: return "Tending"
    if n["creed"] == "Justice" and a[V] >= 2 and a[M] >= 1: return "Fury"
    if (n["creed"] == "Faith" or dom in ("Zealot", "Devoted")) and a[E] <= 0 and a[V] <= 1: return "Ritual"
    if n["creed"] in ("Strength", "Thrill") and a[V] <= 0: return "Curiosity"
    if a[V] >= 2 and a[M] >= 1: return "Fury"
    if a[V] >= 2: return "Freeze" if a[E] <= -1 else "Flight"
    if n["creed"] == "Security" and a[V] >= 1: return "Flight"
    if a[E] <= -2: return "Spectator"
    return "Shock"


def violence_steady(n, resp, dials, vcls="stranger"):
    """True when violence doesn't change how they come across: it is already who they are.
    Never true when someone close to them is involved, except for the hollow."""
    if resp in ("Performed", "Cold", "Justified", "Set"):
        return True
    if vcls in CLOSE:
        return False
    if resp in STEADY:
        return True
    return dial(dials, "V") >= 3 and n["axes"][V] <= 0 and resp in ("Shock", "Spectator")


def place_dissonance(pl, k):
    """Draw k dissonant beats from the place's own fixtures, least-used first."""
    fx = pl.get("fixtures", []) + [{"kind": "mark", "text": m} for m in pl.get("marks", [])]
    used = pl.setdefault("used", {})
    if not fx:
        return []
    order = sorted(fx, key=lambda f: (used.get(f["text"], 0), random.random()))
    out = []
    for f in order[:k]:
        tpl = random.choice(PLACE_KINDS.get(f["kind"], ["{x}"]))
        txt = tpl.replace("{x}", f["text"])
        out.append(txt[0].upper() + txt[1:])
        used[f["text"]] = used.get(f["text"], 0) + 1
    return out


def cmd_violence(a):
    pairs = [(p, load(p)) for p in a.files]
    gone = [n["name"] for _, n in pairs if n["condition"] in ("dead", "comatose")]
    pairs = [(p, n) for p, n in pairs if n["condition"] not in ("dead", "comatose")]
    if gone:
        print("Not responding: %s (dead or comatose)" % ", ".join(gone))
    a.files = [p for p, _ in pairs]
    ns = [n for _, n in pairs]
    pl = load(a.place) if a.place else None
    dials = parse_dials(a.dials) if a.dials else (load(a.world)["dials"] if a.world else
                                                  (pl["dials"] if pl and pl.get("dials") else
                                                   (ns[0]["dials"] if ns else list(DEFAULT_DIALS))))
    v, o = dial(dials, "V"), dial(dials, "O")
    reg = "Weather" if v >= 3 else "Trade" if (v == 2 or (o >= 2 and dial(dials, "D") >= 2)) else "Rupture"
    print("[narrator only] Register: %s. %s" % (reg, REGISTERS[reg]))
    VIEW.clear()
    VIEW.update({"cmd": "violence", "register": reg, "dissonance": [], "aftermath": None, "keeps": None,
                 "responses": [], "absent": list(gone)})
    k = 2 if reg != "Rupture" else 1 + (d(2) == 2)
    beats = place_dissonance(pl, k) if pl else []
    if len(beats) < k:
        if pl is not None:
            print("(The place sheet is thin; add what is always there with `place --add`.)")
        beats += random.sample(DISSONANCE, k - len(beats))
    for beat in beats:
        VIEW["dissonance"].append(beat)
        print("Dissonance: " + beat)
    now, keeps = random.choice(AFTERMATH)
    print("Aftermath: " + now)
    VIEW["aftermath"] = now
    if pl is not None:
        if keeps not in pl.setdefault("marks", []):
            pl["marks"].append(keeps)
        pl.setdefault("history", []).append(now)
        save(pl, a.place)
        print("The place keeps: " + keeps)
        VIEW["keeps"] = keeps
    hurt = set(x.lower() for x in (a.hurt or []))
    members = load(a.circle).get("members", []) if a.circle else []
    for path, n in zip(a.files, ns):
        vc = relation_to(n, a.victim, members)
        ac = relation_to(n, a.attacker, members)
        did_it = bool(a.attacker) and a.attacker.lower() == n["name"].lower()
        if did_it and n["name"].lower() not in hurt:
            r = attacker_response(n, vc[0])
        else:
            r = violence_response(n, n["name"].lower() in hurt, vc[0], ac[0], a.symbol)
        st = violence_steady(n, r, dials, vc[0])
        rel = []
        if a.victim and vc[0] != "stranger": rel.append("%s is their %s" % (a.victim, vc[1]))
        if a.attacker and ac[0] != "stranger": rel.append("%s is their %s" % (a.attacker, ac[1]))
        if a.symbol and a.symbol == n["creed"]: rel.append("it strikes at what they hold highest")
        if a.record and n["name"].lower() not in hurt and not did_it:
            n["memory"].append({"day": n["day"], "event": "witnessed", "with": a.attacker or "",
                                "note": "%s hurt" % (a.victim or "someone")})
            fx = apply_affect(n, "witnessed", vc[0], EVENTS["witnessed"][2])
            save(n, path)
        VIEW["responses"].append({"name": n["name"], "response": r, "desc": RESPONSES[r], "steady": st,
                                  "relations": rel})
        print("%s (%s%s): %s - %s%s" % (n["name"], processing(n), "; " + "; ".join(rel) if rel else "", r,
                                        RESPONSES[r], " | outwardly unchanged: this is already who they are" if st
                                        else " | outward manner changes for the rest of the day"))
    print("Show all of it from outside. Name no one's feelings; let the dissonance sit unexplained.")


def cmd_place(a):
    import os
    pl = load(a.file) if os.path.exists(a.file) else {"name": a.name or a.file, "dials": parse_dials(a.dials),
                                                       "fixtures": [], "marks": [], "used": {}, "history": []}
    if a.dials:
        pl["dials"] = parse_dials(a.dials)
    for item in a.add or []:
        kind, _, text = item.partition(":")
        kind = kind.strip().lower()
        if kind not in PLACE_KINDS or not text.strip():
            sys.exit("--add takes kind:text, kind one of " + ", ".join(k for k in PLACE_KINDS if k != "mark"))
        pl["fixtures"].append({"kind": kind, "text": text.strip()})
    save(pl, a.file)
    print("%s | dials %s" % (pl["name"], ",".join(map(str, pl["dials"]))))
    for f in pl["fixtures"]:
        print("  always there (%s): %s" % (f["kind"], f["text"]))
    for m in pl.get("marks", []):
        print("  since then: " + m)


def cmd_tie(a):
    n = load(a.file)
    if not a.to.strip():
        sys.exit("Name who or what the tie is to.")
    if a.to.strip().lower() == n["name"].lower():
        sys.exit("A tie needs someone or something other than themself.")
    t = next((t for t in n["ties"] if (t.get("who") or "").lower() == a.to.lower()), None)
    if t is None and a.relabel:
        t = next((t for t in n["ties"] if t["label"] == a.relabel), None)
    if t is None:
        t = {"kind": "kin", "label": a.to, "loyalty": 3, "reach": 3}
        n["ties"].append(t)
    t["who"], t["role"], t["label"] = a.to, a.role, a.to
    t["kind"] = {"child": "kin", "parent": "kin", "sibling": "kin", "spouse": "lover", "student": "dependant",
                 "subordinate": "dependant", "follower": "dependant", "spiritual": "mentor", "comrade": "group",
                 "symbol": "cause", "pet": "pet"}.get(a.role, a.role if a.role in TIE_KINDS else "friend")
    if a.loyalty: t["loyalty"] = a.loyalty
    if a.reach: t["reach"] = a.reach
    save(n, a.file)
    print("%s: %s is their %s (loyalty %d, reach %d) -> %s" % (n["name"], a.to, a.role, t["loyalty"], t["reach"],
                                                              rel_class(a.role, t["loyalty"])))


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
    x.add_argument("--victim"); x.add_argument("--attacker"); x.add_argument("--symbol", choices=CREEDS)
    x.add_argument("--circle")
    for fl in ("solemn", "festive", "superior", "duty", "drunk", "tired", "sick", "grieving", "private"):
        x.add_argument("--" + fl, action="store_true")
    x.add_argument("--their-strength", type=int, default=2); x.add_argument("--ground", type=int, default=0)
    x.add_argument("--dry-run", action="store_true", help="look without recording that they showed it")
    x.add_argument("--taste", help="something in the scene that may touch one of their likes or dislikes")
    x.add_argument("--spirit", choices=["shared", "scorned"], help="the other party shares or scorns what they hold about the unseen")
    x.set_defaults(f=cmd_meet)
    x = sp.add_parser("ask"); x.add_argument("file"); x.add_argument("--who", default="player")
    x.add_argument("--touched", action="store_true"); x.add_argument("--asked", action="store_true")
    x.set_defaults(f=cmd_ask)
    x = sp.add_parser("event"); x.add_argument("file"); x.add_argument("kind", choices=list(EVENTS))
    x.add_argument("--who", default="player"); x.add_argument("--size", type=int, choices=[1, 2])
    x.add_argument("--trade", action="store_true"); x.add_argument("--note")
    x.add_argument("--about", help="who or what the event concerns, as named in their ties (for loss)")
    x.set_defaults(f=cmd_event)
    x = sp.add_parser("affinity"); x.add_argument("a"); x.add_argument("b")
    x.add_argument("--tie", choices=["kin", "lover", "friend", "mentor", "rival", "enemy", "creditor", "debtor",
                                     "master", "dependant"]); x.set_defaults(f=cmd_affinity)
    x = sp.add_parser("scene"); x.add_argument("files", nargs="+"); x.add_argument("--world")
    x.add_argument("--place"); x.add_argument("--circle"); x.add_argument("--present", nargs="*")
    x.add_argument("--danger", nargs="*", choices=DANGER)
    x.add_argument("--prose", help="the narration so far this scene")
    x.add_argument("--seal", help="a sealed record for the people at the table; the narrator never reads it")
    x.set_defaults(f=cmd_scene)
    x = sp.add_parser("status"); x.add_argument("file")
    x.add_argument("condition", choices=["present", "dead", "comatose", "amnesiac"])
    x.add_argument("--restore", action="store_true"); x.set_defaults(f=cmd_status)
    x = sp.add_parser("violence"); x.add_argument("files", nargs="*"); x.add_argument("--world")
    x.add_argument("--dials"); x.add_argument("--hurt", nargs="*"); x.add_argument("--place")
    x.add_argument("--victim"); x.add_argument("--attacker"); x.add_argument("--symbol", choices=CREEDS)
    x.add_argument("--circle"); x.add_argument("--record", action="store_true",
                                               help="write what each witness felt into their ledger")
    x.set_defaults(f=cmd_violence)
    x = sp.add_parser("place"); x.add_argument("file"); x.add_argument("--name"); x.add_argument("--dials")
    x.add_argument("--add", nargs="*"); x.set_defaults(f=cmd_place)
    x = sp.add_parser("tie"); x.add_argument("file"); x.add_argument("--to", required=True)
    x.add_argument("--role", required=True, choices=ROLES); x.add_argument("--loyalty", type=int, choices=range(1, 7))
    x.add_argument("--reach", type=int, choices=range(1, 7)); x.add_argument("--relabel")
    x.set_defaults(f=cmd_tie)
    x = sp.add_parser("tide"); x.add_argument("world"); x.add_argument("--dials"); x.set_defaults(f=cmd_tide)
    x = sp.add_parser("audit"); x.add_argument("--life", action="store_true", help="only family, tastes, pets and outlook")
    x.set_defaults(f=cmd_audit)
    x = sp.add_parser("learn"); x.add_argument("file"); x.add_argument("--subject", required=True)
    x.add_argument("--claim", required=True); x.add_argument("--source", required=True, choices=list(SOURCE_BASE))
    x.add_argument("--from", dest="source_name"); x.add_argument("--reliability", type=float); x.add_argument("--fact")
    x.add_argument("--secret", action="store_true"); x.add_argument("--stressed", action="store_true")
    x.set_defaults(f=cmd_learn)
    x = sp.add_parser("tell"); x.add_argument("teller"); x.add_argument("hearer"); x.add_argument("--about", required=True)
    x.set_defaults(f=cmd_tell)
    x = sp.add_parser("beliefs"); x.add_argument("file"); x.add_argument("--about"); x.set_defaults(f=cmd_beliefs)
    x = sp.add_parser("habit"); x.add_argument("file"); x.add_argument("act")
    x.add_argument("--times", type=int, default=1); x.set_defaults(f=cmd_habit)
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
