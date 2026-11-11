# NPC dialogue translations (roadmap 6.3b), merged into the tables of tools/gen_i18n.py.
# NPC lines are looked up like server messages: exact sentence first, then Lua patterns.
# Words in {braces} are keywords the player must type, so they stay English in every language.
# Each row: (English, Portuguese-Brazil, Spanish).

VOC = {
    "Vanguards hold the front line with sword, axe or club and a shield.": (
        "Vanguardas seguram a linha de frente com espada, machado ou clava e um escudo.",
        "Los Vanguardias mantienen la primera línea con espada, hacha o maza y un escudo."),
    "Rangers strike from afar with bow, crossbow or spear.": (
        "Rangers atacam de longe com arco, besta ou lança.",
        "Los Rangers atacan desde lejos con arco, ballesta o lanza."),
    "Arcanists wield wands and fill the field with fire and lightning.": (
        "Arcanistas empunham varinhas e enchem o campo de fogo e relâmpagos.",
        "Los Arcanistas empuñan varitas y llenan el campo de fuego y rayos."),
    "Mystics wield rods, heal their allies and command nature.": (
        "Místicos empunham cajados, curam seus aliados e comandam a natureza.",
        "Los Místicos empuñan bastones, curan a sus aliados y dominan la naturaleza."),
}

MODE = {
    "Normal: the tower's usual rules. Death costs experience, as it always has.": (
        "Normal: as regras comuns da torre. A morte custa experiência, como sempre.",
        "Normal: las reglas habituales de la torre. La muerte cuesta experiencia, como siempre."),
    "Hardcore: deaths cost half again as much, but you earn 25% more experience and 15% more loot.": (
        "Hardcore: as mortes custam 50% a mais, mas você ganha 25% mais experiência e 15% mais saque.",
        "Hardcore: las muertes cuestan un 50% más, pero ganas un 25% más de experiencia y un 15% más de botín."),
    "Death Game: if a monster or the tower kills you, this character is gone for good. In return: 50% more experience, 30% more loot, and honours no one else can earn. Another player can never end you this way.": (
        "Jogo da Morte: se um monstro ou a torre matar você, este personagem se perde para sempre. Em troca: 50% mais experiência, 30% mais saque e honras que ninguém mais pode ganhar. Outro jogador nunca pode acabar com você assim.",
        "Juego de la Muerte: si un monstruo o la torre te mata, este personaje se pierde para siempre. A cambio: un 50% más de experiencia, un 30% más de botín y honores que nadie más puede ganar. Otro jugador nunca puede acabar contigo así."),
}

EXACT = [
    ("Good. Now choose how you will live in the tower: {normal}, {hardcore} or {death game}? You may always step down later, but never up.",
     "Bom. Agora escolha como você viverá na torre: {normal}, {hardcore} ou {death game}? Você sempre poderá descer depois, mas nunca subir.",
     "Bien. Ahora elige cómo vivirás en la torre: {normal}, {hardcore} o {death game}. Siempre podrás bajar después, pero nunca subir."),
    ("Then choose again: {vanguard}, {ranger}, {arcanist} or {mystic}?",
     "Então escolha de novo: {vanguard}, {ranger}, {arcanist} ou {mystic}?",
     "Entonces elige de nuevo: {vanguard}, {ranger}, {arcanist} o {mystic}."),
    ("Something is wrong with your papers. Speak to a gamemaster.",
     "Há algo errado com seus papéis. Fale com um gamemaster.",
     "Hay algo mal con tus papeles. Habla con un gamemaster."),
    ("May the tower be kind to you.", "Que a torre seja gentil com você.", "Que la torre sea amable contigo."),
    ("Come back when you are ready to choose.", "Volte quando estiver pronto para escolher.", "Vuelve cuando estés listo para elegir."),
    ("You already live by the gentlest rules the tower has.",
     "Você já vive pelas regras mais brandas que a torre tem.",
     "Ya vives con las reglas más suaves que tiene la torre."),
    ("No perk is waiting for you. Perks come from finishing every story quest on a floor.",
     "Nenhuma vantagem espera por você. Vantagens vêm de terminar todas as missões da história de um andar.",
     "No te espera ninguna ventaja. Las ventajas llegan al terminar todas las misiones de historia de un piso."),
]

RULES = [
    ("^Welcome to Hearthgate, (.-)%. Before you climb, choose your path: {vanguard}, {ranger}, {arcanist} or {mystic}%?$",
     "Bem-vindo a Hearthgate, %1. Antes de subir, escolha seu caminho: {vanguard}, {ranger}, {arcanist} ou {mystic}?",
     "Bienvenido a Hearthgate, %1. Antes de subir, elige tu camino: {vanguard}, {ranger}, {arcanist} o {mystic}."),
    ("^Back again, (.-)%? If the tower weighs too heavy, I can let you {step down} to an easier way of living%.$",
     "De volta, %1? Se a torre pesar demais, posso deixar você {step down} para um jeito de viver mais fácil.",
     "¿Otra vez por aquí, %1? Si la torre pesa demasiado, puedo dejarte {step down} a una forma de vivir más fácil."),
    ("^It is written: (.-), (.-)%. The temple is through the gate%. Climb well%.$",
     "Está escrito: %1, %2. O templo fica depois do portão. Suba bem.",
     "Está escrito: %1, %2. El templo está al otro lado de la puerta. Que subas bien."),
    ("^It is written%. You now live by the (.-) rules%.$",
     "Está escrito. Agora você vive pelas regras %1.",
     "Está escrito. Ahora vives según las reglas %1."),
    ("^You may step down to (.-)%. This can never be undone%.$",
     "Você pode descer para %1. Isto nunca pode ser desfeito.",
     "Puedes bajar a %1. Esto nunca se puede deshacer."),
    ("^Step down to (.-) forever%? {yes} or {no}%?$",
     "Descer para %1 para sempre? {yes} ou {no}?",
     "¿Bajar a %1 para siempre? {yes} o {no}."),
    ("^It is written: (.-)%.$", "Está escrito: %1.", "Está escrito: %1."),
    ("^Floor (%d+) perk%. Choose one: (.+)$", "Vantagem do Andar %1. Escolha uma: %2", "Ventaja del Piso %1. Elige una: %2"),
]

# the vocation and mode explanations are followed by a fixed question
for text, (pt, es) in VOC.items():
    q = "Will you walk the path of the (%a+)%? {yes} or {no}%?"
    RULES.append(("^" + text.replace(".", "%.").replace("(", "%(").replace(")", "%)") + " " + q + "$",
                  pt + " Você vai seguir o caminho do %1? {yes} ou {no}?",
                  es + " ¿Seguirás el camino del %1? {yes} o {no}."))
for text, (pt, es) in MODE.items():
    # plain-text lines: escape Lua pattern characters
    esc = "".join("%" + c if c in "^$()%.[]*+-?" else c for c in text)
    RULES.append(("^" + esc + " Is that your choice%? {yes} or {no}%?$",
                  pt + " É a sua escolha? {yes} ou {no}?",
                  es + " ¿Es tu elección? {yes} o {no}."))
