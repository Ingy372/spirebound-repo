# Rules for player outfits (and any detailed person)

Written after Jay's review of the four class outfits (2026-11-15: "they don't look bad but they are also lacking
a detail refine"). Player outfits are what players look at all day and may pay for, so they get the highest bar.
Worked examples: `art/models/vanguard.py`, `ranger.py`, `arcanist.py`, `mystic.py`, all built on
`art/models/humanoid.py`. Colours live in `art/pipeline/outfit_palettes.py`.

## What was wrong with the first versions (measured against Tibia's own outfits)

- **Bobble-heads:** the head was a third of the figure and a smooth dome. Tibia's is about a fifth, with a hair shape.
- **Sausage bodies:** arms, legs and torso melted together. Tibia draws a dark line wherever a limb crosses the body.
- **No costume:** one colour per garment, no belt, cuffs, hems, clasps or trim.
- **Small:** about 30 px tall against Tibia's 36-38.

## The recipe

1. **Identity in the docstring**, three lines: *Silhouette* (the outline that tells this class from the others at
   a glance: gear, hood, robe shape), *Colours* (2 main colours + 1 metal or accent + hair), *Details* (at least six
   named small things: hem, buckle, cuffs, clasp, emblem...).
2. **Build on `humanoid.py`.** The outfit file is a `SPEC` plus its own garments and gear. Never copy the body code.
3. **Colours as anchors** in `outfit_palettes.py`: each colour is (dark, light, mid); run
   `python art/pipeline/outfit_palettes.py` to rebuild the ramps.
4. **Render, check, look:** `sh art/pipeline/render.sh <name>`, `python art/pipeline/check_creature.py <name>` (ALL PASS),
   then `python tools/art_outfits.py vanguard ranger arcanist mystic` (close-up beside Tibia's outfits) and
   `python tools/art_lineup.py ...` (on grass at game size).

## The rules

| # | Rule | How it is enforced |
|---|---|---|
| O1 | **Head about a fifth of the figure.** `head_r` height stays under 0.140. | `humanoid.spec()` refuses bigger |
| O2 | **Limbs are separate parts** (`arm_a`/`arm_b`, `leg_a`/`leg_b`, `boot_a`/`boot_b`) and are never "soft" with the torso, so dark lines separate them. | built into `humanoid.py` |
| O3 | **Skin shows:** a face with eyes on the surface, a nose highlight and brows; skin-coloured hands below a cuff. A face must not be covered by hair or a hood from the front: keep fringes above the brow. | built in; look at the south view |
| O4 | **Hair has a shape:** the cap plus at least two outfit pieces (fringe, nape, locks, back hair, braid, hood) and 2-3 drawn strand lines. Never a bare dome. Strand lines use the hair's second-darkest tone, not black. | per outfit; `outfit_palette.base()` |
| O5 | **Each class owns a silhouette.** Hold gear OUT from the body and at an angle that is not the figure's lean (a sword forward-and-out, a bow or staff upright at the side). Two classes must never share an outline. | look at the lineup |
| O6 | **Six named details minimum**, in three kinds: edges (hem, cuffs, collar piping, shield rim), fastenings (belt, buckle, clasp, straps), and marks (emblem, runes, beads, fletchings). | docstring "Details:" line |
| O7 | **Trim is a line, never a disc.** Piping, hems and collar edges are thin rings or tubes. A capped ring seen from above becomes a plate or a halo. | lesson from the arcanist's collar |
| O8 | **Tall things go BEHIND the head** (collars, hoods' points, quivers, staff tops), tilted back, so nothing rings or hides the face. | lesson from the arcanist's collar |
| O9 | **Metal, cloth and leather look different.** Metal: widest ramp, near-white top tone, little grain. Cloth: medium ramp, grain 0.3-0.45. Leather: warm, narrow ramp. Light cloth needs a light shadow tone too or it turns grey. | `outfit_palettes.py` anchors |
| O10 | **Robes:** bell shape narrower than the canvas (base radii about 0.15 x 0.18), a contrasting hem, shoes peeking out; the legs check is set to 0 with a comment. | `CHECK` in the model |
| O11 | **Fixed placement.** Every outfit uses `humanoid.CANVAS_OFFSET` (not AUTO_PLACE), so outfits, add-ons and mounts line up. | `CANVAS_OFFSET = H.CANVAS_OFFSET` |
| O12 | **Eyes are small** (about 2 px, dark brown, not black). Jay will judge eyes in the game before more changes. | `humanoid.DEFAULTS["eye_r"]` |
| O13 | **Plan for colour zones.** In the game a player recolours head, body, legs and feet. Keep hair in "hair"; the main garment in torso/arms (or robe); trousers or the second colour in legs; boots in boots. Gear and metal are never recoloured. | part names |
| O14 | **One outline per character, NPCs included.** Before adding a hat, coat or weapon, look at the approved people (`python tools/art_outfits.py <new> vesper priest ...`): if the new figure's outline matches one of them, change the signature, not the colours. Vesper owns coat + wide hat. | lesson from the Bounty Warden (2026-11-25) |
| O15 | **Hats in this view:** a dome crown with a small brim reads as a helmet, a plume pointing backward stands up like a horn in the south view (lay it along the crown), and a red band under a brim reads as glowing eyes. A hat needs a tall flat-topped crown and a brim tipped back about 0.4 (Vesper). | Bounty Warden first render |
| O16 | **Light grey hair reads as a steel helmet.** Grey or white hair uses a darker salt-and-pepper ramp (top tone about 170) and five or more strand lines. | Bounty Warden |
| O17 | **Gear on the back is edge-on from the side.** A crossbow, quiver or shield on the back spans left-right, so facing east or west it hides behind the body: sweep its far ends backward (-X) so it shows from the side, and check the signature count facing E and W. | Bounty Warden's crossbow (1 px facing E before the sweep) |
| O18 | **Neighbouring garments need different colours.** A brown hood over a brown jerkin and brown trousers reads as one blob: change the value or hue of each neighbour (the bandit got a charcoal jerkin). | Road Bandit first render |
| O19 | **Where a big prop goes:** at the hip it reads as a third leg; on the shoulder it hides the face; on the back (O8, O17) it reads from every side. A cap sits ON the crown, smaller than the head and above the brow; a cap the size of the head hides the face. | Quartermaster (three tries) |
| O20 | **A monster must never pass for a player.** Monsters and NPCs never use a class outfit's signature (the Ranger's pointed hood, the Vanguard's kite shield, the Arcanist's high collar, the Mystic's shoulder leaves). | Road Bandit: round hood, not pointed |
| O21 | **Eyes that a helm or hood would hide:** set hoods back so the eyes show; a full helm gets its own glowing eye parts on the visor; a skull needs big dark sockets, cheekbones and a crack line (a smooth skull reads as an egg), and bone must show from behind too (a spine below a short jerkin). | Ruin Sentinel, Ruin Archer |
| O22 | **Touching the canvas's right and bottom edges is normal** (every approved figure does, like Tibia's own sprites, rule A6 is about being CUT there). Only the top and left edges must stay clear. | measured on all approved people |
| O23 | **A boss's big weapon never crosses the face from any side.** Keep a great axe's head at shoulder height, out and a little behind the hand, and turn its blades about 55-60 degrees toward the front so the flats read facing south as well as east/west. Horns on a closed helm start high and back, or the near horn covers the visor in profile. | Axe-Lord (eyes hidden facing west until both moved) |

## Addons: base, addon 1, addon 2 (Jay, 2026-11-25)

Jay: "tibia has the base outfit, addon 1 and addon 2. Not every outfit needs one, but it'll give us more content for
quests for certain outfits." Worked examples: the Vanguard's Crested Helm and Knight's Mantle (`vanguard_a1.py`, `vanguard_a2.py`, approved by
Jay 2026-11-25: "Looks good to me"), and the Ranger's, Arcanist's and Mystic's pairs. `art/models/addon_kit.py` gives
an addon file the base's moving anchors (head, shoulders, belt, hands).

| # | Rule | How it is enforced |
|---|---|---|
| A1 | **Plan addons with the outfit.** Every new player outfit's docstring says "Addons:" with what addon 1 and addon 2 are, or "none" and why. Player and shop outfits normally get both; NPCs never need them. | docstring |
| A2 | **An addon only adds.** In the client it is an overlay drawn on top of the base, so it can cover the base but never remove or reshape it. Good addons: headgear, a mantle or cloak, shoulder pieces, a back item, a held prop in a free hand. Never: a different weapon in a hand that already holds one, or anything that needs the base's part gone. | `addon_overlay.py` stops if an addon would need to erase more than 12 base pixels |
| A3 | **Addons never touch the frozen base.** The addon file imports the base model, adds its parts after the base's part list (so the base's part numbers stay the same) and renders as `<base>_a1` / `<base>_a2`. Its colours are NEW keys in the base's palette; the base's own keys never change. | `render.sh` still refuses the approved base; compare palette.json before committing |
| A4 | **Each addon reads alone and with the other.** Addon 1 at the head or front, addon 2 at the back or shoulders, so both can be worn together without one hiding the other. Judge `art/output/<base>_addons_preview.png` (base, addon 1, addon 2, both) and the both-on walk loops. | look at the preview |
| A5 | **Checker on each addon render** (`check_creature.py <base>_a1`): its SIGNATURE is the addon's own parts, and headgear counts as the head (put helm parts in HEAD_PARTS). Literal values only in SIGNATURE/CHECK/HEAD_PARTS/LEG_PARTS: the checker reads those lines without importing the model. | ALL PASS before Jay sees it |
| A6 | **Stay inside the canvas.** Addons widen the figure; nothing may be cut by the 64x64 canvas's right edge (the mantle was narrowed for that). | look at the west view |
| A7 | **Into the game only when approved.** `tools/make_creature_sheets.py` packs `<base>_a1` (and `_a2`, only together with `_a1`) as the look's addon rows once they are in `art/APPROVED.txt`; a player then needs the addon itself (`player:addOutfitAddon(look, 1 or 2)`), normally from a quest. | approval list |
| A8 | **Headgear goes over or outside the hair, never inside it.** A circlet and gem on the Arcanist's brow sat under her fringe and showed 0 pixels from every side. Big hair (fringes, buns, hoods) hides anything on the head's surface: rise above it (antlers, a crest) or float beside it (runestones), and check after the first render. Small things (horns, books, owls) need to be bigger than feels right: the first owl, book and antlers all vanished at game size. | lesson from the Arcanist, Mystic and Ranger addons |
| A9 | **Signature parts must face every way; one-sided details are checked only where they face.** An owl's face or a horn at the front hip cannot show from behind: put the whole owl, or the shoulder guard, in SIGNATURE and write why in a comment. A pale animal on a pale-haired figure, or a tan one on sandy hair, merges with the head: give a companion its own colour. | Mystic's owl (tan on sandy hair read as a second head) |

How to make them: `sh art/pipeline/render.sh vanguard_a1`, `sh art/pipeline/render.sh vanguard_a2`, the checker on
both, then `python art/pipeline/addon_overlay.py vanguard` (overlays, preview, walk loops).

## Still to do

- The town NPCs, bandits, sentinel, archer and the boss still use the old copied body; move each onto `humanoid.py`
  when it is next touched. Done 2026-11-25: the Bounty Warden, Guild Warden, Quartermaster, Brannoch, Road Bandit,
  Bandit Captain, Ruin Archer and Ruin Sentinel.
- The colour-mask layer for player recolouring (rule O13) is not generated yet (roadmap R22 / 6.4).
