# Places

A place sheet records what is always there: the things that keep going when something happens,
and the marks that what happened leaves behind. Violent scenes draw their dissonance from it.

## Making one

```
python scripts/forge.py place warming.json --name "Warming room" --dials 0,2,2,2,3,1,1 --add "sound:the prayer bell" "animal:the monastery cats" "light:the morning light through the shutters" "routine:the bread run before Lauds" "object:the old copper kettle" "smell:woodsmoke and wet wool" "person:the old porter"
```

Kinds: **sound, light, animal, routine, object, smell, taste, person, weather**. Aim for six to ten
things a regular would name without thinking. They should belong to this place and no other.

## How it's used

- **Dissonance**: each violent scene draws one or two fixtures, least-used first, and frames
  them by kind ("the prayer bell goes on, exactly on time", "the cats come to look, then lose
  interest", "the light is lovely"). Nothing is ever explained.
- **Marks**: each violent scene's aftermath leaves something the place keeps (a stain that won't
  scrub out, a door that stays shut, a chair nobody uses). Marks join the sheet and can surface
  in later scenes ("a door that stays shut; nobody mentions it"). The place remembers.
- **Dials**: a place can carry its own scene dials; `violence --place` uses them for the register
  if none are given.

If a scene happens somewhere without a sheet, make one before the scene if you can. The generic
list exists only as a fallback, and it will repeat over a long campaign.
