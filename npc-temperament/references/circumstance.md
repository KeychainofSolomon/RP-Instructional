# Circumstance

How the situation amends the way a person comes across. Mood decides the band and the person's
nature decides the form. Circumstance (hurt, fear, grief, drink, a funeral, the boss in the room)
then amends that form so it fits the moment, unless their nature is the kind that doesn't bend.
The script does all of this in `meet`. Read this file when narrating without code, or before
adding anything new to the system.

## Contents
1. Tags
2. The circumstances
3. How amendment works
4. Colour, speech, quirks, voices, masks, approaches, asks
5. Lasting states
6. Amendment review (required when adding anything)

## 1. Tags

Every form carries tags describing what it does:

| Tag | Means | Forms |
|---|---|---|
| levity | play, jokes | Teasing-Fond, Bargaining-Humour, Boastful, Flirtatious, Gossipy, Performing, Mockery, Toying |
| display | performing for others | Boastful, Flirtatious, Mercurial, Performing, Preaching, Manipulation, Mockery |
| leisure | needs time and ease | Hospitable, Mentoring, Bargaining-Humour, Curious, Gossipy |
| dominant | taking space, control | Mentoring, Appraising, Boastful, Testing, Contempt, Mockery, Predatory, Righteous Wrath, Territorial, Toying |
| action | moving, doing, striking | Protective, Fear-Aggression, Righteous Wrath, Territorial, Violent Outburst |
| warm / intimate / giving | closeness, care, gifts | Confiding, Forgiving, Generous, Gruff-Kind, Hospitable, Loyal, Protective, Reverent, Teasing-Fond, Tender, Flirtatious |
| formal | set forms, protocol | Respectful, Reverent, Dutiful, Preaching, Ritual, Obstruction |
| cold | distance | Appraising, Indifferent, Testing, Transactional, Cold Refusal, Contempt, Grudge, Obstruction, Predatory |
| guarded / sad / petty / fear / covert / rage | as named | Evasive, Wary, Withdrawn, Suspicion · Melancholic, Withdrawn, Reproach · Envy/Spite · Fear-Aggression · Manipulation, Sabotage · Violent Outburst |
| plain | neutral | Candid, Gruff-Kind, Loyal, Practical, Respectful, Distracted, Dutiful, Transactional |
| wounded | the four wounded responses | Wounded-Selfless, -Panic, -Stoic, -Shock |

Contradiction sides and circumstance colour carry tags too (section 4).

## 2. The circumstances (in priority order: higher wins)

| # | Circumstance | Comes from | Blocks | Becomes (Kind / Middle / Hostile) | Exempt or softened by nature |
|---|---|---|---|---|---|
| 1 | **hurt** | badly hurt, in agony, in mortal fear | everything but wounded | their wounded response | — (pain breaks every face) |
| 2 | **frozen** | violence → Freeze | levity, display, leisure, action, dominant, giving, intimate | Withdrawn / Withdrawn / Grudge | — |
| 3 | **afraid** | violence → Flight; danger they're scarred by; a yield-or-flee stratagem | levity, display, leisure, dominant | Protective / Wary / Fear-Aggression | exempt: Volatility ≤ −2. Dominance ≥ 3 blusters instead |
| 4 | **enraged** | violence → Fury; Hostile with Volatility ≥ 2 and about-you ≤ −3 | warm, intimate, leisure, giving, sad (Protective allowed) | Protective / Dutiful / Righteous Wrath | Discipline ≥ 2: held very still, not loud |
| 5 | **stunned** | violence → Shock | levity, display, leisure, dominant, action | Practical / Distracted / Cold Refusal | — |
| 6 | **tending** | violence → Tending | levity, display, leisure, dominant, giving, intimate, formal, covert, petty, fear, rage | Protective / Distracted / Cold Refusal | — |
| 6b | **protecting** | violence → Shield or Covering | levity, display, leisure, giving, intimate, sad | Protective / Wary / Territorial | — |
| 7 | **grieving** | a loss (length by relationship; colour by processing style) | levity, display, leisure; Fear-Aggression becomes Reproach or Grudge | Tender or Practical / Melancholic / Reproach or Grudge | gallows humour if they laugh at the wrong moments, or Energy and Openness ≥ 2 |
| 8 | **sick** | a day of falling sick (lasts 2–4 days) | display, levity, action | Practical / Distracted / Cold Refusal | — |
| 9 | **exhausted** | a tired day, no rest | display, action, leisure | Practical / Distracted / Cold Refusal | — |
| 10 | **intoxicated** | drink or drugs (rest of the day) | swaps: Dutiful→Distracted, Wary→Flirtatious or Melancholic, Cold Refusal→Mockery, Evasive→Confiding, Withdrawn→Melancholic, and more | — | exempt: Discipline ≥ 3 (very careful about every word) |
| 11 | **starving** | Survival Starved, not sick | giving | Practical / Transactional / Grudge | Warmth ≥ 3 gives what they can't spare |
| 12 | **solemn** | a funeral, rite, sacred place (violence → Ritual too) | levity, display, leisure, action (Preaching allowed) | Reverent / Ritual / Cold Refusal | exempt: Hollow, or a quarter Predator (unmoved; the dissonance stays) |
| 13 | **festive** | a celebration | swaps for the outgoing: Wary→Curious, Dutiful→Gossipy | — | — |
| 14 | **superior** | someone they answer to is present | display, levity, rage; Mockery→Contempt, Toying→Cold Refusal, Territorial→Obstruction, Boastful→Dutiful | Respectful / Dutiful / Obstruction | exempt: Dominance ≥ 3 (talks over them) |
| 15 | **intimate** | in private, trust ≥ guard + 2 | swaps: Wary→Confiding, Withdrawn→Melancholic, Dutiful→Candid, Evasive→Confiding, Performing→Mercurial | — | — |
| 16 | **public** | an audience | swaps: Confiding→Loyal, Tender→Practical (unless Energy ≥ 2 or Warmth ≥ 3), Reproach→Cold Refusal (unless Dramatic) | — | — |
| 17 | **duty** | on post, working | swaps: Flirtatious→Dutiful (unless Discipline ≤ −1), Gossipy→Dutiful, Distracted→Wary, Hospitable→Practical, Bargaining-Humour→Transactional | — | — |

## 3. How amendment works

1. Take the form the person would show (band, voice, face).
2. If it fits every active circumstance (no blocked tag, or blocked only where their nature
   softens it), apply any swaps that also fit, and stop.
3. Otherwise try, in order: swaps for this form, the replacement of each circumstance it clashes
   with, every active circumstance's replacement, then a neutral fallback for the band. Take the
   first that fits **all** active circumstances.
4. If nothing fits them all, the lowest-priority circumstance **yields**: it stays as colour
   only, and the search repeats.

Higher-priority circumstances therefore always win. Frozen rage stays frozen, and the rage shows
as colour ("held very still; every word measured"). The result is always explainable: "Grudge,
amended from Fear-Aggression, because grief."

## 4. Everything else the circumstance touches

- **Colour.** Each circumstance adds a short description ("eyes on the exits", "pale, slow,
  short of breath"). Each is tagged and dropped if a stronger circumstance blocks it, so a
  frozen person is never also "loud, close, leaning in". The contradiction side is filtered the
  same way: no "lightness under it" in frozen rage, no "can't keep still" while frozen.
- **Trace of another voice.** A blended person shows a trace of their next-strongest voice
  (a quarter or more), amended by the same circumstances.
- **Intensity.** "barely" Cool, "fully" Warm, "openly" or "utterly" Hostile, "deeply" Kind,
  from where the mood sits in its band.
- **Speech.** One mode each for volume (loud, hushed, soft, low, silent), flow (clipped, short,
  trailing, rambling, broken by breath, flat) and register (formal, procedural). The highest-priority
  circumstance claims each.
- **Quirks.** Idle and social quirks stop under stress (hurt, frozen, afraid, enraged, stunned,
  tending, grieving, solemn, superior). Stress quirks surface (never sits with back to a door,
  third person when nervous, touches a lucky object, laughs at the wrong moments). Compulsive and
  constant quirks persist. Social quirks grow in festivity and drink. A dead person's belonging
  surfaces in grief.
- **Voices.** A circumstance can call a voice forward: fear the Vigilant, Sensitive or Devoted
  side; rage the Commanding, Mercurial, Zealot or Predator side; grief the Serious, Mercurial,
  Self-Sacrificing or Devoted side; drink the Mercurial, Adventurous, Dramatic or Leisurely side;
  a party the Dramatic or Adventurous side. It must be at least a quarter of them.
- **Masks.** Each circumstance changes how easily a face slips: hurt drops it outright; rage,
  drink, grief, fear and intimacy thin it; formality, a superior and an audience thicken it.
- **Approaches.** Each circumstance shifts approach scores: humour lands badly on the grieving,
  hurt, enraged and solemn; patience lands well on the afraid, sick, tired and stunned;
  deference helps with the enraged and in solemn or superior company; drink and festivity make
  humour and familiarity land better.
- **Asks.** No one grieving raises anything but their grief; no one sick raises anything but
  their health.
- **Compulsions.** Grief feeds vices: each grieving day adds temptation to a substance, gambling,
  cruelty or lust compulsion.

## 5. Lasting states

Grief (8–14 days after a loss), sickness (2–4 days after falling ill) and intoxication (the rest of
the day) are tracked on the ledger and tick down with each day roll. Shaken states from violence
last the rest of that day. Exhaustion comes from the day itself.

## 6. Amendment review (required when adding anything)

The system is meant to grow. Every addition must be reviewed against every circumstance before it
is used, so that a new trait never ends up flirting while shot.

When you add a **form**, **circumstance**, **quirk**, **style**, **contradiction pair** or
**violence response**:
1. Give it its tags (forms, colour, contradiction sides), its kind (quirks), its block,
   replacement, swaps, exemptions, colour tags and speech category (circumstances).
2. Run `python scripts/forge.py audit`. It checks every form under every combination of up to three
   circumstances, in every band, across 35 personality profiles (over 4.6 million cases), plus
   all colour and contradiction text. It fails on any form or colour that still clashes, any
   circumstance that can't satisfy itself, any missing tag, kind, side text or replacement, and
   any violence response without a circumstance.
3. Fix what it reports, then also read a few results with your own judgement. The audit proves
   consistency, not sense: it can't tell that a terrified braggart should bluster rather than go
   quiet. Spot-check the new piece in two or three situations that would test it.
