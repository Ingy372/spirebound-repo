# Rules for insects, crawlers and other odd bodies (wasp, snapper, toad, thornsnap...)

Written during the insects-and-crawlers cleanup (Jay, 2026-11-15). These creatures have no shared body like
`art/models/quadruped.py`, because each body is different (wings, shells, hops, vines), so each keeps its own
model file. Everything else from `art/QUADRUPED_RULES.md` still applies: identity first, Tibia look-alike for
size only, `AUTO_PLACE = (1, 1)`, 8-tone ramps with grain, `HEIGHT_SHEAR = 0.30`, `LEAN` about 10, and
`python art/pipeline/check_creature.py <name>` must print ALL PASS before Jay sees it.

After the checker passes, every creature also gets the refinement pass in `art/DETAIL_RULES.md`
(real anatomy, no plain balls, drawn lines, surface marks, rims).

## The recipe

1. **Identity in the docstring** (Coat / Signature / Attitude), exactly as for four-legged creatures.
2. **Tell the checker your body plan** in the model file:
   - `HEAD_PARTS = [...]`: the parts that make the face (a wasp: head, face, eye; a plant: jaw, mouth, thorn).
   - `LEG_PARTS = [...]`: the parts that are legs, or `[]` for no legs (a vine, a floating crystal).
   - `SIGNATURE = [...]`: parts that must show from all four directions.
   - `CHECK = {...}` only with a reason in a comment (a flier's thin dangling legs; "the size of a dog").
3. **Render, check, look** (`tools/art_review.py <name> 4`), then all of a group together on grass
   (`tools/art_lineup.py wasp snapper toad thornsnap`).

## Rules learned here

| # | Rule | Why |
|---|---|---|
| C1 | **Stand out on grass.** The meadow grass is a yellow-green (about 80,110,30). A creature's main colour must not be that hue: go bluer (teal, emerald), darker, browner, redder or brighter. | The first toad, snapper and thornsnap vanished into the grass (checker "stands out on grass"). |
| C2 | **Things that open must open SIDEWAYS.** The camera looks down from above, so jaws, pincers or petals that open up-and-down hide their inside. Open them left-right (like a flytrap) and the inside shows. | The thornsnap read as a closed red berry until its jaws opened sideways. |
| C3 | **Show the inside with a bright colour.** An open mouth or throat gets a glowing accent (amber, pink) against a darker outside, with teeth or thorns on the rim. | It is the creature's most important detail and only has a few pixels. |
| C4 | **See-through parts get a low weight.** Wings or membranes use weight about 0.35 in `PIXEL_RULES["weight"]`, so the body wins any pixel they share and shows through. Give them a smoky mid-tone ramp, never near-white. | Opaque white wings covered the wasp's body. |
| C5 | **Limbs and the signature contrast.** If claws, knobs or a beak are the signature, the skin and legs are a darker, duller colour than they are. | Pale claws and knobs pop against slate skin and a dark shell. |
| C6 | **A marking down the back** (stripe, saddle, crest) is the cheapest signature: it shows from every direction. | The toad's yellow spine stripe reads at game size from all sides. |
| C7 | **Raised necks make the north view tall.** If the north view is too big, lower the neck or `GROUND_STRETCH` before shrinking `SIZE` below the look-alike's size. | The thornsnap was too tall facing north. |
| C8 | **Colour families already taken in Tibia's version don't count as ours.** If the brief fixes the colours (the wasp must be yellow and black), shift the hue (amber-gold, blue-black) and add a new accent (ember eyes). | Keeps Jay's brief while staying clearly not Tibia's. |

## Creatures cleaned up to these rules

| Creature | Coat (vs Tibia's) | Signature | Attitude |
|---|---|---|---|
| Meadow Wasp | amber-gold and blue-black (Tibia: lemon and brown-black) | ember-red eyes, long hooked stinger, smoky wings | hunting, abdomen low |
| Reed Snapper | dark bog-green plated shell, khaki rim, slate-blue skin (Tibia tortoise: tan) | three rows of pale horn knobs, bright reeds, ivory hooked beak | low, wide and armoured |
| Hopper Toad | emerald-teal with lemon belly (Tibia: orange-gold) | yellow spine stripe, golden eyes | squat, ready to spring |
| Thornsnap | dark blue-green vine (Tibia carniphila: grass green) | crimson flytrap head, amber throat, thorn teeth | lunging snake |
