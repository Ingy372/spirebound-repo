# Detail rules: how to make a sprite look refined, not "ok"

Written after Jay's second review (2026-11-15): the sprites "look ok, but their detail isn't refined enough...
the wasp wings look too short, the toad looks like a plushy, the reed snapper looks like a mix between a crab
and a turtle". The checker (`art/pipeline/check_creature.py`) cannot see any of this. These rules can.
Apply them to EVERY creature and outfit after the checker passes and before Jay sees it.
Worked examples: `art/models/toad.py`, `wasp.py`, `snapper.py`, `thornsnap.py`.

## The refinement pass (do all seven, in order)

1. **Name the real thing and list its anatomy.** Write, in the model's docstring under "Detail:", the 5-8
   features a child would draw to show what it is. A wasp: three body sections, a thin waist, long veined wings,
   bent antennae, jaws, six jointed legs, a stinger. If the model is missing one, add it.
   *A sprite reads as "plush" or "toy" when it is the idea of the animal without its anatomy.*
2. **One animal, not two.** A hybrid in the brief ("turtle-crab") becomes ONE believable animal that borrows a
   single trait from the other (the snapper is a snapping turtle that scuttles sideways). Never glue two
   animals' parts together. Record the choice in `QUESTIONS.md` so Jay can overrule it.
3. **Break up every ball.** No body, head or limb may be a single smooth ellipsoid:
   - bodies get 2-4 overlapping lumps (flanks, rump, hump, throat);
   - heads get brow ridges, a jaw or beak, a snout;
   - limbs get two segments with a visible joint, and feet with toes or claws.
4. **Draw the lines a pixel artist would draw.** Use thin dark tubes (a part called "line", "seam", "vein" or
   "strand"; weight 2-3.5, thin 2, radius about 0.006-0.008) for: mouth lines, plate seams on shells, wing veins,
   leaf midribs, hair strands, belt and armour edges. Put the part in the same "soft" group as the surface it
   lies on. One or two per region: a cross of lines on a round shape looks like a scar or a stitched ball.
5. **Add surface marks in three sizes.** Big: blotches or bands (flat ellipsoids, darker). Medium: a stripe,
   saddle or rim (lighter or contrasting). Small: warts, knobs, spots, thorns, rivets (tiny raised shapes,
   lighter than the surface, weight 2.5+). A surface with only grain looks unfinished.
6. **Proportions from the real thing, measured.** Look up the real proportion and state it in a comment:
   wasp wings reach past the middle of the abdomen; a toad is wider than it is tall and its eyes sit on top;
   a turtle's shell is most of its body. Then compare your side view against that sentence.
7. **Edges and rims.** Anything with a rim gets one in a second colour: shell rims, jaw lips, shield rims,
   robe hems, cuffs, wing leading edges. Rims are the cheapest way to make a shape look designed.

## Colour refinement

- **Tone down toy colours.** Saturated mid-tones on a smooth shape read as plastic. Keep the hue, but make the
  ramp run from a dark, slightly cool shadow to a light, slightly warm highlight, and mottle it with grain and blotches.
- **Eyes are small and set in.** An eye is 2-4 pixels under a brow or lid, not a big bright disc. Big round eyes
  with big pupils are a cartoon. (Jay will judge eyes in the game before any more eye changes.)
- **Pale parts are for the signature only** (beak, claws, tusks, teeth, horn knobs): everything else stays mid or dark,
  so the pale parts pop.

## How to check your own work (the checker cannot)

- `python tools/art_review.py <name> 4` and ask of each direction: *could I name this animal from the outline alone?*
- Count the details in the east view: there should be at least five different things to look at
  (for the snapper: plates, knobs, reeds, rim, beak, eye, claws).
- Put it beside its Tibia look-alike (`.local/lookalike/board.py <name>`): ours should have about as many
  distinct shapes and lines inside the outline as theirs, never fewer than half.
- Look for the "ball test": squint; if any part turns into a plain circle or sausage, it needs rule 3.

## Before and after (what each fix was)

| Creature | It looked like | The fix |
|---|---|---|
| Hopper Toad | a plush ball with big toy eyes | flat wide body of five lumps, brow ridges over small slit-pupil eyes, a drawn mouth line, warts and blotches, two-part legs with toes, muted mottled colour |
| Meadow Wasp | a bee with stubby wings | wings 2x longer with a dark leading-edge vein, a thin waist, six tapering abdomen bands, jaws, elbowed antennae, two-part legs |
| Reed Snapper | a turtle with crab pincers glued on | one animal: a snapping turtle with plate seams, three rows of horn knobs, a hooked two-part beak, thick clawed legs, a ridged tail |
| Thornsnap | a decent flytrap, plain leaves | a pale midrib on each leaf, a collar of sepals behind the head, a pale lip on each jaw rim |
