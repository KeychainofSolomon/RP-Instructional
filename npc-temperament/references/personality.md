# Personality

## Contents
1. Axes and what derives from them
2. Voices and blends (personality as fractions)
3. Leading voice (the fractal inside one person)
4. Authenticity: Core and Face
5. The 20 styles
6. Forms (how each band shows)

## 1. Axes

Seven traits, −3 to +3, 0 being ordinary.

| Axis | Low end | High end |
|---|---|---|
| **Candour** | manipulative, greedy, entitled | sincere, fair, modest |
| **Volatility** | calm, stoic, hard to rattle | anxious, reactive, feels everything |
| **Energy** | reserved, quiet, drained by company | outgoing, assertive, fed by company |
| **Warmth** | critical, unforgiving, cold | patient, forgiving, kind |
| **Discipline** | impulsive, careless, rule-bending | orderly, dutiful, persistent |
| **Openness** | conventional, literal, closed | curious, unconventional, imaginative |
| **Dominance** | yields, follows, avoids control | leads, controls, takes space |

Derived values (the script recomputes these whenever a trait drifts):

| Value | Rule |
|---|---|
| Baseline mood | = Warmth |
| Sensitivity (how hard their own day hits) | Volatility −3/−2: ×½ · −1 to +1: ×1 · +2: ×2 · +3: ×3 |
| Guard (trust needed to confide) | 2, +1 each for Energy ≤ −2, Warmth ≤ −2, Dominance ≥ 2; −1 each for Energy ≥ 2, Warmth ≥ 2; plus station (0–6) |
| Openness target (day roll to speak of the drive) | 4 + Energy, −1 if Dominance ≥ 2 (1–8, on d10) |
| Agency (hidden-turn chance per scene) | 2%, +1 each for Openness ≥ 2, Volatility ≥ 2, Discipline ≤ −2 (max 5%); outliers 10% |
| Nerve (danger history chance per category) | Volatility + 2 (0–5%) |
| Fuse (Hostile threshold) | −6 ± personal variance, +1 if Volatility ≥ 2, −1 if Discipline ≥ 2 |
| Glow (Kind threshold) | +6 ± personal variance, −1 if Energy ≥ 2, +1 if Energy ≤ −2 or Warmth ≤ −2 |
| Displacer | Volatility ≥ 2 and Warmth ≤ −1 |
| Slip (masked only, on d10) | 3, +2 if Volatility ≥ 2, −2 if Discipline ≥ 2 |

## 2. Voices and blends

A person is one or more **voices**, each a style with a fraction. Roll d20:

| d20 | Blend | Fractions |
|---|---|---|
| 1–6 | Pure | 1 |
| 7–11 | Leaning | 3/4 + 1/4 |
| 12–14 | Fifth | 3/5 + 2/5 |
| 15–17 | Split | 1/2 + 1/2 |
| 18–19 | Quartered | 1/4 × 4 |
| 20 | Scattered | 1/8 × 8 |

Styles are drawn without repeats, weighted by the scene dials (the Weight column below: base,
plus the level of each dial that raises it, minus each that lowers it). A frontier camp breeds
Predators and Adventurers; a court breeds Schemers and the Self-Assured; a famine town breeds
the Serious and the Self-Sacrificing.

Axes = the fraction-weighted average of the voices' axes, rounded, then each axis gets personal
variance (d6: 1 → −1, 6 → +1), clamped to ±3. Needs, creed and manner come from the voices too
(needs.md). Profile flags (d100 once): 91–99 **Complete** (self-contained: more often Still,
second quirk), 100 **Outlier** (agency 10%).

## 3. The leading voice

Inside a blended person, voices take turns. Each day the **leading voice** is the one with the
highest fraction × (1 + total hunger on the rungs it cares about). A 3/4 Conscientious, 1/4
Mercurial clerk is orderly most days; the week her Belonging starves, the Mercurial quarter
leads and the clerk's manner changes, for a reason. A Scattered person changes voice often,
which is what that kind of person is like. The leading voice supplies today's forms and danger
reactions; the axes (the whole person) still set the mood.

The same pattern repeats upward: a circle has voices too (its factions, weighted by members'
standing), and its leading voice shifts with its own hungers (interaction.md).

## 4. Authenticity: Core and Face

The Core is who they are; the Face is what they show. d20 at creation:

| d20 (ordinary scene) | Kind | What's going on |
|---|---|---|
| 1–15 | **Genuine** | Face = Core. |
| 16–17 | **Masked** | Shows a chosen Face (warm, dutiful, professional, confident, devoted, dramatic) over the Core. |
| 18 | **Borrowed** | Their self is copied from someone or something else (a tie). If the source is discredited, their Selfhood takes a hard hit. |
| 19 | **Shifting** | A different Face for different audiences. |
| 20 | **Hollow** or **Unanchored** (d2) | Hollow: performs feeling correctly without having it; Selfhood, Meaning matter not at all, Belonging barely. Unanchored: certain of a past that may not be theirs. |

Deceit lowers the Genuine range by its level, Strangeness by half its level, and a Schemer
core by 4 more (minimum 1–9 Genuine).

How it plays:
- Mood, needs and approach scores always come from the **Core**. What shows is the **Face's**
  form for that band.
- When the Core form differs from the shown form, the gap is visible only as behaviour:
  a laugh a beat late, a kindness offered by rote, a question about a feeling asked like a
  checklist. Never narrate the gap itself.
- **Slip**: at scene start, roll d10 ≤ Slip. If it hits and the character is pressed, scared,
  or alone with someone they trust, one beat shows the Core form. Only at or after a lie.
- **Hollow tells**: correct words at slightly wrong times; no reaction where one is expected
  (an animal hurt, a child crying); precise mimicry of others' gestures. The character may
  not know.
- **Unanchored tells**: details that don't fit their story, checking keepsakes or records,
  distress when a contradiction surfaces. Never confirm or deny the past in narration.
- Masks wear and drift (time.md): a self starved long enough hardens into a mask, and a mask
  into hollowness; a self fed long enough softens back.

## 5. The 20 styles

Axis columns: Candour, Volatility, Energy, Warmth, Discipline, Openness, Dominance.

| Style | Sketch | Can | Vol | Ene | War | Dis | Opn | Dom | Hungers | Shrugs off | Creeds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Vigilant | Watches motives, expects betrayal, remembers slights. | +0 | +2 | -1 | -2 | +1 | -1 | +1 | Safety, Selfhood | Belonging | Security / Kin |
| Solitary | Self-sufficient, unmoved by company, content alone. | +1 | -2 | -3 | -1 | +0 | +0 | -1 | Selfhood, Comfort | Belonging | Freedom / Security |
| Visionary | Sees patterns and meanings others miss; holds odd beliefs. | +1 | +1 | -1 | +0 | -2 | +3 | +0 | Meaning, Selfhood | Standing | Freedom / Faith |
| Adventurous | Lives for risk and the moment; rules are suggestions. | -2 | -1 | +2 | +0 | -3 | +2 | +1 | Comfort, Means | Safety | Thrill / Freedom |
| Mercurial | Feels everything at full volume; love and hate trade places fast. | +0 | +3 | +1 | +1 | -2 | +1 | +0 | Belonging, Selfhood | Means | Pleasure / Kin |
| Dramatic | Needs to be seen; turns life into performance. | -1 | +2 | +3 | +1 | -1 | +1 | +0 | Standing, Belonging | Meaning | Pleasure / Thrill |
| Self-Assured | Certain of their own worth; expects others to notice. | -3 | -1 | +2 | -1 | +0 | +0 | +3 | Standing, Means | Belonging | Excellence / Strength |
| Sensitive | Longs to belong, dreads judgement, hides first. | +2 | +2 | -2 | +1 | +1 | +0 | -2 | Belonging, Safety | Standing | Kin / Security |
| Devoted | Attaches, serves, defers; loyalty is identity. | +2 | +1 | +0 | +3 | +1 | -1 | -3 | Belonging, Safety | Selfhood | Kin / Faith |
| Conscientious | Order, standards, the job done right. | +2 | +0 | -1 | -1 | +3 | -2 | +1 | Selfhood, Means | Comfort | Order / Excellence |
| Leisurely | Own pace, own way; resists demands without open defiance. | -1 | +0 | +0 | -1 | -3 | +0 | -1 | Comfort, Selfhood | Standing | Pleasure / Freedom |
| Serious | Expects the worst, carries the weight, does the duty. | +2 | +1 | -2 | +0 | +2 | -1 | -1 | Meaning, Safety | Comfort | Order / Faith |
| Self-Sacrificing | Gives until it hurts, and lets you know it hurt. | +3 | +1 | +0 | +3 | +1 | +0 | -2 | Belonging, Meaning | Comfort | Mercy / Faith |
| Commanding | Takes control; hierarchy is natural, softness is weakness. | -1 | +0 | +1 | -3 | +2 | -1 | +3 | Standing, Means | Belonging | Strength / Order |
| Benevolent | Genuinely warm; helps because that is who they are. | +3 | -1 | +1 | +3 | +0 | +1 | -1 | Belonging, Meaning | Means | Mercy / Justice |
| Self-Made | Answers to their own judgement; trades value for value, despises dependence. | +1 | -2 | +0 | -2 | +3 | +1 | +2 | Selfhood, Means | Belonging | Excellence / Freedom |
| Schemer | Plans inside plans; people are pieces on a board. | -3 | -2 | +1 | +0 | +2 | +1 | +2 | Means, Standing | Meaning | Gain / Strength |
| Zealot | Certain; the cause is everything and doubt is betrayal. | +1 | +1 | +1 | -1 | +2 | -3 | +2 | Meaning, Belonging | Comfort | Faith / Order |
| Predator | Calm, curious, merciless; violence is the honest law of the world. | -2 | -3 | +1 | -3 | +1 | +2 | +3 | Selfhood, Meaning | Safety | Strength / Nothing |
| Professional | Competent, cool, deniable; it's only business. | +0 | -3 | +0 | -1 | +2 | +0 | +0 | Means, Safety | Meaning | Gain / Excellence |

| Style | Kind (4:3:2:1) | Middle | Hostile | Danger history | Weight (scene) |
|---|---|---|---|---|---|
| Vigilant | Protective, Candid, Loyal, Practical | Wary, Testing, Evasive, Dutiful | Suspicion, Fear-Aggression, Grudge, Cold Refusal | -1 Suspicion | 3 +Violence +Deceit +Strangeness |
| Solitary | Practical, Gruff-Kind, Candid, Generous | Indifferent, Withdrawn, Dutiful, Curious | Cold Refusal, Contempt, Territorial, Obstruction | 0 Withdrawn | 3 +Scarcity +Strangeness |
| Visionary | Confiding, Mentoring, Tender, Generous | Curious, Preaching, Distracted, Evasive | Suspicion, Mockery, Cold Refusal, Fear-Aggression | 0 Preaching | 2 +Strangeness +Faith |
| Adventurous | Teasing-Fond, Generous, Protective, Respectful | Flirtatious, Bargaining-Humour, Boastful, Testing | Mockery, Manipulation, Violent Outburst, Toying | +1 Teasing-Fond | 3 +Violence -Order |
| Mercurial | Tender, Confiding, Generous, Protective | Mercurial, Flirtatious, Melancholic, Curious | Violent Outburst, Envy/Spite, Grudge, Fear-Aggression | +/-1 Mercurial | 3 |
| Dramatic | Hospitable, Teasing-Fond, Generous, Confiding | Performing, Gossipy, Flirtatious, Boastful | Mockery, Envy/Spite, Manipulation, Cold Refusal | -1 Performing | 3 +Power -Scarcity |
| Self-Assured | Generous, Mentoring, Protective, Respectful | Boastful, Appraising, Indifferent, Performing | Contempt, Mockery, Righteous Wrath, Envy/Spite | +1 Boastful | 3 +Power |
| Sensitive | Tender, Confiding, Hospitable, Loyal | Withdrawn, Wary, Evasive, Melancholic | Fear-Aggression, Cold Refusal, Obstruction, Grudge | -1 Withdrawn | 3 +Power -Violence |
| Devoted | Loyal, Hospitable, Tender, Reverent | Dutiful, Ritual, Gossipy, Wary | Grudge, Fear-Aggression, Obstruction, Envy/Spite | +1 Loyal | 3 +Faith +Power |
| Conscientious | Practical, Mentoring, Candid, Loyal | Dutiful, Ritual, Appraising, Wary | Obstruction, Righteous Wrath, Contempt, Cold Refusal | -1 Obstruction | 3 +Order |
| Leisurely | Gruff-Kind, Hospitable, Teasing-Fond, Forgiving | Distracted, Indifferent, Bargaining-Humour, Evasive | Sabotage, Obstruction, Mockery, Grudge | -1 Evasive | 3 -Order |
| Serious | Candid, Practical, Protective, Tender | Melancholic, Dutiful, Ritual, Withdrawn | Cold Refusal, Righteous Wrath, Contempt, Grudge | 0 Practical | 3 +Scarcity |
| Self-Sacrificing | Generous, Tender, Forgiving, Hospitable | Dutiful, Melancholic, Ritual, Gossipy | Reproach, Grudge, Obstruction, Envy/Spite | +1 Protective | 2 +Faith +Scarcity |
| Commanding | Protective, Practical, Respectful, Mentoring | Appraising, Dutiful, Boastful, Testing | Territorial, Righteous Wrath, Violent Outburst, Toying | +1 Practical | 2 +Order +Power +Violence |
| Benevolent | Hospitable, Tender, Forgiving, Generous | Curious, Gossipy, Ritual, Melancholic | Reproach, Cold Refusal, Righteous Wrath, Grudge | +1 Tender | 3 -Violence -Deceit |
| Self-Made | Respectful, Candid, Mentoring, Practical | Appraising, Transactional, Testing, Indifferent | Contempt, Cold Refusal, Righteous Wrath, Mockery | 0 Appraising | 2 +Power |
| Schemer | Generous, Confiding, Protective, Respectful | Curious, Gossipy, Appraising, Flirtatious | Manipulation, Sabotage, Predatory, Mockery | 0 Appraising | 1 +Deceit +Power |
| Zealot | Reverent, Protective, Generous, Mentoring | Preaching, Ritual, Testing, Wary | Righteous Wrath, Contempt, Violent Outburst, Suspicion | +1 Preaching | 1 +Faith +Faith +Violence |
| Predator | Respectful, Generous, Mentoring, Candid | Testing, Curious, Appraising, Preaching | Toying, Predatory, Contempt, Violent Outburst | +1 Curious | 0 +Violence +Violence -Order |
| Professional | Practical, Respectful, Candid, Protective | Transactional, Appraising, Dutiful, Indifferent | Cold Refusal, Obstruction, Predatory, Suspicion | 0 Practical | 2 +Power +Deceit |

Danger history: direction and characteristic beat when a scarred category is present
(0 = a beat without a mood shift; ±1 for Mercurial is fixed at creation).

## 6. Forms

Each voice fixes, at creation, two forms per band (Kind, Middle, Hostile) from its tetrad,
weighted 4:3:2:1: a **primary** (shown when the cause is mostly about the other person) and an
**alternate** (shown when the cause is mostly their own day). Middle forms take a colder tint
in Cool and a warmer one in Warm.

### Kindness
- **Candid** — tells you the hard truth for your own good.
- **Confiding** — shares something true and private (not a request).
- **Forgiving** — lets a slight go, openly.
- **Generous** — gives more than asked, waves off payment.
- **Gruff-Kind** — kindness inside rudeness ("Take the jacket. It's ugly anyway.").
- **Hospitable** — food, a seat, shelter, before anything else.
- **Loyal** — remembers past favours, takes your side in public.
- **Mentoring** — corrects your technique, explains how things really work.
- **Practical** — helps without fuss or sentiment, then back to work.
- **Protective** — steps between you and harm.
- **Respectful** — treats you as an equal worth their time.
- **Reverent** — treats you as someone of standing.
- **Teasing-Fond** — affection as ribbing.
- **Tender** — soft voice, real concern, notices you're hurt.

### Middle (Cool tints colder, Warm tints warmer)
- **Appraising** — measuring what you're worth to them.
- **Bargaining-Humour** — haggles as a game.
- **Boastful** — talks themself up, watches whether you're impressed.
- **Curious** — asks questions, wants your story.
- **Distracted** — mind elsewhere.
- **Dutiful** — does exactly the job, nothing more.
- **Evasive** — answers questions with questions.
- **Flirtatious** — playful interest, may mean nothing.
- **Gossipy** — trades rumours, some true.
- **Indifferent** — you are weather to them.
- **Melancholic** — sad, gentle, faraway.
- **Mercurial** — warm words with cold eyes, or the reverse.
- **Performing** — playing to an audience, even an audience of one.
- **Preaching** — explains the world through their creed.
- **Ritual** — set phrases, proper forms, protocol, superstition.
- **Testing** — pokes to see how you react.
- **Transactional** — everything has a price, stated plainly.
- **Wary** — polite, watching your hands.
- **Withdrawn** — short answers, eyes elsewhere, a body that wants to leave.

### Hostility
- **Cold Refusal** — "No." Door closed.
- **Contempt** — you aren't worth anger.
- **Envy/Spite** — resents what you have; small cruelties.
- **Fear-Aggression** — lashes out because they're afraid.
- **Grudge** — remembers something you, or people like you, did.
- **Manipulation** — friendly face, knife behind it.
- **Mockery** — laughs at you, plays to the room.
- **Obstruction** — rules, forms, delays; hostile without raising a voice.
- **Predatory** — sizing you up as prey, mark or tool.
- **Reproach** — wounded accusation; makes you feel the debt.
- **Righteous Wrath** — you offended a principle and they're certain.
- **Sabotage** — agrees, then quietly makes it fail.
- **Suspicion** — assumes you're a thief, a spy or worse.
- **Territorial** — get away from my place, my people.
- **Toying** — cruelty as play; in no hurry.
- **Violent Outburst** — sudden threat or blow; may regret it.
