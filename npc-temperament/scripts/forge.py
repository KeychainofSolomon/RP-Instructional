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
 "reunion": (1, 1, [(W, 1), (E, 1)], {"Belonging": 2}),
 "joy": (0, 0, [(E, 1), (O, 1)], {"Comfort": 1}),
 "witnessed": (0, 0, [(V, 1)], {"Safety": -1}),
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
    about_you = trust + ap + creed + social + cont + dang
    feel = clamp(int(round((n.get("affect") or {}).get("feeling", 0) / 2)), -3, 3)
    about_them = td["mood"] + chronic(n) + feel
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
    habit_note = None
    hf = habit_form(n, key, active)
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
                               infl[-1] in [x[0] for x in SIDE_TEXT[n["contradiction"]["pair"]]]) else None
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
    tint = {"Cool": "colder ", "Warm": "warmer "}.get(band, "")
    print("[narrator only] %s toward %s" % (n["name"], a.who))
    print("Mood %+d = baseline %+d, their day %+d (%s), chronic %+d, feeling %+d, trust %+d, approach %+d, "
          "creed %+d, social %+d, contagion %+d, danger %+d%s" % (mood, dv["baseline"], td["mood"], td["cause"],
                                                                 chronic(n), feel, trust, ap, creed, social, cont,
                                                                 dang, capped))
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
        th = td["thought"] if isinstance(td["thought"], list) else [td["thought"], None]
        print("Unbidden thought (seed: %s): %s. Never name the thought; show only this, or the words they "
              "let slip. They don't know where it came from%s." % (th[0], thought_ripple(n, active),
              "; if they wonder aloud, they may blame " + th[1] if th[1] else ""))
    if form in FORM_TAGS and not form.startswith("Wounded") and not a.dry_run:
        axes_ = [ax for tg in FORM_TAGS[form] for ax in TAG_AXES.get(tg, [])]
        for note in incline(n, form, axes_):
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
        th = arise_thought(nn, {"fixtures": [{"kind": "smell", "text": "woodsmoke"}], "marks": ["a stain"]},
                           {"present": ["Bram", nn["name"]], "danger": ["violence"], "prose": "The kettle whistled.",
                            "dials": [3, 1, 3, 3, 3, 1, 1], "circle": {"today": {"cause": "a lean week", "value": -1}}})
        if th:
            arisen += 1
            seeds_seen.add(th[0].split(":")[0])
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
            base, spread = GRIEF_DAYS.get(role or "kin", (7, 7))
            days = base + (d(spread) if spread else 0)
            if role in ("mentor", "spiritual", "symbol"):
                st["Meaning"] = clamp(st["Meaning"] - 2, -2, 1)
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
    n["memory"].append({"day": n["day"], "event": a.kind, "with": a.who, "note": a.note or ""})
    derive(n)
    save(n, a.file)
    print("Recorded %s%s. " % (a.kind, " with " + a.who if a.who else "") + "; ".join(notes))


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
    print("Regard %s <-> %s: %+d (%s)" % (x["name"], y["name"], total,
                                          ", ".join("%s %+d" % p for p in parts)))
    print("Use it as trust between them; each still reacts through their own mood and manner.")


def cmd_scene(a):
    pairs = [(p, load(p)) for p in a.files]
    gone = [n["name"] for _, n in pairs if n["condition"] in ("dead", "comatose")]
    pairs = [(p, n) for p, n in pairs if n["condition"] not in ("dead", "comatose")]
    if gone:
        print("Not taking part: %s (dead or comatose)" % ", ".join(gone))
    if not pairs:
        sys.exit("No one present can take part.")
    a.files = [p for p, _ in pairs]
    ns = [n for _, n in pairs]
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
    pl = load(a.place) if getattr(a, "place", None) else None
    ctx = {"world": load(a.world) if a.world else None, "dials": dials, "place": pl,
           "circle": load(a.circle) if getattr(a, "circle", None) else None,
           "present": [m["name"] for m in ns] + (a.present or []), "danger": a.danger or [],
           "prose": a.prose or ""}
    for path, n in zip(a.files, ns):
        th = arise_thought(n, pl, ctx)
        if n.get("today") is not None:
            n["today"]["thought"] = list(th) if th else None
            save(n, path)
        if th:
            print("A thought arises in %s. Seed: %s. They don't know where it came from%s."
                  % (n["name"], th[0], "; if they wonder, they may put it down to " + th[1] if th[1] else ""))
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
    af["feeling"] = round(af["feeling"] * 0.5, 2) if abs(af["feeling"]) >= 0.5 else 0.0
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
        af["habit"][k] = round(max(0.0, af["habit"][k] - 0.02), 3)
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


def incline(n, key, axes=None, times=1):
    """Someone did or showed `key` again. Returns notes."""
    inc = n.setdefault("inclinations", {})
    rec = inc.setdefault(key, {"strength": 0.0, "count": 0, "last": n["day"]})
    notes = []
    before = rec["strength"]
    for _ in range(times):
        rec["strength"] = round(rec["strength"] + INCLINE_GAIN * (1 - rec["strength"]), 4)
        rec["count"] += 1
        for axis, sgn in (axes or []):
            affect(n)["pressure"][axis] += sgn * INCLINE_PRESS
    rec["last"] = n["day"]
    if before < 0.5 <= rec["strength"]:
        notes.append("%s has become a habit: it fills the gaps when nothing else decides" % key)
    same = [c for c in n["compulsions"] if c["urge"].lower() == key.lower() or c.get("from_habit") == key]
    if rec["strength"] >= 0.7 and not same:
        n["compulsions"].append({"urge": key, "control": 9, "threshold": 3, "pressure": 0, "from_habit": key})
        notes.append("%s has become a compulsion (control 9)" % key)
    elif rec["strength"] >= 0.7 and same and not same[0].get("fed_by_habit"):
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


# ---------- unbidden thoughts: they arise; they are not chosen; only their ripple shows ----------
THOUGHT_ARISE = 25   # percent per person per scene
DRIFT = ["a tune from long ago", "a street they lived on as a child", "a sum that doesn't come out",
         "the face of a stranger from years back", "a word in a language they barely know",
         "what there is to eat tonight", "a smell from somewhere else entirely", "a door they forgot to lock",
         "someone's laugh", "the weather on a day that doesn't matter", "a promise they half remember",
         "the colour of a room they were once in", "a joke they never told", "an animal they once had"]


STOP = set("the a an and or but of to in on at for with from by as is was were be been it its this that "
           "they them their there here have has had not no you your he she his her him we our us i me my "
           "into onto over under then than so if when what which who whom whose just very more most".split())


def _prose_words(text):
    words = [w.strip(".,;:!?\"'()[]").lower() for w in (text or "").split()]
    return [w for w in words if len(w) > 4 and w not in STOP]


def _thought_sources(n, ctx):
    """Everything a thought could rise from, at every level, with a salience each. Hidden from the
    character, who doesn't know any of this exists."""
    src = []
    level = ["times"]
    add = lambda text, w, seen=None: src.append((text, max(0.05, w), seen, level[0]))
    # the times
    level[0] = 'times'
    w = ctx.get("world") or {}
    for h in (w.get("history") or [])[-3:]:
        if "->" in h:
            add("how things have been changing lately", 0.6)
    dl = ctx.get("dials") or n.get("dials") or DEFAULT_DIALS
    if dial(dl, "V") >= 2: add("the killings lately", 0.4 * dial(dl, "V"))
    if dial(dl, "S") >= 2: add("whether there will be enough", 0.4 * dial(dl, "S"))
    if dial(dl, "F") >= 2: add("a prayer, half-remembered", 0.3 * dial(dl, "F"))
    if dial(dl, "X") >= 2: add("whether something they saw was real", 0.3 * dial(dl, "X"))
    # the circle
    level[0] = 'circle'
    c = ctx.get("circle") or {}
    if (c.get("today") or {}).get("cause"):
        add("their people: %s" % c["today"]["cause"], 1.0 + abs((c["today"] or {}).get("value", 0)))
    # the person
    level[0] = 'memory'
    for m in (n.get("memory") or [])[-12:]:
        age = max(1, n["day"] - m.get("day", 0))
        base = abs(EVENT_AFFECT.get(m["event"], (0, 2, ""))[1])
        add("a memory: %s%s" % (m["event"], (" (" + m["note"] + ")") if m.get("note") else ""), base / (1 + age / 10.0))
    level[0] = 'ties'
    for t in n.get("ties", []):
        add("someone or something of theirs: %s" % t["label"], 0.3 * t["loyalty"])
    level[0] = 'wants'
    dr = n.get("drive", {})
    if dr.get("rung"):
        st = n["needs"]["state"][dr["rung"]]
        add("what they want: %s" % dr["text"], 0.8 + 0.8 * deficit(st))
    for cp in n.get("compulsions", []):
        add("the pull of %s" % cp["urge"], 0.5 + cp.get("pressure", 0))
    for k, r in (n.get("inclinations") or {}).items():
        add("the habit of %s" % k.lower(), 1.5 * r["strength"])
    for code in n.get("codes", []):
        add("a line they don't cross: %s" % code["code"], 0.3)
    for i in range(7):
        if n.get("core") and n["core"][i] != n["axes"][i]:
            add("who they used to be", 0.8)
            break
    level[0] = 'small things'
    for q in n.get("quirks", []):
        add("something small and theirs: %s" % q, 0.3)
    # the day
    level[0] = 'day'
    td = n.get("today") or {}
    if td.get("cause"):
        add("today: %s" % td["cause"], 1.0 + abs(td.get("value", 0)))
    f = (n.get("affect") or {}).get("feeling", 0)
    if abs(f) >= 3:
        add("a weight they can't put down" if f < 0 else "a lightness they can't account for", abs(f) / 3.0)
    level[0] = 'body'
    for r in RUNGS[:4]:
        if n["needs"]["state"][r] < 0:
            add("the body: %s" % r.lower(), 0.6 * deficit(n["needs"]["state"][r]), "their own body")
    # the encounter
    level[0] = 'encounter'
    for who in ctx.get("present") or []:
        if who and who.lower() != n["name"].lower():
            tr = total_trust(n, who)
            add("%s, there in the room" % who, 0.5 + 0.2 * abs(tr), who)
    # the moment and the place
    level[0] = 'place'
    pl = ctx.get("place") or {}
    for fx in pl.get("fixtures", []):
        add("the place: %s" % fx["text"], 0.8, fx["text"])
    for mk in pl.get("marks", []):
        add("the place: %s" % mk, 0.9, mk)
    level[0] = 'danger'
    for cat in ctx.get("danger") or []:
        add("the danger in the room (%s)" % cat, 1.5, cat)
    # the prose
    level[0] = 'prose'
    for wd in _prose_words(ctx.get("prose")):
        add("a word in the air: %s" % wd, 0.7, wd)
    # nothing at all
    level[0] = 'drift'
    for drift in random.sample(DRIFT, 3):
        add("nothing to do with anything: %s" % drift, 0.5)
    return src


def arise_thought(n, pl=None, ctx=None):
    """The box: whether a thought arises, and from where. Unpredictable by design: every salience is
    scrambled before the draw. Returns (seed, what they might put it down to) or None."""
    if random.uniform(0, 100) > THOUGHT_ARISE:
        return None
    ctx = dict(ctx or {})
    if pl is not None:
        ctx.setdefault("place", pl)
    src = _thought_sources(n, ctx)
    levels = {}
    for item in src:
        levels.setdefault(item[3], []).append(item)
    lw = {lv: max(x[1] for x in items) * random.lognormvariate(0, 0.9) for lv, items in levels.items()}
    pick = max(lw, key=lw.get)
    items = levels[pick]
    iw = [x[1] * random.lognormvariate(0, 0.6) for x in items]
    seed, _, seen, _ = items[iw.index(max(iw))]
    perceivable = [x[2] for x in src if x[2]]
    if seen and random.random() < 0.6:
        guess = seen
    elif perceivable:
        guess = random.choice(perceivable)
    else:
        guess = None
    return seed, guess


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
         "symbol"]
ROLE_OF_KIND = {"kin": "kin", "lover": "lover", "friend": "friend", "mentor": "mentor", "rival": "rival",
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
              "rival": (1, 3), "creditor": (0, 2), "debtor": (0, 2), "symbol": (7, 7)}


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
PLACE_KINDS = {  # how a place's own fixtures turn dissonant
 "sound": ["{x} goes on, exactly on time", "{x} doesn't stop"],
 "light": ["{x} is lovely", "{x} falls across all of it the same"],
 "animal": ["{x} go about their business", "{x} come to look, then lose interest"],
 "routine": ["{x} happens anyway, on schedule", "someone starts on {x} out of habit"],
 "object": ["{x} sits there, untouched", "someone straightens {x}"],
 "smell": ["{x} is still in the air", "{x} cuts through everything"],
 "taste": ["{x} is still on the tongue", "{x} in the mouth, under everything"],
 "person": ["{x} keeps at what they were doing", "{x} looks up, then back down"],
 "weather": ["{x} goes on outside", "{x} doesn't care"],
 "mark": ["{x}, still", "{x}; nobody mentions it"],
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
    if resp == "Performed":
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
    k = 2 if reg != "Rupture" else 1 + (d(2) == 2)
    beats = place_dissonance(pl, k) if pl else []
    if len(beats) < k:
        if pl is not None:
            print("(The place sheet is thin; add what is always there with `place --add`.)")
        beats += random.sample(DISSONANCE, k - len(beats))
    for beat in beats:
        print("Dissonance: " + beat)
    now, keeps = random.choice(AFTERMATH)
    print("Aftermath: " + now)
    if pl is not None:
        if keeps not in pl.setdefault("marks", []):
            pl["marks"].append(keeps)
        pl.setdefault("history", []).append(now)
        save(pl, a.place)
        print("The place keeps: " + keeps)
    hurt = set(x.lower() for x in (a.hurt or []))
    members = load(a.circle).get("members", []) if a.circle else []
    for path, n in zip(a.files, ns):
        vc = relation_to(n, a.victim, members)
        ac = relation_to(n, a.attacker, members)
        r = violence_response(n, n["name"].lower() in hurt, vc[0], ac[0], a.symbol)
        st = violence_steady(n, r, dials, vc[0])
        rel = []
        if a.victim and vc[0] != "stranger": rel.append("%s is their %s" % (a.victim, vc[1]))
        if a.attacker and ac[0] != "stranger": rel.append("%s is their %s" % (a.attacker, ac[1]))
        if a.symbol and a.symbol == n["creed"]: rel.append("it strikes at what they hold highest")
        if a.record and n["name"].lower() not in hurt:
            n["memory"].append({"day": n["day"], "event": "witnessed", "with": a.attacker or "",
                                "note": "%s hurt" % (a.victim or "someone")})
            fx = apply_affect(n, "witnessed", vc[0], EVENTS["witnessed"][2])
            save(n, path)
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
                 "symbol": "cause"}.get(a.role, a.role if a.role in TIE_KINDS else "friend")
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
    x.add_argument("--prose", help="the narration so far this scene; its words can seed a thought")
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
    x = sp.add_parser("audit"); x.set_defaults(f=cmd_audit)
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
