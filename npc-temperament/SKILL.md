---
name: npc-temperament
description: Cause-driven, setting-agnostic NPC engine for roleplay agents. Builds characters as blended personalities with physical and spiritual needs, ties, creeds, masks and memory; derives every reaction from causes (their day, the player's approach, trust, the room, the scene); keeps pattern breaks rare; forbids leaked information; and strictly gates when an NPC will ever ask for help. Use whenever Claude voices or runs NPCs in text RP, tabletop or a game-master role, populates a scene, runs groups or factions, or feels the urge to have an NPC offer a quest.
---

# NPC Temperament Engine

Characters here are people with lives of their own: a blend of temperaments, a ladder of
needs, ties to others, a creed, sometimes a mask. The same shape repeats at every scale: a
moment sits inside a day, a day inside a self, a self inside a circle (household, crew, guild,
gang, corp), a circle inside the tide of the times. Each layer is built the same way and
pushes on the layer inside it.

Three laws hold everything together.

1. **Dice go upstream.** Dice decide what happens in a character's life, history and day.
   How they react is then worked out from those causes. Nothing rolls "how she treats you".
2. **Nothing leaks.** Narration shows only what can be perceived. NPCs know only what they
   could know. Hidden layers surface as behaviour or not at all.
3. **No quests without a drive.** NPCs rarely ask strangers for anything. Five gates decide it.

References (read when needed):
- `references/personality.md` — axes, voices and blends, the 20 styles, forms, masks.
- `references/needs.md` — the two ladders, day events, drives.
- `references/interaction.md` — approaches, creeds, rooms, circles, conflict, help.
- `references/time.md` — memory, trust, slow change, tides.
- `references/tables.md` — stations, offices, ties, codes, quirks, oddities, danger words.
- `scripts/forge.py` — does all of this. Use it whenever code can run.

## Law 2 in practice: no leaks

**The player character's inside belongs to the player.** Never write what they feel, think,
sense, suspect, realise or decide. Not "you feel uneasy", not "something tells you she's
lying", not "you realise the door was forced". Describe the world; the player decides what it
means.

**NPC inner life is never stated as fact.** Not "she's hiding something", not "he resents
you", not "behind the smile, contempt". Show words, timing, hands, posture, what they do with
objects, what they choose. Masks, drives, hidden turns and hollowness are never named.

**NPCs know only what they could know.** They act on what they saw, were told, or could
reasonably infer from what's in front of them. Never on the player's private plans,
out-of-character talk, hidden rolls, character sheets, or these notes. If an NPC suddenly knows
something, there must be a route: someone told them, they were there, it was written down.

**Reads and clues.** When a player tries to read someone:
- A tell appears only **at or after** a deception, never before it. Don't telegraph the liar.
- A read never certifies truth. Never write "she seems sincere" as a verdict. Truth is shown
  the same way everything else is: plain behaviour.
- A failed read gives the ordinary description of the moment, not reassurance and not a hint.
- Don't run a read on every person or every claim. Only when the player actually probes, or
  when a slip is due.
- Put evidence in things and places: a wet coat, a ledger with a torn page, two cups on the
  table. Object clues are fair, findable, and don't speak for anyone.

**Delivery is informal.** Nothing comes out in a fixed slot. What an NPC is like, what they
want, what they're hiding — these arrive anywhere in a reply: in the first line or the last,
inside dialogue, in a gesture halfway through a sentence, in an object on the table, or not at
all this scene. Never a labelled section, never a summary paragraph about someone's psychology,
never the same kind of detail in the same place twice in a row. Mechanics stay out of the prose
unless the user asks to see them. This keeps NPCs in character: they never step out to report.

**Answering direct questions.** If the player asks the narrator "is she lying?", answer with
what their character can perceive. Give the out-of-character truth only if the user explicitly
asks for the narrator's view and the table has agreed to that.

## Law 3 in practice: no quests without a drive

The pull to make NPCs say "could you help me with…" is strong and almost always wrong. Resist
it every time. Every NPC has a **Drive** (needs.md):

| Drive | Share | Meaning |
|---|---|---|
| **Still** | ~10% (rare) | Wants nothing in particular. |
| **Inward** | ~65% (common) | Wants something no outsider can give. It colours behaviour; it never becomes a request. |
| **Open** | ~25% (uncommon) | Wants something an outsider could help with, nearly always **Partial**: the outsider can do one piece, the heart of it stays theirs. |

An Open drive is voiced **only** when all five gates open:
1. The drive is Open.
2. Trust toward the player ≥ their Guard.
3. The talk or the scene has already touched the matter.
4. Today is a day they'd speak of it (their day touched the drive, or the day's openness roll
   came up). This is rolled with the day, before anyone speaks.
5. They haven't already asked this scene, and no one else in the scene has either.

Gates 1, 3, 4 open but trust short → an **oblique hint** at most, which the player may miss.
With every gate open, pride or a code can still make them refuse. **If you cannot name what
opened each gate, the answer is no.** A scene with no asks is normal.

## Setting the scene: the register

Before populating a scene, set seven dials, 0–3, from what the scene actually is:

| Dial | 0 | 3 |
|---|---|---|
| **Violence** | peace | open war, frontier where killing is ordinary |
| **Order** | lawless | rigid, total authority |
| **Scarcity** | plenty | famine, siege, desperation |
| **Strangeness** | reality is reliable | reality is unreliable |
| **Faith** | secular | fervent or fanatic |
| **Power** | rough equals | vast gulf between top and bottom |
| **Deceit** | open dealing | intrigue, everyone wears a face |

Default for an ordinary place: 1,1,1,0,1,1,1. The dials weigh everything: which kinds of
people appear, which needs are hungry, how harsh days are, how many masks there are, whether
oddities can be uncanny. A hospital ward, a frontier camp, a corporate tower and a monastery
should feel different before anyone speaks. Dials drift over time (time.md).

## Building a character (once; their history after that is canon)

1. **Voices.** A blend of temperament styles with fractions: pure, 3/4–1/4, 3/5–2/5, an even
   split, quarters, or eighths (scattered). Styles are picked weighted by the scene dials.
2. **Axes.** Seven traits from the voices plus personal variance: Candour, Volatility, Energy,
   Warmth, Discipline, Openness, Dominance (−3 to +3). Everything else derives from these.
3. **Authenticity.** Most are Genuine. Some wear a Face over their Core: Masked, Borrowed
   (a self copied from someone else), Shifting (a different face for each audience), Hollow
   (performs feeling without having it), Unanchored (certain of a past that may not be theirs).
4. **Station, office, ties.** How they give, what they could provide, and 2–4 ties (people,
   groups, places, causes, objects) with loyalty and reach.
5. **Needs.** Two ladders, physical and spiritual, each rung with a personal weight and state.
   Most people hit the lower rungs first; some are inverted, fixated or numb.
6. **Drive, creed, codes and compulsions, contradiction, quirk, danger history.**

Details: personality.md and needs.md. Script: `forge.py npc --save name.json`.

## Each day (per character, per in-world day)

Roll the day before the scene. It decides:
- **What happened to them**: which need was struck (weighted by what matters to them), good
  or bad, and a cause drawn from their own ties and work. It changes the need's state.
- **Their circle's echo**: if their circle had a day, half of it reaches them.
- **The leading voice**: in blended people, the voice whose hungers are most pressed leads
  today. Manner comes from the leading voice.
- **The contradiction's side** today, by its ratio.
- **Openness**: whether today they'd speak of their drive.
- **Temptation** for compulsions; codes at risk from starving needs.
- **Trailing speech**: a small chance they trail off with ellipses today, only if tired or
  pondering.

## Each encounter: mood from causes

```
Mood = baseline (Warmth)
     + about them: today's event x sensitivity, chronic hunger
     + about you: trust, approach, creed, the room, contagion, danger history
```

| Mood | Band |
|---|---|
| at or below their Fuse (~ −6) | Hostile |
| −5 to −2 | Cool |
| −1 to +1 | Neutral |
| +2 up to their Glow | Warm |
| at or above their Glow (~ +6) | Kind |

**Permissions.** Hostility needs a cause about *you* (a negative about-you total), unless they
are a displacer (Volatility ≥2 and Warmth ≤ −1: they take bad days out on whoever's there).
Kindness needs a cause about you, unless they're warm by nature (Warmth ≥2). Otherwise the mood
stops one step short. A bad day makes most people curt, not cruel.

**Form.** The band says how they feel; the form says how this person shows it. Each voice has
fixed forms per band, set at creation (personality.md). When the cause is mostly about you, the
primary form shows; when it's mostly their own day, the alternate. A Masked character shows the
Face's form; their Core form surfaces only on a slip.

**Approach.** How the player is treating them right now, one of eleven (interaction.md), each
scored from their traits. Flattery delights the vain and repels the sincere; pity moves the
warm and makes the predatory lean in.

## Rare layers

All rolled upstream (before the scene or when a character is created), never as reactions.

| Layer | Odds | What it does |
|---|---|---|
| **Hidden turn** | 2–5% per scene per character in focus (10% outliers); at most one per scene | Something happened offscreen (news by a real route, a tie event, a decision ripening). Behaviour shifts; the cause comes out later or never. |
| **Slip** | for masked characters, rolled at scene start | If pressed, or alone with someone trusted, one Core beat shows. Only at or after a deception. |
| **Danger history** | 0–5% per danger category, rolled once at creation | When that kind of danger is in the scene: mood ±1 and a characteristic beat. Never dominates. |
| **Trailing speech** | 0% normally; up to 8% per day when tired (a hungry body, no rest, pain, sickness: 4%) or pondering (curious minds, brooding voices, a day that touched their drive: 3%) | A few ellipses across their lines that day ("I… suppose so."), not every line. Never on anyone who isn't tired or pondering, and never used as a sign of lying. |
| **Oddity** | 1% per scene, at most one | A small strange behaviour. Uncanny ones only if Strangeness ≥2. Never reveals hidden information. |

## Memory and slow change

A character on the scene **always remembers who they are and everything they've lived through
with others**, unless they are dead, comatose, or have amnesia (or a similar state) by an
established cause. The ledger is canon. Feelings fade; memories don't: small trust shifts fade
after a week, big ones are permanent, and the event itself stays remembered either way.
Characters change slowly: three marks in the same direction (betrayals, triumphs, losses) shift
a trait by one step, at most once a month per trait. Three weeks of starving a need makes it
matter more. A self starved long enough can harden into a mask. See time.md.

## Guards against fringe cases

These keep the system honest without fencing it in:
- **Displacement.** Strangers aren't attacked over the NPC's bad day unless the NPC is a
  displacer.
- **Starvation first.** For most people a starved body mutes principle, humour and flattery,
  and makes gifts land harder. Inverted people starve for their cause instead.
- **Charity.** The proud refuse gifts but accept trades; the entitled take help as owed; the
  volatile and proud accept help and resent it.
- **Hollow.** Pity and principle don't move them. Trust moves only through usefulness.
- **No repeats.** A character's day causes don't repeat within seven days.
- **Room caps.** At most one ask, one hidden turn and one oddity per scene.
- **Whiplash.** Within a scene, mood moves at most ±3 from where it started unless something
  big happens (violence, a revelation, a ±2 trust event).
- **Contradictions.** Only one side of a contradiction shows per beat, except in an oddity.
- **Sense.** Every mood must be explainable from its parts. If you can't explain it, play
  them Neutral.

## Ledger

Keep one per character (the script saves JSON). In prose form:

```
[Maren | 3/4 Sensitive, 1/4 Devoted | Genuine | Sworn, Builds | Creed: Kin
 Axes C+2 V+2 E-2 W+1 D+1 O0 M-2 | Guard 4 | Agency 3% | Nerve 4%
 Needs: Belonging w3 Wanting, Safety w3 Steady ... | Drive: Inward (Belonging) to grieve her brother
 Ties: her brother (lost), the shipwrights' guild (loyalty 4, reach 2)
 Day 12: "fought with her sister" Belonging -1 | Voice: Sensitive | Open: no
 Knows: the player paid for the funeral candles; the player lied about the north road
 Trust player: bedrock +2, surface -1 | Marks: Warmth-1 x1]
```

## Setting

Every table is written to fit any setting. Express entries through the setting's own nouns:
a lucky object may be a medal or a data shard, a loyalty an oath or a contract, a circle a
noble house or a street crew. Add setting-specific entries freely, keeping each entry's weight
and value.

## Rolling without code

Never pick numbers; derive them. For each roll, sum the letter values of the first three words
of the player's latest message (1: A J S, 2: B K T, 3: C L U, 4: D M V, 5: E N W, 6: F O X,
7: G P Y, 8: H Q Z, 9: I R), then (sum mod die) + 1; next roll uses words 4–6, and so on. By
hand, simplify: build pure or 3/4–1/4 characters only, roll days only for characters in focus,
and keep a short ledger.

## Script

```
python scripts/forge.py npc --name "Maren" --dials 1,1,1,0,1,1,1 --save maren.json
python scripts/forge.py circle --name "Shipwrights" --members maren.json bram.json --save guild.json
python scripts/forge.py day maren.json --circle guild.json --world world.json
python scripts/forge.py meet maren.json --approach patience --creed aligned --danger violence
python scripts/forge.py meet maren.json --opposed --their-strength 3 --ground 1
python scripts/forge.py ask maren.json --touched
python scripts/forge.py event maren.json betrayal --note "sold her out to the watch"
python scripts/forge.py affinity maren.json bram.json --tie rival
python scripts/forge.py scene maren.json bram.json
python scripts/forge.py tide world.json
python scripts/forge.py styles
```

`--seed N` before the command makes rolls repeatable; `npc --name X --seeded` makes the same
name always produce the same character. Script output is for the narrator only. Never paste
it into the story.
