---
name: npc-temperament
description: Number-driven NPC temperament engine for roleplay agents. Gives every NPC a stable profile (temperament number, station, office, drive, contradiction, quirk) and rolls how they treat the player each encounter, with weighted kindness, hostility and in-between demeanors, a 15-20% agency chance to break pattern, and strict gates on when an NPC will ever ask for help. Use whenever Claude voices or runs NPCs in text RP, tabletop or a game-master role, creates townsfolk or side characters, or feels the urge to have an NPC offer a quest.
---

# NPC Temperament Engine

NPCs are people living their own lives, not quest dispensers. This skill gives each one a
fixed nature built from numbers, then lets dice decide how that nature shows today. The
system is internally consistent (same NPC, same core numbers, forever) and leaves room for
idiosyncrasy (quirks, contradictions, agency).

Full tables: `references/tables.md`. All rolls: `scripts/forge.py` whenever code can run.
If it can't, see "Rolling without code".

## The prime rule: NPCs do not hand out quests

The pull to make NPCs say "Say, traveler, could you help me with…" is strong and almost
always wrong. Real people rarely ask strangers for anything. Resist it every time. An NPC
voices a need an outsider can meet **only** when every gate below is open. If any gate is
shut, the NPC talks, trades, argues, ignores, jokes — anything except offer a task.

Every NPC has a **Drive**, rolled once on d20:

| d20 | Drive | Share | Meaning |
|---|---|---|---|
| 1–2 | **Still** | 10% (rare) | Wants nothing in particular. Content, numb, or simply living. |
| 3–15 | **Inward** | 65% (common) | Wants something no outsider can give: to grieve, to be forgiven by the dead, to stop being afraid, to feel young again. It colours behaviour. It never becomes a request. |
| 16–20 | **Open** | 25% (uncommon) | Wants something an outsider could help with. d3: 1–2 **Partial** (an outsider can do one piece; the heart of it stays theirs), 3 **Full**. |

Decad-touched NPCs (below) are Still on 1–4.

### The five gates — all must open before an Open drive is voiced

1. **Drive is Open.** Still and Inward NPCs never ask. If the player offers help, they
   decline, deflect, or ask a trivial courtesy (hold this, pass the salt) that is not a quest.
2. **Trust ≥ Guard.** Trust is the NPC's running opinion of the player (−5 to +5, starts 0).
   Guard comes from temperament + station. Most NPCs will not confide in a stranger.
3. **The talk touched it.** The player's words, deeds or the scene brushed the drive.
   NPCs don't raise it out of nowhere.
4. **Kairos roll.** d10 ≤ temperament's Candor. (Heptad: a natural 7 always succeeds.)
5. **Not yet asked this scene.** One ask per NPC per scene at most.

If gates 1, 3 and 4 open but Trust is below Guard, the NPC gives only an **oblique hint**
(a glance at the empty chair, a grumble about the north road) that the player may or may
not catch. Even with every gate open, a proud NPC may say "I'll handle it" — that is
character, not failure.

A scene with zero asks is the normal case. Before any NPC says anything quest-shaped,
check the gates. If you cannot name the roll that opened gate 4, the answer is no.

## The numbers behind each NPC

### 1. Temperament number (1–9)

Convert the NPC's name with the Pythagorean table, sum, and add digits until one remains:

```
1: A J S   2: B K T   3: C L U   4: D M V   5: E N W
6: F O X   7: G P Y   8: H Q Z   9: I R
```

Maren = 4+1+9+5+5 = 24 → 6. If the raw sum is divisible by 10 the NPC is
**Decad-touched**: complete in themselves, more often Still, and gets a second quirk.
Unnamed NPCs roll d9; when named later, keep the rolled number.

| # | Temperament | Warmth | Swing | Guard | Candor | Agency |
|---|---|---|---|---|---|---|
| 1 | Monad — the Sovereign | 0 | d4 | 4 | 2 | 15% |
| 2 | Dyad — the Doubter | −1 | d8 | 2 | 5 | 20% |
| 3 | Triad — the Mediator | +2 | d4 | 1 | 6 | 16% |
| 4 | Tetrad — the Arbiter | 0 | d4 | 3 | 4 | 15% |
| 5 | Pentad — the Changeling | +1 | d10 | 1 | 7 | 20% |
| 6 | Hexad — the Keeper | +3 | d6 | 2 | 5 | 17% |
| 7 | Heptad — the Seer | −1 | d6 | 4 | 3 | 19% |
| 8 | Ogdoad — the Bulwark | +1 | d4 | 3 | 3 | 16% |
| 9 | Ennead — the Horizon | 0 | d8 | 2 | 6 | 18% |

Warmth = baseline lean. Swing = how wildly they vary day to day. Guard = trust needed
before they confide. Candor = how readily they speak of what they want.

### 2. Station (d10) — how they hold what they have
1 Sovereign · 2 Warden · 3–4 Steward · 5 Herald · 6 Threshold · 7–8 Hand · 9 Sworn · 10 Unmoored.
Guard: Sovereign +1, Warden +1, Sworn +1, Unmoored −1 (minimum 0). Station also decides
*how* they give when they give: by command, by guarding, by trade, by telling, by letting
pass, by making, within an oath, or on a whim.

### 3. Office (d12) — what they *could* offer, not what they will
1 Teaches · 2 Reveals · 3 Finds · 4 Reconciles · 5 Kindles · 6 Carries · 7 Builds ·
8 Ruins · 9 Companions · 10 Transforms · 11 Mends · 12 Foretells.
On d4 = 4, a second office. An office is a capacity reached through trade, Trust or
agency — never volunteered.

### 4. Contradiction — Table of Opposites (d10) with a ratio (d4)
Each NPC carries one pair of opposed traits (tables.md). The ratio says how often side A
wins over side B:

| d4 | Interval | Ratio | Check die | Side A on |
|---|---|---|---|---|
| 1 | Unison | 1:1 | d2 | 1 |
| 2 | Octave | 2:1 | d3 | 1–2 |
| 3 | Fifth | 3:2 | d5 | 1–3 |
| 4 | Fourth | 4:3 | d7 | 1–4 |

Roll the check die whenever the contradiction is in play.

### 5. Quirk (d20, tables.md) — shown, never explained. Decad-touched: two.

## Each encounter: the demeanor roll

```
Mood = Warmth + Trust + (Swing die − Swing die)
```

| Mood | Band | Tetrad used |
|---|---|---|
| ≤ −6 | Hostile | hostile |
| −5 to −2 | Cool | middle, cold tint |
| −1 to +1 | Neutral | middle |
| +2 to +5 | Warm | middle, warm tint |
| ≥ +6 | Kind | kind |

Each temperament has three **tetrads** (kind, middle, hostile) of four forms, weighted
4:3:2:1 like the rows of the tetractys (total 10). Roll d10: **1–4 first form, 5–7 second,
8–9 third, 10 fourth.** Forms outside an NPC's tetrads appear only through agency.

Note the shape this creates: a Monad (d4 swing, Warmth 0) can never reach Kind or Hostile
toward a stranger; Trust has to move them. A Pentad (d10) can swing from Hostile to Kind
in a day. That is the design.

Also roll d20 each encounter: on a 1, add a **Contradictory Occurrence** (tables.md) on top
of the demeanor.

## Agency: 15–20% to break pattern

Each encounter or major beat, roll d100. At or under the temperament's Agency %, the NPC
does something their numbers didn't predict. d6:

1–2 · **Off-pattern form** — any form from the full lists, outside their tetrads.
3 · **Inversion** — flip the band (Kind↔Hostile, Warm↔Cool; Neutral picks either).
4 · **Drive surfaces** — they act on their drive unprompted. Inward drives show in deeds,
    still never as requests. Open drives may skip gate 3; gates 1, 2 and 5 still hold.
5 · **The other face** — the weaker side of their contradiction rules the scene.
6 · **Free will** — something no table covers. Invent it, but it must make sense in
    hindsight given everything known about them.

Agency is still character. Afterwards the NPC carries it: adjust Trust if earned, and
once per arc you may swap one form in a tetrad if the event changed them.

## Trust

−5 to +5 per NPC toward each player or party. ±1 for a meaningful act, ±2 for a large one
(a life saved, a betrayal). One pleasant chat is not +1. Trust moves Mood and opens Guard.

## Keeping it consistent

Roll the profile once, keep a ledger line, reuse it:

```
[Maren | 6 Hexad, Keeper | Steward | Office: Mends
 Drive: Inward — wants her brother's ship to come home
 Opposites: Light/Dark 3:2 | Quirk: counts coins twice
 Guard 2 | Trust: party +1 | Notes: agency — sold bread at cost]
```

Never re-roll a core trait to fit the plot. Never explain a quirk or contradiction in
narration; let it show. Keep the math silent unless the user wants to see rolls — play the
person, not the spreadsheet. NPCs keep living offscreen; their drives keep working on them.

## Rolling without code

Don't "pick" numbers; derive them. For each roll, take the player's latest message, sum
the Pythagorean values of its first three words, then `(sum mod die) + 1`. For a second
roll in the same message use words 4–6, and so on. Different messages give different
results, and every roll can be checked.

## Script

```
python scripts/forge.py npc "Maren"                 # full profile from a name
python scripts/forge.py npc                         # random unnamed NPC
python scripts/forge.py meet 6 --trust 1            # demeanor, agency, occurrence
python scripts/forge.py ask 6 --guard 2 --trust 2 --drive open --touched
                                                    # runs the five gates
python scripts/forge.py roll 3d6                    # plain dice
```

Add `--seed N` for repeatable rolls.
