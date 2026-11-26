import corpse_kit
# the robe hides the body: torso and legs sink with it, the bones, cage-helm, lantern and chain lie on top
corpse_kit.make(globals(), "underkeeper", mode="shatter", fall=0.5, seed=5, scatter=0.34, cloth=(0.8, 0.12),
                soft=("torso", "leg_a", "leg_b", "boot_a", "boot_b"), keep=(1.0, 0.75, 0.45))
