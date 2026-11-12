# Knowledge

What people believe, and how they came to believe it.

## 1. Four domains, kept apart

1. **What happened**: the campaign's own record of events. No person holds it.
2. **What each person believes**: their beliefs, below. Never marked true or false.
3. **What the narrator is told**: briefs say what someone believes and how they'd tell it, never
   whether it's so.
4. **What the player has found out**: only what has reached them in play.

Characters act and speak only from domain 2. A person can be certain and wrong.

## 2. A belief

| Field | Meaning |
|---|---|
| subject | what it's about ("you" means the player) |
| claim | what they believe |
| source | witnessed, heard, read, inferred, imagined |
| from | who they had it from, and anyone else they've heard it from since |
| day, last | when they learnt it, when it was last repeated to them |
| confidence | how sure they are; told to the narrator as certain, sure, fairly sure, unsure, half-believes |
| reliability | how far they trusted the source when they heard it |
| meaning | what they take it to mean: proof of what they thought, a warning, none of their business, a lie being spread, an opportunity, a sign, a scandal worth repeating, a wrong to put right, a shame on someone's people, a joke, a worry (from traits, voices and creed) |
| distortions | what's gone wrong in it: the wrong person, timing, numbers, place, order, grown or shrunk in the telling, a reason nobody gave |
| hops | how many tellings from the source |
| secret | kept to themself |

## 3. How beliefs move

- **Confidence** starts from the source (witnessed .85, read .6, heard .5, inferred .45,
  imagined .3), scaled by the source's reliability (for hearsay, their trust in the teller), and
  nudged by how credulous they are (the warm and earnest believe more readily; the vigilant,
  schemers and the suspicious less).
- **Witnessing** gets a detail wrong 10% of the time, 35% under stress; imagining, 30%.
- **Telling** passes the teller's surest version on as hearsay. Each telling may add a distortion
  (25%; 40% from spinners, palterers and manipulators, who tend to make it bigger or add a motive;
  more again from gossiping manners). Hearing the same claim again makes them surer, true or not.
- **Secrets** pass only to someone the teller trusts strongly.
- **Each day** second-hand certainty fades if nothing repeats it, and memory now and then rewrites
  a detail of anything, even what they saw.

This is what makes rumours drift, false accusations take hold, eyewitnesses disagree, and secrets
outlive the people who first kept them.

## 4. Commands

```
forge.py learn FILE --subject S --claim C --source witnessed|heard|read|inferred|imagined [--from NAME] [--secret] [--stressed]
forge.py tell TELLER HEARER --about S
forge.py beliefs FILE [--about S]
```

## 5. Audit

Checks that confidence stays in range, no belief stores whether it's true, what was seen is held
more surely than hearsay, rumours carry more wrong details after five tellings than after one,
secrets don't pass to the untrusted, and nobody passes on what they don't know.
