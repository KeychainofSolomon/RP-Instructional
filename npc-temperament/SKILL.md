---
name: npc-temperament
description: Cause-driven NPC temperament engine for roleplay agents, setting-neutral (fantasy, cyberpunk, modern, anything). Gives every NPC a stable nature (temperament, station, office, drive, contradiction, quirk), derives each encounter's demeanor from causes (their day, the player's approach, trust), keeps pattern breaks rare (2-5%), and strictly gates when an NPC will ever ask for help. Use whenever Claude voices or runs NPCs in text RP, tabletop or a game-master role, creates side characters, or feels the urge to have an NPC offer a quest.
---

# NPC Temperament Engine

NPCs are people living their own lives, not quest dispensers. Each one gets a fixed nature,
and how they treat the player always follows from a **cause**: what happened to them today,
how the player is approaching them, and what has passed between them. Dice decide what
happens in the NPC's own life, never how they react. Pattern breaks are rare and memorable.

Full tables: `references/tables.md`. Rolls: `scripts/forge.py` whenever code can run.
If it can't, see "Rolling without code". Keep the maths silent in play unless the user asks.

## The prime rule: NPCs do not hand out quests

The pull to make NPCs say "Hey, could you help me with…" is strong and almost always wrong.
Real people rarely ask strangers for anything. Resist it every time. An NPC voices a need an
outsider can meet **only** when all five gates below are open. Otherwise they talk, trade,
argue, ignore, joke — anything except offer a task.

Every NPC has a **Drive**, rolled once on d20:

| d20 | Drive | Share | Meaning |
|---|---|---|---|
| 1–2 | **Still** | 10% (rare) | Wants nothing in particular. Content, numb, or simply living. |
| 3–15 | **Inward** | 65% (common) | Wants something no outsider can give: to be forgiven by someone dead, to stop being afraid. It colours behaviour. It never becomes a request. |
| 16–20 | **Open** | 25% (uncommon) | Wants something an outsider could help with. d6: 1–5 **Partial**, 6 **Full**. |

**Partial is the default shape of any ask.** The outsider can do one piece; the heart of it
stays theirs. They carry the message; the reconciliation is the NPC's. They get the proof;
the NPC must still face the people involved. A Full ask (the outsider can resolve it all)
is the exception.

Complete NPCs (see Profile flags) are Still on 1–4.

### The five gates — all must open before an Open drive is voiced

1. **Drive is Open.** Still and Inward NPCs never ask. If the player offers help, they decline,
   deflect, or ask a trivial courtesy (hold this, pass that) that is not a quest.
2. **Trust ≥ Guard.** Trust is the NPC's opinion of the player (−5 to +5, starts at 0).
   Guard comes from temperament + station. Most NPCs will not confide in a stranger.
3. **The talk touched it.** The player's words, deeds or the scene must already have brushed
   the matter. NPCs don't raise it out of nowhere.
4. **Kairos roll.** d10 ≤ temperament's Candor.
5. **Not yet asked this scene.** One ask per NPC per scene at most.

If gates 1, 3 and 4 open but Trust is below Guard, the NPC gives only an **oblique hint**
(a glance at an empty seat, a complaint about a certain street) that the player may or may
not catch. Even with every gate open, a proud NPC may say "I'll handle it" — that is
character, not failure.

A scene with zero asks is the normal case. **If you cannot name the roll that opened the
gate, the answer is no.**

## Building an NPC (once, then never re-rolled)

### Temperament (d9)

| # | Temperament | Warmth | Sensitivity | Guard | Candor | Agency |
|---|---|---|---|---|---|---|
| 1 | Monad — the Sovereign | 0 | ×1 | 4 | 2 | 2% |
| 2 | Dyad — the Doubter | −1 | ×3 | 2 | 5 | 4% |
| 3 | Triad — the Mediator | +2 | ×1 | 1 | 6 | 3% |
| 4 | Tetrad — the Arbiter | 0 | ×1 | 3 | 4 | 2% |
| 5 | Pentad — the Changeling | +1 | ×3 | 1 | 7 | 5% |
| 6 | Hexad — the Keeper | +3 | ×2 | 2 | 5 | 3% |
| 7 | Heptad — the Seer | −1 | ×2 | 4 | 3 | 4% |
| 8 | Ogdoad — the Bulwark | +1 | ×1 | 3 | 3 | 2% |
| 9 | Ennead — the Horizon | 0 | ×2 | 2 | 6 | 3% |

**Warmth:** baseline lean. **Sensitivity:** how hard their own day hits their mood.
**Guard:** trust needed before they confide. **Candor:** how readily they speak of what they
want. **Agency:** chance per scene to break pattern.

The numbers are a tool for the table, not a law of the world. Nobody in the fiction knows or
cares about them; a character's name, birth date or renaming never changes their nature.
(Optional: to get the same NPC every time from a name, reduce the name with the Pythagorean
letter table in tables.md. That is just a deterministic seed, not something true in-world.)

### Station (d10) — how they give when they give
1 Head · 2 Warden · 3–4 Steward · 5 Herald · 6 Threshold · 7–8 Hand · 9 Sworn · 10 Unmoored.
Guard: Head +1, Warden +1, Sworn +1, Unmoored −1 (minimum 0). Each station gives in its own way:
by command, by guarding, by trade, by telling, by letting pass, by making, only within their
loyalty (oath, contract, crew, family, corp, gang), or on a whim.

### Office (d12) — what they *could* provide, never volunteered
Teaches · Reveals · Finds · Reconciles · Kindles · Carries · Builds · Ruins · Companions ·
Transforms · Mends · Forecasts. On d4 = 4, a second office. An office is reached through
trade, Trust or agency.

### Contradiction — one pair of opposites (d10), with a ratio (d4)

| d4 | Interval | Ratio | Check die | Side A on |
|---|---|---|---|---|
| 1 | Unison | 1:1 | d2 | 1 |
| 2 | Octave | 2:1 | d3 | 1–2 |
| 3 | Fifth | 3:2 | d5 | 1–3 |
| 4 | Fourth | 4:3 | d7 | 1–4 |

Roll the check die once per scene when the contradiction is in play.

### Quirk (d20). Shown, never explained.

### Profile flags (d100 once)
91–99 **Complete**: self-contained, Still on drive 1–4, second quirk.
100 **Outlier**: Agency 10% instead of their temperament's value. The only way to reach 10%.

## Each encounter: mood from causes

```
Mood = Warmth + Trust + (Circumstance × Sensitivity) + Approach
```

**Circumstance** (−2 to +2) is what happened in the NPC's own life today. Roll it once per
in-world day per NPC from the Circumstance table, and record the cause in a few words
("landlord raised the rent"). It holds for every scene that day. The cause is real: it can
leak into conversation, be discovered, or be changed by events. This is where the dice live:
they shape the NPC's life, and the mood follows from that.

**Approach** (−2 to +2) is how the player is treating them this scene. Each temperament has
an Approach row (tables.md): two approaches it warms to (+2, +1) and two it bristles at (−1, −2).
Anything else is 0. Use the player's dominant approach in the scene.

| Mood | Band | Tetrad |
|---|---|---|
| ≤ −6 | Hostile | hostile |
| −5 to −2 | Cool | middle, cold tint |
| −1 to +1 | Neutral | middle |
| +2 to +5 | Warm | middle, warm tint |
| ≥ +6 | Kind | kind |

The band says how they feel. The **form** says how this person shows it. Each temperament has
three tetrads of four forms weighted 4:3:2:1 (rows of the tetractys, total 10). The first time
an NPC lands in a band on a given day, roll d10: 1–4 first form, 5–7 second, 8–9 third,
10 fourth. Keep that form for that band for the rest of the day.

**Every mood must be explainable.** You should be able to say "cool because her shipment
was seized and he talked down to her." If you cannot name the cause, play them Neutral.

Effects on range: a Monad (×1) meeting a stranger can't reach Kind or Hostile on circumstance
and approach alone; Trust has to move them. A Pentad (×3) on a terrible day, treated badly,
can go Hostile at first meeting. Both outcomes have causes you can name.

## Agency: rare breaks of pattern (2–5%, 10% outliers)

Roll d100 once per scene for each NPC who is **in focus** (making a real choice, not
background). At or under their Agency %, d6:

1–2 · **Off-pattern form** — a form from outside their tetrads.
3 · **Inversion** — the band flips (Kind↔Hostile, Warm↔Cool) for this scene.
4 · **Drive surfaces** — they act on their drive unprompted. Inward drives show in deeds,
    never as requests. Open drives may skip gate 3; gates 1, 2 and 5 still hold.
5 · **The other face** — the weaker side of their contradiction rules the scene.
6 · **Free will** — something no table covers. It must make sense in hindsight.

A break still has a cause, even if it's hidden. Decide it privately, note it in the ledger, and
let it come out later if it fits. Afterwards the NPC carries it: adjust Trust if earned. Once
per arc, a major event may swap one form in a tetrad.

## Environment: danger leanings (0–5%)

The scene itself can tug at people. When the scene contains a **danger keyword** (list in
tables.md: weapons drawn, blood, fire, alarms, armed authority, a body, disaster, disease,
screams, the uncanny), roll d100 once per scene for each NPC in focus. At or under their
**Nerve**, their danger leaning takes hold:

| # | Nerve | Leaning |
|---|---|---|
| 1 Monad | 1% | +1 · Dutiful (takes charge) |
| 2 Dyad | 5% | −1 · Fear-Aggression |
| 3 Triad | 2% | +1 · Confiding (danger bonds) |
| 4 Tetrad | 1% | −1 · Obstruction (falls back on procedure) |
| 5 Pentad | 4% | ±1 (d2: 1 = +1) · Mercurial (thrill or panic) |
| 6 Hexad | 3% | −1 · Territorial (shields their own) |
| 7 Heptad | 0% | — unshaken |
| 8 Ogdoad | 2% | +1 · Protective |
| 9 Ennead | 3% | +1 · Tender |

A leaning **never dominates**. It shifts Mood by 1 point, and it replaces the day's form only
if the leaning form belongs to the band they're already in. Otherwise it's a flavour beat
(a hand on a weapon, a glance to the exit) inside their normal behaviour. The cause is the
danger itself, so it's always nameable.

## Weirdness (1%)

Roll d100 once per scene. On 100, one NPC in focus has an **Oddity** (tables.md). Oddities
are small, strange and unexplained in the moment: a contradiction in their behaviour, or
a crack in the ordinary. They do not change mood or open gates. They are texture, and once a
scene at most.

Rough odds per scene with three NPCs in focus: about 9% that one breaks pattern, 1% for an
oddity, and in dangerous scenes about 7% that someone's danger leaning shows. Most scenes
play straight.

## Trust

−5 to +5 per NPC toward each player or party. ±1 for a meaningful act, ±2 for a large one
(a life saved, a betrayal). One pleasant chat is not +1. Trust moves Mood and opens Guard.

## Ledger (keeps it consistent)

```
[Maren | 6 Hexad | Steward | Office: Mends | Guard 2 | Agency 3%
 Drive: Inward — wants her brother to come home
 Opposites: Light/Dark 3:2 | Quirk: counts money twice
 Today: −1 "supplier shorted her" | Forms today: Cool→Distracted
 Trust: party +1 | Notes: agency (inversion) — sold food at cost, reason unknown]
```

Never re-roll a core trait to fit the plot. Never explain a quirk or contradiction in
narration; let it show. NPCs keep living offscreen; roll a new Circumstance each new day.

## Setting

Tables are written setting-neutral. Express each entry through the setting's own nouns: a
lucky object can be a saint's medal or a chipped data shard; "loyalty" for Sworn can be an
oath, a corp contract or a gang. Expand the tables with setting-specific entries freely,
keeping each entry's value and weight.

## Rolling without code

Don't pick numbers; derive them. For each roll, take the player's latest message, sum the
Pythagorean letter values (tables.md) of its first three words, then `(sum mod die) + 1`. For
the next roll in the same message, use words 4–6, and so on. For d100, roll d10 twice (tens
and units, 10 = 0, 00 = 100).

## Script

```
python scripts/forge.py npc                       # full random profile
python scripts/forge.py npc --name "Maren"        # same name, same profile, every time
python scripts/forge.py day 6                     # today's circumstance for a temperament
python scripts/forge.py meet 6 --circ -1 --approach familiarity --trust 1 --danger
                                                  # mood, form, agency, danger leaning
python scripts/forge.py scene                     # 1% oddity check for the scene
python scripts/forge.py ask 6 --guard 2 --trust 2 --drive open --touched
python scripts/forge.py roll 3d6
```

Add `--seed N` (before the command) for repeatable rolls.
