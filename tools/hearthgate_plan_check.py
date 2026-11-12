from PIL import Image, ImageDraw, ImageFont
W, H = 112, 96
# name: (x, y, w, h, kind, door)   kind: hub/shop/civic/house/yard/green
B = {
 "THE HEARTH": (42, 38, 30, 23, "hub", None),
 "Quartermaster": (44, 2, 10, 9, "shop", (53, 6)), "Post Office": (44, 13, 10, 9, "shop", (53, 17)),
 "Alchemist": (41, 23, 13, 9, "shop", (52, 31)),
 "Guardhouse": (60, 2, 10, 9, "civic", (60, 6)), "Tailor": (60, 13, 10, 9, "shop", (60, 17)),
 "Fletcher": (60, 23, 13, 9, "shop", (61, 31)),
 "General Store": (3, 38, 10, 9, "shop", (8, 46)), "Weaponsmith": (14, 38, 10, 9, "shop", (19, 46)),
 "Runewright": (26, 37, 11, 10, "shop", (36, 45)),
 "Coach Yard": (2, 52, 9, 9, "yard", (6, 52)), "Armorer": (14, 52, 9, 9, "shop", (18, 52)),
 "Inn": (24, 52, 13, 15, "civic", (36, 59)), "Workshop": (14, 62, 9, 9, "shop", (14, 66)),
 "Old Well Yard": (2, 62, 9, 9, "green", None),
 "Hunters' Hall": (77, 33, 18, 14, "civic", (77, 40)), "Training Yard": (96, 33, 13, 14, "yard", (102, 46)),
 "SPIRE MANOR": (78, 53, 22, 16, "manor", (89, 53)), "Spire Gardens": (101, 53, 9, 16, "green", None),
 "Ascendancy": (75, 2, 15, 11, "civic", (82, 12)), "Guild Hall": (93, 2, 15, 11, "civic", (100, 12)),
 "Hearthgate Green": (12, 14, 25, 21, "green", None),
 "Pocket garden W": (48, 83, 6, 8, "green", None),
}
houses = {"Crown Row": [(75, 21), (84, 21), (93, 21), (102, 21)], "Northside": [(2, 2), (11, 2), (20, 2), (29, 2)],
          "Greenside": [(2, 14), (2, 24)], "Lantern Row N": [(2, 72), (15, 72), (24, 72)],
          "Squareside": [(38, 72), (46, 72), (60, 72), (68, 72)], "Lantern Row S": [(3, 83), (12, 83), (21, 83), (30, 83), (39, 83)],
          "Manor Walk": [(77, 72), (86, 72), (95, 72)], "Southgate Row": [(62, 83), (71, 83), (80, 83), (89, 83), (98, 83)]}
n = 0
for d, lst in houses.items():
    for (x, y) in lst:
        n += 1
        B[f"{d} {n}"] = (x, y, 8, 8, "house", None)
print("houses", n)
STREETS = {"North Avenue": (55, 1, 4, 31), "South Avenue": (55, 72, 4, 23), "West High Road": (1, 48, 36, 3),
           "East High Road": (77, 48, 34, 3), "Hearth Ring": (37, 32, 40, 40), "Coach Lane": (11, 51, 3, 30),
           "Lantern Lane W": (1, 80, 54, 3), "Lantern Lane E": (59, 80, 51, 3), "Crown Court": (71, 13, 39, 8),
           "Mill Lane": (1, 10, 43, 3), "Avenue lane W": (38, 11, 17, 2), "Crown Lane": (59, 11, 16, 2),
           "Manor Walk": (77, 69, 33, 3), "Green Walk": (1, 35, 25, 3)}


def ov(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


bad = 0
names = list(B)
for i, a in enumerate(names):
    x, y, w, h = B[a][:4]
    if x < 2 or y < 2 or x + w - 1 > 109 or y + h - 1 > 93:
        print("OUT OF BOUNDS", a); bad += 1
    for b in names[i + 1:]:
        if ov(B[a], B[b]):
            print("OVERLAP", a, b); bad += 1
    for s, r in STREETS.items():
        if a != "THE HEARTH" and ov(B[a], r):
            print("ON STREET", a, s); bad += 1
print("problems", bad)
spawn = (56, 49)
for k, p in {"nearest locker (60,47)": (60, 47), "Trader Osric counter (52,51)": (52, 51), "Banker (48,51)": (48, 51), "Priest (60,52)": (60, 52),
             "Alchemist door": (52, 32), "Fletcher door": (61, 32), "Runewright door": (37, 45), "Inn door": (37, 59),
             "Hunters' Hall door": (76, 40), "Manor door": (89, 52), "Weaponsmith door": (19, 47), "Armorer door": (18, 51),
             "General Store door": (8, 47), "North gate": (56, 0), "South gate": (56, 95), "West gate": (0, 49), "East gate": (111, 49),
             "Coach Yard": (6, 51), "Training Yard": (102, 47), "Guild Hall door": (100, 13), "Ascendancy door": (82, 13)}.items():
    print(f"{k}: {abs(p[0]-spawn[0]) + abs(p[1]-spawn[1])} steps")

S = 10
img = Image.new("RGB", (W * S, H * S), (72, 132, 62))
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("arialbd.ttf", 12); fs = ImageFont.truetype("arial.ttf", 10)
except OSError:
    f = fs = ImageFont.load_default()
d.rectangle([S, S, (W - 1) * S - 1, (H - 1) * S - 1], fill=(120, 120, 124))
for s, (x, y, w, h) in STREETS.items():
    col = (232, 224, 196) if s in ("North Avenue", "South Avenue", "Hearth Ring") else (150, 142, 128) if "High Road" in s else (176, 176, 180)
    d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=col)
COL = {"hub": (250, 246, 228), "shop": (176, 92, 72), "civic": (120, 150, 200), "house": (214, 170, 110), "yard": (150, 110, 70),
       "green": (96, 170, 84), "manor": (236, 204, 96)}
for name, (x, y, w, h, kind, door) in B.items():
    d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=COL[kind], outline=(40, 30, 20), width=2)
    if kind != "house":
        label = name
        tw = d.textlength(label, font=f if kind in ("hub", "manor") else fs)
        d.text((x * S + (w * S - tw) / 2, y * S + h * S / 2 - 6), label, fill=(0, 0, 0), font=f if kind in ("hub", "manor") else fs)
    if door:
        d.rectangle([door[0] * S + 2, door[1] * S + 2, door[0] * S + S - 3, door[1] * S + S - 3], fill=(255, 255, 255), outline=(0, 0, 0))
for dn, lst in houses.items():
    x = min(p[0] for p in lst); y = lst[0][1]
    d.text((x * S + 3, y * S + 30), dn, fill=(60, 30, 0), font=fs)
# wall and gates
d.rectangle([0, 0, W * S - 1, H * S - 1], outline=(210, 200, 170), width=S)
for gx in range(55, 59):
    d.rectangle([gx * S, 0, gx * S + S - 1, S - 1], fill=(232, 224, 196)); d.rectangle([gx * S, (H - 1) * S, gx * S + S - 1, H * S - 1], fill=(232, 224, 196))
for gy in range(48, 51):
    d.rectangle([0, gy * S, S - 1, gy * S + S - 1], fill=(150, 142, 128)); d.rectangle([(W - 1) * S, gy * S, W * S - 1, gy * S + S - 1], fill=(150, 142, 128))
d.ellipse([56 * S - 4, 49 * S - 4, 57 * S + 4, 50 * S + 4], fill=(220, 40, 40), outline=(0, 0, 0))
d.text((46 * S, 62 * S), "Hearth Square (stalls, fountain, Monument)", fill=(60, 50, 30), font=fs)
d.text((12, H * S - 26), "Hearthgate plan v3   red dot = spawn / respawn   white squares = doors   north is up   1 square = 1 tile x10", fill=(255, 255, 255), font=fs)
img.save(r"C:\Users\Muth3\Desktop\spirebound-repo\docs\HEARTHGATE_PLAN.png")
print("saved")
