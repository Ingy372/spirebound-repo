# Rules for four-legged creatures (boar, wolf, ram, mole, and every later one)

Written after the Bristle Boar rework (Jay, 2026-11-15: "create rules that will apply to all 4 legged creatures...
so when I switch to a less expensive model, it's still able to produce premium results"). The boar
(`art/models/boar.py`) is the worked example. Follow the steps in order. Do not skip the checker.

## The recipe

1. **Write the identity first, in the model file's docstring, before any shapes.** Three lines:
   - *Coat:* a colour family that is NOT the Tibia look-alike's (Tibia's boar is orange-brown, ours is charcoal).
   - *Signature:* one or two features Tibia's version does not have, that show from above (ours: an ember-red
     crest down the spine, big ivory tusks sweeping out and up). List them in `SIGNATURE = [...]`.
   - *Attitude:* one pose word and how the body shows it (ours: "about to charge" = head low and forward,
     tall shoulder hump, small hindquarters, ears pinned back, tail straight up).
2. **Build on `art/models/quadruped.py`.** The creature file is a `SPEC` of sizes plus its own extras (see the boar).
   Never copy the leg, walk or tail code into a creature file again.
3. **Find the Tibia look-alike** (`LOOKALIKES` in `tools/art_refs.py`) and set `REFERENCE`. It is for size and
   readability only: never match its colours or pose.
4. **Render, then run the checker until every line passes:**
   `sh art/pipeline/render.sh <name>` then `python art/pipeline/check_creature.py <name>`.
   Each FAIL line says what to change.
5. **Then look.** `python tools/art_review.py <name> 4` (all four directions, standing + walk) and view the
   creature on grass at game size. Fix what the eye catches, re-run the checker, and only then show Jay.

## The rules, and why each exists

| # | Rule | How it is enforced |
|---|---|---|
| 1 | **Tibia size.** The longest side in the east view is 0.85-1.2x the look-alike's. | checker "size" (`SIZE`) |
| 2 | **Nothing cut off, placed like Tibia.** Each direction sits against the tile's right and bottom edges and spills up-left. | `AUTO_PLACE = (1, 1)`; checker "fits the canvas" |
| 3 | **Legs show from every direction.** Feet are planted wider than the body, so they are visible from above when walking north/south. | `quadruped.spec()` refuses feet inside the body; checker "legs show" |
| 4 | **Legs join the body.** Shoulder and haunch muscles sit over the tops of the legs. Stout animals: thick short legs (`leg_r` 0.035+); runners: long thin ones. | built into `quadruped.build()` |
| 5 | **The head is a separate shape** with its own dark contour where it overlaps the chest, and takes at least a tenth of the sprite. | head is not "soft" with the body; checker "head is big enough" |
| 6 | **Eyes always show** (south, east, west): on the head's surface, bright, 2+ pixels. | `quadruped.on_surface()`; checker "eyes show" |
| 7 | **The face carries the attitude.** Angry: dark brows slanting down toward the snout, head below the shoulders. Calm: head up, no brows. | per creature (boar's brows) |
| 8 | **Signature features show from all four directions.** Put them on top (crest, horns, mane, back markings) or sticking out sideways (tusks), never only on the flanks or belly. | `SIGNATURE`; checker "signature shows" |
| 9 | **Obviously not Tibia's.** At least 35% of our pixels use colours that are nowhere in the look-alike's sprite. | checker "obviously not the Tibia sprite" |
| 10 | **Three values, not one.** Coat, a clearly lighter or darker second area (belly, snout, legs), and one bright accent (crest, eyes, tusks). A sprite that is one brown from nose to tail reads as a blob. | palette; checker "contrast" |
| 11 | **8-tone ramps with grain.** Every coat ramp has 8 colours; `PIXEL_RULES` comes from `quadruped.pixel_rules()` (grain + tone thresholds). Dark coats pass `dark=True`, and their lightest tone must still be mid-grey (~130) or the animal becomes a black hole on grass. | `quadruped.pixel_rules()`; checker "tones" |
| 12 | **North/south length.** `GROUND_STRETCH` 1.0 for stocky animals, up to 1.6 for long lean ones. If the north or south view is over 58 px tall, lower it. | checker "fits the canvas" |
| 13 | **The walk has a second motion.** Besides the legs, something else moves every frame: crest flick, tail, ears, head nod. | `nod`, `bob`, creature extras; checker "walk moves" |
| 14 | **Light lean.** `HEIGHT_SHEAR = 0.30`, `LEAN` 10-18. (Only tiny low animals like the rat use 0.) | copy from the boar |

## What the checker cannot see (look for these yourself)

- The silhouette alone should say which animal it is: squint at the sheet on plain grey.
- Tusks, horns and tails should not merge into one lump with the head in the east/west view.
- On grass, at game size, the animal should not disappear or look like a hole.
- Jay judges feel and looks last; the checker passing is the entry ticket, not the finish line.

## Creatures built to these rules

| Creature | Coat (vs Tibia's) | Signature | Attitude |
|---|---|---|---|
| Bristle Boar | charcoal (Tibia: orange-brown) | ember-red spine crest, big ivory tusks | about to charge |
| Meadow Wolf | tawny ochre (Tibia: grey) | charcoal saddle, black-tipped tail, amber eyes | prowling |
| Grey Alpha | moonlit teal-silver (Tibia war wolf: grey) | near-black mane, cheek scars, ice-blue eyes | dominant |
| Burrow Mole | mouse-grey (Tibia: near-black) | ivory spade-claws, pink snout | hunched digger |
| Stonehorn Ram | russet fleece, charcoal face (Tibia sheep: white) | pale stone curled horns | ready to butt |

## Lessons from the rollout

- Grey and brown coats are risky: Tibia's sprites already use whole grey and brown ramps, so a plain grey or
  brown animal fails rule 9. Give the coat a hue (ochre, russet, teal-silver) or a value Tibia's lacks.
- Short-legged animals (moles, badgers) may lower the leg checks in `CHECK`; say why in a comment.
- If a direction is too big for the canvas (pixelize warns "too big"), lower `SIZE` before `GROUND_STRETCH`.
- Horns and tusks must contrast with the face behind them (pale horn on a dark face, or the reverse),
  or they merge into one lump at game size.
