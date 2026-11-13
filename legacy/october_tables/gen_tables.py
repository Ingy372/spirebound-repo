#!/usr/bin/env python3
"""Spirebound seed-table generator.
Single source of truth for every number in data/*.csv.
Edit the constants here, rerun, commit the CSVs. Never hand-edit a CSV.
Run: python3 tools/gen_tables.py
"""
import csv, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

def w(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

def xp_for(level):
    L = level
    return int((50/3) * (L**3 - 6*L**2 + 17*L - 12))

# Hunting band tops (not caps — there is no level cap). Used for pacing targets only.
BAND_TOP = {1: 22, 2: 34, 3: 46, 4: 58, 5: 70}
HOURS_TO = {22: 14, 34: 40, 46: 80, 58: 145, 70: 235}

# trash hp range, trash xp avg, kills/hour solo at band, col avg per trash kill, supply share of gross
FLOOR = {
 1: dict(hp=(60,180),   xp=34,  kph=240, col=5.5, sup=0.25, band=(1,22)),
 2: dict(hp=(350,600),  xp=90,  kph=205, col=15,  sup=0.30, band=(18,34)),
 3: dict(hp=(700,1100), xp=115, kph=190, col=24,  sup=0.32, band=(30,46)),
 4: dict(hp=(1100,1700),xp=145, kph=165, col=36,  sup=0.34, band=(42,58)),
 5: dict(hp=(1600,2400),xp=170, kph=150, col=52,  sup=0.35, band=(54,70)),
}
w("xp_table.csv", ["level","total_xp_to_reach","xp_to_next"], [[L, xp_for(L), xp_for(L+1)-xp_for(L)] for L in range(1,71)])

MATS = [
 (5101,"Hearthroot",1,"common",2,"F1 trash"),
 (5102,"Boar Hide",1,"common",3,"F1 boars"),
 (5103,"Cinderstone",1,"keen",25,"F1 elites, labyrinth chests"),
 (5104,"Stair Iron",1,"tempered",0,"Gate Hound, Axe-Lord first kill and Echo"),
 (5201,"Horn Shard",2,"common",6,"F2 trash"),
 (5202,"Ridge Pelt",2,"common",8,"F2 cats"),
 (5203,"Blightglass",2,"keen",60,"F2 elites"),
 (5204,"Aurochs Horn",2,"tempered",0,"Horn Brute, Crowned Aurochs + Echo"),
 (5301,"Spore Cap",3,"common",10,"F3 trash"),
 (5302,"Mossweave",3,"common",12,"F3 crawlers"),
 (5303,"Fog Amber",3,"keen",110,"F3 elites"),
 (5304,"Heartwood",3,"tempered",0,"Mossback Warden, Sleeping Trunk + Echo"),
 (5401,"Eel Scale",4,"common",15,"F4 eels"),
 (5402,"Drowned Iron",4,"common",18,"F4 drowned"),
 (5403,"Tide Pearl",4,"keen",170,"F4 elites"),
 (5404,"Helm Steel",4,"tempered",0,"Lake Knight, Closed Helm + Echo"),
 (5501,"Arena Sand",5,"common",22,"F5 trash"),
 (5502,"Drill Core",5,"common",26,"F5 constructs"),
 (5503,"Champion Seal",5,"keen",240,"F5 elites"),
 (5504,"Colossus Core",5,"tempered",0,"Arena Warden, Empty Colossus + Echo"),
 (5901,"Spire Scrap",0,"spireforged",0,"Echo 15% + pity, optional bosses 10%"),
 (5902,"Last Blow Shard",0,"spireforged",0,"First-kill last hit only. Bound. Counts as a Spire Scrap AND forces that upgrade to succeed"),
 (5911,"Blackstone Shard",1,"keen",40,"Underkeep, all wings"),
]
w("materials.csv",["item_id","name","floor","tier","npc_buy_price","source"],MATS)

def mk(mid, floor, zone, name, role, hpm=1.0, dmgm=1.0, note="", drops=""):
    f = FLOOR[floor]
    lo,hi = f["hp"]; base_hp = (lo+hi)/2
    # Boss HP comes from a damage model, not a guess:
    # sustained single-target DPS of one prepared player at the band
    # = (trash avg HP * kills/h / 3600) * 2.5 (no walking/looting while on a boss)
    dps = base_hp*f["kph"]/3600*2.5
    # role: (players expected, seconds to kill at that headcount)
    MODEL = {"elite":(2,25),"mini":(4,90),"optional":(4,180),"field_boss":(8,150),"floor_boss":(8,300)}
    if role=="trash":
        hp=base_hp*hpm; xp=f["xp"]*hpm*(0.6+0.4*dmgm)
    else:
        n,t = MODEL[role]; hp=dps*n*t*hpm
        xp=f["xp"]*{"elite":14,"mini":30,"optional":55,"field_boss":90,"floor_boss":260}[role]*hpm
    hp=int(round(hp,-1)); xp=int(round(xp))
    band_mid = sum(f["band"])/2
    php = 150 + band_mid*11
    hits = {"trash":14,"elite":7,"mini":5,"field_boss":4,"floor_boss":3.2,"optional":4}[role]
    dmg = int(php/hits*dmgm)
    c = f["col"]
    cmul={"trash":1,"elite":14,"mini":30,"field_boss":0,"floor_boss":0,"optional":40}[role]
    cmin=int(c*cmul*0.5); cmax=int(c*cmul*1.5)+(1 if cmul else 0)
    resp={"trash":60,"elite":600,"mini":1800,"field_boss":0,"floor_boss":0,"optional":0}[role]
    return [mid,floor,zone,name,role,hp,xp,dmg,cmin,cmax,resp,drops,note]

M=[]
M+= [mk(101,1,"camp","Bristle Boar","trash",0.7,0.8,"charges 2 tiles after 600ms telegraph","5102:40%:1-2;5101:25%:1"),
     mk(102,1,"camp","Meadow Wolf","trash",0.8,1.0,"spawns in packs of 3","5101:30%:1"),
     mk(103,1,"camp","Field Shardling","trash",0.6,0.9,"flees at 20% hp","5101:40%:1-2"),
     mk(104,1,"camp","Road Bandit","trash",1.2,1.1,"","5101:20%:1"),
     mk(105,1,"camp","Thornsnap","trash",1.0,0.9,"stationary, 1-tile poison field","5101:45%:1-2"),
     mk(106,1,"labyrinth","Ruin Sentinel","trash",1.5,1.2,"-50% damage taken from its front tile","5101:20%:1;5103:2%:1"),
     mk(107,1,"labyrinth","Ruin Archer","trash",1.1,1.1,"ranged 4","5101:20%:1;5103:2%:1"),
     mk(108,1,"underkeep","Mire Toad","trash",1.3,1.0,"Underkeep W1, slime field on death","5911:6%:1"),
     mk(109,1,"underkeep","Black Crawler","trash",1.4,1.2,"Underkeep W1","5911:6%:1"),
     mk(151,1,"camp","Bandit Captain","elite",1.0,1.0,"1 per bandit camp","5103:35%:1-2;recipe_scrap_keen_f1:3%:1"),
     mk(152,1,"camp","Grey Alpha","elite",1.0,1.0,"howl: wolves +20% speed 10s","5103:35%:1-2"),
     mk(153,1,"labyrinth","Sentinel Captain","elite",1.1,1.0,"labyrinth level 3","5103:45%:1-2"),
     mk(171,1,"secret","Old Tusk","mini",1.0,1.0,"secret s2","dye_mudbrown:100%:1;5103:100%:2-3"),
     mk(191,1,"pass","Gate Hound","field_boss",1.0,1.0,"see 10_BOSSES","5104:100%:1"),
     mk(192,1,"boss","Axe-Lord of the Stair","floor_boss",1.0,1.0,"see 10_BOSSES","5104:100%:2-4"),
     mk(111,2,"underkeep","Vault Rat","trash",0.8,1.0,"Underkeep W2 (tuned F2)","5911:8%:1"),
     mk(112,2,"underkeep","Chain Ghoul","trash",1.3,1.1,"Underkeep W2, slow on hit","5911:8%:1"),
     mk(181,2,"underkeep","Drain Matron","mini",1.0,1.0,"Underkeep W2 side boss, daily per character","5911:100%:3-5;5203:50%:1"),
     mk(113,3,"underkeep","Trap Mimic","trash",1.2,1.2,"Underkeep W3, looks like a chest","5911:10%:1"),
     mk(114,3,"underkeep","Iron Shade","trash",1.0,1.3,"Underkeep W3","5911:10%:1"),
     mk(115,4,"underkeep","Keep Warden","elite",1.0,1.1,"Underkeep W4, packs of 3","5911:40%:2;5403:15%:1"),
     mk(182,5,"underkeep","Vault Warden","optional",1.0,1.0,"Underkeep W5 boss. Chained lantern + tower shield silhouette. NOT a scythe","5911:100%:6;5504:30%:1;5901:10%:1"),
     mk(201,2,"camp","Horned Grazer","trash",0.9,0.9,"herds of 4","5201:40%:1-2"),
     mk(202,2,"camp","Ridge Cat","trash",0.9,1.2,"pounce 3 tiles after telegraph","5202:35%:1"),
     mk(203,2,"camp","Dust Strider","trash",1.0,1.0,"fast","5201:30%:1"),
     mk(204,2,"camp","Hill Cutthroat","trash",1.2,1.1,"bleed","5201:20%:1"),
     mk(205,2,"camp","Blight Wasp","trash",0.7,1.0,"poison","5201:30%:1"),
     mk(206,2,"labyrinth","Stonehide Bull","trash",1.6,1.2,"line charge 3","5201:30%:1;5203:2%:1"),
     mk(251,2,"camp","Herd Bull","elite",1.0,1.0,"","5203:35%:1-2;recipe_scrap_keen_f2:3%:1"),
     mk(252,2,"camp","Ridge Matriarch","elite",1.0,1.0,"","5203:35%:1-2"),
     mk(271,2,"secret","Ridge Alpha","mini",1.0,1.0,"secret s14","5203:100%:2-3"),
     mk(272,2,"secret","Hollow Bull","optional",1.0,1.0,"secret s19, instanced","5204:50%:1;5901:10%:1"),
     mk(273,2,"secret","Fir Rumor Beast","optional",1.2,1.0,"secret s21, Sundays 20:00 ET in a gated glade","8051:100%:1"),
     mk(291,2,"pass","Horn Brute","field_boss",1.0,1.0,"","5204:100%:1"),
     mk(292,2,"boss","Crowned Aurochs","floor_boss",1.0,1.0,"","5204:100%:2-4"),
     mk(301,3,"camp","Spore Bat","trash",0.7,1.0,"blind 1s","5301:40%:1"),
     mk(302,3,"camp","Moss Crawler","trash",1.2,0.9,"","5302:40%:1-2"),
     mk(303,3,"camp","Fog Lurker","trash",1.0,1.2,"invisible until adjacent","5301:30%:1"),
     mk(304,3,"camp","Bark Mantis","trash",1.1,1.2,"","5302:25%:1"),
     mk(305,3,"camp","Lantern Wisp","trash",0.6,1.0,"ranged","5301:35%:1"),
     mk(306,3,"labyrinth","Rootbound Husk","trash",1.6,1.1,"root 1s","5302:30%:1;5303:2%:1"),
     mk(351,3,"camp","Moss Elder","elite",1.0,1.0,"","5303:35%:1-2;recipe_scrap_keen_f3:3%:1"),
     mk(371,3,"secret","Canopy Mother","mini",1.0,1.0,"secret s26","5303:100%:2-3"),
     mk(372,3,"secret","Waking Root","optional",1.0,1.0,"secret s31, instanced","5304:50%:1;5901:10%:1"),
     mk(391,3,"pass","Mossback Warden","field_boss",1.0,1.0,"","5304:100%:1"),
     mk(392,3,"boss","Sleeping Trunk","floor_boss",1.0,1.0,"","5304:100%:2-4"),
     mk(401,4,"camp","Lake Eel","trash",0.9,1.1,"water edge","5401:40%:1-2"),
     mk(402,4,"camp","Drowned Footman","trash",1.2,1.0,"","5402:40%:1"),
     mk(403,4,"camp","Reed Witch","trash",0.8,1.2,"ranged, silence 2s","5401:25%:1"),
     mk(404,4,"camp","Tide Crab","trash",1.4,0.9,"high armor","5402:30%:1"),
     mk(405,4,"labyrinth","Helm Knight","trash",1.7,1.2,"shield front","5402:30%:1;5403:2%:1"),
     mk(406,4,"camp","Castle Hound","trash",0.9,1.1,"packs of 3","5401:25%:1"),
     mk(451,4,"camp","Drowned Sergeant","elite",1.0,1.0,"","5403:35%:1-2;recipe_scrap_keen_f4:3%:1"),
     mk(471,4,"secret","Eel King","mini",1.0,1.0,"secret s38","5403:100%:2-3"),
     mk(472,4,"secret","The Unhelmed","optional",1.0,1.0,"secret s41, instanced","5404:50%:1;5901:10%:1"),
     mk(491,4,"pass","Lake Knight","field_boss",1.0,1.0,"","5404:100%:1"),
     mk(492,4,"boss","Knight of the Closed Helm","floor_boss",1.0,1.0,"","5404:100%:2-4"),
     mk(501,5,"camp","Deserter","trash",1.1,1.1,"","5501:40%:1-2"),
     mk(502,5,"camp","Drill Construct","trash",1.4,1.0,"","5502:40%:1"),
     mk(503,5,"camp","Arena Hound","trash",0.8,1.1,"packs of 3","5501:30%:1"),
     mk(504,5,"camp","Pit Brawler","trash",1.2,1.3,"knockback 1","5501:25%:1"),
     mk(505,5,"camp","Ring Archer","trash",0.9,1.1,"ranged","5501:30%:1"),
     mk(506,5,"labyrinth","Sand Golem","trash",1.8,1.2,"","5502:30%:1;5503:2%:1"),
     mk(551,5,"camp","Deserter Lieutenant","elite",1.0,1.0,"","5503:35%:1-2;recipe_scrap_keen_f5:3%:1"),
     mk(571,5,"secret","Deserter Captain","mini",1.0,1.0,"secret s50","5503:100%:2-3"),
     mk(572,5,"secret","Cracked Copy","optional",1.0,1.0,"secret s53, instanced","5504:50%:1;5901:10%:1"),
     mk(591,5,"pass","Arena Warden","field_boss",1.0,1.0,"","5504:100%:1"),
     mk(592,5,"boss","Empty Colossus","floor_boss",1.0,1.0,"splits at 50%","5504:100%:2-4"),
]
# Starter Fields (22_CORE_DETAILS): levels 1-8 in ~45 min, generous XP per HP
for mid,nm,hp,xp,dmg in [(1001,"Field Rat",25,9,6),(1002,"Hopper Toad",40,14,8),(1003,"Sproutling",55,19,10)]:
    M.append([mid,1,"starter",nm,"trash",hp,xp,dmg,0,2,30,"5101:15%:1","Starter Fields, Guarded zone"])
# Apex spawns (owner input): over-tuned, self-healing, best XP per HP on the floor
APEX=[(1181,1,"Stonehorn Ram"),(1281,2,"Mesa Wyrmling"),(1381,3,"Grove Hydraling"),(1481,4,"Siege Beast"),(1581,5,"Undying Champion")]
for mid,fl,nm in APEX:
    f=FLOOR[fl]; base=sum(f["hp"])/2
    band_mid=sum(f["band"])/2; php=150+band_mid*11
    M.append([mid,fl,"apex",nm,"apex",int(round(base*3.5,-1)),int(round(f["xp"]*4.5)),int(php/14*1.4),int(f["col"]*3*0.5),int(f["col"]*3*1.5)+1,60,"keen mat of floor:4%:1;common mats of floor:60%:1-2","self-heal; Contested zone; see 11 Apex spawns"])
ECHO=[]
for r in M:
    if r[4]=="floor_boss":
        f=FLOOR[r[1]]; dps=(sum(f["hp"])/2)*f["kph"]/3600*2.5
        ECHO.append([r[0]+5000,r[1],"Echo of "+r[3],int(round(dps*4*240,-2)),int(r[6]*0.25),"party of 4, 8-min enrage, lockout 20h per character per floor","Tempered mat 1-2; Spire Scrap 15% +5% per scrapless kill (per character)"])
w("echoes.csv",["monster_id","floor","name","hp","xp","rules","drops"],ECHO)
w("monsters.csv",["monster_id","tuned_floor","zone","name","role","hp","xp","melee_max","col_min","col_max","respawn_s","drops(item:chance:qty)","notes"],M)

PATHS=[("vanguard","Arming Sword"),("cleaver","Greatsword"),("shade","Dagger Pair"),("slinger","Shortbow"),("arcanist","Focus")]
PFX={1:"Hearth",2:"Ridge",3:"Rootwood",4:"Lakesteel",5:"Ringforged"}
ATK={1:14,2:22,3:30,4:38,5:46}
PRICE={1:400,2:1500,3:3500,4:6500,5:10000}
wp=[]; iid=6000
for f in range(1,6):
    for p,base in PATHS:
        iid+=1; atk=ATK[f]
        if p=="cleaver": atk=int(atk*1.35)
        if p=="shade": atk=int(atk*0.72)
        if p=="slinger": atk=int(atk*0.85)
        wp.append([iid,f,p,f"{PFX[f]} {base}",atk,PRICE[f],int(PRICE[f]*0.2)])
    iid+=1
    wp.append([iid,f,"vanguard",f"{PFX[f]} Heater Shield",f"def {10+6*f}",int(PRICE[f]*0.6),int(PRICE[f]*0.12)])
w("weapons.csv",["item_id","floor","path","name","attack","npc_sell_price","npc_buy_price"],wp)

ARM=[("heavy","Vanguard, Cleaver",1.0),("light","Shade, Slinger",0.7),("robe","Arcanist",0.45)]
SLOTS=[("helm",0.2),("body",0.4),("legs",0.25),("boots",0.15)]
ar=[]; iid=7000
for f in range(1,6):
    for a,who,m in ARM:
        total=(8+7*f)*m
        for s,sw in SLOTS:
            iid+=1
            extra = f"focus regen +{4*f}%" if (a=="robe" and s=="body") else (f"dodge +{f}%" if (a=="light" and s=="body") else "")
            ar.append([iid,f,a,who,f"{PFX[f]} {a.title()} {s.title()}",s,max(1,round(total*sw)),int(PRICE[f]*0.6*sw*2),int(PRICE[f]*0.6*sw*0.4),extra])
w("armor.csv",["item_id","floor","class","for_paths","name","slot","armor","npc_sell_price","npc_buy_price","bonus"],ar)

CONS=[
 (8001,"Travel Bread","food",6,"regen 3 min","all towns"),
 (8002,"Smoked Ham","food",12,"regen 6 min","all towns"),
 (8003,"Hearth Stew","food",0,"crafted only (s4 recipe); regen 10 min, +5% stamina regen","crafted"),
 (8011,"Minor Salve","heal",45,"heals 70-110 HP; shared 2s cooldown","all towns"),
 (8012,"Salve","heal",110,"heals 220-300 HP","F2+ towns"),
 (8013,"Greater Salve","heal",250,"heals 480-620 HP","F4+ towns"),
 (8014,"Bandage","heal",15,"3s channel, 20% max HP, breaks on damage","all towns"),
 (8021,"Minor Tonic","resource",50,"restores 60-90 Stamina/Focus","all towns"),
 (8022,"Tonic","resource",120,"restores 160-220","F2+ towns"),
 (8023,"Greater Tonic","resource",260,"restores 340-440","F4+ towns"),
 (8031,"Basic Arrow","ammo",1,"atk 5; 70% recoverable","all towns"),
 (8032,"Broadhead","ammo",0,"crafted only; Pinshot ammo; atk 9","crafted"),
 (8033,"Signal Arrow","ammo",0,"crafted only; Mark ammo","crafted"),
 (8034,"Ironpoint Arrow","ammo",4,"atk 11","F3+ towns"),
 (8041,"Lantern","tool",80,"light radius 4","all towns"),
 (8042,"Rope","tool",30,"rope spots","all towns"),
 (8043,"Shovel","tool",30,"dig spots","all towns"),
 (8051,"Debt Chip","special",0,"clears one death's XP debt if used within 60s of that death; bound","s1 W5 weekly, s21 weekly"),
]
w("consumables.csv",["item_id","name","type","npc_sell_price","effect","where"],CONS)

SH=[]
def shop(npc,town,items):
    for it in items: SH.append([npc,town]+list(it))
base_sup=[("Travel Bread",6,""),("Smoked Ham",12,""),("Minor Salve",45,""),("Bandage",15,""),("Minor Tonic",50,""),("Basic Arrow",1,""),("Rope",30,""),("Shovel",30,""),("Lantern",80,"")]
shop("Marra the Quartermaster","Hearthgate",base_sup)
shop("Pell the Innkeeper","Millcross",[("Travel Bread",7,""),("Smoked Ham",13,""),("Minor Salve",48,""),("Bandage",16,""),("Basic Arrow",1,"")])
for f,town in [(2,"Highrest"),(3,"Rootwell"),(4,"Lakehold"),(5,"Ringhold")]:
    it=list(base_sup)+[("Salve",110,""),("Tonic",120,"")]
    if f>=3: it.append(("Ironpoint Arrow",4,""))
    if f>=4: it+=[("Greater Salve",250,""),("Greater Tonic",260,"")]
    shop(f"Quartermaster of {town}",town,it)
for f,town in [(1,"Hearthgate"),(2,"Highrest"),(3,"Rootwell"),(4,"Lakehold"),(5,"Ringhold")]:
    for r in wp:
        if r[1]==f: SH.append([f"Smith of {town}",town,r[3],r[5],f"buys back at {r[6]}"])
    for r in ar:
        if r[1]==f: SH.append([f"Armorer of {town}",town,r[4],r[7],f"buys back at {r[8]}"])
w("shops.csv",["npc","town","item","sell_price_col","note"],SH)

H=[]; hid=0
def houses(floor,district,kind,n,price,rent,size):
    global hid
    for i in range(n):
        hid+=1
        m = [0.75,1.0,1.4][i%3] if kind!="guildhall" else 1.0
        H.append([hid,floor,district,kind,f"{district} {kind} {i+1}",int(round(price*m,-2)),int(round(rent*m,-1)),size])
houses(1,"Hearthgate","cottage",24,18000,1000,"4x5 to 7x7")
houses(1,"Hearthgate","inn room",8,6000,400,"3x3")
houses(1,"Millcross","cottage",6,12000,800,"5x5")
houses(2,"Highrest","house",20,45000,2500,"5x6 to 8x8")
houses(3,"Rootwell","treehouse",16,70000,4000,"5x6 to 8x8")
houses(3,"Rootwell","guildhall",1,400000,20000,"18x14, 2 levels")
houses(4,"Lakehold","house",16,100000,5500,"5x6 to 8x8")
houses(5,"Ringhold","house",12,140000,7500,"6x6 to 9x9")
houses(5,"Ringhold","guildhall",1,800000,40000,"22x16, 3 levels")
w("houses.csv",["house_id","floor","district","kind","name","price_col","rent_col_per_week","footprint"],H)

# ---------------- secrets (content authored in tools/secrets_src.csv) ----------------
SEC_BASE={1:1500,2:3500,3:6000,4:10000,5:16000}; SEC_MUL={"Small":1,"Mid":2,"Large":4}
src=os.path.join(os.path.dirname(os.path.abspath(__file__)),"secrets_src.csv")
SR=[]
for r in csv.DictReader(open(src)):
    lump=SEC_BASE[int(r["floor"])]*SEC_MUL[r["tier"]]
    SR.append([r["secret_id"],r["floor"],r["name"],r["tier"],lump,int(lump*0.15),r["trigger"],r["non_holder_gate"],r["content"]])
assert len(SR)==60, "proof ships exactly 60 secrets"
w("secrets.csv",["secret_id","floor","name","tier","lump_sum_col","copy_price_col","trigger","non_holder_gate","content"],SR)

L=["# Economy check (generated by tools/gen_tables.py — do not edit)\n",
"Solo-equivalent active hunting at the floor band. Gross includes ~15% from NPC buyback of common materials.\n",
"| Floor | XP/h | Gross col/h | Supplies | Net col/h | Mid house = net hours | Weekly rent = net hours | Large secret = net hours |","|---|---|---|---|---|---|---|---|"]
BASE=SEC_BASE
HP_={1:18000,2:45000,3:70000,4:100000,5:140000}
RENT={1:1000,2:2500,3:4000,4:5500,5:7500}
fails=0
for f,d in FLOOR.items():
    xph=d["xp"]*d["kph"]; gross=d["col"]*d["kph"]*1.15; net=gross*(1-d["sup"])
    hh,rh,sh=HP_[f]/net,RENT[f]/net,BASE[f]*4/net
    ok = 15<=hh<=25 and 0.8<=rh<=1.5 and 5<=sh<=12
    fails += (not ok)
    L.append(f"| {f} | {xph:,.0f} | {gross:,.0f} | {int(d['sup']*100)}% | {net:,.0f} | {hh:.1f} | {rh:.1f} | {sh:.1f} |" + ("" if ok else " **OUT OF TARGET**"))
L.append("\nTargets (07_ECONOMY): mid house 15–25 net hours; rent 0.8–1.5 net hours per week; large secret 5–12 net hours.\n")
L.append("## Level pacing\n\n| Band top level | Total XP | Target cumulative active hours | Avg XP/h needed in that stretch | Floor XP/h supplied (solo) |\n|---|---|---|---|---|")
pL,pH=1,0
for i,(lv,h) in enumerate(HOURS_TO.items(), start=1):
    need=(xp_for(lv)-xp_for(pL))/(h-pH)
    sup=FLOOR[i]["xp"]*FLOOR[i]["kph"]
    L.append(f"| {lv} | {xp_for(lv):,} | {h} | {need:,.0f} | {sup:,} |")
    pL,pH=lv,h
L.append("\nSupplied XP/h within ±25% of needed is acceptable.")
L.append("\n## Party vs solo (owner requirement: team hunting must pay more per person)\n\n| Party | Kill-speed factor vs solo | XP mult | Per-person XP/h vs solo | Col mult | Per-person col/h vs solo |\n|---|---|---|---|---|---|")
for n,distinct,k in [(2,2,1.6),(3,3,2.1),(4,4,2.5),(4,2,2.3)]:
    mx=1+0.30*(n-1)+0.10*(distinct-1); mc=1+0.15*(n-1)
    px=k*mx/n; pc=k*mc/n
    if px<1.05: fails+=1
    L.append(f"| {n} players, {distinct} paths | {k} | {mx:.2f} | {px:.2f}x | {mc:.2f} | {pc:.2f}x |")
L.append("\nGate: every party row must give at least 1.05x solo XP per person. Party col per person is intentionally near solo; group content (apex, labyrinth, Echoes) adds the rest.")
open(os.path.join(OUT,"economy_check.md"),"w").write("\n".join(L)+"\n")
print("ok",len(M),"monsters",len(wp),"weapons",len(ar),"armor",len(SH),"shop rows",len(H),"houses","fails",fails)

import sys
if fails: sys.exit("economy_check: %d floor(s) out of target" % fails)
