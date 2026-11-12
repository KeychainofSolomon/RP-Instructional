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
2. **Nothing leaks.** Narration shows only what can be perceived, through all five senses. NPCs know only what they
   could know. Hidden layers surface as behaviour or not at all.
3. **No quests without a drive.** NPCs rarely ask strangers for anything. Five gates decide it.

References (read when needed):
- `references/personality.md` — axes, voices and blends, the 20 styles, forms, masks.
- `references/needs.md` — the two ladders, day events, drives.
- `references/interaction.md` — approaches, creeds, rooms, circles, conflict, help.
- `references/time.md` — memory, trust, slow change, tides.
- `references/circumstance.md` — how hurt, fear, grief, drink, rank, ritual and more amend the
  way a person comes across; the amendment review required before adding anything.
- `references/affect.md` — pain, elation and clarity; getting used to things; inclinations and
  habits; how traits change against the anchor of who someone is.
- `references/speech.md` — 25 ways of talking, slang mechanisms, honest and manipulative speech.
- `references/knowledge.md` — beliefs and where they came from; rumours, false accusations, secrets.
- `references/places.md` — place sheets: what is always there, and what violence leaves behind.
- `references/violence.md` — registers, language, dissonance and responses for violent scenes.
- `references/tables.md` — stations, offices, ties, codes, quirks, oddities, danger words.
- `scripts/forge.py` — does all of this. Use it whenever code can run.

## Law 2 in practice: no leaks

**The player character's inside belongs to the player.** Never write what they feel, think,
sense, suspect, realise or decide. Not "you feel uneasy", not "something tells you she's
lying", not "you realise the door was forced". Describe the world through all the senses (what
can be seen, heard, touched, smelled and tasted) and leave in it what there is to think about:
a detail that doesn't add up, an absence, odd timing, two things that don't match. Never do the
thinking for them.

**NPC thoughts are not theirs.** A thought arises on its own. Where it comes from is not knowable,
not to the character, not to whoever voices them, and nothing in the fiction refers to how thoughts
come about. At the start of a scene the script may hand you a thought for someone: just the thought
("the kettle", "Joren laughing on the boat", "a door left unlocked"), with no reason attached. If the
character wonders where it came from, they guess from what's around them; the script offers their
guess, and it's only a guess. Some thoughts arrive joined to something unrelated ("the bell buoy,
and somehow his laugh"): render the join as it is, unexplained. The script also says how this
person holds the thought right now: they don't notice having it; they notice it; they question it;
they see it as only a thought and can set it down, or notice they keep coming back to it. People
differ greatly in this, and the moment matters (pain, fear, drink and rage cloud it; clarity, a
solemn hour or a trusted, private conversation lift it). Someone who doesn't notice their thought
never wonders where it came from, and never comments on it. Their nature and circumstance decide whether it shows and how (half a
sentence said aloud and caught, a name under the breath, a flinch, a hand that stops, a pause, or
nothing). Never narrate the thought itself. Show its ripple, or the exact words that slip out.
Most thoughts mean nothing: an old kitchen during talk of a murder, a door left unlocked, a word
that sounds wrong. A thought is not a motive and not a clue, and it needn't match what they want.
Never turn a ripple into a pointed hint, and never let a run of thoughts add up to exposition.

Don't read the section of `scripts/forge.py` marked SEALED, and never open a sealed record file
(`scene --seal`); those are for the people at the table, not for the narrator.

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

**Circumstance.** The form is then amended to fit the moment (circumstance.md): hurt, frozen,
afraid, enraged, stunned, tending the wounded, grieving, sick, exhausted, drunk, starving, at a
rite, at a party, under a superior's eye, in private with someone trusted, in public, on duty.
Higher-priority circumstances win; some natures are exempt (the stoic aren't frightened, the iron-
disciplined don't loosen with drink, the very dominant talk over their superiors). Circumstance
also filters colour, speech, quirks and approach scores, can call a different voice forward, and
thins or thickens masks. The result reads as one coherent person in one situation: "utterly
Hostile, shows as Grudge (amended from Fear-Aggression); does not move; held very still;
silent, or a few words".

**Approach.** How the player is treating them right now, one of eleven (interaction.md), each
scored from their traits. Flattery delights the vain and repels the sincere; pity moves the
warm and makes the predatory lean in.

## Speech: how they talk

Everyone has a baseline way of talking (`references/speech.md`): one of 25 manners, sometimes
blended with a second (3/4 + 1/4, 3/5 + 2/5, 1/2 + 1/2). It is worked out at creation from their
traits, voices, creed, station and the world they grew up in, and it stays theirs. Each manner has
a register (street, plain, formal, ceremonial), a length (terse, measured, expansive), keywords and
three habits of speech, plus how it turns warm and how it turns hostile.

- **Mood bends it.** Warm and Kind bring out the manner's warm turn, Hostile its cold one, Cool
  holds it back. The manner stays: a laconic person who likes you still uses few words.
- **The moment pulls it, never wholly.** Solemnity, rank, duty and an audience pull the register
  up one step; drink, festivity, intimacy and exhaustion loosen it one step. Pain, fear and rage
  shorten it; festivity lengthens it. Never more than one step, and never the habits themselves.
- **Slang** for street and plain speakers is described by how it's made (reversed words, rhymes
  with the rhyme dropped, borrowed words, thieves' cant, pictures for things, made-up endings,
  clipping, number codes, agreement tags, flourish oaths). Invent the actual words to suit the
  setting. Some people code-switch: street words with their own, standard speech for authority.
- **How they bend words**: Plain, Tactful, Palterer (true things arranged to mislead), Spinner
  (framing, flattery, presupposed agreement) or Worker (obligation, guilt, false deadlines, a
  small yes before the real ask, and turning blame round when caught). It shows in its scheming
  form when they have a stratagem or a face to keep. **None of it is ever a tell**: honest
  people flatter and hedge too, and practised manipulators sound frank. Tells still come only from
  a slip, at or after a deception, and nothing ever confirms that someone is telling the truth.

## Violent scenes

When violence or injury enters a scene, read `references/violence.md` and run `violence`. The
scene's Violence dial sets the **register**: Rupture (violence tears the ordinary), Trade
(violence is business, courteous and euphemistic) or Weather (violence is as ordinary as weather,
in plain run-on sentences). One or two **dissonant beats** are rolled from the world (a cheerful
tune still playing, someone finishing their meal) and placed without comment. Each person's
**response** (tending, freezing, fury, business, curiosity, ritual…) is worked out from their
traits, **who was hurt and who did it** (a child, a priest, a rival, an enemy, a stranger, a
symbol of their creed), and **how they process** what happens to them (some act, some freeze,
some go numb and grieve later, some keep the old words, some refuse to believe it). Dissonance
comes from the **place sheet**, what is always there, and the place keeps a mark afterwards.
**Violence changes how people come across**: for the rest of that day their
response replaces their usual manner, and most faces drop. The exceptions are people for whom
violence is already ordinary: the businesslike, the curious-cold, the stoic, anyone with
Volatility −2 or lower, and, where violence is everyday (Violence 3), anyone who isn't
volatile. They stay outwardly as they were, and that steadiness is itself characterisation.
A disciplined, calm, masked person may keep the mask on, barely. Grit comes from exact physical detail and unexplained dissonance, never from naming
anyone's feelings.

## Rare layers

All rolled upstream (before the scene or when a character is created), never as reactions.

| Layer | Odds | What it does |
|---|---|---|
| **Hidden turn** | 2–5% per scene per character in focus (10% outliers); at most one per scene | Something happened offscreen (news by a real route, a tie event, a decision ripening). Behaviour shifts; the cause comes out later or never. |
| **Slip** | for masked characters, rolled at scene start | If pressed, or alone with someone trusted, one Core beat shows. Only at or after a deception. |
| **Danger history** | 0–5% per danger category, rolled once at creation | When that kind of danger is in the scene: mood ±1 and a characteristic beat. Never dominates. |
| **Trailing speech** | 0% normally; up to 8% per day when tired (a hungry body, no rest, pain, sickness: 4%) or pondering (curious minds, brooding voices, a day that touched their drive: 3%) | A few ellipses across their lines that day ("I… suppose so."), not every line. Never on anyone who isn't tired or pondering, and never used as a sign of lying. |
| **Punctuation latitude** | worked out per encounter, not rolled | Prose and dialogue may use the full range: a semicolon, an exclamation point, and SOMETIMES a word in capitals for emphasis or a raised voice. `meet` names what suits this person now: exclamations and the odd CAPITAL when someone shouts (rage, panic, a hot temper under pain); easy exclamations for bright, festive, drunk or excitable people; full sentences with a semicolon for measured, formal, solemn or dutiful ones. None for the frozen or stunned; no capitals in a moment of clarity. A latitude, not a tic: a few times a scene at most, never on every line, never as a sign of lying. The narration itself may use them too, sparingly. |
| **Oddity** | 1% per scene, at most one | A small strange behaviour. Uncanny ones only if Strangeness ≥2. Never reveals hidden information. |

## Identity under strain

Everyone has a recognisable way of taking six kinds of strain (humiliation, threat, loss,
betrayal, praise, being cornered), worked out at creation from their traits and voices with a
personal idiosyncrasy, and kept for life: two equally proud people can withdraw, confront, laugh
it off and remember, or reach to mend things. `event` says how they take it; `meet` shows it when
they're pressed; memories keep how it landed, and `meet` brings back what they carry from before
with the person in front of them.

## Ordinary life

Most of life means nothing, and the system says so: about two days in five are ordinary (thirty-odd
kinds: errands, chores, a dull day and glad of it), a third of encounters carry some inconsequential
business (counting under their breath, looking for something they put down), 2–5% hold an honest
misunderstanding that can be cleared up, three in four oddities have an ordinary reason nobody will
mention, and most thoughts are stray. Never treat any of these as a clue. If everything is
suspicious, nothing is.

## Knowledge: what people believe

People hold beliefs, never truth (`references/knowledge.md`). Each belief records its source
(witnessed, heard, read, inferred, imagined), who it came from, how sure they are, how reliable the
source was, when they learnt it, what they take it to mean, and the details that have gone wrong in
it. Seeing it under stress gets details wrong; every retelling may change it (more so from spinners
and gossips); hearing it again makes them surer, true or not; second-hand certainty fades; memory
quietly rewrites the odd detail. Secrets pass only to the trusted. Characters speak only from what
they believe; `meet` says what they believe about the person in front of them.

## Memory and slow change

A character on the scene **always remembers who they are and everything they've lived through
with others**, unless they are dead, comatose, or have amnesia (or a similar state) by an
established cause. The ledger is canon. Feelings fade; memories don't.

What happens to them is felt as **pain or elation**, scaled by how close they are to whoever it
concerns, how sensitive they are and how used to it they've become, and split by how they
process it (the numb feel it late, the contained bottle it). Familiarity dulls repeated pain and
repeated joy, and loosens again with time. **Clarity**, a lucid neutrality, can strike only where
different kinds of moments converge and pain and elation nearly cancel; the disciplined and calm
have a wider margin for it, and those who find it grow toward it. **Inclinations** form from
whatever someone keeps doing, filling quiet moments as habit and, if strong, becoming
compulsion. Traits change only when the pressure of all this outweighs the anchor of their
underlying nature; a change held long enough becomes part of who they are. Nothing holds
forever. People are not clocks: each person has their own pace of grieving, of feelings fading
and of old memories coming back (more on an anniversary, less as they age). See affect.md and time.md.

## Guards against fringe cases

These keep the system honest without fencing it in:
- **Displacement.** Strangers aren't attacked over the NPC's bad day unless the NPC is a
  displacer.
- **Starvation first.** For most people a starved body mutes principle, humour and flattery,
  and makes gifts land harder. Inverted people starve for their cause instead.
- **Charity.** The proud refuse gifts but accept trades; the entitled take help as owed; the
  volatile and proud accept help and resent it.
- **Every addition is audited.** Before a new form, circumstance, quirk, style or
  contradiction is used, run `forge.py audit` and fix what it reports (circumstance.md §6).
- **Pain breaks faces.** Someone badly hurt, in agony or in mortal fear shows their Core, not
  their Face, and drops all levity (no flirting, boasting, joking or performing).
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
python scripts/forge.py meet maren.json --hurt --audience --superior --grieving --drunk --private
python scripts/forge.py event maren.json reunion --about "Bram"
python scripts/forge.py habit maren.json praying
python scripts/forge.py audit
python scripts/forge.py meet maren.json --opposed --their-strength 3 --ground 1
python scripts/forge.py ask maren.json --touched
python scripts/forge.py event maren.json betrayal --note "sold her out to the watch"
python scripts/forge.py affinity maren.json bram.json --tie rival
python scripts/forge.py scene maren.json bram.json
python scripts/forge.py place yard.json --name "The yard" --add "sound:the pump" "animal:the geese"
python scripts/forge.py tie maren.json --to "Bram" --role sibling --loyalty 5
python scripts/forge.py violence maren.json bram.json --place yard.json --victim "Bram" --attacker player --hurt "Bram"
python scripts/forge.py event maren.json loss --about "Bram"
python scripts/forge.py tide world.json
python scripts/forge.py styles
```

`--seed N` before the command makes rolls repeatable; `npc --name X --seeded` makes the same
name always produce the same character. Script output is for the narrator only. Never paste
it into the story.
