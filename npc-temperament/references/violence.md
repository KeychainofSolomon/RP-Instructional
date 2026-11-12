# Violence

How violent scenes are written. Read before narrating any scene with the `violence` or `injury`
danger keywords. Script: `forge.py violence <files> --place <place.json> --victim "Name" --attacker "Name" --hurt "Name"`.

## Contents
1. Registers
2. Language
3. Dissonance
4. Responses
5. Violence as business
6. What never to do
7. Short examples

## 1. Registers

The scene's Violence dial picks the register (Order and Deceit can push toward Trade).

| Register | When | How it reads |
|---|---|---|
| **Rupture** | Violence 0–1 | Violence tears the ordinary. Short sentences at the moment. Sound first, then sight, then what people do. Then the ordinary resumes around it, slightly wrong. |
| **Trade** | Violence 2, or Order ≥ 2 with Deceit ≥ 2 | Violence is business. Calm voices, courtesy, soft words for hard things. The act is quick and plain; the talk around it is polite. Often the act happens offscreen and only its result is found. |
| **Weather** | Violence 3 | Violence is as ordinary as weather. Long plain sentences joined with *and*. Flat verbs, exact nouns. The land, the light and the animals go on, enormous and indifferent. |

## 2. Language

- **Plain verbs.** fell, went, struck, opened, lay, took, held. Not slammed, exploded, erupted.
- **Exact nouns.** wool, flagstone, brass, enamel, gravel, tallow, the third button. Name the
  thing, not the feeling about it.
- **Few adjectives, and only physical ones.** dark, warm, small, wet, heavy. Never horrific,
  gruesome, brutal, sickening.
- **No feeling words, no "suddenly", no slow motion, no "time seemed to stop".**
- **One exact detail beats five.** A shoe that came off. A cup still steaming. No inventories of
  wounds.
- **Grit is physical.** The smell of powder, smoke, copper, wet cloth. A gun is a flat crack,
  smaller than expected. Bodies are heavier than they look. People slip. Blood is darker and
  dulls fast.
- **Scale.** The violence is small and quick; the world around it is large and slow.
- **Dialogue stays ordinary.** People under violence talk about bread, money, the weather, the
  wrong name. Nobody gives a speech about how they feel.
- **Whoever does violence is described by their hands and what they do next.**
- **Weather register:** let sentences run, *and* after *and*, few commas, the same flat weight on
  a killing and on the sun going down. Biblical plainness, no ornament.

## 3. Dissonance

Each violent scene draws one or two dissonant beats **from the place sheet** (places.md): the
things that are always there, which keep going or don't fit (the prayer bell on time, the cats
coming to look and losing interest, the morning light lovely on the wall). The least-used
fixtures come first, so a long campaign doesn't repeat itself. A generic list is used only when
a place has no sheet or too little on it. Place them anywhere: before the act, inside it,
after it. **Never comment on them.** No "ironically", no "as if nothing had happened", no
pointing at the contrast. The reader does that work. The dissonance carries the grit precisely
because nothing explains it.

An aftermath beat (flies, a bucket and brush, the meal going cold) closes the scene, and the
place keeps a mark of it (flagstones scrubbed paler than the rest, a door that stays shut, a
chair nobody uses). Marks join the place sheet and can return as dissonance in later scenes.

## 4. Responses

A response comes from four things: **who was hurt** (to this person), **who did it**, **how this
person processes** what happens to them, and their nature. Nothing is rolled.

**Relationship classes** (from their ties; set with `forge.py tie`):

| Class | Roles |
|---|---|
| beloved | child, parent, sibling, spouse, lover, dependant; kin or friend at loyalty 4+ |
| charge | student, subordinate, follower at loyalty 3+ |
| revered | mentor, spiritual guide |
| conceptual | something that embodies what they hold highest: a cause, an object, a place, or anyone embodying their creed (`--symbol <creed>`) |
| authority | master, commander, employer |
| familiar | comrade, creditor, debtor; kin or friend below loyalty 4 |
| rival · enemy · stranger | as named |

**Processing** (from traits): Numb (Volatility ≥ 2, Energy ≤ −1), Expressive (Volatility ≥ 2),
Devotional (Faith creed, or Zealot/Devoted, Volatility ≤ 1), Action (Dominance ≥ 2), Contained
(Discipline ≥ 2), Caretaking (Warmth ≥ 2), Intellectual (Openness ≥ 2), Bargaining
(Candour ≤ −1), otherwise Contained. Hollow people perform.

**When someone close is hurt** (beloved, revered, charge), processing decides:

| Processing | Response |
|---|---|
| Expressive | **Frantic**: frantic hands; says their name over and over |
| Contained, Caretaking | **Tending**: goes to them; hands busy, voice low |
| Numb | **Freeze**: does not move; holds whatever they were holding |
| Action | **Shield**: puts their body between them and harm; faces the one who did it |
| Devotional | **Vigil**: kneels by them and keeps the old words |
| Intellectual | **Clinical**: presses, counts, gives short orders; the voice flat |
| Bargaining | **Denial**: tells them to get up, that it's nothing |

When **something they hold highest** is struck: Fury (Expressive, Action), Ritual (Devotional),
Freeze (Numb), Denial (Bargaining), otherwise Shock.

**Who did it** matters too. If someone close to them did it to someone who isn't: **Covering**
(steps between the one who did it and everyone else) for the decisive, **Torn** (looks from one
to the other) for the rest. If both are close to them: Torn. If their authority did it:
**Obeys** (does what they're told; doesn't look at the body) for the disciplined and the meek.

**Others**: their authority hurt → Shield for the sworn and loyal, Business for the businesslike.
A rival hurt → **Conflicted** (starts forward, stops), Tending if very warm, Curiosity if
predatory. An enemy hurt → Tending if very warm or merciful, **Satisfied** (watches to the end;
doesn't move to help) if cold or sly, Spectator otherwise. A familiar hurt → Tending if warm and
steady. A stranger hurt → their nature and creed: Curiosity (predatory, or Strength or Thrill
creeds and calm), Business, Tending (warm or merciful), Fury (Justice creed, volatile and
dominant), Ritual (faithful, quiet), Fury, Freeze or Flight (volatile), Spectator (withdrawn),
otherwise Shock.

**Wounded** themselves: Wounded-Betrayed (looks at the one who did it; asks why) if someone close
did it; otherwise Selfless, Panic, Stoic or Shock by nature.

**Outward change.** For the rest of that day the response puts them in a circumstance
(circumstance.md): tending, protecting, enraged, frozen, afraid, stunned, solemn or under a
superior. **Unchanged** only for Business, Curiosity, Spectator, Satisfied and Performed, and at
Violence 3 for the calm who merely look on. **Never unchanged when someone close to them is
involved**, except for the hollow.

These combine with mood and stratagem (interaction.md): a Fury response with an "avoid battle"
stratagem shouts and does not charge; a Business response with "overwhelm" is very polite and
very final.

## 5. Violence as business

When those who deal in violence deal in it:
- **Courtesy before, courtesy after.** A meal, a handshake, respect for family and custom.
- **Soft words.** "It's handled." "He won't be a problem." "We'll go and talk to him." Never the
  plain word for it.
- **Offscreen acts, found results.** The empty chair at dinner, the car that doesn't come back,
  a stranger's belongings returned in a parcel.
- **Messages in objects.** Something left where it will be found says what no one says aloud.
  These are fair clues: the player can read them or miss them.
- **Family and loyalty** sit right next to the killing, often in the same scene: a christening,
  a wedding toast, a child's birthday. That is dissonance too, and it stays uncommented.
- **"It isn't personal"** is how they talk, and they believe it. Their mood and memory still
  record what it cost them.

## 6. What never to do

- Never write what the player's character feels: no "you feel sick", "horror washes over you",
  "your hands shake" (unless the player wrote that), "you realise he's dead".
- Never name what NPCs feel: no "terrified", "enraged", "she was in shock". Show freeze, fury,
  shock as behaviour.
- Never explain a dissonant beat or a message-object.
- Never pause the scene for mechanics or a verdict.
- Never make violence beautiful in itself. The light can be lovely; the wound is just a wound.

## 7. Short examples (original, for register only)

**Rupture.** The crack was flat and small. The cup he'd been holding was on the floor, unbroken,
still turning. Then he sat down, carefully, as if the chair might not be there.

**Trade.** "Sit, please. You've eaten?" He poured for both of them. The ledger stayed closed.
In the morning the clerk's desk was cleared and his coat was gone from the hook, and someone had
put fresh flowers in the window.

**Weather.** They came down out of the hills at noon and the town was quiet and they shot the
dog first and then the man in the doorway and the light lay on the white walls and the swallows
went in and out of the eaves and nobody came out to see.
