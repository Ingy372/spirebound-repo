# Builds server/data-spirebound/lib/spirebound/i18n_pt.lua and i18n_es.lua from one table
# (pt and es sit side by side so none is forgotten). Kept in the repo as tools/gen_i18n.py.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "server", "data-spirebound", "lib", "spirebound")

# (English, Portuguese-Brazil, Spanish)
EXACT = [
 ("Put the construction kit on the floor first.", "Coloque o kit de construção no chão primeiro.", "Pon primero el kit de construcción en el suelo."),
 ("You may construct this only inside a house.", "Você só pode construir isto dentro de uma casa.", "Solo puedes construir esto dentro de una casa."),
 ("It is empty.", "Está vazio.", "Está vacío."),
 ("Your training room is ready. Use training weapons on the dummy, just like the one in town.", "Sua sala de treino está pronta. Use armas de treino no boneco, como o da cidade.", "Tu sala de entrenamiento está lista. Usa armas de entrenamiento en el muñeco, igual que el del pueblo."),
 ("Something is biting! Use your rod again, quickly!", "Algo mordeu a isca! Use a vara de novo, rápido!", "¡Algo ha picado! ¡Usa la caña otra vez, rápido!"),
 ("You are out. Well fought!", "Você foi eliminado. Bem lutado!", "Estás fuera. ¡Bien peleado!"),
 ("Nobody dies in the Arena, Death Game climber. You are safe here.", "Ninguém morre na Arena, escalador do Jogo da Morte. Você está seguro aqui.", "Nadie muere en la Arena, escalador del Juego de la Muerte. Aquí estás a salvo."),
 ("You left the sign-up list.", "Você saiu da lista de inscrição.", "Saliste de la lista de inscripción."),
 ("Your Hardcore death penalty for this skill is paid off.", "A penalidade de morte Hardcore desta habilidade foi paga.", "La penalización de muerte Hardcore de esta habilidad está saldada."),
 ("Another player struck you moments before your death. The tower spares your life this time.", "Outro jogador atingiu você momentos antes da sua morte. A torre poupa sua vida desta vez.", "Otro jugador te golpeó momentos antes de tu muerte. La torre te perdona la vida esta vez."),
 ("Hardcore: your death costs extra training. Your next skill and magic progress goes to paying it off first.", "Hardcore: sua morte custa treino extra. Seu próximo progresso de habilidade e magia será usado primeiro para pagar isso.", "Hardcore: tu muerte cuesta entrenamiento extra. Tu próximo progreso de habilidad y magia se usará primero para saldarlo."),
 ("Your amulet of loss shatters. It cannot protect a Hardcore climber.", "Seu amuleto da perda se despedaça. Ele não protege um escalador Hardcore.", "Tu amuleto de pérdida se hace añicos. No protege a un escalador Hardcore."),
 ("Your house is already a Fortune Hall.", "Sua casa já é um Salão da Fortuna.", "Tu casa ya es un Salón de la Fortuna."),
 ("Your house is now a Fortune Hall. Players inside can bet with !dice <amount> high|low. Gold only; the hall keeps 5%.", "Sua casa agora é um Salão da Fortuna. Quem estiver dentro pode apostar com !dice <valor> high|low. Apenas ouro; o salão fica com 5%.", "Tu casa ahora es un Salón de la Fortuna. Quienes estén dentro pueden apostar con !dice <cantidad> high|low. Solo oro; el salón se queda con el 5%."),
 ("!mannequin save <1-3> stores your outfit, !mannequin wear <1-3> puts it on.", "!mannequin save <1-3> guarda seu visual, !mannequin wear <1-3> o veste.", "!mannequin save <1-3> guarda tu atuendo, !mannequin wear <1-3> te lo pone."),
 ("Press J to open your Journal: secrets, fishing log, quests, hunting task, top climbers and the Memorial.", "Pressione J para abrir seu Diário: segredos, registro de pesca, missões, tarefa de caça, melhores escaladores e o Memorial.", "Pulsa J para abrir tu Diario: secretos, registro de pesca, misiones, tarea de caza, mejores escaladores y el Memorial."),
 ("You murdered someone near town. The guards will hunt you for 30 minutes.", "Você assassinou alguém perto da cidade. Os guardas vão caçar você por 30 minutos.", "Asesinaste a alguien cerca del pueblo. Los guardias te perseguirán durante 30 minutos."),
 ("You are now a murderer (red). Towns, shops and boss rooms are closed to you, and death will cost you everything you carry.", "Você agora é um assassino (vermelho). Cidades, lojas e salas de chefes estão fechadas para você, e a morte custará tudo o que você carrega.", "Ahora eres un asesino (rojo). Los pueblos, las tiendas y las salas de jefe están cerradas para ti, y la muerte te costará todo lo que llevas."),
 ("The grate is rusted shut, but you hear water and voices far below. (The Underkeep opens in a later update.)", "A grade está enferrujada e fechada, mas você ouve água e vozes bem lá embaixo. (O Subforte abre numa atualização futura.)", "La reja está oxidada y cerrada, pero oyes agua y voces muy abajo. (La Subfortaleza abrirá en una actualización futura.)"),
 ("Fresh tracks in the mud. Old Tusk was here recently.", "Pegadas frescas na lama. Old Tusk esteve aqui há pouco.", "Huellas frescas en el barro. Old Tusk estuvo aquí hace poco."),
 ("The shrine's chest holds 1,000 gold, and its guardians wake!", "O baú do santuário guarda 1.000 de ouro, e seus guardiões despertam!", "¡El cofre del santuario guarda 1.000 de oro y sus guardianes despiertan!"),
 ("The Siege begins! Hold the throne room with only your guild inside to score. Everyone has the same health, hits and heals.", "O Cerco começou! Segure a sala do trono só com a sua guilda lá dentro para pontuar. Todos têm a mesma vida, dano e cura.", "¡Comienza el Asedio! Mantén la sala del trono solo con tu gremio dentro para puntuar. Todos tienen la misma vida, golpes y curas."),
 ("You left the Siege list.", "Você saiu da lista do Cerco.", "Saliste de la lista del Asedio."),
 ("The Twin Fang Warden rises. Defeat it alone to earn the second blade.", "O Guardião da Presa Gêmea desperta. Derrote-o sozinho para ganhar a segunda lâmina.", "El Guardián del Colmillo Gemelo se alza. Derrótalo en solitario para ganar la segunda hoja."),
 ("Too late. The third Twin Fang was claimed moments ago.", "Tarde demais. A terceira Presa Gêmea foi reivindicada há pouco.", "Demasiado tarde. El tercer Colmillo Gemelo fue reclamado hace un momento."),
 ("The strongbox is empty. It refills every day.", "O cofre está vazio. Ele se enche todos os dias.", "El cofre está vacío. Se rellena cada día."),
 ("You open the old strongbox. Come back tomorrow for more.", "Você abre o velho cofre. Volte amanhã para mais.", "Abres el viejo cofre. Vuelve mañana para más."),
 ("Cavebot on: you earn 45% experience and half the loot while it runs.", "Cavebot ligado: você ganha 45% de experiência e metade do saque enquanto ele roda.", "Cavebot activado: ganas el 45% de experiencia y la mitad del botín mientras funcione."),
 ("Cavebot off. Full rewards return in 10 minutes.", "Cavebot desligado. As recompensas completas voltam em 10 minutos.", "Cavebot desactivado. Las recompensas completas vuelven en 10 minutos."),
 # Journal window text
 ("No quests yet. Talk to the people of Hearthgate.", "Ainda sem missões. Fale com o povo de Hearthgate.", "Aún no hay misiones. Habla con la gente de Hearthgate."),
 ("No active task. Ask Taskmaster Rhen in Hearthgate.", "Nenhuma tarefa ativa. Pergunte ao Mestre de Tarefas Rhen em Hearthgate.", "Ninguna tarea activa. Pregunta al Maestro de Tareas Rhen en Hearthgate."),
 ("No names yet. May it stay that way.", "Nenhum nome ainda. Que continue assim.", "Aún no hay nombres. Ojalá siga así."),
 ("Report to Taskmaster Rhen.", "Apresente-se ao Mestre de Tarefas Rhen.", "Informa al Maestro de Tareas Rhen."),
 ("Ready to report", "Prontas para entregar", "Listas para informar"),
 ("In progress", "Em andamento", "En curso"),
 ("Available", "Disponíveis", "Disponibles"),
 ("Completed", "Concluídas", "Completadas"),
 ("Secrets", "Segredos", "Secretos"),
 ("Fishing log", "Registro de pesca", "Registro de pesca"),
 ("Quests", "Missões", "Misiones"),
 ("Hunting task", "Tarefa de caça", "Tarea de caza"),
 ("Top climbers", "Melhores escaladores", "Mejores escaladores"),
 ("The Memorial", "O Memorial", "El Memorial"),
]

# (Lua pattern, Portuguese replacement, Spanish replacement); %1.. are captures
RULES = [
 ("^You fished up (.+)%.$", "Você pescou %1.", "Pescaste %1."),
 ("^You brought down (.+)%.$", "Você derrubou %1.", "Derribaste a %1."),
 ("^You drove (.+) back to their gate%.$", "Você fez %1 recuar até o portão.", "Hiciste retroceder a %1 hasta su puerta."),
 ("^You earned the title (.+)%.$", "Você ganhou o título %1.", "Has ganado el título %1."),
 ("^Weekend bonus: (.+)!$", "Bônus de fim de semana: %1!", "¡Bonificación de fin de semana: %1!"),
 ("^You earned a Boss Sigil: (.-)%. Use it in a house Summoning Circle %(!summon%)%.$", "Você ganhou um Sigilo de Chefe: %1. Use-o no Círculo de Invocação de uma casa (!summon).", "Has ganado un Sello de Jefe: %1. Úsalo en el Círculo de Invocación de una casa (!summon)."),
 ("^Mannequin (%d+) now wears your outfit%.$", "O manequim %1 agora veste o seu visual.", "El maniquí %1 ahora lleva tu atuendo."),
 ("^You collect (%d+) worms from the pond's edge%.$", "Você coleta %1 minhocas na beira do lago.", "Recoges %1 gusanos a la orilla del estanque."),
 ("^Your guild needs at least (%d+) fighters for the Siege%.$", "Sua guilda precisa de pelo menos %1 lutadores para o Cerco.", "Tu gremio necesita al menos %1 luchadores para el Asedio."),
 ("^Task complete: (%d+) (.-)s%. Report to any taskmaster %(Floor 1: Taskmaster Rhen in Hearthgate's Hunters' Hall%)%.$", "Tarefa concluída: %1 %2. Apresente-se a qualquer mestre de tarefas (Andar 1: Mestre de Tarefas Rhen, no Salão dos Caçadores de Hearthgate).", "Tarea completada: %1 %2. Informa a cualquier maestro de tareas (Piso 1: Maestro de Tareas Rhen, en el Salón de Cazadores de Hearthgate)."),
 ("^Task: (%d+) of (%d+) (.-)s%.$", "Tarefa: %1 de %2 %3.", "Tarea: %1 de %2 %3."),
 ("^You finished every story quest on Floor (%d+)%. Registrar Maelis in Hearthgate can grant you a perk: say 'perk'%.$", "Você terminou todas as missões da história do Andar %1. A Registradora Maelis em Hearthgate pode lhe dar uma vantagem: diga 'perk'.", "Has terminado todas las misiones de historia del Piso %1. La Registradora Maelis en Hearthgate puede darte una ventaja: di 'perk'."),
 ("^You caught a (.-) %(([%d%.]+) kg%)! New in your fishing log%.$", "Você pescou %1 (%2 kg)! Novo no seu registro de pesca.", "¡Has pescado %1 (%2 kg)! Nuevo en tu registro de pesca."),
 ("^You caught a (.-) %(([%d%.]+) kg%)!$", "Você pescou %1 (%2 kg)!", "¡Has pescado %1 (%2 kg)!"),
 ("^Floor (%d+) was already cleared%.$", "O Andar %1 já foi limpo.", "El Piso %1 ya estaba despejado."),
 ("^You discovered (.-)%. The Info Broker would pay for this%.$", "Você descobriu %1. O Corretor de Informações pagaria por isso.", "Has descubierto %1. El Corredor de Información pagaría por esto."),
 ("^You have found (%d+) of (%d+) secrets%. Sell what you know to the Info Broker in Hearthgate%.$", "Você encontrou %1 de %2 segredos. Venda o que sabe ao Corretor de Informações em Hearthgate.", "Has encontrado %1 de %2 secretos. Vende lo que sabes al Corredor de Información en Hearthgate."),
 ("^Fish kinds in your log: (%d+) of (%d+)%.$", "Tipos de peixe no seu registro: %1 de %2.", "Tipos de pez en tu registro: %1 de %2."),
 ("^Language set to (.+)%.$", "Idioma definido: %1.", "Idioma establecido: %1."),
 ("^Floor (%d+)$", "Andar %1", "Piso %1"),
 ("^(%s*)%[x%] Floor (%d+) %- (.-) %((%a+)%) %- found$", "%1[x] Andar %2 - %3 (%4) - encontrado", "%1[x] Piso %2 - %3 (%4) - encontrado"),
 ("^%[ %] Floor (%d+) %- %?%?%? %((%a+)%)(.*)$", "[ ] Andar %1 - ??? (%2)%3", "[ ] Piso %1 - ??? (%2)%3"),
 ("^(%s*)%[x%] (.-) %- caught (%d+), best ([%d%.]+) kg$", "%1[x] %2 - pescados %3, melhor %4 kg", "%1[x] %2 - pescados %3, mejor %4 kg"),
 ("^(%d+) of (%d+) defeated%.$", "%1 de %2 derrotados.", "%1 de %2 derrotados."),
 ("^Reward: (%d+) gold, (%d+) task points?%.$", "Recompensa: %1 de ouro, %2 ponto(s) de tarefa.", "Recompensa: %1 de oro, %2 punto(s) de tarea."),
]

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_npc  # NPC dialogue (roadmap 6.3b)
EXACT.extend(i18n_npc.EXACT)
RULES.extend(i18n_npc.RULES)

HEADERS = {
    "pt": "Portuguese (Brazil)",
    "es": "Spanish",
}


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    for lang, idx in (("pt", 1), ("es", 2)):
        out = [
            f"-- {HEADERS[lang]} text (roadmap 6.3). GENERATED by tools/gen_i18n.py: edit the table there and rerun.",
            "-- Keys are the exact English messages; rules are Lua patterns with %1 captures.",
            "SpireI18n.register(" + lua_str(lang) + ", {",
        ]
        for row in EXACT:
            out.append(f"\t[{lua_str(row[0])}] = {lua_str(row[idx])},")
        out.append("}, {")
        for row in RULES:
            out.append(f"\t{{ {lua_str(row[0])}, {lua_str(row[idx])} }},")
        out.append("})")
        with open(os.path.join(OUT, f"i18n_{lang}.lua"), "w", encoding="utf8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
    print(f"i18n: {len(EXACT)} sentences, {len(RULES)} patterns, 2 languages")


if __name__ == "__main__":
    main()
